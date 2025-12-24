"""
用户反馈路由
处理用户反馈相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from models.feedback import Feedback
from models.user import User
from schemas.feedback import FeedbackSubmit

router = APIRouter()

@router.post("/submit")
async def submit_feedback(feedback_data: FeedbackSubmit, db: Session = Depends(get_db)):
    """
    提交用户反馈
    
    提交用户反馈信息，包括反馈类型、内容和满意度评分
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == feedback_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 创建反馈记录
        feedback = Feedback(
            user_id=feedback_data.user_id,
            feedback_type=feedback_data.feedback_type,
            content=feedback_data.content,
            score=feedback_data.score,
            submit_time=datetime.now()
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return {
            "code": 200,
            "msg": "反馈提交成功",
            "data": {
                "feedback_id": feedback.id,
                "submit_time": feedback.submit_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"反馈提交失败: {str(e)}")

@router.get("/history")
async def get_feedback_history(
    user_id: int = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(5, ge=1, le=20, description="每页条数"),
    db: Session = Depends(get_db)
):
    """
    查询历史反馈
    
    分页查询用户的历史反馈记录
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总数
        total = db.query(Feedback).filter(Feedback.user_id == user_id).count()
        
        # 分页查询反馈记录
        feedbacks = db.query(Feedback).filter(
            Feedback.user_id == user_id
        ).order_by(
            Feedback.submit_time.desc()
        ).offset(offset).limit(page_size).all()
        
        # 转换为字典格式
        feedback_list = [feedback.to_dict() for feedback in feedbacks]
        
        return {
            "code": 200,
            "msg": "查询成功",
            "data": {
                "total": total,
                "list": feedback_list,
                "page": page,
                "page_size": page_size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询反馈历史失败: {str(e)}")


@router.delete("/{feedback_id}")
async def delete_feedback(feedback_id: int, user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """
    删除单条反馈
    仅允许反馈所属用户删除（简单权限校验，后续可改为从 token 中解析用户）
    """
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")

        if feedback.user_id != user_id:
            raise HTTPException(status_code=403, detail="没有权限删除此反馈")

        db.delete(feedback)
        db.commit()

        return {
            "code": 200,
            "msg": "删除成功",
            "data": {"feedback_id": feedback_id}
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除反馈失败: {str(e)}")




