"""
用户偏好模型
定义用户偏好设置相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class UserPreference(Base):
    """用户偏好表模型"""
    __tablename__ = "user_preference"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    preference_key = Column(String(50), nullable=False, comment="偏好键")
    preference_value = Column(Text, comment="偏好值")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference(id={self.id}, user_id={self.user_id}, key='{self.preference_key}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preference_key": self.preference_key,
            "preference_value": self.preference_value,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }


