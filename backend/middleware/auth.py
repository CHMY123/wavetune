"""
认证中间件
处理用户身份验证和会话管理
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from models.user import User
from models.user_session import UserSession

security = HTTPBearer()

class AuthManager:
    """认证管理器"""
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """获取当前用户"""
        token = credentials.credentials
        
        # 查找会话
        session = db.query(UserSession).filter(
            UserSession.session_token == token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=401, detail="无效的会话令牌")
        
        # 检查会话是否过期
        if session.is_expired():
            session.is_active = False
            db.commit()
            raise HTTPException(status_code=401, detail="会话已过期")
        
        # 查找用户
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="用户不存在或已被禁用")
        
        # 更新最后活动时间
        session.last_activity = datetime.now()
        db.commit()
        
        return user
    
    @staticmethod
    def get_current_user_optional(
        request: Request,
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        """获取当前用户（可选）"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            
            # 查找会话
            session = db.query(UserSession).filter(
                UserSession.session_token == token,
                UserSession.is_active == True
            ).first()
            
            if not session or session.is_expired():
                return None
            
            # 查找用户
            user = db.query(User).filter(User.id == session.user_id).first()
            if not user or not user.is_active:
                return None
            
            return user
        except Exception:
            return None
    
    @staticmethod
    def require_permission(permission: str):
        """权限装饰器"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # 这里可以实现基于角色的权限控制
                # 目前简化处理，所有认证用户都有权限
                return await func(*args, **kwargs)
            return wrapper
        return decorator

# 依赖注入函数
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    return AuthManager.get_current_user(credentials, db)

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，依赖注入）"""
    return AuthManager.get_current_user_optional(request, db)

def require_auth(user: User = Depends(get_current_user)) -> User:
    """要求认证（依赖注入）"""
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    """要求管理员权限（依赖注入）"""
    # 这里可以根据实际需求实现管理员权限检查
    # 目前简化处理
    if not user.is_active:
        raise HTTPException(status_code=403, detail="权限不足")
    return user


