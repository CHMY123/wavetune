import torch
import flwr as fl
import argparse
import os
import sys
import glob
import torch.optim as optim
import torch.nn as nn
import numpy as np
from tqdm import tqdm

# 添加上级目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import MultimodalFatigueModel
from data_loader import DualBranchFatigueDataset, create_dataloaders

class SuperNodeClient(fl.client.Client):
    def __init__(self, client_id, data_path, batch_size=8, epochs=1, use_gpu=True):
        self.client_id = client_id
        self.data_path = data_path
        self.batch_size = batch_size
        self.epochs = epochs
        self.use_gpu = use_gpu and torch.cuda.is_available()
        
        self.device = torch.device("cuda" if self.use_gpu else "cpu")
        print(f"[LOG] 使用设备: {self.device}")
        
        self.model = MultimodalFatigueModel(num_classes=3).to(self.device)
        print("[LOG] 模型加载完成")
        
        self.train_loader, self.test_loader = self._load_data()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        print("[LOG] 初始化损失函数与优化器...")
        print(f"[LOG] 客户端 {self.client_id} 初始化完成 ✅")
    
    def _load_data(self):
        csv_files = glob.glob(os.path.join(self.data_path, "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"未在 {self.data_path} 找到 CSV 文件")
        
        print(f"[LOG] 客户端 {self.client_id} 加载了 {len(csv_files)} 个数据文件")
        print("✅ 使用完整数据集进行训练")
        
        # 简单划分训练和测试数据
        if len(csv_files) >= 2:
            train_csv = csv_files[:-1]
            test_csv = [csv_files[-1]]
        else:
            train_csv = csv_files
            test_csv = csv_files
        
        # 使用1秒窗口大小
        window_size_sec = 1
        max_data_points = None  # 使用完整数据集
        
        # 创建数据加载器，使用较小的批量大小
        train_loader, test_loader = create_dataloaders(
            train_csv, 
            test_csv, 
            batch_size=self.batch_size,
            window_size_sec=window_size_sec,  # 1秒窗口
            max_data_points=max_data_points  # 使用完整数据集
        )
        
        print(f"[LOG] 训练集大小: {len(train_loader.dataset)}")
        print(f"[LOG] 测试集大小: {len(test_loader.dataset)}")
        
        return train_loader, test_loader
    
    def get_parameters(self, ins):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]
    
    def fit(self, ins):
        # 加载全局模型参数
        parameters = ins.parameters
        config = ins.config
        
        print("[LOG] 加载服务器下发的全局模型参数...")
        
        # 修复：使用fl.common.parameters_to_ndarrays转换参数
        try:
            # 尝试新API
            params_ndarrays = fl.common.parameters_to_ndarrays(parameters)
        except:
            # 兼容旧API
            try:
                params_ndarrays = parameters.ndarrays
            except:
                # 直接使用parameters作为ndarrays
                params_ndarrays = parameters
        
        state_dict = {}
        for k, v in zip(self.model.state_dict().keys(), params_ndarrays):
            state_dict[k] = torch.tensor(v).to(self.device)
        self.model.load_state_dict(state_dict)
        
        # 本地训练
        self.model.train()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        # 早停机制
        best_loss = float('inf')
        patience = 2
        patience_counter = 0
        
        print(f"\n=============================================")
        print(f"[LOG] 客户端 {self.client_id} 开始本地训练 🚀")
        
        for epoch in range(self.epochs):
            epoch_loss = 0
            epoch_correct = 0
            epoch_samples = 0
            
            # 使用进度条
            print(f"\n📈 客户端 {self.client_id} Epoch {epoch+1}/{self.epochs}")
            
            # 批量处理
            with tqdm(total=len(self.train_loader), desc="训练进度", unit="batch") as pbar:
                for batch_idx, (eeg_data, fnirs_data, labels) in enumerate(self.train_loader):
                    # 检查标签值范围
                    if torch.any(labels < 0) or torch.any(labels >= 3):
                        print(f"⚠️  发现无效标签值: {labels}")
                        # 过滤无效标签
                        valid_mask = (labels >= 0) & (labels < 3)
                        if torch.sum(valid_mask) == 0:
                            continue
                        eeg_data = eeg_data[valid_mask]
                        fnirs_data = fnirs_data[valid_mask]
                        labels = labels[valid_mask]
                    
                    eeg_data = eeg_data.to(self.device)
                    fnirs_data = fnirs_data.to(self.device)
                    labels = labels.to(self.device)
                    
                    self.optimizer.zero_grad()
                    outputs = self.model(eeg_data, fnirs_data)
                    loss = self.criterion(outputs, labels)
                    loss.backward()
                    self.optimizer.step()
                    
                    epoch_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    epoch_samples += labels.size(0)
                    epoch_correct += (predicted == labels).sum().item()
                    
                    # 更新进度条
                    batch_accuracy = (predicted == labels).sum().item() / labels.size(0)
                    pbar.update(1)
                    pbar.set_postfix({"loss": f"{loss.item():.4f}", "acc": f"{batch_accuracy:.4f}"})
            
            # 计算 epoch 统计
            if epoch_samples > 0:
                epoch_loss_avg = epoch_loss / len(self.train_loader)
                epoch_accuracy = epoch_correct / epoch_samples
                
                total_loss += epoch_loss_avg
                total_correct += epoch_correct
                total_samples += epoch_samples
                
                print(f"✅ 客户端 {self.client_id} Epoch {epoch+1} 完成: 损失={epoch_loss_avg:.4f}, 准确率={epoch_accuracy:.4f}")
                
                # 早停检查
                if epoch_loss_avg < best_loss:
                    best_loss = epoch_loss_avg
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        print("⏸️ 早停触发")
                        break
            else:
                print("⚠️  无有效训练数据")
                break
        
        # 计算总统计
        if total_samples > 0:
            avg_loss = total_loss / (epoch + 1)
            accuracy = total_correct / total_samples
            
            print(f"\n🏆 客户端 {self.client_id} 训练完成: 损失={avg_loss:.4f}, 准确率={accuracy:.4f}")
        else:
            avg_loss = 0
            accuracy = 0
            print("\n⚠️  训练未完成: 无有效训练数据")
        
        # 修复：使用fl.common.ndarrays_to_parameters转换参数并添加status参数
        try:
            # 尝试新API
            from flwr.common import Code, Status
            return fl.common.FitRes(
                status=Status(code=Code.OK, message="Success"),
                parameters=fl.common.ndarrays_to_parameters(self.get_parameters(None)),
                num_examples=total_samples,
                metrics={"loss": avg_loss, "accuracy": accuracy}
            )
        except:
            # 兼容旧API
            return fl.common.FitRes(
                parameters=self.get_parameters(None),
                num_examples=total_samples,
                metrics={"loss": avg_loss, "accuracy": accuracy}
            )
    
    def evaluate(self, ins):
        # 加载全局模型参数
        parameters = ins.parameters
        config = ins.config
        
        # 修复：使用fl.common.parameters_to_ndarrays转换参数
        try:
            # 尝试新API
            params_ndarrays = fl.common.parameters_to_ndarrays(parameters)
        except:
            # 兼容旧API
            try:
                params_ndarrays = parameters.ndarrays
            except:
                # 直接使用parameters作为ndarrays
                params_ndarrays = parameters
        
        state_dict = {}
        for k, v in zip(self.model.state_dict().keys(), params_ndarrays):
            state_dict[k] = torch.tensor(v).to(self.device)
        self.model.load_state_dict(state_dict)
        
        # 本地评估
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        print("\n📋 开始评估...")
        
        with torch.no_grad():
            with tqdm(total=len(self.test_loader), desc="评估进度", unit="batch") as pbar:
                for eeg_data, fnirs_data, labels in self.test_loader:
                    # 检查标签值范围
                    if torch.any(labels < 0) or torch.any(labels >= 3):
                        print(f"⚠️  发现无效标签值: {labels}")
                        # 过滤无效标签
                        valid_mask = (labels >= 0) & (labels < 3)
                        if torch.sum(valid_mask) == 0:
                            continue
                        eeg_data = eeg_data[valid_mask]
                        fnirs_data = fnirs_data[valid_mask]
                        labels = labels[valid_mask]
                    
                    eeg_data = eeg_data.to(self.device)
                    fnirs_data = fnirs_data.to(self.device)
                    labels = labels.to(self.device)
                    
                    outputs = self.model(eeg_data, fnirs_data)
                    loss = self.criterion(outputs, labels)
                    
                    total_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total_samples += labels.size(0)
                    total_correct += (predicted == labels).sum().item()
                    
                    # 更新进度条
                    batch_accuracy = (predicted == labels).sum().item() / labels.size(0)
                    pbar.update(1)
                    pbar.set_postfix({"loss": f"{loss.item():.4f}", "acc": f"{batch_accuracy:.4f}"})
        
        accuracy = total_correct / total_samples if total_samples > 0 else 0
        avg_loss = total_loss / len(self.test_loader) if len(self.test_loader) > 0 else 0
        
        print(f"\n📊 客户端 {self.client_id} 评估完成: 损失={avg_loss:.4f}, 准确率={accuracy:.4f}")
        
        # 修复：添加status参数
        try:
            # 尝试新API
            from flwr.common import Code, Status
            return fl.common.EvaluateRes(
                status=Status(code=Code.OK, message="Success"),
                loss=avg_loss,
                num_examples=total_samples,
                metrics={"accuracy": accuracy}
            )
        except:
            # 兼容旧API
            return fl.common.EvaluateRes(
                loss=avg_loss,
                num_examples=total_samples,
                metrics={"accuracy": accuracy}
            )

def main():
    parser = argparse.ArgumentParser(description="SuperNode 联邦学习客户端")
    parser.add_argument("--client-id", type=int, required=True, help="客户端ID")
    parser.add_argument("--data-path", type=str, required=True, help="数据文件路径")
    parser.add_argument("--server", type=str, default="127.0.0.1:8080", help="服务器地址")
    parser.add_argument("--batch-size", type=int, default=8, help="批量大小")
    parser.add_argument("--epochs", type=int, default=1, help="本地训练轮数")
    parser.add_argument("--no-gpu", action="store_true", help="禁用GPU")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"[LOG] 联邦学习客户端 {args.client_id} 启动")
    print("=" * 60)
    print(f"[LOG] 服务器地址: {args.server}")
    print(f"[LOG] 数据路径: {args.data_path}")
    print(f"[LOG] 批量大小: {args.batch_size}")
    print(f"[LOG] 本地轮数: {args.epochs}")
    print("=" * 60)
    print("[LOG] 客户端 1 初始化中...")
    print("[LOG] 加载多模态模型...")
    print("[LOG] 开始加载数据集...")
    
    # 初始化客户端
    client = SuperNodeClient(
        client_id=args.client_id,
        data_path=args.data_path,
        batch_size=args.batch_size,
        epochs=args.epochs,
        use_gpu=not args.no_gpu
    )
    
    # 启动客户端
    print("\n[LOG] 尝试连接服务器 127.0.0.1:8090...")
    print("[LOG] 如果连接成功，将开始训练流程...")
    
    # 启动客户端
    fl.client.start_client(
        server_address=args.server,
        client=client
    )

if __name__ == "__main__":
    main()