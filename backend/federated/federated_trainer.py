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