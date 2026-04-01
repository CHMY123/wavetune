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

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 从utils目录导入模型
from utils.models import MultimodalFatigueModel
from data_loader import DualBranchFatigueDataset, create_dataloaders

class FederatedTrainer:
    def __init__(self, data_path, client_id, rounds=1, epochs=1, batch_size=8, use_gpu=False):
        """
        初始化联邦学习训练器
        
        Args:
            data_path: 数据文件路径
            client_id: 客户端ID
            rounds: 联邦学习轮数
            epochs: 每轮本地训练轮数
            batch_size: 批量大小
            use_gpu: 是否使用GPU
        """
        self.data_path = data_path
        self.client_id = client_id
        self.rounds = rounds
        self.epochs = epochs
        self.batch_size = batch_size
        self.use_gpu = use_gpu and torch.cuda.is_available()
        
        # 加载数据，获取类别数
        self.train_loader, self.test_loader = self._load_data()
        
        # 获取数据集的类别数
        num_classes = self._get_num_classes()
        print(f"[联邦学习] 检测到 {num_classes} 个类别")
        
        # 初始化模型
        self.model = MultimodalFatigueModel(num_classes=num_classes)
        if self.use_gpu:
            self.model = self.model.cuda()
        
        # 损失函数和优化器
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        
        # 训练历史
        self.history = {
            'loss': [],
            'accuracy': [],
            'val_loss': [],
            'val_accuracy': []
        }
    
    def _get_num_classes(self):
        """
        获取数据集中的类别数
        """
        # 遍历整个训练数据集，收集所有标签
        if self.train_loader is not None:
            all_labels = []
            for batch in self.train_loader:
                _, _, labels = batch
                all_labels.extend(labels.cpu().numpy())
            
            if all_labels:
                # 获取所有唯一标签
                unique_labels = set(all_labels)
                # 类别数是唯一标签的数量
                num_classes = len(unique_labels)
                return num_classes
        return 3  # 默认值
    
    def _load_data(self):
        """
        加载训练和测试数据
        """
        import glob
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
    
    def train(self, progress_callback=None):
        """
        执行训练
        
        Args:
            progress_callback: 进度回调函数
        
        Returns:
            accuracy: 最终准确率
            loss: 最终损失
            history: 训练历史
        """
        total_steps = self.rounds * self.epochs * len(self.train_loader)
        current_step = 0
        
        for round_num in range(self.rounds):
            print(f"\n=== 第 {round_num + 1}/{self.rounds} 轮训练 ===")
            
            # 本地训练
            self.model.train()
            round_loss = 0
            round_correct = 0
            round_samples = 0
            
            for epoch in range(self.epochs):
                for batch_idx, (eeg_data, fnirs_data, labels) in enumerate(self.train_loader):
                    if self.use_gpu:
                        eeg_data = eeg_data.cuda()
                        fnirs_data = fnirs_data.cuda()
                        labels = labels.cuda()
                    
                    self.optimizer.zero_grad()
                    outputs = self.model(eeg_data, fnirs_data)
                    loss = self.criterion(outputs, labels)
                    loss.backward()
                    self.optimizer.step()
                    
                    round_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    round_samples += labels.size(0)
                    round_correct += (predicted == labels).sum().item()
                    
                    # 更新进度
                    current_step += 1
                    progress = (current_step / total_steps) * 80 + 20  # 20% 是初始化进度
                    if progress_callback:
                        progress_callback(progress, f"正在训练: 第 {round_num + 1} 轮, 第 {epoch + 1}  epoch")
            
            # 计算轮次准确率和损失
            round_accuracy = round_correct / round_samples
            round_avg_loss = round_loss / len(self.train_loader)
            
            # 验证
            val_accuracy, val_loss = self.evaluate()
            
            # 保存历史
            self.history['loss'].append(round_avg_loss)
            self.history['accuracy'].append(round_accuracy)
            self.history['val_loss'].append(val_loss)
            self.history['val_accuracy'].append(val_accuracy)
            
            print(f"轮次 {round_num + 1} 完成: 训练损失={round_avg_loss:.4f}, 训练准确率={round_accuracy:.4f}, 验证损失={val_loss:.4f}, 验证准确率={val_accuracy:.4f}")
        
        # 最终评估
        final_accuracy, final_loss = self.evaluate()
        
        if progress_callback:
            progress_callback(100, "训练完成")
        
        return final_accuracy, final_loss, self.history
    
    def evaluate(self):
        """
        评估模型性能
        
        Returns:
            accuracy: 准确率
            loss: 损失
        """
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for eeg_data, fnirs_data, labels in self.test_loader:
                if self.use_gpu:
                    eeg_data = eeg_data.cuda()
                    fnirs_data = fnirs_data.cuda()
                    labels = labels.cuda()
                
                outputs = self.model(eeg_data, fnirs_data)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_samples += labels.size(0)
                total_correct += (predicted == labels).sum().item()
        
        accuracy = total_correct / total_samples if total_samples > 0 else 0
        avg_loss = total_loss / len(self.test_loader) if len(self.test_loader) > 0 else 0
        
        return accuracy, avg_loss
    
    def save_model(self, path):
        """
        保存模型
        
        Args:
            path: 保存路径
        """
        torch.save(self.model.state_dict(), path)
        print(f"模型已保存到: {path}")
    
    def save_history(self, path):
        """
        保存训练历史
        
        Args:
            path: 保存路径
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        print(f"训练历史已保存到: {path}")