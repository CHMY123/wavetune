"""
联邦学习相关路由
处理联邦学习设备管理、训练记录和统计数据的API请求
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.federated import FederatedTraining, FederatedDevice, FederatedStats, SignalDetectionCount
from models.user import User
from schemas.auth import TokenData
from middleware.auth import get_current_user, get_current_user_optional, require_admin
from config.database import get_db
from typing import List, Optional
import os
import uuid
import subprocess
import time
import json
from datetime import datetime, timezone, timedelta
from utils.s3_helper import upload_file

# 北京时间时区
BEIJING_TZ = timezone(timedelta(hours=8))

router = APIRouter(prefix="/api/federated", tags=["federated"])

# 临时目录用于存储上传的CSV文件
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# 全局训练进度存储
training_progress_store = {}

@router.post("/upload-data")
async def upload_federated_data(
    file: UploadFile = File(...),
    rounds: int = Form(..., ge=1, le=10),
    fatigue_status: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传CSV数据文件参与联邦学习
    
    - **file**: CSV数据文件
    - **rounds**: 训练轮次（1-10）
    - **fatigue_status**: 疲劳状态
    """
    try:
        # 保存上传的文件
        file_id = str(uuid.uuid4())
        file_path = os.path.join(TEMP_DIR, f"{file_id}.csv")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 生成客户端ID
        client_id = f"client_{current_user.id}_{int(time.time())}"
        
        # 记录训练任务
        training = FederatedTraining(
            user_id=current_user.id,
            client_id=client_id,
            round_number=rounds,
            status="pending",
            fatigue_status=fatigue_status,
            training_time=datetime.now(BEIJING_TZ)
        )
        db.add(training)
        db.commit()
        db.refresh(training)
        
        # 启动联邦学习训练
        def run_client():
            try:
                # 在子线程中重新获取数据库会话
                from config.database import get_db
                from models.user import User
                db_thread = next(get_db())
                # 重新查询训练记录
                training_thread = db_thread.query(FederatedTraining).filter(
                    FederatedTraining.id == training.id
                ).first()
                
                # 重新获取用户信息
                user_id = training_thread.user_id
                user_thread = db_thread.query(User).filter(User.id == user_id).first()
                
                # 更新训练状态为训练中
                training_thread.status = "training"
                db_thread.commit()
                print(f"[联邦学习] 开始训练任务 ID: {training.id}, 客户端: {client_id}, 轮次: {rounds}")
                
                # 导入联邦学习训练器
                import sys
                federated_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "federated")
                print(f"[联邦学习] 联邦学习目录: {federated_dir}")
                if federated_dir not in sys.path:
                    sys.path.insert(0, federated_dir)
                
                from federated.federated_trainer import FederatedTrainer
                
                # 初始化训练器
                print(f"[联邦学习] 开始初始化训练器...")
                # 先更新初始化进度
                training_progress_store[training.id] = {
                    "progress": 10,
                    "message": "正在初始化训练器..."
                }
                print(f"[联邦学习] 初始化进度: 10% - 正在初始化训练器...")
                
                trainer = FederatedTrainer(
                    data_path=TEMP_DIR,
                    client_id=client_id,
                    rounds=rounds,
                    epochs=1,
                    batch_size=8,
                    use_gpu=False  # 使用CPU训练以避免GPU资源竞争
                )
                
                # 初始化完成，更新进度
                training_progress_store[training.id] = {
                    "progress": 20,
                    "message": "训练器初始化完成，准备开始训练"
                }
                print(f"[联邦学习] 初始化进度: 20% - 训练器初始化完成，准备开始训练")
                
                # 进度回调函数
                progress_data = {"current": 0}
                def progress_callback(progress, message):
                    progress_data["current"] = progress
                    # 更新全局进度存储
                    training_progress_store[training.id] = {
                        "progress": progress,
                        "message": message
                    }
                    print(f"[联邦学习] 进度更新: {progress:.1f}% - {message}")
                
                # 执行训练
                accuracy, loss, history = trainer.train(progress_callback)
                
                # 保存模型
                model_path = os.path.join(TEMP_DIR, f"{client_id}_model.pth")
                trainer.save_model(model_path)
                
                # 保存训练结果
                result_path = os.path.join(TEMP_DIR, f"{client_id}_result.json")
                trainer.save_history(result_path)
                
                print(f"[联邦学习] 训练完成: 准确率={accuracy:.4f}, 损失={loss:.4f}")
                
                # 更新训练状态和结果
                training_thread.status = "completed"
                training_thread.accuracy = accuracy
                training_thread.loss = loss
                print(f"[联邦学习] 训练任务完成，ID: {training.id}, 准确率: {accuracy:.2f}, 损失: {loss:.2f}")
                
                # 更新联邦学习统计数据
                stats = db_thread.query(FederatedStats).first()
                if stats:
                    stats.total_participants += 1
                    stats.total_rounds += rounds
                    # 简单的移动平均计算
                    stats.average_accuracy = (
                        (stats.average_accuracy * (stats.total_participants - 1) + accuracy) / 
                        stats.total_participants
                    )
                    stats.average_loss = (
                        (stats.average_loss * (stats.total_participants - 1) + loss) / 
                        stats.total_participants
                    )
                    print(f"[联邦学习] 更新统计数据: 总参与数={stats.total_participants}, 总轮次={stats.total_rounds}")
                
                # 更新设备信息
                device = db_thread.query(FederatedDevice).filter(
                    FederatedDevice.user_id == user_id,
                    FederatedDevice.device_id == client_id
                ).first()
                
                if not device:
                    device = FederatedDevice(
                        user_id=user_id,
                        device_id=client_id,
                        device_type="local",
                        status="online",
                        training_count=1,
                        contribution=accuracy * 100
                    )
                    db_thread.add(device)
                    # 更新统计数据中的设备数
                    if stats:
                        stats.total_devices += 1
                    print(f"[联邦学习] 新增设备: {client_id}")
                else:
                    device.training_count += 1
                    device.contribution = (
                        (device.contribution * (device.training_count - 1) + accuracy * 100) / 
                        device.training_count
                    )
                    device.last_participate = training_thread.training_time
                    print(f"[联邦学习] 更新设备: {client_id}, 训练次数={device.training_count}")
                
                # 上传模型参数到缤纷云存储桶
                try:
                    # 使用实际保存的模型文件路径
                    model_path = os.path.join(TEMP_DIR, f"{client_id}_model.pth")
                    if os.path.exists(model_path):
                        # 生成唯一的存储键
                        timestamp = int(time.time())
                        s3_key = f"federated/models/{client_id}_model_{timestamp}.pth"
                        # 上传文件
                        upload_file(model_path, s3_key)
                        print(f"[联邦学习] 模型参数已上传到缤纷云存储桶: {s3_key}")
                    else:
                        print(f"[联邦学习] 模型文件不存在，跳过上传: {model_path}")
                except Exception as e:
                    print(f"[联邦学习] 上传模型参数失败: {str(e)}")
                
                db_thread.commit()
                print(f"[联邦学习] 训练任务 ID: {training.id} 处理完成")
                
            except Exception as e:
                # 更新训练状态为失败
                try:
                    if 'training_thread' in locals() and training_thread:
                        training_thread.status = "failed"
                        db_thread.commit()
                except Exception as commit_error:
                    print(f"[联邦学习] 更新失败状态时出错: {str(commit_error)}")
                print(f"[联邦学习] 客户端训练失败: {str(e)}")
            finally:
                # 清理临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"[联邦学习] 清理临时文件: {file_path}")
                result_file = os.path.join(TEMP_DIR, f"{client_id}_result.json")
                if os.path.exists(result_file):
                    os.remove(result_file)
                    print(f"[联邦学习] 清理结果文件: {result_file}")
                # 关闭数据库会话
                if 'db_thread' in locals():
                    try:
                        db_thread.close()
                    except Exception as close_error:
                        print(f"[联邦学习] 关闭数据库会话时出错: {str(close_error)}")
                print(f"[联邦学习] 训练任务 ID: {training.id} 清理完成")
        
        # 在后台运行客户端
        import threading
        threading.Thread(target=run_client, daemon=True).start()
        
        return {
            "code": 200,
            "msg": "数据上传成功，训练任务已启动",
            "data": {
                "training_id": training.id,
                "client_id": client_id,
                "rounds": rounds
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.get("/training-records")
async def get_training_records(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取联邦学习训练记录
    管理员可以查看所有记录，普通用户只能查看自己的
    """
    try:
        # 手动解析查询参数
        query_params = dict(request.query_params)
        
        # 优先从params[page]和params[page_size]获取
        page = 1
        page_size = 10
        
        # 处理params[page]格式
        if 'params[page]' in query_params:
            try:
                page = int(query_params['params[page]'])
            except ValueError:
                page = 1
        # 处理直接的page参数
        elif 'page' in query_params:
            try:
                page = int(query_params['page'])
            except ValueError:
                page = 1
        
        # 处理params[page_size]格式
        if 'params[page_size]' in query_params:
            try:
                page_size = int(query_params['params[page_size]'])
            except ValueError:
                page_size = 10
        # 处理直接的page_size参数
        elif 'page_size' in query_params:
            try:
                page_size = int(query_params['page_size'])
            except ValueError:
                page_size = 10
        
        # 暂时只允许用户查看自己的记录
        # 后续可以根据实际的权限系统进行调整
        query = db.query(FederatedTraining).filter(
            FederatedTraining.user_id == current_user.id
        )
        
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        records = query.order_by(FederatedTraining.training_time.desc()).offset(offset).limit(page_size).all()
        
        # 构建响应数据
        items = []
        for record in records:
            items.append({
                "id": record.id,
                "user_id": record.user_id,
                "client_id": record.client_id,
                "rounds": record.round_number,
                "accuracy": record.accuracy,
                "loss": record.loss,
                "training_time": record.training_time.isoformat() if record.training_time else None,
                "status": record.status,
                "fatigue_status": record.fatigue_status
            })
        
        return {
            "code": 200,
            "msg": "获取训练记录成功",
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
        }
        
    except Exception as e:
        import traceback
        print(f"获取训练记录失败: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取训练记录失败: {str(e)}")

@router.get("/stats")
async def get_federated_stats(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取联邦学习统计数据
    """
    try:
        stats = db.query(FederatedStats).first()
        
        if not stats:
            # 如果没有统计数据，返回默认值
            stats_data = {
                "total_participants": 0,
                "total_devices": 0,
                "total_rounds": 0,
                "average_accuracy": 0,
                "average_loss": 0
            }
        else:
            stats_data = {
                "total_participants": stats.total_participants,
                "total_devices": stats.total_devices,
                "total_rounds": stats.total_rounds,
                "average_accuracy": stats.average_accuracy,
                "average_loss": stats.average_loss
            }
        
        return {
            "code": 200,
            "msg": "获取统计数据成功",
            "data": stats_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@router.get("/devices")
async def get_federated_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的联邦学习设备列表
    """
    try:
        devices = db.query(FederatedDevice).filter(
            FederatedDevice.user_id == current_user.id
        ).all()
        
        return {
            "code": 200,
            "msg": "获取设备列表成功",
            "data": [
                {
                    "id": device.id,
                    "user_id": device.user_id,
                    "device_id": device.device_id,
                    "device_type": device.device_type,
                    "status": device.status,
                    "last_participate": device.last_participate.isoformat() if device.last_participate else None,
                    "training_count": device.training_count,
                    "contribution": device.contribution
                }
                for device in devices
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备列表失败: {str(e)}")

@router.delete("/training-records/{record_id}")
async def delete_training_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除训练记录
    """
    try:
        record = db.query(FederatedTraining).filter(
            FederatedTraining.id == record_id,
            FederatedTraining.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="训练记录不存在")
        
        db.delete(record)
        db.commit()
        
        return {
            "code": 200,
            "msg": "删除训练记录成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除训练记录失败: {str(e)}")

@router.post("/signal-detection/count")
async def record_signal_detection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录信号检测次数
    """
    try:
        # 查找或创建信号检测计数记录
        detection_count = db.query(SignalDetectionCount).filter(
            SignalDetectionCount.user_id == current_user.id
        ).first()
        
        if not detection_count:
            detection_count = SignalDetectionCount(
                user_id=current_user.id,
                detection_count=1
            )
            db.add(detection_count)
        else:
            detection_count.detection_count += 1
        
        db.commit()
        
        return {
            "code": 200,
            "msg": "记录检测次数成功",
            "data": {
                "detection_count": detection_count.detection_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录检测次数失败: {str(e)}")

@router.get("/signal-detection/count")
async def get_signal_detection_count(
    db: Session = Depends(get_db)
):
    """
    获取信号检测次数（所有用户的总次数）
    """
    try:
        # 计算所有用户的总检测次数
        total_count = db.query(func.sum(SignalDetectionCount.detection_count)).scalar() or 0
        
        return {
            "code": 200,
            "msg": "获取检测次数成功",
            "data": {
                "detection_count": total_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测次数失败: {str(e)}")

@router.get("/training-status/{training_id}")
async def get_training_status(
    training_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取训练状态和进度
    """
    try:
        # 查询训练记录
        training = db.query(FederatedTraining).filter(
            FederatedTraining.id == training_id,
            FederatedTraining.user_id == current_user.id
        ).first()
        
        if not training:
            raise HTTPException(status_code=404, detail="训练记录不存在")
        
        # 获取训练进度
        progress = 0
        message = ""
        
        if training.status == "pending":
            progress = 0
            message = "等待训练开始"
        elif training.status == "training":
            # 从全局进度存储中获取真实进度
            if training.id in training_progress_store:
                progress = training_progress_store[training.id]["progress"]
                message = training_progress_store[training.id]["message"]
            else:
                progress = 0
                message = "训练初始化中..."
        elif training.status == "completed":
            progress = 100
            message = "训练完成"
        elif training.status == "failed":
            message = "训练失败"
        
        return {
            "code": 200,
            "msg": "获取训练状态成功",
            "data": {
                "status": training.status,
                "progress": progress,
                "message": message,
                "accuracy": training.accuracy,
                "loss": training.loss
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取训练状态失败: {str(e)}")
