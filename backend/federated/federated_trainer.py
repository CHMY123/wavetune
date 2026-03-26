"""
联邦学习训练模块
简化版的联邦学习实现，支持单个客户端训练
"""

import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import os
import json
import time
import sys
from datetime import datetime

# 从emotion-tired目录导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../emotion-tired')))
from models import MultimodalFatigueModel
from data_loader import DualBranchFatigueDataset, create_dataloaders

class FederatedTrainer:
    def __init__(self, data_path, client_id, rounds=3, epochs=1, batch_size=8, use_gpu=True):
        print(f"[联邦学习] 开始初始化训练器: 客户端={client_id}, 数据路径={data_path}")
        self.data_path = data_path
        self.client_id = client_id
        self.rounds = rounds
        self.epochs = epochs
        self.batch_size = batch_size
        self.use_gpu = use_gpu and torch.cuda.is_available()
        
        print(f"[联邦学习] 初始化参数: 轮次={rounds}, 批次大小={batch_size}, 使用GPU={self.use_gpu}")
        
        self.device = torch.device("cuda" if self.use_gpu else "cpu")
        print(f"[联邦学习] 使用设备: {self.device}")
        
        # 初始化模型
        print(f"[联邦学习] 开始初始化模型...")
        self.model = MultimodalFatigueModel(num_classes=3).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        print(f"[联邦学习] 模型初始化完成")
        
        # 加载数据
        print(f"[联邦学习] 开始加载数据...")
        self.train_loader, self.test_loader = self._load_data()
        print(f"[联邦学习] 数据加载完成")
        
        # 训练历史
        self.history = {
            "rounds": [],
            "train_loss": [],
            "train_accuracy": [],
            "test_loss": [],
            "test_accuracy": []
        }
        
        print(f"[联邦学习] 初始化完成: 客户端={client_id}, 轮次={rounds}")
    
    def _load_data(self):
        """加载训练数据"""
        import glob
        
        csv_files = glob.glob(os.path.join(self.data_path, "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"未在 {self.data_path} 找到 CSV 文件")
        
        print(f"[联邦学习] 找到 {len(csv_files)} 个数据文件")
        
        # 划分训练和测试数据
        if len(csv_files) >= 2:
            train_csv = csv_files[:-1]
            test_csv = [csv_files[-1]]
        else:
            train_csv = csv_files
            test_csv = csv_files
        
        # 创建数据加载器
        train_loader, test_loader = create_dataloaders(
            train_csv,
            test_csv,
            batch_size=self.batch_size,
            window_size_sec=1,
            max_data_points=None
        )
        
        print(f"[联邦学习] 训练集大小: {len(train_loader.dataset)}")
        print(f"[联邦学习] 测试集大小: {len(test_loader.dataset)}")
        
        return train_loader, test_loader
    
    def train_epoch(self, epoch, round_num):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        print(f"[联邦学习] Round {round_num}/{self.rounds} - Epoch {epoch+1}/{self.epochs}")
        
        for batch_idx, (eeg_data, fnirs_data, labels) in enumerate(self.train_loader):
            # 检查标签值范围
            if torch.any(labels < 0) or torch.any(labels >= 3):
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
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_samples += labels.size(0)
            total_correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = total_correct / total_samples if total_samples > 0 else 0
        
        print(f"[联邦学习] Round {round_num}/{self.rounds} - Epoch {epoch+1} 完成: 损失={avg_loss:.4f}, 准确率={accuracy:.4f}")
        
        return avg_loss, accuracy
    
    def evaluate(self):
        """评估模型"""
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for eeg_data, fnirs_data, labels in self.test_loader:
                # 检查标签值范围
                if torch.any(labels < 0) or torch.any(labels >= 3):
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
        
        avg_loss = total_loss / len(self.test_loader) if len(self.test_loader) > 0 else 0
        accuracy = total_correct / total_samples if total_samples > 0 else 0
        
        return avg_loss, accuracy
    
    def train(self, progress_callback=None):
        """执行联邦学习训练"""
        print(f"[联邦学习] 开始训练，总轮次: {self.rounds}")
        
        final_accuracy = 0
        final_loss = 0
        
        for round_num in range(1, self.rounds + 1):
            # 训练多个epoch
            round_train_loss = 0
            round_train_accuracy = 0
            
            for epoch in range(self.epochs):
                train_loss, train_accuracy = self.train_epoch(epoch, round_num)
                round_train_loss = train_loss
                round_train_accuracy = train_accuracy
            
            # 评估
            test_loss, test_accuracy = self.evaluate()
            
            # 记录历史
            self.history["rounds"].append(round_num)
            self.history["train_loss"].append(round_train_loss)
            self.history["train_accuracy"].append(round_train_accuracy)
            self.history["test_loss"].append(test_loss)
            self.history["test_accuracy"].append(test_accuracy)
            
            # 更新进度
            progress = (round_num / self.rounds) * 100
            print(f"[联邦学习] Round {round_num}/{self.rounds} 完成: 进度={progress:.1f}%, 测试准确率={test_accuracy:.4f}")
            
            if progress_callback:
                progress_callback(progress, f"Round {round_num}/{self.rounds} 完成")
            
            # 保存最终结果
            final_accuracy = test_accuracy
            final_loss = test_loss
        
        print(f"[联邦学习] 训练完成: 最终准确率={final_accuracy:.4f}, 最终损失={final_loss:.4f}")
        
        return final_accuracy, final_loss, self.history
    
    def save_model(self, path):
        """保存模型"""
        torch.save(self.model.state_dict(), path)
        print(f"[联邦学习] 模型已保存到: {path}")
    
    def save_history(self, path):
        """保存训练历史"""
        with open(path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"[联邦学习] 训练历史已保存到: {path}")


def main():
    """测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="联邦学习训练")
    parser.add_argument("--data-path", type=str, required=True, help="数据文件路径")
    parser.add_argument("--client-id", type=str, required=True, help="客户端ID")
    parser.add_argument("--rounds", type=int, default=3, help="训练轮次")
    parser.add_argument("--epochs", type=int, default=1, help="本地训练轮数")
    parser.add_argument("--batch-size", type=int, default=8, help="批量大小")
    parser.add_argument("--output-path", type=str, default="./", help="输出路径")
    parser.add_argument("--no-gpu", action="store_true", help="禁用GPU")
    
    args = parser.parse_args()
    
    # 初始化训练器
    trainer = FederatedTrainer(
        data_path=args.data_path,
        client_id=args.client_id,
        rounds=args.rounds,
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_gpu=not args.no_gpu
    )
    
    # 进度回调函数
    def progress_callback(progress, message):
        print(f"[进度] {progress:.1f}% - {message}")
    
    # 训练
    accuracy, loss, history = trainer.train(progress_callback)
    
    # 保存结果
    os.makedirs(args.output_path, exist_ok=True)
    model_path = os.path.join(args.output_path, f"{args.client_id}_model.pth")
    history_path = os.path.join(args.output_path, f"{args.client_id}_history.json")
    
    trainer.save_model(model_path)
    trainer.save_history(history_path)
    
    # 保存训练结果
    result_path = os.path.join(args.output_path, f"{args.client_id}_result.json")
    result = {
        "client_id": args.client_id,
        "accuracy": float(accuracy),
        "loss": float(loss),
        "rounds": args.rounds,
        "epochs": args.epochs,
        "timestamp": datetime.now().isoformat(),
        "history": history
    }
    
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"[联邦学习] 训练结果已保存到: {result_path}")


if __name__ == "__main__":
    main()
