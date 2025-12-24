"""
场景模型
定义场景配置相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Scene(Base):
    """场景表模型"""
    __tablename__ = "scene"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    scene_name = Column(String(50), nullable=False, comment="场景名称")
    music_type = Column(String(20), nullable=False, comment="音乐类型")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    is_default = Column(Integer, default=0, comment="是否默认场景")
    
    # 关联关系
    user = relationship("User", back_populates="scenes")
    
    def __repr__(self):
        return f"<Scene(id={self.id}, user_id={self.user_id}, name='{self.scene_name}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scene_name": self.scene_name,
            "music_type": self.music_type,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "is_default": self.is_default
        }




