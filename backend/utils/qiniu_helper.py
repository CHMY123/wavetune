import os
from typing import Optional, Tuple
from qiniu import Auth, put_data, put_file, BucketManager
from dotenv import load_dotenv

# 尝试加载 .env 文件（确保在模块导入时可用）
load_dotenv()

# Load config from environment
QINIU_ACCESS_KEY = os.getenv('QINIU_ACCESS_KEY')
QINIU_SECRET_KEY = os.getenv('QINIU_SECRET_KEY')
QINIU_BUCKET = os.getenv('QINIU_BUCKET')
QINIU_DOMAIN = os.getenv('QINIU_DOMAIN')  # 不含协议
QINIU_GET = os.getenv('QINIU_GET')  # 可选的下载域名


def _auth() -> Auth:
    return Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)


def upload_bytes(data: bytes, key: str, bucket: Optional[str] = None, expires: int = 3600) -> Tuple[dict, object]:
    """上传字节数据到七牛，返回(ret, info)。"""
    if bucket is None:
        bucket = QINIU_BUCKET
    token = _auth().upload_token(bucket, key, expires)
    ret, info = put_data(token, key, data)
    return ret, info


def upload_file(path: str, key: str, bucket: Optional[str] = None, expires: int = 3600) -> Tuple[dict, object]:
    if bucket is None:
        bucket = QINIU_BUCKET
    token = _auth().upload_token(bucket, key, expires)
    ret, info = put_file(token, key, path)
    return ret, info


def make_url(key: str) -> str:
    """根据 key 构造外链 URL（使用 QINIU_DOMAIN）。"""
    if not QINIU_DOMAIN:
        # fallback to key path
        return key
    domain = QINIU_GET.rstrip('/')
    return f"http://{domain}/{key}"


def delete_key(key: str, bucket: Optional[str] = None) -> Tuple[dict, object]:
    if bucket is None:
        bucket = QINIU_BUCKET
    bm = BucketManager(_auth())
    return bm.delete(bucket, key)
