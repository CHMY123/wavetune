"""
音乐推荐路由
处理音乐推荐相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import UploadFile, File
import os
import shutil
import time
import uuid
import tempfile
import logging

# 1. 配置日志（全局/局部统一配置，便于排查上传问题）
logger = logging.getLogger("music_api")
logger.setLevel(logging.INFO)
# 控制台输出格式（包含时间、日志名称、级别、文件名、行号、信息）
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3, APIC, TIT2, TPE1
    HAS_MUTAGEN = True
    logger.info("成功导入mutagen库，支持音乐元数据提取")
except Exception as e:
    HAS_MUTAGEN = False
    logger.warning(f"导入mutagen库失败，不支持音乐元数据提取，异常信息：{str(e)}")

from config.database import get_db
from models.music import Music
from utils import qiniu_helper
from utils import s3_helper

router = APIRouter()

# ========== 原有接口（略作日志补充，重点关注upload接口） ==========
@router.get("/recommend")
async def get_music_recommendations(
    fatigue_level: str = Query(..., description="疲劳等级"),
    music_type: Optional[str] = Query(None, description="音乐类型"),
    db: Session = Depends(get_db)
):
    """
    获取音乐推荐列表
    根据疲劳等级和音乐类型筛选推荐音乐
    """
    try:
        logger.info(f"接收音乐推荐请求，疲劳等级：{fatigue_level}，音乐类型：{music_type}")
        # 兼容不同命名：前端可能传 high/Low/Medium/low 等，统一到后端使用的 light/medium/heavy
        lvl = (fatigue_level or '').strip().lower()
        if lvl == 'high':
            lvl = 'heavy'
        elif lvl == 'low':
            lvl = 'light'

        # 验证疲劳等级参数
        if lvl not in ['light', 'medium', 'heavy']:
            logger.warning(f"疲劳等级参数无效，传入值：{fatigue_level}，正规化后：{lvl}")
            raise HTTPException(status_code=400, detail="疲劳等级必须是 light、medium、heavy（或其别名 high/low）")

        # 构建查询条件
        query = db.query(Music)

        # 根据疲劳等级筛选（使用正规化后的 lvl）
        query = query.filter(Music.fatigue_level == lvl)
        
        # 如果指定了音乐类型，则进一步筛选
        if music_type:
            if music_type not in ['natural', 'piano', 'whitenoise', 'mix']:
                logger.warning(f"音乐类型参数无效，传入值：{music_type}")
                raise HTTPException(status_code=400, detail="音乐类型必须是 natural、piano、whitenoise 或 mix")
            query = query.filter(Music.music_type == music_type)
        
        # 按匹配度降序排列
        music_list = query.order_by(Music.match_rate.desc()).all()
        logger.info(f"查询到音乐推荐列表，数量：{len(music_list)}")
        
        # 转换为字典格式
        music_data = [music.to_dict() for music in music_list]
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "music_list": music_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取音乐推荐失败，异常信息：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取音乐推荐失败: {str(e)}")

@router.get("/detail")
async def get_music_detail(
    music_id: int = Query(..., description="音乐ID"),
    db: Session = Depends(get_db)
):
    """
    获取音乐详情
    根据音乐ID获取音乐详细信息
    """
    try:
        logger.info(f"接收音乐详情请求，音乐ID：{music_id}")
        music = db.query(Music).filter(Music.id == music_id).first()
        
        if not music:
            logger.warning(f"音乐ID {music_id} 不存在")
            raise HTTPException(status_code=404, detail="音乐不存在")
        
        logger.info(f"成功获取音乐ID {music_id} 的详情")
        return {
            "code": 200,
            "msg": "获取成功",
            "data": music.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取音乐详情失败，音乐ID：{music_id}，异常信息：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取音乐详情失败: {str(e)}")

@router.get("/list")
async def list_music(
    db: Session = Depends(get_db)
):
    """
    列出所有音乐（不做复杂筛选），供前端获取实时列表
    """
    try:
        logger.info("接收所有音乐列表查询请求")
        music_list = db.query(Music).order_by(Music.match_rate.desc()).all()
        data = [m.to_dict() for m in music_list]
        logger.info(f"成功查询到所有音乐，数量：{len(music_list)}")
        return {"code": 200, "msg": "获取成功", "data": {"music_list": data}}
    except Exception as e:
        logger.error(f"获取音乐列表失败，异常信息：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取音乐列表失败: {str(e)}")

@router.post("")
async def add_music(item: dict, db: Session = Depends(get_db)):
    """
    添加音乐（简易接口，接收 json body）
    """
    try:
        logger.info(f"接收添加音乐请求，请求参数：{item}")
        # 期望字段：title, artist, duration, cover, reason, music_type, fatigue_level, match_rate, src 或 audio_url(optional)
        audio_src = item.get('src') or item.get('audio_url')
        music = Music(
            title=item.get('title'),
            artist=item.get('artist'),
            duration=item.get('duration'),
            cover=item.get('cover'),
            reason=item.get('reason'),
            music_type=item.get('music_type'),
            fatigue_level=item.get('fatigue_level'),
            match_rate=int(item.get('match_rate') or 0),
            audio_url=audio_src
        )
        db.add(music)
        db.commit()
        db.refresh(music)
        logger.info(f"成功添加音乐，音乐ID：{music.id}")
        return {"code": 200, "msg": "添加成功", "data": music.to_dict()}
    except Exception as e:
        db.rollback()
        logger.error(f"添加音乐失败，请求参数：{item}，异常信息：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"添加音乐失败: {str(e)}")

@router.delete("/{music_id}")
async def delete_music(music_id: int, delete_files: Optional[bool] = Query(False, description="是否同时删除磁盘文件"), db: Session = Depends(get_db)):
    """
    删除音乐（简易权限，后续可限制为管理员）
    """
    try:
        logger.info(f"接收删除音乐请求，音乐ID：{music_id}，是否删除文件：{delete_files}")
        music = db.query(Music).filter(Music.id == music_id).first()
        if not music:
            logger.warning(f"删除音乐失败，音乐ID {music_id} 不存在")
            raise HTTPException(status_code=404, detail="音乐不存在")
        # 在删除数据库记录前备份文件路径
        audio_url = music.audio_url
        cover_url = music.cover

        db.delete(music)
        db.commit()

        # 如果请求要求同时删除磁盘文件，则尝试删除对应的静态文件
        if delete_files:
            try:
                # 解析出静态相对路径，如 /static/music/xxx.mp3 或 /static/music_cover/xxx.jpg
                def _remove_static_path(url):
                    if not url:
                        return
                    # 如果是完整 URL，取 path 部分
                    path = url
                    try:
                        # handle full URL
                        if url.startswith('http'):
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            path = parsed.path
                            # 如果属于七牛域名，尝试删除七牛上的对象
                            # 七牛域名应配置在 qiniu_helper.QINIU_DOMAIN
                            try:
                                domain = parsed.netloc
                                if qiniu_helper.QINIU_DOMAIN and domain.endswith(qiniu_helper.QINIU_DOMAIN):
                                    # path 以 /key 开头，去掉前导 /
                                    key = parsed.path.lstrip('/')
                                    try:
                                        qiniu_helper.delete_key(key)
                                        logger.info(f"成功删除七牛云文件，Key：{key}")
                                    except Exception as e:
                                        logger.warning(f"删除七牛云文件失败，Key：{key}，异常信息：{str(e)}")
                                    return
                            except Exception as e:
                                logger.warning(f"解析七牛云域名失败，URL：{url}，异常信息：{str(e)}")
                    except Exception as e:
                        logger.warning(f"解析URL失败，URL：{url}，异常信息：{str(e)}")

                    # 支持 /static/... 或 static/...
                    rel = path.lstrip('/')
                    # 项目根目录为 routers 所在的父级的父级
                    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    file_path = os.path.join(root_dir, rel.replace('/', os.path.sep))
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            logger.info(f"成功删除本地文件，路径：{file_path}")
                        except Exception as e:
                            logger.warning(f"删除本地文件失败，路径：{file_path}，异常信息：{str(e)}")
                    else:
                        logger.warning(f"本地文件不存在，路径：{file_path}")

                _remove_static_path(audio_url)
                _remove_static_path(cover_url)
            except Exception as e:
                logger.warning(f"删除文件流程异常，忽略该错误，异常信息：{str(e)}")

        logger.info(f"成功删除音乐，音乐ID：{music_id}")
        return {"code": 200, "msg": "删除成功", "data": {"music_id": music_id}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除音乐失败，音乐ID：{music_id}，异常信息：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除音乐失败: {str(e)}")

# ========== 重点：上传接口（添加全流程时间统计和详细日志） ==========
@router.post("/upload")
async def upload_music_file(request: Request, file: UploadFile = File(...)):
    """
    接收上传的音乐文件，保存到 static/music 目录并返回可访问的 URL
    简易实现：不做复杂校验，直接保存并返回相对路径
    """
    # 记录上传总耗时
    start_total_time = time.time()
    tmp_path = None
    try:
        logger.info(f"===== 开始处理音乐文件上传 =====")
        logger.info(f"接收上传文件信息，文件名：{file.filename}，文件类型：{file.content_type}，文件流状态：{file.file.mode}")
        
        # 先把文件写到临时文件，便于 mutagen 处理
        original_filename = file.filename
        base, ext = os.path.splitext(original_filename)
        # 生成唯一文件名以避免冲突
        filename = f"{base}_{uuid.uuid4().hex}{ext}"
        logger.info(f"生成唯一文件名：{filename}（原始文件名：{original_filename}）")

        # 记录临时文件写入耗时
        start_tmp_write = time.time()
        tmp = tempfile.NamedTemporaryFile(delete=False)
        try:
            shutil.copyfileobj(file.file, tmp)
            tmp.flush()
            tmp_path = tmp.name
            tmp_size = os.path.getsize(tmp_path)
            logger.info(f"临时文件写入完成，路径：{tmp_path}，文件大小：{tmp_size / 1024 / 1024:.2f} MB，耗时：{time.time() - start_tmp_write:.2f} 秒")
        finally:
            tmp.close()

        # 优先使用 S3（缤纷云），其次使用七牛，最后回退到本地静态目录
        meta = {}
        used_local_tmp = True
        full_src = ""
        src_path = ""
        
        # 记录云存储/本地保存耗时
        start_storage_time = time.time()
        try:
            if s3_helper.S3_ENDPOINT:
                logger.info("开始尝试上传到S3（缤纷云）")
                with open(tmp_path, 'rb') as fobj:
                    data = fobj.read()
                key = f"music/{filename}"
                logger.info(f"S3上传Key：{key}，待上传数据大小：{len(data) / 1024 / 1024:.2f} MB")
                
                # 记录S3上传耗时
                start_s3_upload = time.time()
                ret, info = s3_helper.upload_bytes(data, key)
                s3_upload_cost = time.time() - start_s3_upload
                logger.info(f"S3上传接口调用完成，耗时：{s3_upload_cost:.2f} 秒，返回结果：{ret}，响应信息：{info}")
                
                status = None
                try:
                    status = ret.get('ResponseMetadata', {}).get('HTTPStatusCode')
                except Exception:
                    pass
                if status == 200 or (isinstance(info, dict) and info.get('status_code') == 200):
                    # 核心修改：使用 make_url 生成签名 URL（而非拼接）
                    full_src = s3_helper.make_url(key)
                    src_path = f"/{key}"
                    used_local_tmp = False
                    logger.info(f"S3上传成功，完整URL：{full_src}，相对路径：{src_path}")
                else:
                    raise Exception(f'S3 upload failed，状态码：{status}，响应信息：{info}')
                
            elif qiniu_helper.QINIU_BUCKET:
                logger.info("开始尝试上传到七牛云")
                with open(tmp_path, 'rb') as fobj:
                    data = fobj.read()
                key = f"music/{filename}"
                logger.info(f"七牛上传Key：{key}，待上传数据大小：{len(data) / 1024 / 1024:.2f} MB")
                
                # 记录七牛上传耗时
                start_qiniu_upload = time.time()
                ret, info = qiniu_helper.upload_bytes(data, key)
                qiniu_upload_cost = time.time() - start_qiniu_upload
                logger.info(f"七牛上传接口调用完成，耗时：{qiniu_upload_cost:.2f} 秒，返回结果：{ret}，响应信息：{info}")
                
                try:
                    if getattr(info, 'status_code', None) == 200:
                        full_src = qiniu_helper.make_url(key)
                        src_path = f"/{key}"
                        used_local_tmp = False
                        logger.info(f"七牛上传成功，完整URL：{full_src}，相对路径：{src_path}")
                    else:
                        raise Exception(f'Qiniu upload failed，状态码：{getattr(info, "status_code", None)}')
                except Exception:
                    raise
            else:
                logger.info("未配置云存储，准备回退到本地静态目录保存")
                # 未配置云存储，回退到本地静态目录
                root_dir = os.path.dirname(os.path.dirname(__file__))
                static_music_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music'))
                if not os.path.isdir(static_music_dir):
                    static_music_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music'))
                os.makedirs(static_music_dir, exist_ok=True)
                save_path = os.path.join(static_music_dir, filename)
                shutil.move(tmp_path, save_path)
                tmp_path = None
                src_path = f"/static/music/{filename}"
                try:
                    base_url = str(request.base_url).rstrip('/')
                    full_src = f"{base_url}{src_path}"
                except Exception:
                    full_src = src_path
                logger.info(f"本地静态目录保存成功，保存路径：{save_path}，完整URL：{full_src}，相对路径：{src_path}")
        except Exception as e:
            logger.warning(f"云存储上传失败，回退到本地静态目录，异常信息：{str(e)}")
            # 回退到本地静态目录
            root_dir = os.path.dirname(os.path.dirname(__file__))
            static_music_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music'))
            if not os.path.isdir(static_music_dir):
                static_music_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music'))
            os.makedirs(static_music_dir, exist_ok=True)
            save_path = os.path.join(static_music_dir, filename)
            try:
                shutil.move(tmp_path, save_path)
                logger.info(f"临时文件移动到本地静态目录成功，路径：{save_path}")
            except Exception as e1:
                logger.warning(f"临时文件移动失败，尝试复制文件，异常信息：{str(e1)}")
                # 如果移动失败，尝试复制
                try:
                    with open(tmp_path, 'rb') as r, open(save_path, 'wb') as w:
                        shutil.copyfileobj(r, w)
                    logger.info(f"临时文件复制到本地静态目录成功，路径：{save_path}")
                except Exception as e2:
                    logger.error(f"临时文件复制失败，异常信息：{str(e2)}")
                    raise e2
            tmp_path = None
            src_path = f"/static/music/{filename}"
            try:
                base_url = str(request.base_url).rstrip('/')
                full_src = f"{base_url}{src_path}"
            except Exception:
                full_src = src_path
            logger.info(f"本地静态目录备份保存成功，完整URL：{full_src}，相对路径：{src_path}")
        storage_cost = time.time() - start_storage_time
        logger.info(f"存储流程（云存储/本地）总耗时：{storage_cost:.2f} 秒")

        # 提取元数据与封面（如果可用）
        start_meta_extract = time.time()
        try:
            if HAS_MUTAGEN and tmp_path:
                logger.info("开始提取音乐元数据（标题、艺术家、时长）")
                m = MutagenFile(tmp_path, easy=True)
                if m:
                    title = m.get('title', [None])[0] if 'title' in m else None
                    artist = m.get('artist', [None])[0] if 'artist' in m else None
                    duration = None
                    try:
                        d = int(m.info.length)
                        mm = str(d // 60).zfill(2)
                        ss = str(d % 60).zfill(2)
                        duration = f"{mm}:{ss}"
                    except Exception as e:
                        duration = None
                        logger.warning(f"提取音乐时长失败，异常信息：{str(e)}")
                    meta.update({k: v for k, v in [('title', title), ('artist', artist), ('duration', duration)] if v})
                    logger.info(f"音乐元数据提取成功，元数据：{meta}")
                else:
                    logger.warning("mutagen无法解析该音乐文件，跳过元数据提取")

                try:
                    logger.info("开始提取音乐封面图片")
                    id3 = ID3(tmp_path)
                    pics = [v for k, v in id3.items() if isinstance(v, APIC)]
                    if pics:
                        pic = pics[0]
                        cover_bytes = pic.data
                        cover_key = f"music_cover/cover_{os.path.splitext(filename)[0]}.jpg"
                        logger.info(f"提取到封面图片，大小：{len(cover_bytes) / 1024:.2f} KB，准备上传封面，Key：{cover_key}")
                        try:
                            if s3_helper.S3_ENDPOINT:
                                ret2, info2 = s3_helper.upload_bytes(cover_bytes, cover_key)
                                status2 = ret2.get('ResponseMetadata', {}).get('HTTPStatusCode')
                                if status2 == 200:
                                    meta['cover'] = s3_helper.make_url(cover_key)
                                    logger.info(f"封面上传S3成功，URL：{meta['cover']}")
                            elif qiniu_helper.QINIU_BUCKET:
                                ret2, info2 = qiniu_helper.upload_bytes(cover_bytes, cover_key)
                                if getattr(info2, 'status_code', None) == 200:
                                    meta['cover'] = qiniu_helper.make_url(cover_key)
                                    logger.info(f"封面上传七牛成功，URL：{meta['cover']}")
                            else:
                                # 保存为本地静态文件（music_cover 目录）
                                root_dir = os.path.dirname(os.path.dirname(__file__))
                                static_cover_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music_cover'))
                                if not os.path.isdir(static_cover_dir):
                                    static_cover_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music_cover'))
                                os.makedirs(static_cover_dir, exist_ok=True)
                                cover_name = f"cover_{os.path.splitext(filename)[0]}.jpg"
                                cover_path = os.path.join(static_cover_dir, cover_name)
                                with open(cover_path, 'wb') as cf:
                                    cf.write(cover_bytes)
                                meta['cover'] = f"/static/music_cover/{cover_name}"
                                logger.info(f"封面保存到本地静态目录成功，路径：{cover_path}，URL：{meta['cover']}")
                        except Exception as e:
                            logger.warning(f"封面上传/保存失败，忽略该错误，异常信息：{str(e)}")
                    else:
                        logger.info("未在音乐文件中提取到封面图片")
                except Exception as e:
                    logger.warning(f"提取音乐封面失败，忽略该错误，异常信息：{str(e)}")
        except Exception as e:
            logger.warning(f"元数据/封面提取流程异常，忽略该错误，异常信息：{str(e)}")
        meta_extract_cost = time.time() - start_meta_extract
        logger.info(f"元数据+封面提取总耗时：{meta_extract_cost:.2f} 秒")

        # 清理临时文件（若存在）
        start_clean_tmp = time.time()
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                logger.info(f"临时文件清理成功，路径：{tmp_path}")
            else:
                logger.info("无临时文件需要清理")
        except Exception as e:
            logger.error(f"临时文件清理失败，路径：{tmp_path}，异常信息：{str(e)}")
        clean_tmp_cost = time.time() - start_clean_tmp
        logger.info(f"临时文件清理耗时：{clean_tmp_cost:.2f} 秒")

        # 构造响应
        resp = {"code": 200, "msg": "上传成功", "data": {"src": full_src, "src_rel": src_path}}
        if meta:
            resp['data'].update(meta)
        total_cost = time.time() - start_total_time
        logger.info(f"===== 音乐文件上传流程全部完成，总耗时：{total_cost:.2f} 秒，响应数据：{resp} =====")
        return resp
    except HTTPException:
        raise
    except Exception as e:
        # 异常时清理临时文件
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.info(f"上传异常，已清理临时文件，路径：{tmp_path}")
            except Exception as e2:
                logger.error(f"上传异常，临时文件清理失败，路径：{tmp_path}，异常信息：{str(e2)}")
        total_cost = time.time() - start_total_time
        logger.error(f"===== 音乐文件上传失败，总耗时：{total_cost:.2f} 秒，异常信息：{str(e)} =====", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.post("/upload_cover")
async def upload_cover_file(request: Request, file: UploadFile = File(...)):
    """
    上传单独的封面图片，保存到 static/music_cover 并返回可访问 URL
    """
    start_total_time = time.time()
    try:
        logger.info(f"===== 开始处理封面图片上传 =====")
        logger.info(f"接收封面上传文件信息，文件名：{file.filename}，文件类型：{file.content_type}")
        
        root_dir = os.path.dirname(os.path.dirname(__file__))
        cover_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music_cover'))
        if not os.path.isdir(cover_dir):
            cover_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music_cover'))
        os.makedirs(cover_dir, exist_ok=True)
        logger.info(f"封面保存目录：{cover_dir}")

        filename = file.filename
        save_path = os.path.join(cover_dir, filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(cover_dir, filename)
            counter += 1
        logger.info(f"生成唯一封面文件名：{filename}（原始文件名：{file.filename}）")

        # 如果配置了七牛，优先上传到七牛
        start_qiniu_cover = time.time()
        try:
            # 读取流到内存（通常为图片，大小可控）
            file.file.seek(0)
            content = file.file.read()
            logger.info(f"读取封面文件内容完成，大小：{len(content) / 1024:.2f} KB")
            if qiniu_helper.QINIU_BUCKET:
                key = f"music_cover/{filename}"
                ret, info = qiniu_helper.upload_bytes(content, key)
                qiniu_cover_cost = time.time() - start_qiniu_cover
                logger.info(f"七牛封面上传耗时：{qiniu_cover_cost:.2f} 秒，状态码：{info.status_code}")
                if info.status_code == 200:
                    full = qiniu_helper.make_url(key)
                    rel = f"/{key}"
                    total_cost = time.time() - start_total_time
                    logger.info(f"===== 封面图片上传（七牛）成功，总耗时：{total_cost:.2f} 秒，URL：{full} =====")
                    return {"code": 200, "msg": "上传成功", "data": {"cover": full, "cover_rel": rel}}
                else:
                    logger.warning(f"七牛封面上传失败，状态码：{info.status_code}，回退到本地保存")
        except Exception as e:
            qiniu_cover_cost = time.time() - start_qiniu_cover
            logger.warning(f"七牛封面上传异常，耗时：{qiniu_cover_cost:.2f} 秒，异常信息：{str(e)}，回退到本地保存")

        # 回退到本地保存
        start_local_cover = time.time()
        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)
        local_cover_cost = time.time() - start_local_cover
        logger.info(f"封面图片本地保存成功，路径：{save_path}，耗时：{local_cover_cost:.2f} 秒")

        rel = f"/static/music_cover/{filename}"
        try:
            base = str(request.base_url).rstrip('/')
            full = f"{base}{rel}"
        except Exception:
            full = rel
        total_cost = time.time() - start_total_time
        logger.info(f"===== 封面图片上传（本地）成功，总耗时：{total_cost:.2f} 秒，完整URL：{full}，相对路径：{rel} =====")
        return {"code": 200, "msg": "上传成功", "data": {"cover": full, "cover_rel": rel}}
    except Exception as e:
        total_cost = time.time() - start_total_time
        logger.error(f"===== 封面图片上传失败，总耗时：{total_cost:.2f} 秒，异常信息：{str(e)} =====", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传封面失败: {str(e)}")