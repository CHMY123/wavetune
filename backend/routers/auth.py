"""
认证路由
处理用户注册、登录、登出等认证相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from models.user import User
from models.user_session import UserSession
from models.user_preference import UserPreference
from models.operation_log import OperationLog
from schemas.auth import (
    UserRegister, UserLogin, UserLogout, ChangePassword, 
    ResetPassword, UserProfileUpdate, UserPreferenceUpdate, UserDelete
)
from utils import qiniu_helper

router = APIRouter()

def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """获取用户代理"""
    return request.headers.get('User-Agent', '')

def log_operation(db: Session, user_id: Optional[int], operation_type: str, 
                 operation_desc: str, request: Request, response_status: int = 200):
    """记录操作日志"""
    try:
        log = OperationLog(
            user_id=user_id,
            operation_type=operation_type,
            operation_desc=operation_desc,
            request_method=request.method,
            request_url=str(request.url),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            response_status=response_status
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

@router.post("/register")
async def register_user(
    user_data: UserRegister, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    注册新用户账户
    """
    try:
        # 检查学号是否已存在
        existing_user = db.query(User).filter(User.student_id == user_data.student_id).first()
        if existing_user:
            log_operation(db, None, "user_register", "注册失败-学号已存在", request, 400)
            raise HTTPException(status_code=400, detail="学号已存在")
        
        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                log_operation(db, None, "user_register", "注册失败-邮箱已存在", request, 400)
                raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 创建新用户
        user = User(
            username=user_data.username,
            student_id=user_data.student_id,
            email=user_data.email,
            phone=user_data.phone,
            avatar="/static/avatar/default.jpg",
            is_active=True
        )
        user.set_password(user_data.password)
        
        db.add(user)
        db.flush()  # 获取用户ID
        
        # 创建默认偏好设置
        default_preferences = [
            ("default_fatigue_level", "medium"),
            ("preferred_music_type", "natural"),
            ("notification_enabled", "true"),
            ("auto_play", "false")
        ]
        
        for key, value in default_preferences:
            preference = UserPreference(
                user_id=user.id,
                preference_key=key,
                preference_value=value
            )
            db.add(preference)
        
        db.commit()
        
        log_operation(db, user.id, "user_register", "用户注册成功", request, 200)
        
        return {
            "code": 200,
            "msg": "注册成功",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "student_id": user.student_id,
                "email": user.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, None, "user_register", f"注册失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@router.post("/login")
async def login_user(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    验证用户凭据并创建会话
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.student_id == login_data.student_id).first()
        if not user:
            log_operation(db, None, "user_login", "登录失败-用户不存在", request, 404)
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查用户是否激活
        if not user.is_active:
            log_operation(db, user.id, "user_login", "登录失败-账户未激活", request, 403)
            raise HTTPException(status_code=403, detail="账户未激活")
        
        # 验证密码
        if not user.check_password(login_data.password):
            log_operation(db, user.id, "user_login", "登录失败-密码错误", request, 401)
            raise HTTPException(status_code=401, detail="密码错误")
        
        # 创建会话
        # 检查是否已存在相同设备的活跃会话：若存在，仅更新最后活动时间并延长过期时间，不新增记录
        # 确定用于识别设备的标识：优先使用前端传入的 device_info，否则使用 User-Agent（可进一步改为指纹）
        identifier = login_data.device_info or get_user_agent(request)

        existing_session = None
        try:
            if identifier:
                existing_session = db.query(UserSession).filter(
                    UserSession.user_id == user.id,
                    UserSession.device_info == identifier,
                    UserSession.is_active == True
                ).first()
                # 兼容：如果 device_info 存储为空（之前记录），也尝试按 user_agent 匹配
                if not existing_session and not login_data.device_info:
                    existing_session = db.query(UserSession).filter(
                        UserSession.user_id == user.id,
                        UserSession.user_agent == identifier,
                        UserSession.is_active == True
                    ).first()
        except Exception:
            existing_session = None

        if existing_session:
            # 更新活动时间、IP、user agent 并延长会话
            existing_session.last_activity = datetime.now()
            existing_session.ip_address = get_client_ip(request)
            existing_session.user_agent = get_user_agent(request)
            existing_session.extend_session(hours=24)
            session = existing_session
        else:
            # 创建新会话
            session = UserSession.create_session(
                user_id=user.id,
                device_info=login_data.device_info or get_user_agent(request),
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            db.add(session)
        
        # 更新最后登录时间
        user.last_login_time = datetime.now()
        
        db.commit()
        
        log_operation(db, user.id, "user_login", "用户登录成功", request, 200)
        
        return {
            "code": 200,
            "msg": "登录成功",
            "data": {
                "user": user.to_dict(),
                "session_token": session.session_token,
                "expire_time": session.expire_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, None, "user_login", f"登录失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.post("/logout")
async def logout_user(
    logout_data: UserLogout,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    使会话失效
    """
    try:
        # 查找会话
        session = db.query(UserSession).filter(
            UserSession.session_token == logout_data.session_token
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 使会话失效
        session.is_active = False
        db.commit()
        
        log_operation(db, session.user_id, "user_logout", "用户登出", request, 200)
        
        return {
            "code": 200,
            "msg": "登出成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, None, "user_logout", f"登出失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"登出失败: {str(e)}")


@router.post("/delete")
async def delete_user_account(
    delete_data: UserDelete,
    request: Request,
    db: Session = Depends(get_db)
):
    """删除用户账号及其关联数据（需要会话令牌验证）"""
    try:
        # 验证会话
        session = db.query(UserSession).filter(UserSession.session_token == delete_data.session_token).first()
        if not session or session.user_id != delete_data.user_id:
            raise HTTPException(status_code=403, detail="会话验证失败")

        user_id = delete_data.user_id

        # 删除关联数据：会话、偏好、反馈、场景、操作日志
        try:
            db.query(UserSession).filter(UserSession.user_id == user_id).delete(synchronize_session=False)
            from models.user_preference import UserPreference as _UP
            from models.feedback import Feedback as _FB
            from models.scene import Scene as _SC
            from models.operation_log import OperationLog as _OL

            db.query(_UP).filter(_UP.user_id == user_id).delete(synchronize_session=False)
            db.query(_FB).filter(_FB.user_id == user_id).delete(synchronize_session=False)
            db.query(_SC).filter(_SC.user_id == user_id).delete(synchronize_session=False)
            db.query(_OL).filter(_OL.user_id == user_id).delete(synchronize_session=False)
        except Exception:
            # 若删除关联项失败，继续尝试删除用户并回滚可能的部分删除
            pass

        # 最后删除用户记录
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            # 如果用户头像指向七牛域名，尝试删除七牛对象（容错，不影响主流程）
            try:
                avatar = (u.avatar or '').strip()
                if avatar and avatar.startswith('http') and qiniu_helper.QINIU_DOMAIN:
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(avatar)
                        domain = parsed.netloc
                        if domain.endswith(qiniu_helper.QINIU_DOMAIN):
                            key = parsed.path.lstrip('/')
                            try:
                                qiniu_helper.delete_key(key)
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
            db.delete(u)

        db.commit()

        log_operation(db, user_id, "user_delete", "用户账号已删除", request, 200)

        return {"code": 200, "msg": "用户已删除", "data": None}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, None, "user_delete", f"删除用户失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    修改用户密码
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 验证原密码
        if not user.check_password(password_data.old_password):
            log_operation(db, user.id, "change_password", "修改密码失败-原密码错误", request, 401)
            raise HTTPException(status_code=401, detail="原密码错误")
        
        # 设置新密码
        user.set_password(password_data.new_password)
        db.commit()
        
        log_operation(db, user.id, "change_password", "修改密码成功", request, 200)
        
        return {
            "code": 200,
            "msg": "密码修改成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, user_id, "change_password", f"修改密码失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")

@router.get("/profile")
async def get_user_profile(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取用户资料
    
    获取用户详细信息和偏好设置
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取用户偏好
        preferences = db.query(UserPreference).filter(UserPreference.user_id == user_id).all()
        preference_dict = {p.preference_key: p.preference_value for p in preferences}
        
        user_data = user.to_dict()
        user_data["preferences"] = preference_dict
        
        log_operation(db, user_id, "get_profile", "获取用户资料", request, 200)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_operation(db, user_id, "get_profile", f"获取用户资料失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取用户资料失败: {str(e)}")

@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    更新用户资料
    
    更新用户基本信息
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查邮箱是否被其他用户使用
        if profile_data.email and profile_data.email != user.email:
            existing_email = db.query(User).filter(
                User.email == profile_data.email,
                User.id != user_id
            ).first()
            if existing_email:
                log_operation(db, user_id, "update_profile", "更新资料失败-邮箱已存在", request, 400)
                raise HTTPException(status_code=400, detail="邮箱已被其他用户使用")
        
        # 更新用户信息
        if profile_data.username is not None:
            user.username = profile_data.username
        if profile_data.email is not None:
            user.email = profile_data.email
        if profile_data.phone is not None:
            user.phone = profile_data.phone
        
        db.commit()
        
        log_operation(db, user_id, "update_profile", "更新用户资料成功", request, 200)
        
        return {
            "code": 200,
            "msg": "资料更新成功",
            "data": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, user_id, "update_profile", f"更新用户资料失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"更新用户资料失败: {str(e)}")

@router.put("/preference")
async def update_user_preference(
    preference_data: UserPreferenceUpdate,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    更新用户偏好
    
    更新用户偏好设置
    """
    try:
        # 查找或创建偏好设置
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.preference_key == preference_data.preference_key
        ).first()
        
        if preference:
            preference.preference_value = preference_data.preference_value
        else:
            preference = UserPreference(
                user_id=user_id,
                preference_key=preference_data.preference_key,
                preference_value=preference_data.preference_value
            )
            db.add(preference)
        
        db.commit()
        
        log_operation(db, user_id, "update_preference", f"更新偏好设置-{preference_data.preference_key}", request, 200)
        
        return {
            "code": 200,
            "msg": "偏好设置更新成功",
            "data": preference.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, user_id, "update_preference", f"更新偏好设置失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"更新偏好设置失败: {str(e)}")

@router.get("/sessions")
async def get_user_sessions(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取用户会话列表
    
    获取用户的所有活跃会话
    """
    try:
        # 查找活跃会话
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).order_by(UserSession.last_activity.desc()).all()

        def format_device_display(device_info: str, user_agent: str) -> str:
            """返回简洁、可读的设备描述，用于前端显示。"""
            info = (device_info or "").lower()
            ua = (user_agent or "").lower()

            # 优先使用前端传入的 device_info（通常为自定义短名）
            if device_info and len(device_info) <= 64:
                return device_info

            # 常见平台判定
            if 'iphone' in ua or 'ipad' in ua:
                return 'iPhone/iPad'
            if 'android' in ua:
                return 'Android'
            if 'windows' in ua:
                return 'Windows'
            if 'macintosh' in ua or 'mac os' in ua:
                return 'macOS'
            if 'linux' in ua:
                return 'Linux'

            # 常见浏览器简略信息
            if 'chrome' in ua:
                return 'Chrome'
            if 'firefox' in ua:
                return 'Firefox'
            if 'safari' in ua and 'chrome' not in ua:
                return 'Safari'
            if 'edge' in ua:
                return 'Edge'

            # 最后降级：截取 user_agent 的前 40 个字符作为简短显示
            if user_agent:
                return (user_agent[:40] + '...') if len(user_agent) > 40 else user_agent

            return '未知设备'

        session_list = []
        for session in sessions:
            s = session.to_dict()
            s['device_display'] = format_device_display(session.device_info, session.user_agent)
            session_list.append(s)
        
        log_operation(db, user_id, "get_sessions", "获取用户会话列表", request, 200)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "sessions": session_list
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_operation(db, user_id, "get_sessions", f"获取会话列表失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")

@router.delete("/session/{session_id}")
async def revoke_session(
    session_id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    撤销会话
    
    使指定会话失效
    """
    try:
        # 查找会话
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 使会话失效
        session.is_active = False
        db.commit()
        
        log_operation(db, user_id, "revoke_session", f"撤销会话-{session_id}", request, 200)
        
        return {
            "code": 200,
            "msg": "会话已撤销",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_operation(db, user_id, "revoke_session", f"撤销会话失败-{str(e)}", request, 500)
        raise HTTPException(status_code=500, detail=f"撤销会话失败: {str(e)}")


