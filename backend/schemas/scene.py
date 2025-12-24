"""
场景相关的数据验证模型
使用 Pydantic 进行请求参数验证
"""

from pydantic import BaseModel, Field, validator
from typing import Optional

class SceneCreate(BaseModel):
    """场景创建模型"""
    user_id: int = Field(..., description="用户ID")
    scene_name: str = Field(..., min_length=1, max_length=50, description="场景名称")
    music_type: str = Field(..., description="音乐类型")
    
    @validator('scene_name')
    def validate_scene_name(cls, v):
        if not v.strip():
            raise ValueError('场景名称不能为空')
        return v.strip()
    
    @validator('music_type')
    def validate_music_type(cls, v):
        if v not in ['natural', 'piano', 'whitenoise', 'mix']:
            raise ValueError('音乐类型必须是 natural、piano、whitenoise 或 mix')
        return v




