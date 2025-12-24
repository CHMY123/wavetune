"""
认证相关的数据验证模型
使用 Pydantic 进行请求参数验证
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    student_id: str = Field(..., min_length=1, max_length=20, description="学号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
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
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v

class UserLogin(BaseModel):
    """用户登录模型"""
    student_id: str = Field(..., description="学号")
    password: str = Field(..., description="密码")
    device_info: Optional[str] = Field(None, description="设备信息")
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v.strip():
            raise ValueError('学号不能为空')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v.strip():
            raise ValueError('密码不能为空')
        return v

class UserLogout(BaseModel):
    """用户登出模型"""
    session_token: str = Field(..., description="会话令牌")

class ChangePassword(BaseModel):
    """修改密码模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度至少6位')
        return v

class ResetPassword(BaseModel):
    """重置密码模型"""
    student_id: str = Field(..., description="学号")
    email: EmailStr = Field(..., description="邮箱")
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v.strip():
            raise ValueError('学号不能为空')
        return v.strip()

class UserProfileUpdate(BaseModel):
    """用户资料更新模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None and not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip() if v else v

class UserPreferenceUpdate(BaseModel):
    """用户偏好更新模型"""
    preference_key: str = Field(..., min_length=1, max_length=50, description="偏好键")
    preference_value: Optional[str] = Field(None, description="偏好值")
    
    @validator('preference_key')
    def validate_preference_key(cls, v):
        if not v.strip():
            raise ValueError('偏好键不能为空')
        return v.strip()


