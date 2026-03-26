import os
import glob
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# 导入你写好的数据加载模块和模型架构
from data_loader import create_dataloaders
from models import MultimodalFatigueModel

def main():
    # ==========================================
    # 1. 超参数设置
    # ==========================================
    BATCH_SIZE = 16
    LEARNING_RATE = 1e-3
    NUM_EPOCHS = 10
    WINDOW_SIZE_SEC = 2  # 滑动窗口大小（秒），和 data_loader 保持一致
    NUM_CLASSES = 3      # 分类数 (例如: 0-正常, 1-轻度疲劳, 2-重度疲劳)
    
    # 检查是否有可用的 GPU，没有则使用 CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"当前使用的计算设备: {device}")

    # ==========================================
    # 2. 准备数据集和 DataLoader
    # ==========================================
    # 自动搜索当前目录下的所有 csv 文件
    csv_files = glob.glob("*.csv")
    if not csv_files:
        print("❌ 当前目录下没有找到任何 .csv 数据文件，请放入数据后再运行。")
        return

    # 为了演示，我们将搜索到的 csv 文件简单地划分为训练集和测试集
    # 如果只有一个文件，训练集和测试集就共用这一个（仅做代码跑通测试用）
    if len(csv_files) >= 2:
        train_csv_paths = csv_files[:-1]
        test_csv_paths = [csv_files[-1]]
    else:
        print("⚠️ 警告：只找到一个 CSV 文件，训练集和测试集将使用同一文件（仅限测试跑通）。")
        train_csv_paths = csv_files
        test_csv_paths = csv_files

    print(f"训练集文件: {train_csv_paths}")
    print(f"测试集文件: {test_csv_paths}")

    # 使用你写好的快捷函数创建 DataLoader
    train_loader, test_loader = create_dataloaders(
        train_csv_paths, 
        test_csv_paths, 
        batch_size=BATCH_SIZE, 
        window_size_sec=WINDOW_SIZE_SEC
    )

    NUM_CLASSES = getattr(train_loader.dataset, "num_classes", None)
    if NUM_CLASSES is None:
        raise RuntimeError("未从数据集中获取到 num_classes，请检查 data_loader.py 的标签映射逻辑。")
    print(f"自动推断类别数 NUM_CLASSES = {NUM_CLASSES}")
    if getattr(train_loader.dataset, "label_to_index", None) is not None:
        print(f"原始标签 -> 类别索引 映射: {train_loader.dataset.label_to_index}")
    
    # 检查数据加载器是否为空
    if len(train_loader) == 0:
        print("❌ 训练 DataLoader 为空，请检查 CSV 数据解析逻辑或数据长度！")
        return

    # ==========================================
    # 3. 初始化模型、损失函数和优化器
    # ==========================================
    model = MultimodalFatigueModel(num_classes=NUM_CLASSES).to(device)
    
    # 多分类问题通常使用交叉熵损失函数
    criterion = nn.CrossEntropyLoss()
    
    # 优化器选用 Adam
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

    # ==========================================
    # 4. 开始标准训练循环
    # ==========================================
    print("\n🚀 开始训练模型...")
    for epoch in range(NUM_EPOCHS):
        model.train()  # 设置模型为训练模式 (启用 Dropout 和 BatchNorm 更新)
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        # 遍历训练数据批次
        for batch_idx, (eeg_data, fnirs_data, labels) in enumerate(train_loader):
            # 将数据和标签转移到指定的设备 (GPU/CPU)
            eeg_data = eeg_data.to(device)
            fnirs_data = fnirs_data.to(device)
            labels = labels.to(device)

            # --- 核心 3 步：前向传播、计算损失、反向传播 ---
            optimizer.zero_grad()  # 1. 梯度清零
            
            outputs = model(eeg_data, fnirs_data)  # 2. 前向传播
            loss = criterion(outputs, labels)      # 3. 计算损失
            
            loss.backward()  # 4. 反向传播计算梯度
            optimizer.step() # 5. 更新模型权重

            # 统计损失和准确率
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1) # 获取概率最大的类别作为预测结果
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

        # 计算这一轮的平均训练损失和准确率
        epoch_train_loss = running_loss / len(train_loader)
        epoch_train_acc = 100 * correct_train / total_train

        # ==========================================
        # 5. 验证阶段 (每个 Epoch 结束后在测试集上评估)
        # ==========================================
        model.eval()  # 设置模型为评估模式 (关闭 Dropout，固定 BatchNorm)
        correct_test = 0
        total_test = 0
        running_test_loss = 0.0

        with torch.no_grad():  # 评估时不需要计算梯度，节省显存并加速
            for eeg_data, fnirs_data, labels in test_loader:
                eeg_data = eeg_data.to(device)
                fnirs_data = fnirs_data.to(device)
                labels = labels.to(device)

                outputs = model(eeg_data, fnirs_data)
                loss = criterion(outputs, labels)
                running_test_loss += loss.item()

                _, predicted = torch.max(outputs.data, 1)
                total_test += labels.size(0)
                correct_test += (predicted == labels).sum().item()

        # 计算这一轮的平均测试损失和准确率
        epoch_test_loss = running_test_loss / len(test_loader) if len(test_loader) > 0 else 0
        epoch_test_acc = 100 * correct_test / total_test if total_test > 0 else 0

        # 打印当前 Epoch 的训练概况
        print(f"Epoch [{epoch+1}/{NUM_EPOCHS}] "
              f"| Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:.2f}% "
              f"| Test Loss: {epoch_test_loss:.4f} | Test Acc: {epoch_test_acc:.2f}%")

    # ==========================================
    # 6. 保存模型权重
    # ==========================================
    save_path = "multimodal_fatigue_model.pth"
    torch.save(model.state_dict(), save_path)
    print(f"\n✅ 训练完成！模型已保存至: {save_path}")

if __name__ == "__main__":
    main()
