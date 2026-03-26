import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import os

# 导入师兄的 API (确保 processing_fNIRS_new.py 在同级目录)
from processing_fNIRS_new import get_processing_from_origin_data_48_ch, process_origin_to_fNIRS

class DualBranchFatigueDataset(Dataset):
    def __init__(self, csv_files, window_size_sec=2, step_size_sec=1, is_train=True, eeg_scaler=None, fnirs_scaler=None, label_to_index=None, auto_label_map=True, max_data_points=None):
        """
        双分支多模态数据集
        :param csv_files: CSV 数据文件路径列表 (支持多个被试/多次实验的数据拼接)
        :param window_size_sec: 滑动窗口的时间长度(秒)。例如 2秒。
        :param step_size_sec: 滑动窗口的步长(秒)。例如 1秒。
        :param is_train: 是否为训练集 (决定是否 fit StandardScaler)
        :param max_data_points: 最大数据点数量，只使用前max_data_points个数据点
        """
        self.window_size_sec = window_size_sec
        self.step_size_sec = step_size_sec
        self.max_data_points = max_data_points
        
        # 物理常量定义
        self.eeg_hz = 1000
        self.fnirs_hz = 5
        self.eeg_window_len = self.window_size_sec * self.eeg_hz      # e.g., 2000
        self.fnirs_window_len = self.window_size_sec * self.fnirs_hz  # e.g., 10
        self.eeg_step_len = self.step_size_sec * self.eeg_hz
        
        # 初始化归一化器
        self.eeg_scaler = eeg_scaler if eeg_scaler else StandardScaler()
        self.fnirs_scaler = fnirs_scaler if fnirs_scaler else StandardScaler()
        self.is_train = is_train

        self.eeg_windows = []
        self.fnirs_windows = []
        self.labels = []
        self.raw_labels = None
        self.label_to_index = None
        self.index_to_label = None
        self.num_classes = None

        # 遍历并处理所有提供的数据文件
        for file_path in csv_files:
            self._process_single_trial(file_path)
            
        # 转换为 Numpy 数组方便统一管理
        self.eeg_windows = np.array(self.eeg_windows)
        self.fnirs_windows = np.array(self.fnirs_windows)
        self.labels = np.array(self.labels, dtype=np.int64)
        self.raw_labels = self.labels.copy()
        if label_to_index is not None:
            self.set_label_mapping(label_to_index)
        elif auto_label_map:
            uniq = sorted(np.unique(self.raw_labels).tolist())
            inferred_map = {int(v): i for i, v in enumerate(uniq)}
            self.set_label_mapping(inferred_map)
        
        print(f"✅ 数据集构建完成! 共提取了 {len(self.labels)} 个时间窗口。")
        print(f"EEG 窗口形状: {self.eeg_windows.shape} | fNIRS 窗口形状: {self.fnirs_windows.shape}")
        if self.label_to_index is not None:
            mapped_uniq = sorted(np.unique(self.labels).tolist())
            print(f"标签映射: {self.label_to_index}")
            print(f"类别数: {self.num_classes} | 映射后标签集合: {mapped_uniq}")

    def set_label_mapping(self, label_to_index: dict):
        self.label_to_index = {int(k): int(v) for k, v in label_to_index.items()}
        self.index_to_label = {int(v): int(k) for k, v in self.label_to_index.items()}
        mapped = []
        missing = set()
        for v in self.raw_labels.tolist():
            iv = int(v)
            if iv not in self.label_to_index:
                missing.add(iv)
            else:
                mapped.append(self.label_to_index[iv])
        if missing:
            raise ValueError(f"发现未定义映射的标签值: {sorted(missing)}")
        self.labels = np.array(mapped, dtype=np.int64)
        self.num_classes = len(set(self.label_to_index.values()))

    def _process_single_trial(self, csv_file_path):
        print(f"正在处理数据文件: {csv_file_path} ...")
        
        # 1. 读取原始数据 (兼容以空格或逗号分隔的格式)
        try:
            raw_data = np.loadtxt(csv_file_path, delimiter=',').T
        except ValueError:
            raw_data = np.loadtxt(csv_file_path).T
        
        # 只使用前max_data_points个数据点
        if self.max_data_points is not None:
            raw_data = raw_data[:, :self.max_data_points]
            print(f"⚠️  已截取前 {self.max_data_points} 个数据点")
            
        # 2. 调用师兄的 API 解析 fNIRS 数据
        # 实时代码中 marker 索引为 56
        marker_col_index = 56 
        fNIRS_channels, data_780, data_850, _ = get_processing_from_origin_data_48_ch(raw_data, marker_col_index)
        
        if len(data_780) == 0 or len(data_780[0]) == 0:
            print(f"⚠️ 警告: {csv_file_path} 未解析出有效的 fNIRS 数据，已跳过。")
            return

        # 计算血氧浓度 (HbO, HbR)
        hbo, hbr = process_origin_to_fNIRS(np.array(data_850).T, np.array(data_780).T, [850, 780])
        fnirs_features = np.vstack([hbo, hbr]) # 形状: (72, N_fnirs_samples)
        
        # 3. 提取 EEG 数据 (前 32 个通道，假设索引 1 到 32，具体看真实 CSV)
        eeg_features = raw_data[1:33, :] # 形状: (32, N_eeg_samples)
        
        # 4. 提取标签 (最后一行)
        label_sequence = raw_data[-1, :]
        
        # 5. 长度对齐 (以秒为单位求最小可用时长)
        max_sec_eeg = eeg_features.shape[1] // self.eeg_hz
        max_sec_fnirs = fnirs_features.shape[1] // self.fnirs_hz
        valid_seconds = min(max_sec_eeg, max_sec_fnirs)
        
        # 截取对齐后的有效数据段
        eeg_features = eeg_features[:, :valid_seconds * self.eeg_hz]
        fnirs_features = fnirs_features[:, :valid_seconds * self.fnirs_hz]
        label_sequence = label_sequence[:valid_seconds * self.eeg_hz]

        # 6. 独立归一化 (Channel 维度单独归一化)
        # sklearn 期望的输入是 (Samples, Features)，所以需要转置 fit，再转置回来
        if self.is_train:
            eeg_scaled = self.eeg_scaler.fit_transform(eeg_features.T).T
            fnirs_scaled = self.fnirs_scaler.fit_transform(fnirs_features.T).T
        else:
            eeg_scaled = self.eeg_scaler.transform(eeg_features.T).T
            fnirs_scaled = self.fnirs_scaler.transform(fnirs_features.T).T

        # 7. 滑动窗口切片 (核心对齐逻辑)
        total_eeg_samples = eeg_scaled.shape[1]
        
        for start_idx in range(0, total_eeg_samples - self.eeg_window_len + 1, self.eeg_step_len):
            end_idx = start_idx + self.eeg_window_len
            
            # 计算对应的 fNIRS 索引 (缩小 200 倍)
            fnirs_start = start_idx // 200
            fnirs_end = end_idx // 200
            
            # 切片
            window_eeg = eeg_scaled[:, start_idx:end_idx]
            window_fnirs = fnirs_scaled[:, fnirs_start:fnirs_end]
            
            # 提取标签：取这个窗口最后 1/4 时间内的众数或最后一个非零标记作为当前窗口的标签
            # 根据 trigger.py 的逻辑，大部分是非0的有效 label
            window_labels = label_sequence[end_idx - (self.eeg_hz // 2) : end_idx] 
            valid_labels = window_labels[window_labels != 0]
            if len(valid_labels) > 0:
                # 简单取最后出现的非零标签作为窗口类别 (可根据实际范式调整)
                current_label = int(valid_labels[-1])
            else:
                current_label = 0 # 0 代表无标签或静息态
                
            self.eeg_windows.append(window_eeg)
            self.fnirs_windows.append(window_fnirs)
            self.labels.append(current_label)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        # 转换为 PyTorch 张量
        # 形状输出: 
        # eeg: (32, 2000)
        # fnirs: (72, 10)
        return (
            torch.FloatTensor(self.eeg_windows[idx]), 
            torch.FloatTensor(self.fnirs_windows[idx]), 
            torch.LongTensor([self.labels[idx]]).squeeze()
        )

# --- 辅助函数：快速获取训练和测试 DataLoader ---
def create_dataloaders(train_csv_paths, test_csv_paths, batch_size=32, window_size_sec=2, max_data_points=None):
    print(">>> 正在构建训练集...")
    train_dataset = DualBranchFatigueDataset(train_csv_paths, window_size_sec=window_size_sec, is_train=True, auto_label_map=False, max_data_points=max_data_points)
    
    print(">>> 正在构建测试集 (使用训练集的 Scaler 进行归一化)...")
    test_dataset = DualBranchFatigueDataset(
        test_csv_paths, 
        window_size_sec=window_size_sec, 
        is_train=False, 
        eeg_scaler=train_dataset.eeg_scaler, 
        fnirs_scaler=train_dataset.fnirs_scaler,
        auto_label_map=False,
        max_data_points=max_data_points
    )

    all_raw = np.concatenate([train_dataset.raw_labels, test_dataset.raw_labels]).astype(int)
    uniq = sorted(np.unique(all_raw).tolist())
    label_to_index = {int(v): i for i, v in enumerate(uniq)}
    train_dataset.set_label_mapping(label_to_index)
    test_dataset.set_label_mapping(label_to_index)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    
    return train_loader, test_loader

if __name__ == "__main__":
    # 本地测试代码
    # 自动搜索当前文件夹下的真实 csv 文件进行测试
    import glob
    test_files = glob.glob("*.csv")
    
    if test_files:
        print(f"找到 CSV 文件：{test_files[0]}，开始测试...")
        dataset = DualBranchFatigueDataset([test_files[0]], window_size_sec=2, max_data_points=500)
        if len(dataset) > 0:
            eeg, fnirs, label = dataset[0]
            print(f"取出第一个样本 - EEG 形状: {eeg.shape}, fNIRS 形状: {fnirs.shape}, 标签: {label}")
        else:
            print("数据集为空，可能文件内没有有效数据。")
    else:
        print("当前文件夹下未找到任何 .csv 文件，请提供真实的 csv 文件路径运行测试。")
