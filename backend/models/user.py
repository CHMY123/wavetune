"""
用户模型
定义用户信息相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
import hashlib
import secrets

class User(Base):
    """用户表模型"""
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, comment="用户名")
    student_id = Column(String(20), unique=True, nullable=False, comment="学号")
    password_hash = Column(String(255), comment="密码哈希")
    email = Column(String(100), unique=True, comment="邮箱")
    phone = Column(String(20), comment="手机号")
    avatar = Column(String(255), default="", comment="头像路径")
    detection_count = Column(Integer, default=0, comment="检测次数")
    intervention_count = Column(Integer, default=0, comment="干预次数")
    last_login_time = Column(DateTime, comment="最后登录时间")
    is_active = Column(Boolean, default=True, comment="是否激活")
    create_time = Column(DateTime, default=func.now(), comment="注册时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    feedbacks = relationship("Feedback", back_populates="user")
    scenes = relationship("Scene", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")
    operation_logs = relationship("OperationLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', student_id='{self.student_id}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "student_id": self.student_id,
            "email": self.email,
            "phone": self.phone,
            "avatar": self.avatar,
            "detection_count": self.detection_count,
            "intervention_count": self.intervention_count,
            "last_login_time": self.last_login_time.isoformat() if self.last_login_time else None,
            "is_active": self.is_active,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }
    
    def set_password(self, password: str):
        """设置密码"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        self.password_hash = f"{salt}:{password_hash.hex()}"
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        try:
            salt, stored_hash = self.password_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return password_hash.hex() == stored_hash
        except ValueError:
            return False
