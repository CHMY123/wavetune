"""
用户管理路由
处理用户信息相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime

from config.database import get_db
from models.user import User
from schemas.user import UserUpdate, UserCountUpdate
from utils import qiniu_helper

router = APIRouter()

@router.get("/info")
async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户信息
    
    根据用户ID查询用户详细信息
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.put("/update")
async def update_user_info(user_data: UserUpdate, db: Session = Depends(get_db)):
    """
    更新用户信息
    
    更新用户的基本信息，包括用户名和学号
    """
    try:
        user = db.query(User).filter(User.id == user_data.user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查学号是否与其他用户重复
        existing_user = db.query(User).filter(
            User.student_id == user_data.student_id,
            User.id != user_data.user_id
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="学号已存在")
        
        # 更新用户信息
        user.username = user_data.username
        user.student_id = user_data.student_id
        user.update_time = datetime.now()
        
        db.commit()
        
        return {
            "code": 200,
            "msg": "信息修改成功",
            "data": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

@router.post("/avatar/upload")
async def upload_avatar(
    user_id: int = Form(...),
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    上传头像文件并更新用户头像路径
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查文件格式
        if not avatar.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="仅支持图片格式")
        
        # 检查文件扩展名
        file_extension = os.path.splitext(avatar.filename)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png']:
            raise HTTPException(status_code=400, detail="仅支持 jpg/png 格式")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = f"{user_id}_{file_id}{file_extension}"

        # 优先使用七牛上传（需在 .env 中配置 QINIU_BUCKET 和 QINIU_DOMAIN）
        try:
            content = await avatar.read()
            if qiniu_helper.QINIU_BUCKET:
                key = f"avatar/{filename}"
                ret, info = qiniu_helper.upload_bytes(content, key)
                if info.status_code == 200:
                    avatar_url = qiniu_helper.make_url(key)
                else:
                    # 七牛上传失败，回退到本地保存
                    upload_dir = "static/avatar"
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)
                    with open(file_path, "wb") as buffer:
                        buffer.write(content)
                    avatar_url = f"/uploads/avatar/{filename}"
            else:
                # 未配置七牛，保存到本地
                upload_dir = "static/avatar"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                avatar_url = f"/static/avatar/{filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"头像上传失败: {str(e)}")
        user.avatar = avatar_url
        user.update_time = datetime.now()
        
        db.commit()
        
        return {
            "code": 200,
            "msg": "头像上传成功",
            "data": {
                "avatar_url": avatar_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"头像上传失败: {str(e)}")

@router.put("/count/update")
async def update_user_count(count_data: UserCountUpdate, db: Session = Depends(get_db)):
    """
    更新用户统计次数
    
    更新用户的检测次数或干预次数
    """
    try:
        user = db.query(User).filter(User.id == count_data.user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新对应类型的次数
        if count_data.type == "detection":
            user.detection_count += count_data.count
        elif count_data.type == "intervention":
            user.intervention_count += count_data.count
        else:
            raise HTTPException(status_code=400, detail="无效的统计类型")
        
        user.update_time = datetime.now()
        db.commit()
        
        return {
            "code": 200,
            "msg": "次数更新成功",
            "data": {
                "detection_count": user.detection_count,
                "intervention_count": user.intervention_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新统计次数失败: {str(e)}")




