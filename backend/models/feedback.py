"""
反馈模型
定义用户反馈相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Feedback(Base):
    """用户反馈表模型"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    feedback_type = Column(String(20), nullable=False, comment="反馈类型")
    content = Column(Text, nullable=False, comment="反馈内容")
    score = Column(Integer, nullable=False, comment="满意度评分")
    submit_time = Column(DateTime, default=func.now(), comment="提交时间")
    
    # 关联关系
    user = relationship("User", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, type='{self.feedback_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feedback_type": self.feedback_type,
            "feedback_type_name": self.get_feedback_type_name(),
            "content": self.content,
            "score": self.score,
            "submit_time": self.submit_time.isoformat() if self.submit_time else None,
            # 当前系统没有审核状态字段，使用默认 'pending'（可由后台管理接口更新）
            "status": 'pending'
        }
    
    def get_feedback_type_name(self):
        """获取反馈类型的中文名称"""
        type_mapping = {
            "accuracy": "脑疲劳检测准确性",
            "music": "轻音乐推荐效果", 
            "function": "系统功能建议"
        }
        return type_mapping.get(self.feedback_type, self.feedback_type)




