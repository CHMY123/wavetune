"""
用户相关的数据验证模型
使用 Pydantic 进行请求参数验证
"""

from pydantic import BaseModel, Field, validator
from typing import Optional

class UserUpdate(BaseModel):
    """用户信息更新模型"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    student_id: str = Field(..., min_length=1, max_length=20, description="学号")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v.strip():
            raise ValueError('学号不能为空')
        return v.strip()

class UserCountUpdate(BaseModel):
    """用户统计次数更新模型"""
    user_id: int = Field(..., description="用户ID")
    type: str = Field(..., description="统计类型")
    count: int = Field(default=1, ge=1, description="新增次数")
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['detection', 'intervention']:
            raise ValueError('统计类型必须是 detection 或 intervention')
        return v




