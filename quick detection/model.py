import torch
import torch.nn as nn
import torch.nn.functional as F

class BIOTModule(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(BIOTModule, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, 1, 1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.dilated_conv1 = nn.Conv2d(out_channels, out_channels, 3, 1, 2, 2)
        self.dilated_conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 4, 4)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.shortcut = nn.Sequential()
        if in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        identity = self.shortcut(x)
        out = F.relu(self.bn1(self.conv1(x)))
        dilated_out = F.relu(self.dilated_conv1(out))
        dilated_out = F.relu(self.bn2(self.dilated_conv2(dilated_out)))
        out = out + dilated_out + identity
        out = F.relu(out)
        return out


class FatigueDetectionModel(nn.Module):
    def __init__(self, time_steps, num_classes=3):
        super(FatigueDetectionModel, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, 3, 1, 1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.biot = BIOTModule(32, 64)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.bilstm = nn.LSTM(
            input_size=64,
            hidden_size=128,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.5
        )
        self.fc1 = nn.Linear(128 * 2, 64)
        self.fc2 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        batch_size, time_steps, C, H, W = x.size()
        x = x.view(batch_size * time_steps, C, H, W)
        cnn_out = self.cnn(x)
        biot_out = self.biot(cnn_out)
        biot_out = self.adaptive_pool(biot_out)
        features = biot_out.view(batch_size, time_steps, -1)
        lstm_out, _ = self.bilstm(features)
        lstm_out = lstm_out[:, -1, :]
        out = F.relu(self.fc1(lstm_out))
        out = self.dropout(out)
        out = self.fc2(out)
        return out
