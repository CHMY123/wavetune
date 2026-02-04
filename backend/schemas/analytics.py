"""
数据分析相关的数据验证模型
定义数据分析面板需要的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# 时间范围模型
class TimeRange(BaseModel):
    """时间范围"""
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")


# 基础统计模型
class BaseStats(BaseModel):
    """基础统计数据"""
    total: int = Field(..., description="总数")
    active: Optional[int] = Field(None, description="活跃数")
    growth: Optional[float] = Field(None, description="增长率")


# 用户统计模型
class UserStats(BaseModel):
    """用户统计数据"""
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    new_users_today: int = Field(..., description="今日新增用户")
    role_distribution: Dict[str, int] = Field(..., description="角色分布")
    growth_trend: List[Dict[str, Any]] = Field(..., description="增长趋势")


# 音乐统计模型
class MusicStats(BaseModel):
    """音乐统计数据"""
    total_music: int = Field(..., description="总音乐数")
    total_plays: int = Field(..., description="总播放量")
    top_played: List[Dict[str, Any]] = Field(..., description="播放量排行")
    type_distribution: Dict[str, int] = Field(..., description="音乐类型分布")
    mood_distribution: Dict[str, int] = Field(..., description="音乐情绪分布")


# 疲劳检测统计模型
class FatigueStats(BaseModel):
    """疲劳检测统计数据"""
    total_detections: int = Field(..., description="总检测次数")
    avg_fatigue_level: float = Field(..., description="平均疲劳等级")
    level_distribution: Dict[str, int] = Field(..., description="疲劳等级分布")
    detection_trend: List[Dict[str, Any]] = Field(..., description="检测趋势")
    intervention_stats: Dict[str, int] = Field(..., description="干预统计")


# 系统操作统计模型
class SystemStats(BaseModel):
    """系统操作统计数据"""
    total_operations: int = Field(..., description="总操作次数")
    error_rate: float = Field(..., description="错误率")
    operation_type_distribution: Dict[str, int] = Field(..., description="操作类型分布")
    response_time_trend: List[Dict[str, Any]] = Field(..., description="响应时间趋势")
    error_trend: List[Dict[str, Any]] = Field(..., description="错误趋势")


# 仪表盘概览模型
class DashboardOverview(BaseModel):
    """仪表盘概览数据"""
    user_stats: UserStats = Field(..., description="用户统计")
    music_stats: MusicStats = Field(..., description="音乐统计")
    fatigue_stats: FatigueStats = Field(..., description="疲劳检测统计")
    system_stats: SystemStats = Field(..., description="系统操作统计")


# 图表数据模型
class ChartData(BaseModel):
    """图表数据"""
    title: str = Field(..., description="图表标题")
    type: str = Field(..., description="图表类型")
    data: Dict[str, Any] = Field(..., description="图表数据")
    options: Optional[Dict[str, Any]] = Field(None, description="图表配置")


# 分析响应模型
class AnalyticsResponse(BaseModel):
    """分析响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="获取分析数据成功", description="消息")
    data: Dict[str, Any] = Field(..., description="分析数据")
