"""
系统配置模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from config.database import Base


class SystemConfig(Base):
    """
    系统配置表
    """
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(255), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, nullable=False, comment="配置值")
    description = Column(Text, nullable=True, comment="配置描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            "id": self.id,
            "config_key": self.config_key,
            "config_value": self.config_value,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
