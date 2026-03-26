import torch
import numpy as np
import argparse
import glob
import os
from sklearn.preprocessing import StandardScaler

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import MultimodalFatigueModel
from processing_fNIRS_new import get_processing_from_origin_data_48_ch, process_origin_to_fNIRS

class FatigueQuickDetector:
    def __init__(self, model_path="multimodal_fatigue_model.pth", num_classes=7):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_classes = num_classes  # ← 自动匹配
        self.model = self._load_model(model_path)
        self.eeg_scaler = StandardScaler()
        self.fnirs_scaler = StandardScaler()
        self._fitted = False
        
        # 匹配你训练时的 7 分类标签
        self.label_names = {
            0: "静息态",
            1: "正常",
            2: "轻度疲劳",
            3: "中度疲劳",
            4: "重度疲劳",
            5: "疲劳恢复期",
            6: "其他"
        }

    def _load_model(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        model = MultimodalFatigueModel(num_classes=self.num_classes)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        print(f"✅ 模型加载成功: {model_path}")
        print(f"📊 使用设备: {self.device}")
        return model

    def preprocess_csv(self, csv_path, window_size_sec=2):
        print(f"\n📁 正在处理文件: {csv_path}")
        
        try:
            raw_data = np.loadtxt(csv_path, delimiter=',').T
        except ValueError:
            raw_data = np.loadtxt(csv_path).T
        
        print(f"   原始数据形状: {raw_data.shape}")
        
        marker_col_index = 56
        fNIRS_channels, data_780, data_850, _ = get_processing_from_origin_data_48_ch(raw_data, marker_col_index)
        
        if len(data_780) == 0 or len(data_780[0]) == 0:
            print("   ⚠️ 警告: 未解析出有效的 fNIRS 数据")
            return None, None
        
        hbo, hbr = process_origin_to_fNIRS(
            np.array(data_850).T, 
            np.array(data_780).T, 
            [850, 780]
        )
        fnirs_features = np.vstack([hbo, hbr])
        eeg_features = raw_data[1:33, :]
        
        eeg_window_len = window_size_sec * 1000
        fnirs_window_len = window_size_sec * 5
        
        eeg_window = eeg_features[:, :eeg_window_len]
        fnirs_window = fnirs_features[:, :fnirs_window_len]
        
        print(f"   EEG 窗口形状: {eeg_window.shape}")
        print(f"   fNIRS 窗口形状: {fnirs_window.shape}")
        
        if not self._fitted:
            eeg_scaled = self.eeg_scaler.fit_transform(eeg_window.T).T
            fnirs_scaled = self.fnirs_scaler.fit_transform(fnirs_window.T).T
            self._fitted = True
        else:
            eeg_scaled = self.eeg_scaler.transform(eeg_window.T).T
            fnirs_scaled = self.fnirs_scaler.transform(fnirs_window.T).T
        
        return eeg_scaled, fnirs_scaled

    def predict(self, eeg_data, fnirs_data):
        if eeg_data is None or fnirs_data is None:
            return None
        
        eeg_tensor = torch.FloatTensor(eeg_data).unsqueeze(0).to(self.device)
        fnirs_tensor = torch.FloatTensor(fnirs_data).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(eeg_tensor, fnirs_tensor)
            probs = torch.softmax(output, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_class].item()
        
        result = {
            "class_id": pred_class,
            "label": self.label_names[pred_class],
            "confidence": round(confidence * 100, 2),
            "probabilities": {
                self.label_names[i]: round(probs[0, i].item() * 100, 2) 
                for i in range(self.num_classes)
            }
        }
        return result

    def detect_csv(self, csv_path):
        eeg_data, fnirs_data = self.preprocess_csv(csv_path)
        if eeg_data is None:
            return None
        return self.predict(eeg_data, fnirs_data)

def main():
    parser = argparse.ArgumentParser(description="多模态疲劳快速检测工具")
    parser.add_argument("--csv", type=str, default=None, help="CSV 文件路径")
    parser.add_argument("--model", type=str, default="multimodal_fatigue_model.pth", help="模型权重文件路径")
    parser.add_argument("--batch", action="store_true", help="批量检测当前目录下所有 CSV 文件")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 多模态疲劳快速检测工具")
    print("=" * 60)
    
    detector = FatigueQuickDetector(model_path=args.model)
    
    if args.batch:
        csv_files = glob.glob("*.csv")
        if not csv_files:
            print("❌ 当前目录下没有找到 CSV 文件")
            return
        
        print(f"\n📂 找到 {len(csv_files)} 个 CSV 文件，开始批量检测...\n")
        
        results = []
        for csv_file in csv_files:
            result = detector.detect_csv(csv_file)
            if result:
                results.append((csv_file, result))
        
        print("\n" + "=" * 60)
        print("📊 批量检测结果汇总")
        print("=" * 60)
        
        for csv_file, result in results:
            print(f"\n📄 {csv_file}")
            print(f"   预测结果: {result['label']} (置信度: {result['confidence']}%)")
            print(f"   概率分布: {result['probabilities']}")
        
        if results:
            label_counts = {}
            for _, result in results:
                label = result['label']
                label_counts[label] = label_counts.get(label, 0) + 1
            
            print("\n📈 统计汇总:")
            for label, count in label_counts.items():
                print(f"   {label}: {count} 次")
    
    else:
        csv_path = args.csv
        if not csv_path:
            candidates = glob.glob("*.csv")
            if not candidates:
                print("❌ 请指定 CSV 文件路径或使用 --batch 批量检测")
                return
            csv_path = candidates[0]
            print(f"📂 自动选择文件: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"❌ 文件不存在: {csv_path}")
            return
        
        result = detector.detect_csv(csv_path)
        
        if result:
            print("\n" + "=" * 60)
            print("🎯 检测结果")
            print("=" * 60)
            print(f"预测类别: {result['label']}")
            print(f"置信度: {result['confidence']}%")
            print(f"\n概率分布:")
            for label, prob in result['probabilities'].items():
                bar = "█" * int(prob / 5)
                print(f"  {label}: {prob}% {bar}")
        else:
            print("❌ 检测失败，请检查数据文件格式")

if __name__ == "__main__":
    main()