"""
联邦学习相关模型
定义联邦学习训练记录、设备信息和统计数据的数据库表结构
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from config.database import Base
import enum

class TrainingStatus(str, enum.Enum):
    """训练状态枚举"""
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"

class DeviceStatus(str, enum.Enum):
    """设备状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"

class FederatedTraining(Base):
    """联邦学习训练记录表"""
    __tablename__ = "federated_training"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(String(50), nullable=False)
    round_number = Column(Integer, nullable=False)
    accuracy = Column(Float, default=0)
    loss = Column(Float, default=0)
    training_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(TrainingStatus), default=TrainingStatus.PENDING)
    fatigue_status = Column(String(50), nullable=True)

class FederatedDevice(Base):
    """联邦学习设备表"""
    __tablename__ = "federated_device"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(50), nullable=False)
    device_type = Column(String(50), nullable=False)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_participate = Column(DateTime(timezone=True), nullable=True)
    training_count = Column(Integer, default=0)
    contribution = Column(Float, default=0)

class FederatedStats(Base):
    """联邦学习统计表"""
    __tablename__ = "federated_stats"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    total_participants = Column(Integer, default=0)
    total_devices = Column(Integer, default=0)
    total_rounds = Column(Integer, default=0)
    average_accuracy = Column(Float, default=0)
    average_loss = Column(Float, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SignalDetectionCount(Base):
    """信号监测检测次数表"""
    __tablename__ = "signal_detection_count"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    detection_count = Column(Integer, default=0)
    last_detection = Column(DateTime(timezone=True), nullable=True)
