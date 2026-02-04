"""
CMS管理路由
处理内容管理系统的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from datetime import datetime, timedelta
import os
import shutil

from config.database import get_db
from models.user import User
from models.music import Music
from models.feedback import Feedback
from models.operation_log import OperationLog
from models.system_config import SystemConfig
from schemas.admin import (
    MusicCreate, MusicUpdate, MusicResponse,
    UserUpdateAdmin, UserResponseAdmin,
    FeedbackUpdate, FeedbackResponseAdmin,
    SystemConfigUpdate, SystemConfigResponse,
    BatchDeleteRequest, BatchUpdateRequest,
    PaginationRequest, PaginationResponse, AdminResponse
)
from middleware.auth import require_admin
from routers.auth import log_operation, get_client_ip, get_user_agent

router = APIRouter(prefix="/admin", tags=["admin"])


# 音乐管理
@router.post("/music")
async def create_music(
    music_data: MusicCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    创建音乐
    
    管理员创建新的音乐记录
    """
    try:
        # 创建音乐记录
        music = Music(
            title=music_data.title,
            artist=music_data.artist,
            duration=music_data.duration,
            cover=music_data.cover,
            audio_url=music_data.audio_url,
            music_type=music_data.music_type,
            mood=music_data.mood,
            description=music_data.description
        )
        
        db.add(music)
        db.commit()
        db.refresh(music)
        
        log_operation(db, current_user.id, "create_music", f"创建音乐-{music.title}", request)
        
        return {
            "code": 200,
            "msg": "音乐创建成功",
            "data": music.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "create_music", f"创建音乐失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"创建音乐失败: {str(e)}")


@router.get("/music")
async def get_music_list(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    music_type: Optional[str] = None,
    mood: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取音乐列表
    
    支持分页、搜索和筛选
    """
    try:
        query = db.query(Music)
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    Music.title.ilike(f"%{search}%"),
                    Music.artist.ilike(f"%{search}%")
                )
            )
        
        # 筛选
        if music_type:
            query = query.filter(Music.music_type == music_type)
        if mood:
            query = query.filter(Music.mood == mood)
        
        # 分页
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        music_list = query.order_by(Music.id.desc()).offset(offset).limit(page_size).all()
        
        return {
            "code": 200,
            "msg": "获取音乐列表成功",
            "data": {
                "items": [music.to_dict() for music in music_list],
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音乐列表失败: {str(e)}")


@router.get("/music/{music_id}")
async def get_music_detail(
    music_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取音乐详情
    """
    music = db.query(Music).filter(Music.id == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail="音乐不存在")
    
    return {
        "code": 200,
        "msg": "获取音乐详情成功",
        "data": music.to_dict()
    }


@router.put("/music/{music_id}")
async def update_music(
    music_id: int,
    music_data: MusicUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新音乐
    """
    try:
        music = db.query(Music).filter(Music.id == music_id).first()
        if not music:
            raise HTTPException(status_code=404, detail="音乐不存在")
        
        # 更新音乐信息
        update_data = music_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(music, field, value)
        
        db.commit()
        db.refresh(music)
        
        log_operation(db, current_user.id, "update_music", f"更新音乐-{music.title}", request)
        
        return {
            "code": 200,
            "msg": "音乐更新成功",
            "data": music.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "update_music", f"更新音乐失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"更新音乐失败: {str(e)}")


@router.delete("/music/{music_id}")
async def delete_music(
    music_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    删除音乐
    """
    try:
        music = db.query(Music).filter(Music.id == music_id).first()
        if not music:
            raise HTTPException(status_code=404, detail="音乐不存在")
        
        # 删除音乐文件（如果需要）
        # if music.audio_url and os.path.exists(music.audio_url):
        #     os.remove(music.audio_url)
        # if music.cover and os.path.exists(music.cover):
        #     os.remove(music.cover)
        
        db.delete(music)
        db.commit()
        
        log_operation(db, current_user.id, "delete_music", f"删除音乐-{music.title}", request)
        
        return {
            "code": 200,
            "msg": "音乐删除成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "delete_music", f"删除音乐失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"删除音乐失败: {str(e)}")


@router.post("/music/batch-delete")
async def batch_delete_music(
    delete_data: BatchDeleteRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    批量删除音乐
    """
    try:
        # 检查音乐是否存在
        music_list = db.query(Music).filter(Music.id.in_(delete_data.ids)).all()
        if not music_list:
            raise HTTPException(status_code=404, detail="音乐不存在")
        
        # 删除音乐
        for music in music_list:
            db.delete(music)
        
        db.commit()
        
        log_operation(db, current_user.id, "batch_delete_music", f"批量删除音乐-{len(delete_data.ids)}条", request)
        
        return {
            "code": 200,
            "msg": f"成功删除{len(delete_data.ids)}条音乐",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "batch_delete_music", f"批量删除音乐失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"批量删除音乐失败: {str(e)}")


# 用户管理
@router.get("/users")
async def get_user_list(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    
    支持分页、搜索和筛选
    """
    try:
        query = db.query(User)
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.student_id.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        # 筛选
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # 分页
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        user_list = query.order_by(User.id.desc()).offset(offset).limit(page_size).all()
        
        return {
            "code": 200,
            "msg": "获取用户列表成功",
            "data": {
                "items": [user.to_dict() for user in user_list],
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户详情
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "code": 200,
        "msg": "获取用户详情成功",
        "data": user.to_dict()
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新用户信息
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        log_operation(db, current_user.id, "update_user", f"更新用户-{user.username}", request)
        
        return {
            "code": 200,
            "msg": "用户信息更新成功",
            "data": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "update_user", f"更新用户失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")


@router.post("/users/batch-update")
async def batch_update_user(
    update_data: BatchUpdateRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    批量更新用户
    """
    try:
        # 检查用户是否存在
        user_list = db.query(User).filter(User.id.in_(update_data.ids)).all()
        if not user_list:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 批量更新
        for user in user_list:
            setattr(user, update_data.field, update_data.value)
        
        db.commit()
        
        log_operation(db, current_user.id, "batch_update_user", f"批量更新用户-{len(update_data.ids)}条", request)
        
        return {
            "code": 200,
            "msg": f"成功更新{len(update_data.ids)}条用户信息",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "batch_update_user", f"批量更新用户失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"批量更新用户失败: {str(e)}")


# 反馈管理
@router.get("/feedback")
async def get_feedback_list(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取反馈列表
    
    支持分页、搜索和筛选
    """
    try:
        query = db.query(Feedback).join(User, Feedback.user_id == User.id)
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    Feedback.content.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%")
                )
            )
        
        # 筛选
        if type:
            query = query.filter(Feedback.type == type)
        if status:
            query = query.filter(Feedback.status == status)
        
        # 分页
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        feedback_list = query.order_by(Feedback.id.desc()).offset(offset).limit(page_size).all()
        
        # 构造响应数据
        feedback_data = []
        for feedback in feedback_list:
            data = feedback.to_dict()
            data["username"] = feedback.user.username if feedback.user else "未知用户"
            feedback_data.append(data)
        
        return {
            "code": 200,
            "msg": "获取反馈列表成功",
            "data": {
                "items": feedback_data,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取反馈列表失败: {str(e)}")


@router.put("/feedback/{feedback_id}")
async def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新反馈
    """
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")
        
        # 更新反馈信息
        update_data = feedback_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        db.commit()
        db.refresh(feedback)
        
        log_operation(db, current_user.id, "update_feedback", f"更新反馈-{feedback.id}", request)
        
        return {
            "code": 200,
            "msg": "反馈更新成功",
            "data": feedback.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "update_feedback", f"更新反馈失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"更新反馈失败: {str(e)}")


# 系统配置管理
@router.get("/config")
async def get_system_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取系统配置
    """
    try:
        configs = db.query(SystemConfig).all()
        
        return {
            "code": 200,
            "msg": "获取系统配置成功",
            "data": [config.to_dict() for config in configs]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")


@router.put("/config")
async def update_system_config(
    config_data: SystemConfigUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新系统配置
    """
    try:
        # 查找或创建配置
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_data.config_key
        ).first()
        
        if config:
            # 更新配置
            config.config_value = config_data.config_value
            if config_data.description:
                config.description = config_data.description
        else:
            # 创建新配置
            config = SystemConfig(
                config_key=config_data.config_key,
                config_value=config_data.config_value,
                description=config_data.description
            )
            db.add(config)
        
        db.commit()
        
        log_operation(db, current_user.id, "update_config", f"更新系统配置-{config_data.config_key}", request)
        
        return {
            "code": 200,
            "msg": "系统配置更新成功",
            "data": config.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        log_operation(db, current_user.id, "update_config", f"更新系统配置失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"更新系统配置失败: {str(e)}")


# 上传文件
@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    上传文件
    
    支持上传音乐文件和封面图片
    """
    try:
        # 确保上传目录存在
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 构建文件URL
        file_url = f"/{file_path}"
        
        log_operation(db, current_user.id, "upload_file", f"上传文件-{file.filename}", request)
        
        return {
            "code": 200,
            "msg": "文件上传成功",
            "data": {
                "filename": filename,
                "file_url": file_url
            }
        }
        
    except Exception as e:
        log_operation(db, current_user.id, "upload_file", f"上传文件失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


# 系统统计
@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取仪表盘统计数据
    """
    try:
        # 用户统计
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(User.role == "admin").count()
        
        # 音乐统计
        total_music = db.query(Music).count()
        
        # 反馈统计
        total_feedback = db.query(Feedback).count()
        # 由于Feedback模型没有status字段，这里使用所有反馈数
        pending_feedback = total_feedback
        
        # 操作日志统计（最近7天）
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_operations = db.query(OperationLog).filter(
            OperationLog.create_time >= seven_days_ago
        ).count()
        
        return {
            "code": 200,
            "msg": "获取仪表盘统计数据成功",
            "data": {
                "user_stats": {
                    "total_users": total_users,
                    "new_users_today": 0,
                    "growth_trend": [],
                    "role_distribution": {
                        "admin": admin_users,
                        "user": total_users - admin_users
                    }
                },
                "music_stats": {
                    "total_music": total_music,
                    "total_plays": 0
                },
                "fatigue_stats": {
                    "total_detections": 0,
                    "avg_fatigue_level": 0,
                    "level_distribution": {}
                },
                "system_stats": {
                    "total_operations": recent_operations,
                    "error_rate": 0
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表盘统计数据失败: {str(e)}")



