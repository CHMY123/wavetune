"""
系统统计路由
处理首页统计数据相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from config.database import get_db
from models.system_stats import SystemStats

router = APIRouter()

@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """
    获取系统统计数据
    
    返回首页展示的统计数据，包括检测次数、干预次数、参与设备、模型准确率等
    """
    try:
        # 查询所有统计数据
        stats_records = db.query(SystemStats).all()
        
        if not stats_records:
            raise HTTPException(status_code=404, detail="统计数据不存在")
        
        # 转换为前端需要的格式
        stats_mapping = {
            "detection_count": {
                "id": 1,
                "label": "检测次数",
                "icon": "DataAnalysis",
                "iconClass": "detection"
            },
            "intervention_count": {
                "id": 2,
                "label": "干预次数", 
                "icon": "Headphones",
                "iconClass": "music"
            },
            "device_count": {
                "id": 3,
                "label": "参与设备",
                "icon": "Monitor",
                "iconClass": "devices"
            },
            "model_accuracy": {
                "id": 4,
                "label": "模型准确率",
                "icon": "TrendCharts",
                "iconClass": "accuracy"
            }
        }
        
        stats_list = []
        for record in stats_records:
            if record.stat_name in stats_mapping:
                stat_info = stats_mapping[record.stat_name].copy()
                stat_info["value"] = record.stat_value
                stats_list.append(stat_info)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "stats": stats_list
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")




