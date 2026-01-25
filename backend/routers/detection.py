from fastapi import APIRouter, UploadFile, File, HTTPException, Body
import pandas as pd
import io
from typing import Tuple, Dict, Any

from utils.quick_detect import detect_from_array
from services.two_back_service import two_back_service
from services.data_storage import data_storage_service

router = APIRouter()


@router.post('/upload')
async def upload_and_detect(file: UploadFile = File(...)):
    """接收 CSV 文件，解析为 20x20 数组并运行检测，返回疲劳等级与概率。"""
    try:
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail='只接受 CSV 文件')

        content = await file.read()
        # 使用 pandas 读取，无 header
        df = pd.read_csv(io.BytesIO(content), header=None)
        if df.shape != (20, 20):
            raise HTTPException(status_code=400, detail='CSV 必须是 20x20 的数值表格')
        arr = df.values.astype(float)
        label, prob = detect_from_array(arr)

        # 返回更友好的标签名（前端显示使用首字母大写）
        label_map = {0: 'Low', 1: 'Medium', 2: 'High'}

        return {
            'code': 200,
            'msg': '检测完成',
            'data': {
                'label': int(label),
                'label_name': label_map.get(label, 'unknown'),
                'probabilities': prob.tolist()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
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
