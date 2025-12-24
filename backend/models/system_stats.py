"""
系统统计模型
定义系统统计数据相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from config.database import Base

class SystemStats(Base):
    """系统统计表模型"""
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stat_name = Column(String(50), nullable=False, comment="统计名称")
    stat_value = Column(String(20), nullable=False, comment="统计值")
    stat_unit = Column(String(10), comment="单位")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<SystemStats(id={self.id}, name='{self.stat_name}', value='{self.stat_value}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "stat_name": self.stat_name,
            "stat_value": self.stat_value,
            "stat_unit": self.stat_unit,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }




