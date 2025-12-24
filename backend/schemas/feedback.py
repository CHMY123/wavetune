"""
反馈相关的数据验证模型
使用 Pydantic 进行请求参数验证
"""

from pydantic import BaseModel, Field, validator
from typing import Optional

class FeedbackSubmit(BaseModel):
    """反馈提交模型"""
    user_id: int = Field(..., description="用户ID")
    feedback_type: str = Field(..., description="反馈类型")
    content: str = Field(..., min_length=10, max_length=500, description="反馈内容")
    score: int = Field(..., ge=1, le=5, description="满意度评分")
    
    @validator('feedback_type')
    def validate_feedback_type(cls, v):
        if v not in ['accuracy', 'music', 'function']:
            raise ValueError('反馈类型必须是 accuracy、music 或 function')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('反馈内容不能为空')
        return v.strip()




