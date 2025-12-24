"""
场景配置路由
处理场景配置相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from models.scene import Scene
from models.user import User
from schemas.scene import SceneCreate

router = APIRouter()

@router.get("/list")
async def get_scene_list(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取场景列表
    
    获取用户的所有场景配置（包括系统默认场景）
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 查询用户的所有场景（包括系统默认场景）
        scenes = db.query(Scene).filter(
            (Scene.user_id == user_id) | (Scene.is_default == 1)
        ).order_by(Scene.is_default.desc(), Scene.create_time.desc()).all()
        
        # 转换为字典格式
        scene_list = [scene.to_dict() for scene in scenes]
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "scene_list": scene_list
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取场景列表失败: {str(e)}")

@router.post("/create")
async def create_scene(scene_data: SceneCreate, db: Session = Depends(get_db)):
    """
    创建场景
    
    创建用户自定义场景
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == scene_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查用户是否已有同名场景
        existing_scene = db.query(Scene).filter(
            Scene.user_id == scene_data.user_id,
            Scene.scene_name == scene_data.scene_name
        ).first()
        
        if existing_scene:
            raise HTTPException(status_code=400, detail="场景名称已存在")
        
        # 创建新场景
        scene = Scene(
            user_id=scene_data.user_id,
            scene_name=scene_data.scene_name,
            music_type=scene_data.music_type,
            is_default=0,  # 用户自定义场景
            create_time=datetime.now()
        )
        
        db.add(scene)
        db.commit()
        db.refresh(scene)
        
        return {
            "code": 200,
            "msg": "场景创建成功",
            "data": scene.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建场景失败: {str(e)}")

@router.get("/apply")
async def apply_scene(
    scene_id: int = Query(..., description="场景ID"),
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    应用场景
    
    应用指定场景，返回场景配置信息
    """
    try:
        # 查询场景
        scene = db.query(Scene).filter(Scene.id == scene_id).first()
        if not scene:
            raise HTTPException(status_code=404, detail="场景不存在")
        
        # 检查场景权限（用户自己的场景或系统默认场景）
        if scene.user_id != user_id and scene.is_default != 1:
            raise HTTPException(status_code=403, detail="无权限访问该场景")
        
        return {
            "code": 200,
            "msg": "应用成功",
            "data": {
                "scene_name": scene.scene_name,
                "music_type": scene.music_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用场景失败: {str(e)}")

@router.delete("/delete")
async def delete_scene(
    scene_id: int = Query(..., description="场景ID"),
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    删除场景
    
    删除用户自定义场景（不允许删除系统默认场景）
    """
    try:
        # 查询场景
        scene = db.query(Scene).filter(Scene.id == scene_id).first()
        if not scene:
            raise HTTPException(status_code=404, detail="场景不存在")
        
        # 检查是否为系统默认场景
        if scene.is_default == 1:
            raise HTTPException(status_code=403, detail="不允许删除默认场景")
        
        # 检查场景归属
        if scene.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权限删除该场景")
        
        # 删除场景
        db.delete(scene)
        db.commit()
        
        return {
            "code": 200,
            "msg": "场景删除成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除场景失败: {str(e)}")




