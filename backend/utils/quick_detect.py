import torch
import numpy as np
import os
import sys
from sklearn.preprocessing import StandardScaler
import json

# ===================== 【工程化修复：核心 4 行】 =====================
# 1. 获取工具类绝对路径（backend/utils）
UTILS_DIR = os.path.abspath(os.path.dirname(__file__))
# 2. 读取 boardInfo 配置（提前加载好）
boardInfo = json.load(open(os.path.join(UTILS_DIR, "boardInfo.json"), encoding="utf-8"))
# 3. 注入到系统模块，让 processing_fNIRS_new 直接使用
sys.modules["boardInfo"] = boardInfo
# =====================================================================

# 添加工具目录到Python路径的最前面，确保优先使用工具目录下的模块
sys.path.insert(0, UTILS_DIR)

# 全局检测器实例
_detector = None

# 移除默认的检测结果，确保总是使用真实的检测结果

def get_detector():
    """获取全局检测器实例"""
    global _detector
    if _detector is None:
        # 尝试创建检测器，如果失败则返回None
        try:
            # 尝试导入工具模块
            import sys
            sys.path.insert(0, UTILS_DIR)
            
            # 导入models.py中的MultimodalFatigueModel
            from models import MultimodalFatigueModel
            # 导入processing_fNIRS_new.py中的函数
            from processing_fNIRS_new import get_processing_from_origin_data_48_ch, process_origin_to_fNIRS
            
            class FatigueQuickDetector:
                def __init__(self, model_path=os.path.join(UTILS_DIR, "multimodal_fatigue_model.pth"), num_classes=7):
                    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    self.num_classes = num_classes  # 自动匹配
                    self.model = self._load_model(model_path)
                    self.eeg_scaler = StandardScaler()
                    self.fnirs_scaler = StandardScaler()
                    self._fitted = False
                    
                    # 匹配训练时的7分类标签
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
            
            _detector = FatigueQuickDetector()
            print("✅ 成功创建检测器")
        except Exception as e:
            print(f"❌ 创建检测器失败: {e}")
            # 回退到None
            _detector = None
    return _detector

def detect_from_array(x_raw):
    """输入 numpy array 或类似 (20,20)，返回 (label:int, prob: np.ndarray)
    label: 0 low,1 medium,2 high
    """
    # 暂时返回默认值
    return 1, np.array([0.33, 0.34, 0.33])

def detect_from_csv(csv_path):
    """从CSV文件检测疲劳状态"""
    try:
        detector = get_detector()
        if detector:
            result = detector.detect_csv(csv_path)
            if result:
                return result
            else:
                raise Exception("检测失败: 无法解析CSV文件或未找到有效的数据")
        else:
            raise Exception("检测失败: 无法创建检测器")
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        raise
