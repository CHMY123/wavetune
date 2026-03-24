import torch
import torch.nn as nn
import torch.nn.functional as F

# --- 1. EEG 正式分支：Biot-CNN-BiLSTM 架构 ---
class EEG_Extractor(nn.Module):
    def __init__(self, in_channels=32, embed_dim=128):
        super().__init__()
        
        # 第一阶段：CNN (提取局部时空特征，同时充当大模型的 Tokenizer 分词器)
        # 作用：将极长的高频脑电信号（如2000个采样点）压缩，提取局部波形特征
        self.cnn = nn.Sequential(
            nn.Conv1d(in_channels, 64, kernel_size=25, stride=5, padding=12),
            nn.BatchNorm1d(64),
            nn.GELU(),
            nn.Conv1d(64, 128, kernel_size=10, stride=2, padding=4),
            nn.BatchNorm1d(128),
            nn.GELU()
        )
        
        # 第二阶段：BIOT / Transformer Encoder (提取高阶空间/通道全局特征)
        # 作用：利用自注意力机制（Self-Attention）捕捉不同脑区在各个频段上的长距离空间相关性
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=128,          # 必须与 CNN 的输出通道数一致
            nhead=8,              # 8 个注意力头
            dim_feedforward=256, 
            dropout=0.3, 
            batch_first=True      # 期望输入维度: (Batch, Seq_Len, Features)
        )
        self.biot_transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        # 第三阶段：BiLSTM (提取长距离时序演变特征)
        # 作用：捕捉脑电信号在一段时间内的动态变化规律（疲劳的累积效应）
        self.bilstm = nn.LSTM(
            input_size=128, 
            hidden_size=64, 
            num_layers=2,
            batch_first=True, 
            bidirectional=True, 
            dropout=0.3
        )
        
        # 映射到指定的嵌入维度，准备与 fNIRS 进行晚期融合
        self.fc = nn.Linear(64 * 2, embed_dim)

    def forward(self, x):
        # x 输入形状: (Batch, 32, Time)  例如 (16, 32, 2000)
        
        # 1. CNN 提取局部特征
        x = self.cnn(x)  # 形状变为 -> (Batch, 128, Time')
        
        # 2. 维度转换以适配 Transformer 和 LSTM 
        # 将形状转置为 -> (Batch, Time', 128)
        x = x.transpose(1, 2)
        
        # 3. BIOT 特征提取 (自注意力机制)
        x = self.biot_transformer(x) # 形状保持 -> (Batch, Time', 128)
        
        # 4. BiLSTM 时序特征提取
        lstm_out, (hn, cn) = self.bilstm(x) # 形状变为 -> (Batch, Time', 128)
        
        # 5. 取 BiLSTM 最后一个时间步的输出作为整段 EEG 信号的总结特征
        last_step_out = lstm_out[:, -1, :] # 形状变为 -> (Batch, 128)
        
        out = F.relu(self.fc(last_step_out)) # 形状变为 -> (Batch, embed_dim)
        return out


# --- 2. fNIRS 分支：低频时序提取网络 (BiLSTM) ---
# (保持不变，专门处理低频血氧数据)
class fNIRS_Extractor(nn.Module):
    def __init__(self, in_channels=72, hidden_dim=64, embed_dim=64):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=in_channels, 
            hidden_size=hidden_dim, 
            num_layers=2, 
            batch_first=True, 
            bidirectional=True, 
            dropout=0.3
        )
        self.fc = nn.Linear(hidden_dim * 2, embed_dim)

    def forward(self, x):
        # x: (Batch, 72, 5) -> (Batch, Channels, Time)
        x = x.transpose(1, 2) # -> (Batch, 5, 72)
        lstm_out, _ = self.lstm(x) 
        last_step_out = lstm_out[:, -1, :] 
        out = F.relu(self.fc(last_step_out)) 
        return out


# --- 3. 晚期融合主模型 (Late Fusion) ---
# (结构保持不变，底层引擎已升级)
class MultimodalFatigueModel(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        self.eeg_embed_dim = 128
        self.fnirs_embed_dim = 64
        
        # 实例化正式版分支
        self.eeg_branch = EEG_Extractor(in_channels=32, embed_dim=self.eeg_embed_dim)
        self.fnirs_branch = fNIRS_Extractor(in_channels=72, hidden_dim=64, embed_dim=self.fnirs_embed_dim)
        
        fused_dim = self.eeg_embed_dim + self.fnirs_embed_dim # 128 + 64 = 192
        
        self.classifier = nn.Sequential(
            nn.Linear(fused_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, eeg_data, fnirs_data):
        eeg_features = self.eeg_branch(eeg_data)       
        fnirs_features = self.fnirs_branch(fnirs_data) 
        
        fused_features = torch.cat((eeg_features, fnirs_features), dim=1) 
        logits = self.classifier(fused_features)       
        return logits

# --- 4. 本地维度的压力测试 ---
if __name__ == "__main__":
    print("🚀 正在加载正式版 Biot-CNN-BiLSTM 多模态架构...")
    
    # 模拟你们真实的 2 秒滑动窗口数据
    # EEG: 1000Hz * 2s = 2000 个采样点
    dummy_eeg = torch.randn(16, 32, 2000)  
    # fNIRS: 5Hz (或10Hz) * 2s = 10(或20) 个采样点
    dummy_fnirs = torch.randn(16, 72, 10)   
    
    model = MultimodalFatigueModel(num_classes=3)
    
    # 计算模型参数量
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 模型总可训练参数量: {total_params:,}")
    
    output = model(dummy_eeg, dummy_fnirs)
    
    print(f"✅ 前向传播测试通过！输出形状: {output.shape} (期望: [16, 3])")