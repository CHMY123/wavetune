import os
import sys
import numpy as np
import joblib
import torch
import importlib.util

# 项目根目录（workspace 根，backend 的上一级）
# quick detection 目录与 backend 同级，因此需要上溯两个目录层级
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
QD_DIR = os.path.join(ROOT, 'quick detection')

SCALER_PATH = os.path.join(QD_DIR, 'scaler.pkl')
MODEL_PY = os.path.join(QD_DIR, 'model.py')
MODEL_WEIGHTS = os.path.join(QD_DIR, 'best_model.pth')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def _load_scaler():
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"scaler not found: {SCALER_PATH}")
    return joblib.load(SCALER_PATH)


_model = None
_scaler = None


def _load_model():
    global _model, _scaler
    if _model is not None and _scaler is not None:
        return _model, _scaler

    if not os.path.exists(MODEL_PY):
        raise FileNotFoundError(f"model.py not found in quick detection dir: {MODEL_PY}")

    # 导入 model.py 为模块
    spec = importlib.util.spec_from_file_location('qd_model', MODEL_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # scaler
    _scaler = _load_scaler()

    # 实例化模型类；默认类名为 FatigueDetectionModel
    if not hasattr(mod, 'FatigueDetectionModel'):
        raise RuntimeError('FatigueDetectionModel class not found in model.py')
    ModelClass = getattr(mod, 'FatigueDetectionModel')
    # time_steps 和 num_classes 与训练时一致
    _model = ModelClass(time_steps=20, num_classes=3).to(device)
    if not os.path.exists(MODEL_WEIGHTS):
        raise FileNotFoundError(f"weights not found: {MODEL_WEIGHTS}")
    state = torch.load(MODEL_WEIGHTS, map_location=device)
    # state may be a state_dict or whole checkpoint
    if isinstance(state, dict) and 'state_dict' in state:
        state = state['state_dict']
    _model.load_state_dict(state)
    _model.eval()
    return _model, _scaler


def detect_from_array(x_raw):
    """输入 numpy array 或类似 (20,20)，返回 (label:int, prob: np.ndarray)
    label: 0 low,1 medium,2 high
    """
    model, scaler = _load_model()
    x = np.array(x_raw, dtype=np.float32)
    if x.shape != (20, 20):
        raise ValueError('输入必须为 20x20')
    x_flat = x.reshape(-1, 20)
    x_flat = scaler.transform(x_flat)
    x = x_flat.reshape(20, 20)
    seq = x[:15, :].reshape(15, 1, 4, 5)
    x_tensor = torch.FloatTensor(seq).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x_tensor)
        prob = torch.softmax(logits, dim=1).cpu().numpy().flatten()
    label = int(np.argmax(prob))
    return label, prob
