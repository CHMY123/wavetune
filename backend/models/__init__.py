"""
数据模型初始化文件
导入所有模型以确保 SQLAlchemy 能够正确识别表结构
"""

from .user import User
from .feedback import Feedback
from .music import Music
from .scene import Scene
from .system_stats import SystemStats
from .user_session import UserSession
from .user_preference import UserPreference
from .operation_log import OperationLog

__all__ = [
    "User",
    "Feedback", 
    "Music",
    "Scene",
    "SystemStats",
    "UserSession",
    "UserPreference",
    "OperationLog"
]


