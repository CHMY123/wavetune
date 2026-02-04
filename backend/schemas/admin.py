"""
CMS相关的数据验证模型
定义内容管理系统需要的数据结构
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# 音乐管理相关模型
class MusicCreate(BaseModel):
    """创建音乐"""
    title: str = Field(..., description="音乐标题")
    artist: str = Field(..., description="艺术家")
    duration: int = Field(..., description="时长（秒）")
    cover: Optional[str] = Field(None, description="封面路径")
    audio_url: str = Field(..., description="音频文件路径")
    music_type: str = Field(..., description="音乐类型")
    mood: str = Field(..., description="音乐情绪")
    description: Optional[str] = Field(None, description="音乐描述")


class MusicUpdate(BaseModel):
    """更新音乐"""
    title: Optional[str] = Field(None, description="音乐标题")
    artist: Optional[str] = Field(None, description="艺术家")
    duration: Optional[int] = Field(None, description="时长（秒）")
    cover: Optional[str] = Field(None, description="封面路径")
    audio_url: Optional[str] = Field(None, description="音频文件路径")
    music_type: Optional[str] = Field(None, description="音乐类型")
    mood: Optional[str] = Field(None, description="音乐情绪")
    description: Optional[str] = Field(None, description="音乐描述")


class MusicResponse(BaseModel):
    """音乐响应"""
    id: int
    title: str
    artist: str
    duration: int
    cover: Optional[str]
    audio_url: str
    music_type: str
    mood: str
    description: Optional[str]
    play_count: int
    created_at: datetime


# 用户管理相关模型
class UserUpdateAdmin(BaseModel):
    """管理员更新用户信息"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    is_active: Optional[bool] = Field(None, description="是否激活")
    role: Optional[str] = Field(None, description="用户角色")


class UserResponseAdmin(BaseModel):
    """管理员用户响应"""
    id: int
    username: str
    student_id: str
    email: Optional[str]
    phone: Optional[str]
    avatar: Optional[str]
    role: str
    is_active: bool
    detection_count: int
    intervention_count: int
    last_login_time: Optional[datetime]
    created_at: datetime


# 反馈管理相关模型
class FeedbackUpdate(BaseModel):
    """更新反馈"""
    status: Optional[str] = Field(None, description="反馈状态")
    reply: Optional[str] = Field(None, description="反馈回复")


class FeedbackResponseAdmin(BaseModel):
    """管理员反馈响应"""
    id: int
    user_id: int
    username: str
    type: str
    content: str
    status: str
    reply: Optional[str]
    created_at: datetime


# 系统配置相关模型
class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    config_key: str = Field(..., description="配置键")
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")


class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    id: int
    config_key: str
    config_value: str
    description: Optional[str]
    updated_at: datetime


# 批量操作相关模型
class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., description="要删除的ID列表")


class BatchUpdateRequest(BaseModel):
    """批量更新请求"""
    ids: List[int] = Field(..., description="要更新的ID列表")
    field: str = Field(..., description="要更新的字段")
    value: str = Field(..., description="更新的值")


# 分页相关模型
class PaginationRequest(BaseModel):
    """分页请求"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页大小")
    search: Optional[str] = Field(None, description="搜索关键词")
    filter: Optional[dict] = Field(None, description="筛选条件")


class PaginationResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    total_pages: int


# 通用响应模型
class AdminResponse(BaseModel):
    """CMS通用响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="操作成功", description="消息")
    data: Optional[dict] = Field(None, description="数据")
