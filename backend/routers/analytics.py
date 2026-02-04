"""
数据分析路由
处理数据分析面板的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from config.database import get_db
from models.user import User
from models.music import Music
from models.operation_log import OperationLog
from models.two_back import TwoBack
from models.feedback import Feedback
from schemas.analytics import (
    TimeRange, UserStats, MusicStats, FatigueStats, SystemStats,
    DashboardOverview, ChartData, AnalyticsResponse
)
from middleware.auth import require_admin
from routers.auth import log_operation

router = APIRouter(prefix="/analytics", tags=["analytics"])


# 辅助函数：获取时间范围的默认值
def get_default_time_range(days: int = 30) -> TimeRange:
    """
    获取默认时间范围
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    return TimeRange(start_time=start_time, end_time=end_time)


# 辅助函数：格式化日期
def format_date(date_obj: datetime) -> str:
    """
    格式化日期为字符串
    """
    return date_obj.strftime("%Y-%m-%d")


# 用户分析
@router.get("/users")
async def get_user_analytics(
    time_range: Optional[TimeRange] = None,
    request: Request = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户分析数据
    """
    try:
        # 使用默认时间范围
        if not time_range:
            time_range = get_default_time_range()
        
        # 总用户数
        total_users = db.query(User).count()
        
        # 活跃用户数（30天内有登录）
        active_threshold = datetime.now() - timedelta(days=30)
        active_users = db.query(User).filter(
            User.last_login_time >= active_threshold
        ).count()
        
        # 今日新增用户
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = db.query(User).filter(
            User.create_time >= today_start
        ).count()
        
        # 角色分布
        role_distribution = db.query(
            User.role,
            func.count(User.id)
        ).group_by(User.role).all()
        role_dist_dict = {role: count for role, count in role_distribution}
        
        # 增长趋势（按天）
        growth_trend = []
        current_date = time_range.start_time
        while current_date <= time_range.end_time:
            next_date = current_date + timedelta(days=1)
            user_count = db.query(User).filter(
                User.create_time >= current_date,
                User.create_time < next_date
            ).count()
            growth_trend.append({
                "date": format_date(current_date),
                "count": user_count
            })
            current_date = next_date
        
        # 构造响应
        user_stats = UserStats(
            total_users=total_users,
            active_users=active_users,
            new_users_today=new_users_today,
            role_distribution=role_dist_dict,
            growth_trend=growth_trend
        )
        
        if request:
            log_operation(db, current_user.id, "get_user_analytics", "获取用户分析数据", request)
        
        return {
            "code": 200,
            "msg": "获取用户分析数据成功",
            "data": user_stats.model_dump()
        }
        
    except Exception as e:
        if request:
            log_operation(db, current_user.id, "get_user_analytics", f"获取用户分析数据失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取用户分析数据失败: {str(e)}")


# 音乐分析
@router.get("/music")
async def get_music_analytics(
    time_range: Optional[TimeRange] = None,
    request: Request = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取音乐分析数据
    """
    try:
        # 使用默认时间范围
        if not time_range:
            time_range = get_default_time_range()
        
        # 总音乐数
        total_music = db.query(Music).count()
        
        # 总播放量（假设Music模型有play_count字段）
        total_plays_result = db.query(func.sum(Music.play_count)).scalar()
        total_plays = total_plays_result or 0
        
        # 播放量排行
        top_played = db.query(
            Music.id,
            Music.title,
            Music.artist,
            Music.play_count
        ).order_by(Music.play_count.desc()).limit(10).all()
        
        top_played_list = [
            {
                "id": music.id,
                "title": music.title,
                "artist": music.artist,
                "play_count": music.play_count
            }
            for music in top_played
        ]
        
        # 音乐类型分布
        type_distribution = db.query(
            Music.music_type,
            func.count(Music.id)
        ).group_by(Music.music_type).all()
        type_dist_dict = {music_type: count for music_type, count in type_distribution}
        
        # 音乐情绪分布
        mood_distribution = db.query(
            Music.mood,
            func.count(Music.id)
        ).group_by(Music.mood).all()
        mood_dist_dict = {mood: count for mood, count in mood_distribution}
        
        # 构造响应
        music_stats = MusicStats(
            total_music=total_music,
            total_plays=total_plays,
            top_played=top_played_list,
            type_distribution=type_dist_dict,
            mood_distribution=mood_dist_dict
        )
        
        if request:
            log_operation(db, current_user.id, "get_music_analytics", "获取音乐分析数据", request)
        
        return {
            "code": 200,
            "msg": "获取音乐分析数据成功",
            "data": music_stats.model_dump()
        }
        
    except Exception as e:
        if request:
            log_operation(db, current_user.id, "get_music_analytics", f"获取音乐分析数据失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取音乐分析数据失败: {str(e)}")


# 疲劳检测分析
@router.get("/fatigue")
async def get_fatigue_analytics(
    time_range: Optional[TimeRange] = None,
    request: Request = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取疲劳检测分析数据
    """
    try:
        # 使用默认时间范围
        if not time_range:
            time_range = get_default_time_range()
        
        # 总检测次数
        total_detections = db.query(TwoBack).count()
        
        # 平均疲劳等级
        avg_fatigue_result = db.query(func.avg(TwoBack.fatigue_level)).scalar()
        avg_fatigue_level = float(avg_fatigue_result) if avg_fatigue_result else 0.0
        
        # 疲劳等级分布
        level_distribution = db.query(
            TwoBack.fatigue_level,
            func.count(TwoBack.id)
        ).group_by(TwoBack.fatigue_level).all()
        level_dist_dict = {str(level): count for level, count in level_distribution}
        
        # 检测趋势（按天）
        detection_trend = []
        current_date = time_range.start_time
        while current_date <= time_range.end_time:
            next_date = current_date + timedelta(days=1)
            detection_count = db.query(TwoBack).filter(
                TwoBack.created_at >= current_date,
                TwoBack.created_at < next_date
            ).count()
            detection_trend.append({
                "date": format_date(current_date),
                "count": detection_count
            })
            current_date = next_date
        
        # 干预统计
        intervention_stats = db.query(
            User.intervention_count,
            func.count(User.id)
        ).group_by(User.intervention_count).all()
        intervention_dict = {str(count): user_count for count, user_count in intervention_stats}
        
        # 构造响应
        fatigue_stats = FatigueStats(
            total_detections=total_detections,
            avg_fatigue_level=avg_fatigue_level,
            level_distribution=level_dist_dict,
            detection_trend=detection_trend,
            intervention_stats=intervention_dict
        )
        
        if request:
            log_operation(db, current_user.id, "get_fatigue_analytics", "获取疲劳检测分析数据", request)
        
        return {
            "code": 200,
            "msg": "获取疲劳检测分析数据成功",
            "data": fatigue_stats.model_dump()
        }
        
    except Exception as e:
        if request:
            log_operation(db, current_user.id, "get_fatigue_analytics", f"获取疲劳检测分析数据失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取疲劳检测分析数据失败: {str(e)}")


# 系统操作分析
@router.get("/system")
async def get_system_analytics(
    time_range: Optional[TimeRange] = None,
    request: Request = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取系统操作分析数据
    """
    try:
        # 使用默认时间范围
        if not time_range:
            time_range = get_default_time_range()
        
        # 总操作次数
        total_operations = db.query(OperationLog).count()
        
        # 错误率
        error_operations = db.query(OperationLog).filter(
            OperationLog.response_status >= 400
        ).count()
        error_rate = (error_operations / total_operations * 100) if total_operations > 0 else 0.0
        
        # 操作类型分布
        operation_type_distribution = db.query(
            OperationLog.operation_type,
            func.count(OperationLog.id)
        ).group_by(OperationLog.operation_type).all()
        operation_type_dist_dict = {op_type: count for op_type, count in operation_type_distribution}
        
        # 响应时间趋势（这里简化处理，实际应该记录响应时间）
        response_time_trend = []
        current_date = time_range.start_time
        while current_date <= time_range.end_time:
            next_date = current_date + timedelta(days=1)
            # 假设我们有响应时间数据
            avg_response_time = 0.1  # 简化处理
            response_time_trend.append({
                "date": format_date(current_date),
                "avg_response_time": avg_response_time
            })
            current_date = next_date
        
        # 错误趋势（按天）
        error_trend = []
        current_date = time_range.start_time
        while current_date <= time_range.end_time:
            next_date = current_date + timedelta(days=1)
            error_count = db.query(OperationLog).filter(
                OperationLog.created_at >= current_date,
                OperationLog.created_at < next_date,
                OperationLog.response_status >= 400
            ).count()
            error_trend.append({
                "date": format_date(current_date),
                "count": error_count
            })
            current_date = next_date
        
        # 构造响应
        system_stats = SystemStats(
            total_operations=total_operations,
            error_rate=error_rate,
            operation_type_distribution=operation_type_dist_dict,
            response_time_trend=response_time_trend,
            error_trend=error_trend
        )
        
        if request:
            log_operation(db, current_user.id, "get_system_analytics", "获取系统操作分析数据", request)
        
        return {
            "code": 200,
            "msg": "获取系统操作分析数据成功",
            "data": system_stats.model_dump()
        }
        
    except Exception as e:
        if request:
            log_operation(db, current_user.id, "get_system_analytics", f"获取系统操作分析数据失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取系统操作分析数据失败: {str(e)}")


# 仪表盘概览
@router.get("/dashboard")
async def get_dashboard_overview(
    time_range: Optional[TimeRange] = None,
    request: Request = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取仪表盘概览数据
    """
    try:
        # 使用默认时间范围
        if not time_range:
            time_range = get_default_time_range()
        
        # 获取各模块的分析数据
        user_data = await get_user_analytics(time_range, request, current_user, db)
        music_data = await get_music_analytics(time_range, request, current_user, db)
        fatigue_data = await get_fatigue_analytics(time_range, request, current_user, db)
        system_data = await get_system_analytics(time_range, request, current_user, db)
        
        # 构造仪表盘概览数据
        dashboard_data = DashboardOverview(
            user_stats=UserStats(**user_data["data"]),
            music_stats=MusicStats(**music_data["data"]),
            fatigue_stats=FatigueStats(**fatigue_data["data"]),
            system_stats=SystemStats(**system_data["data"])
        )
        
        if request:
            log_operation(db, current_user.id, "get_dashboard_overview", "获取仪表盘概览数据", request)
        
        return {
            "code": 200,
            "msg": "获取仪表盘概览数据成功",
            "data": dashboard_data.model_dump()
        }
        
    except Exception as e:
        if request:
            log_operation(db, current_user.id, "get_dashboard_overview", f"获取仪表盘概览数据失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取仪表盘概览数据失败: {str(e)}")


# 图表数据
@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    time_range: Optional[TimeRange] = None,
    request: Request = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取图表数据
    
    chart_type: 用户增长趋势、音乐播放排行、疲劳等级分布、系统错误率趋势
    """
    try:
        # 使用默认时间范围
        if not time_range:
            time_range = get_default_time_range()
        
        chart_data = None
        
        if chart_type == "user_growth":
            # 用户增长趋势
            user_data = await get_user_analytics(time_range, request, current_user, db)
            growth_trend = user_data["data"]["growth_trend"]
            
            chart_data = ChartData(
                title="用户增长趋势",
                type="line",
                data={
                    "xAxis": [item["date"] for item in growth_trend],
                    "series": [{
                        "name": "新增用户",
                        "data": [item["count"] for item in growth_trend]
                    }]
                },
                options={
                    "xAxis": {"type": "category", "name": "日期"},
                    "yAxis": {"type": "value", "name": "新增用户数"}
                }
            )
            
        elif chart_type == "music_ranking":
            # 音乐播放排行
            music_data = await get_music_analytics(time_range, request, current_user, db)
            top_played = music_data["data"]["top_played"]
            
            chart_data = ChartData(
                title="音乐播放量排行",
                type="bar",
                data={
                    "xAxis": [f"{item['title']} - {item['artist']}" for item in top_played[:10]],
                    "series": [{
                        "name": "播放量",
                        "data": [item["play_count"] for item in top_played[:10]]
                    }]
                },
                options={
                    "xAxis": {"type": "category", "name": "音乐", "axisLabel": {"rotate": 45}},
                    "yAxis": {"type": "value", "name": "播放量"}
                }
            )
            
        elif chart_type == "fatigue_distribution":
            # 疲劳等级分布
            fatigue_data = await get_fatigue_analytics(time_range, request, current_user, db)
            level_distribution = fatigue_data["data"]["level_distribution"]
            
            chart_data = ChartData(
                title="疲劳等级分布",
                type="pie",
                data={
                    "series": [{
                        "name": "疲劳等级",
                        "data": [
                            {"name": level, "value": count}
                            for level, count in level_distribution.items()
                        ]
                    }]
                },
                options={
                    "tooltip": {"trigger": "item"},
                    "legend": {"orient": "vertical", "left": "left"}
                }
            )
            
        elif chart_type == "error_trend":
            # 系统错误率趋势
            system_data = await get_system_analytics(time_range, request, current_user, db)
            error_trend = system_data["data"]["error_trend"]
            
            chart_data = ChartData(
                title="系统错误趋势",
                type="line",
                data={
                    "xAxis": [item["date"] for item in error_trend],
                    "series": [{
                        "name": "错误数",
                        "data": [item["count"] for item in error_trend]
                    }]
                },
                options={
                    "xAxis": {"type": "category", "name": "日期"},
                    "yAxis": {"type": "value", "name": "错误数"}
                }
            )
            
        else:
            raise HTTPException(status_code=400, detail="无效的图表类型")
        
        if request:
            log_operation(db, current_user.id, "get_chart_data", f"获取图表数据-{chart_type}", request)
        
        return {
            "code": 200,
            "msg": "获取图表数据成功",
            "data": chart_data.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if request:
            log_operation(db, current_user.id, "get_chart_data", f"获取图表数据失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")
