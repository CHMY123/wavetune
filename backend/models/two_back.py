# 2-Back 实验数据模型
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class TwoBackSession(Base):
    """2-Back 实验会话模型"""
    __tablename__ = "two_back_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    participant_id = Column(String(100), index=True, nullable=False)
    settings = Column(JSON, nullable=False)  # 实验设置
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="initialized")  # initialized, in_progress, completed
    completed_blocks = Column(Integer, nullable=False, default=0)
    overall_hit_rate = Column(Float, nullable=True)
    total_trials = Column(Integer, nullable=True)

    # 关系
    trials = relationship("TwoBackTrial", back_populates="session", cascade="all, delete-orphan")
    kss_scores = relationship("TwoBackKSSScore", back_populates="session", cascade="all, delete-orphan")
    performance_metrics = relationship("TwoBackPerformanceMetric", back_populates="session", cascade="all, delete-orphan")

class TwoBackTrial(Base):
    """2-Back 实验试次模型"""
    __tablename__ = "two_back_trials"

    id = Column(Integer, primary_key=True, index=True)
    trial_id = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(String(100), ForeignKey("two_back_sessions.session_id"), nullable=False)
    block_num = Column(Integer, nullable=False)
    trial_index = Column(Integer, nullable=False)
    stimulus = Column(String(10), nullable=False)
    is_target = Column(Integer, nullable=False)  # 0=False, 1=True
    key_pressed = Column(Integer, nullable=False)  # 0=False, 1=True
    response_time = Column(Float, nullable=True)  # 反应时（秒）
    is_hit = Column(Integer, nullable=True)  # 0=False, 1=True
    is_false_alarm = Column(Integer, nullable=True)  # 0=False, 1=True
    is_miss = Column(Integer, nullable=True)  # 0=False, 1=True
    is_correct_reject = Column(Integer, nullable=True)  # 0=False, 1=True
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 关系
    session = relationship("TwoBackSession", back_populates="trials")

class TwoBackKSSScore(Base):
    """KSS 疲劳量表评分模型"""
    __tablename__ = "two_back_kss_scores"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("two_back_sessions.session_id"), nullable=False)
    round_num = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)  # 1-9
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 关系
    session = relationship("TwoBackSession", back_populates="kss_scores")

class TwoBackPerformanceMetric(Base):
    """实验表现指标模型"""
    __tablename__ = "two_back_performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("two_back_sessions.session_id"), nullable=False)
    round_num = Column(Integer, nullable=False)
    hit_rate = Column(Float, nullable=False)  # 命中率
    false_alarm_rate = Column(Float, nullable=False)  # 虚报率
    avg_response_time = Column(Float, nullable=False)  # 平均反应时（毫秒）
    hits = Column(Integer, nullable=False)
    false_alarms = Column(Integer, nullable=False)
    misses = Column(Integer, nullable=False)
    correct_rejects = Column(Integer, nullable=False)
    total_trials = Column(Integer, nullable=False)

    # 关系
    session = relationship("TwoBackSession", back_populates="performance_metrics")

class TwoBackExperimentData(Base):
    """实验数据汇总模型"""
    __tablename__ = "two_back_experiment_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    participant_id = Column(String(100), index=True, nullable=False)
    experiment_data = Column(JSON, nullable=False)  # 完整的实验数据
    analysis_result = Column(JSON, nullable=True)  # 分析结果
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
