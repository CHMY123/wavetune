import torch
import flwr as fl
import argparse
import os
import sys
import glob
import torch.optim as optim
import torch.nn as nn

# 添加上级目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import MultimodalFatigueModel
from data_loader import DualBranchFatigueDataset, create_dataloaders

class FedClient(fl.client.Client):
    def __init__(self, client_id, data_path, batch_size=16, epochs=1):
        self.client_id = client_id
        self.data_path = data_path
        self.batch_size = batch_size
        self.epochs = epochs
        self.model = MultimodalFatigueModel(num_classes=3)
        self.train_loader, self.test_loader = self._load_data()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
    
    def _load_data(self):
        csv_files = glob.glob(os.path.join(self.data_path, "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"未在 {self.data_path} 找到 CSV 文件")
        
        print(f"客户端 {self.client_id} 加载了 {len(csv_files)} 个数据文件")
        
        # 简单划分训练和测试数据
        if len(csv_files) >= 2:
            train_csv = csv_files[:-1]
            test_csv = [csv_files[-1]]
        else:
            train_csv = csv_files
            test_csv = csv_files
        
        train_loader, test_loader = create_dataloaders(
            train_csv, 
            test_csv, 
            batch_size=self.batch_size,
            window_size_sec=2
        )
        
        return train_loader, test_loader
    
    def get_parameters(self, ins):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]
    
    def fit(self, ins):
        # 加载全局模型参数
        parameters = ins.parameters
        config = ins.config
        
        state_dict = {}
        for k, v in zip(self.model.state_dict().keys(), parameters):
            state_dict[k] = torch.tensor(v)
        self.model.load_state_dict(state_dict)
        
        # 本地训练
        self.model.train()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        for epoch in range(self.epochs):
            for batch_idx, (eeg_data, fnirs_data, labels) in enumerate(self.train_loader):
                self.optimizer.zero_grad()
                outputs = self.model(eeg_data, fnirs_data)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_samples += labels.size(0)
                total_correct += (predicted == labels).sum().item()
        
        accuracy = total_correct / total_samples
        avg_loss = total_loss / len(self.train_loader)
        
        print(f"客户端 {self.client_id} 训练完成: 损失={avg_loss:.4f}, 准确率={accuracy:.4f}")
        
        return fl.common.FitRes(
            parameters=self.get_parameters(None),
            num_examples=total_samples,
            metrics={"loss": avg_loss, "accuracy": accuracy}
        )
    
    def evaluate(self, ins):
        # 加载全局模型参数
        parameters = ins.parameters
        config = ins.config
        
        state_dict = {}
        for k, v in zip(self.model.state_dict().keys(), parameters):
            state_dict[k] = torch.tensor(v)
        self.model.load_state_dict(state_dict)
        
        # 本地评估
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for eeg_data, fnirs_data, labels in self.test_loader:
                outputs = self.model(eeg_data, fnirs_data)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_samples += labels.size(0)
                total_correct += (predicted == labels).sum().item()
        
        accuracy = total_correct / total_samples
        avg_loss = total_loss / len(self.test_loader) if len(self.test_loader) > 0 else 0
        
        print(f"客户端 {self.client_id} 评估完成: 损失={avg_loss:.4f}, 准确率={accuracy:.4f}")
        
        return fl.common.EvaluateRes(
            loss=avg_loss,
            num_examples=total_samples,
            metrics={"accuracy": accuracy}
        )

def main():
    parser = argparse.ArgumentParser(description="联邦学习客户端")
    parser.add_argument("--client-id", type=int, required=True, help="客户端ID")
    parser.add_argument("--data-path", type=str, required=True, help="数据文件路径")
    parser.add_argument("--server", type=str, default="127.0.0.1:8090", help="服务器地址")
    parser.add_argument("--batch-size", type=int, default=16, help="批量大小")
    parser.add_argument("--epochs", type=int, default=1, help="本地训练轮数")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"🚀 联邦学习客户端 {args.client_id} 启动")
    print("=" * 60)
    print(f"服务器地址: {args.server}")
    print(f"数据路径: {args.data_path}")
    print(f"批量大小: {args.batch_size}")
    print(f"本地训练轮数: {args.epochs}")
    
    # 初始化客户端
    client = FedClient(
        client_id=args.client_id,
        data_path=args.data_path,
        batch_size=args.batch_size,
        epochs=args.epochs
    )
    
    # 启动客户端
    fl.client.start_client(
        server_address=args.server,
        client=client
    )

if __name__ == "__main__":
    main()