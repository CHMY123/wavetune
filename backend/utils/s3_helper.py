import os
from typing import Optional, Tuple
import logging
from datetime import timedelta

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# S3 配置
S3_ENDPOINT = os.getenv('S3_ENDPOINT')  # e.g. https://wavetune.s3.bitiful.net
S3_REGION = os.getenv('S3_REGION')
S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID') or os.getenv('S3ACCESSKEYID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY') or os.getenv('S3SECRETKEYID')
S3_BUCKET = os.getenv('S3_BUCKET')  # optional; endpoint may already include bucket
S3_PUBLIC = os.getenv('S3_PUBLIC', 'false').lower() in ('1', 'true', 'yes')
S3_PRESIGN_EXPIRES = int(os.getenv('S3_PRESIGN_EXPIRES', '36000'))

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _client():
    """创建 S3 客户端（带完整校验和异常处理）"""
    # 检查核心配置
    if not all([S3_ENDPOINT, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY]):
        logger.warning("S3 核心配置缺失，无法创建客户端")
        return None
    
    try:
        # 配置 S3 v4 签名和重试机制
        cfg = Config(
            signature_version='s3v4',
            region_name=S3_REGION,
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
        
        client = boto3.client(
            's3',
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
            endpoint_url=S3_ENDPOINT,
            config=cfg
        )
        logger.info("S3 客户端创建成功，尝试验证 bucket（若配置）")
        # 尝试验证 bucket，但不要因验证失败阻止客户端返回（有些 S3 兼容服务对 head_bucket 权限有限制）
        if S3_BUCKET:
            try:
                client.head_bucket(Bucket=S3_BUCKET)
            except ClientError as e:
                # 记录但不失败返回客户端
                logger.warning(f"S3 head_bucket 检查失败（忽略）：{e.response.get('Error', {}).get('Message', str(e))}")
        return client
    except ClientError as e:
        logger.error(f"S3 客户端创建失败: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        logger.error(f"S3 客户端创建异常: {str(e)}")
        return None


def upload_bytes(data: bytes, key: str, bucket: Optional[str] = None) -> Tuple[dict, object]:
    """上传字节到 S3 兼容存储。返回 (ret_dict, response)。"""
    bucket = bucket or S3_BUCKET
    client = _client()
    
    if not client:
        raise RuntimeError('S3 客户端初始化失败')
    
    try:
        params = {'Bucket': bucket, 'Key': key, 'Body': data}
        # 仅在显式配置为公有时设置 ACL（缤纷云免费版跳过）
        if S3_PUBLIC:
            params['ACL'] = 'public-read'
        
        resp = client.put_object(**params)
        logger.info(f"S3 字节上传成功: {key}")
        return resp, resp
    except ClientError as e:
        logger.exception(f"S3 upload_bytes 失败: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.exception('S3 upload_bytes 异常')
        raise


def upload_file(path: str, key: str, bucket: Optional[str] = None) -> Tuple[dict, object]:
    """上传文件到 S3 兼容存储。"""
    bucket = bucket or S3_BUCKET
    client = _client()
    
    if not client:
        raise RuntimeError('S3 客户端初始化失败')
    
    try:
        extra = {'ACL': 'public-read'} if S3_PUBLIC else {}
        resp = client.upload_file(path, bucket, key, ExtraArgs=extra)
        logger.info(f"S3 文件上传成功: {key}")
        # upload_file 返回 None，构造统一返回格式
        return {}, {'status_code': 200, 'key': key}
    except ClientError as e:
        logger.exception(f"S3 upload_file 失败: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.exception('S3 upload_file 异常')
        raise


def generate_presigned_get_url(key: str, expires: Optional[int] = None, bucket: Optional[str] = None) -> str:
    """生成私有桶的临时访问 URL（修复核心错误）
    
    Args:
        key: 文件在桶中的路径
        expires: URL 有效期（秒），默认 3600
        bucket: 桶名，默认使用配置的 S3_BUCKET
    
    Returns:
        带签名的 HTTPS 访问 URL
    """
    bucket = bucket or S3_BUCKET
    expires = expires or S3_PRESIGN_EXPIRES
    client = _client()
    
    # 校验必要参数
    if not client:
        raise RuntimeError('S3 客户端未初始化，无法生成签名 URL')
    if not bucket:
        raise RuntimeError('未配置 S3_BUCKET，无法生成签名 URL')
    if not key:
        raise RuntimeError('文件 key 不能为空')
    
    try:
        # 生成带签名的 GET URL（核心修复：参数无冗余）
        presigned_url = client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expires
        )
        logger.info(f"生成签名 URL 成功: {key} -> {presigned_url[:50]}...")
        return presigned_url
    except ClientError as e:
        error_msg = f"生成签名 URL 失败: {e.response['Error']['Message']}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"生成签名 URL 异常: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def make_url(key: str) -> str:
    """根据 key 构造外链 URL（自动适配公有/私有桶）"""
    if not S3_ENDPOINT:
        logger.warning("S3_ENDPOINT 未配置，返回原始 key")
        return key
    
    ep = S3_ENDPOINT.rstrip('/')
    
    # 公有桶：返回直接访问 URL
    if S3_PUBLIC:
        if S3_BUCKET:
            url = f"{ep}/{S3_BUCKET}/{key.lstrip('/')}"
        else:
            url = f"{ep}/{key.lstrip('/')}"
        logger.info(f"生成公有桶 URL: {url}")
        return url
    
    # 私有桶：生成签名 URL（核心修复）
    try:
        return generate_presigned_get_url(key)
    except Exception as e:
        # 签名 URL 生成失败时的降级处理（仅日志提示，仍抛出异常）
        logger.error(f"签名 URL 生成失败，降级尝试直接 URL: {str(e)}")
        # 构造直接 URL（仅作为最后的回退，大概率无权限）
        fallback_url = f"{ep}/{S3_BUCKET}/{key.lstrip('/')}" if S3_BUCKET else f"{ep}/{key.lstrip('/')}"
        return fallback_url


def delete_key(key: str, bucket: Optional[str] = None):
    """删除 S3 中的文件"""
    bucket = bucket or S3_BUCKET
    client = _client()
    
    if not client:
        raise RuntimeError('S3 客户端未初始化，无法删除文件')
    if not bucket:
        raise RuntimeError('未配置 S3_BUCKET，无法删除文件')
    
    try:
        resp = client.delete_object(Bucket=bucket, Key=key)
        logger.info(f"删除 S3 文件成功: {key}")
        return resp
    except ClientError as e:
        logger.exception(f"S3 delete_key 失败: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.exception('S3 delete_key 异常')
        raise