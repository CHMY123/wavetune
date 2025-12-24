"""
操作日志模型
定义系统操作日志相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class OperationLog(Base):
    """操作日志表模型"""
    __tablename__ = "operation_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), comment="用户ID")
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    operation_desc = Column(String(255), comment="操作描述")
    request_method = Column(String(10), comment="请求方法")
    request_url = Column(String(255), comment="请求URL")
    request_params = Column(Text, comment="请求参数")
    response_status = Column(Integer, comment="响应状态码")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    execution_time = Column(Integer, comment="执行时间(ms)")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="operation_logs")
    
    def __repr__(self):
        return f"<OperationLog(id={self.id}, user_id={self.user_id}, type='{self.operation_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operation_type": self.operation_type,
            "operation_desc": self.operation_desc,
            "request_method": self.request_method,
            "request_url": self.request_url,
            "response_status": self.response_status,
            "ip_address": self.ip_address,
            "execution_time": self.execution_time,
            "create_time": self.create_time.isoformat() if self.create_time else None
        }


