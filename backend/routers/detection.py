from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from typing import Tuple

from utils.quick_detect import detect_from_array

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
