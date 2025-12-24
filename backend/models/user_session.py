"""
用户会话模型
定义用户会话相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
import secrets
from datetime import datetime, timedelta

class UserSession(Base):
    """用户会话表模型"""
    __tablename__ = "user_session"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    session_token = Column(String(255), unique=True, nullable=False, comment="会话令牌")
    device_info = Column(String(255), comment="设备信息")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    expire_time = Column(DateTime, nullable=False, comment="过期时间")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now(), comment="最后活动时间")
    
    # 关联关系
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, token='{self.session_token[:10]}...')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_token": self.session_token,
            "device_info": self.device_info,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "is_active": self.is_active,
            "expire_time": self.expire_time.isoformat() if self.expire_time else None,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
    
    @classmethod
    def create_session(cls, user_id: int, device_info: str = None, ip_address: str = None, user_agent: str = None, expire_hours: int = 24):
        """创建新的用户会话"""
        session_token = secrets.token_urlsafe(32)
        expire_time = datetime.now() + timedelta(hours=expire_hours)
        
        session = cls(
            user_id=user_id,
            session_token=session_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expire_time=expire_time
        )
        return session
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.now() > self.expire_time
    
    def extend_session(self, hours: int = 24):
        """延长会话时间"""
        self.expire_time = datetime.now() + timedelta(hours=hours)
        self.last_activity = datetime.now()


