from fastapi import APIRouter, UploadFile, File, HTTPException, Body
import pandas as pd
import io
import os
from typing import Tuple, Dict, Any

from utils.quick_detect import detect_from_csv
from services.two_back_service import two_back_service
from services.data_storage import data_storage_service

router = APIRouter()


@router.post('/upload')
async def upload_and_detect(file: UploadFile = File(...)):
    """接收 CSV 文件，解析为多模态数据并运行检测，返回疲劳等级与概率。"""
    try:

        # 保存临时文件
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # 使用新的检测逻辑
        result = detect_from_csv(temp_file_path)
        
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        if result is None:
            raise HTTPException(status_code=400, detail='无法解析 CSV 文件或未找到有效的数据')

        return {
            'code': 200,
            'msg': '检测完成',
            'data': result
        }
    except HTTPException:
        raise
    except Exception as e:
        # 清理临时文件
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f'检测失败: {str(e)}')


@router.post('/two-back/init')
async def init_two_back_experiment(
    settings: Dict[str, Any] = Body(None)
):
    """初始化 2-Back 实验，返回实验配置和会话 ID"""
    try:
        # 调用服务初始化实验
        session_data = two_back_service.init_experiment(settings)
        
        # 保存会话到数据库
        data_storage_service.save_session(session_data)

        return {
            'code': 200,
            'msg': '实验初始化成功',
            'data': session_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'实验初始化失败: {str(e)}')


@router.post('/two-back/generate-sequence')
async def generate_two_back_sequence(
    trials: int = Body(..., embed=True),
    match_rate: float = Body(default=0.28),
    letters: list = Body(default=["A", "B", "C", "D", "E"])
):
    """生成 2-Back 实验刺激序列"""
    try:
        if trials < 3:
            raise HTTPException(status_code=400, detail='试次数必须大于等于 3')

        # 调用服务生成序列
        sequence, is_target = two_back_service.generate_2back_sequence(
            length=trials,
            match_rate=match_rate,
            letters=letters
        )

        return {
            'code': 200,
            'msg': '序列生成成功',
            'data': {
                'sequence': sequence,
                'targets': is_target
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'序列生成失败: {str(e)}')


@router.post('/two-back/record-trial')
async def record_two_back_trial(
    request_data: Dict[str, Any] = Body(...)
):
    session_id = request_data.get('session_id')
    trial_data = request_data.get('trial_data')
    if not session_id or not trial_data:
        raise HTTPException(status_code=400, detail='缺少必要参数: session_id 或 trial_data')
    """记录 2-Back 实验试次数据"""
    try:
        # 调用服务记录试次
        result = two_back_service.record_trial(session_id, trial_data)
        
        # 保存试次到数据库
        data_storage_service.save_trial(session_id, trial_data)

        return {
            'code': 200,
            'msg': '试次记录成功',
            'data': result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'试次记录失败: {str(e)}')


@router.post('/two-back/record-kss')
async def record_two_back_kss(
    session_id: str = Body(..., embed=True),
    round: int = Body(..., embed=True),
    score: int = Body(..., embed=True)
):
    """记录 2-Back 实验 KSS 评分"""
    try:
        if score < 1 or score > 9:
            raise HTTPException(status_code=400, detail='KSS 评分必须在 1-9 之间')

        # 调用服务记录 KSS
        result = two_back_service.record_kss(session_id, round, score)
        
        # 保存 KSS 到数据库
        data_storage_service.save_kss_score(session_id, {'round': round, 'score': score, 'timestamp': result['timestamp']})

        return {
            'code': 200,
            'msg': 'KSS 评分记录成功',
            'data': result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'KSS 评分记录失败: {str(e)}')


@router.post('/two-back/complete')
async def complete_two_back_experiment(
    session_id: str = Body(..., embed=True)
):
    """完成 2-Back 实验，返回实验结果分析"""
    try:
        # 调用服务完成实验
        analysis_result = two_back_service.complete_experiment(session_id)
        
        # 更新会话状态到数据库
        session_data = data_storage_service.get_session(session_id)
        if session_data:
            session_data['status'] = 'completed'
            session_data['end_time'] = analysis_result['end_time']
            session_data['overall_hit_rate'] = analysis_result['overall_hit_rate']
            session_data['total_trials'] = analysis_result['total_trials']
            data_storage_service.save_session(session_data)

        return {
            'code': 200,
            'msg': '实验完成成功',
            'data': analysis_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'实验完成失败: {str(e)}')


@router.post('/two-back/trigger')
async def send_two_back_trigger(
    marker: int = Body(..., embed=True),
    port: int = Body(default=12345),
    ip: str = Body(default='127.0.0.1')
):
    """发送 2-Back 实验 EEG 触发信号"""
    try:
        # 调用服务发送触发信号
        result = two_back_service.trigger(marker, port, ip)

        return {
            'code': 200,
            'msg': '触发信号发送成功',
            'data': result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'触发信号发送失败: {str(e)}')

@router.post('/process_csv')
async def process_csv(file: UploadFile = File(...)):
    """处理CSV文件并返回提取的数据"""
    try:
        import tempfile
        import numpy as np
        from utils.processing_fNIRS_new import get_processing_from_origin_data_48_ch, process_origin_to_fNIRS
        
        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 加载并处理数据
        print(f"📁 处理文件: {temp_file_path}")
        try:
            raw_data = np.loadtxt(temp_file_path, delimiter=',').T
        except ValueError:
            raw_data = np.loadtxt(temp_file_path).T
        print(f"   原始数据形状: {raw_data.shape}")
        
        # 提取数据，只取前500个点
        max_points = 500
        eeg_data = raw_data[1:33, :max_points].tolist()
        fnirs_raw = raw_data[33:57, :max_points].tolist()
        marker_data = raw_data[56, :max_points].tolist()
        label_data = raw_data[-1, :max_points].tolist()
        
        marker_col_index = 56
        fNIRS_channels, data_780, data_850, _ = get_processing_from_origin_data_48_ch(raw_data, marker_col_index)
        
        hbo, hbr = [], []
        if len(data_780) > 0 and len(data_780[0]) > 0:
            hbo, hbr = process_origin_to_fNIRS(
                np.array(data_850).T, 
                np.array(data_780).T, 
                [850, 780]
            )
            # 只取前500个点
            hbo = hbo.T[:, :max_points].tolist()
            hbr = hbr.T[:, :max_points].tolist()
        
        extracted_data = {
            'eeg': eeg_data,
            'fnirs_raw': fnirs_raw,
            'hbo': hbo,
            'hbr': hbr,
            'marker': marker_data,
            'label': label_data,
            'shape': list(raw_data.shape)
        }
        
        # 清理临时文件
        import os
        os.unlink(temp_file_path)
        
        return extracted_data
    except Exception as e:
        # 确保临时文件被清理
        if 'temp_file_path' in locals():
            try:
                import os
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
