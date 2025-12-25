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
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3, APIC, TIT2, TPE1
    HAS_MUTAGEN = True
except Exception:
    HAS_MUTAGEN = False

from config.database import get_db
from models.music import Music
from utils import qiniu_helper
import tempfile

router = APIRouter()

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
        # 兼容不同命名：前端可能传 high/Low/Medium/low 等，统一到后端使用的 light/medium/heavy
        lvl = (fatigue_level or '').strip().lower()
        if lvl == 'high':
            lvl = 'heavy'
        elif lvl == 'low':
            lvl = 'light'

        # 验证疲劳等级参数
        if lvl not in ['light', 'medium', 'heavy']:
            raise HTTPException(status_code=400, detail="疲劳等级必须是 light、medium、heavy（或其别名 high/low）")

        # 构建查询条件
        query = db.query(Music)

        # 根据疲劳等级筛选（使用正规化后的 lvl）
        query = query.filter(Music.fatigue_level == lvl)
        
        # 如果指定了音乐类型，则进一步筛选
        if music_type:
            if music_type not in ['natural', 'piano', 'whitenoise', 'mix']:
                raise HTTPException(status_code=400, detail="音乐类型必须是 natural、piano、whitenoise 或 mix")
            query = query.filter(Music.music_type == music_type)
        
        # 按匹配度降序排列
        music_list = query.order_by(Music.match_rate.desc()).all()
        
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
        music = db.query(Music).filter(Music.id == music_id).first()
        
        if not music:
            raise HTTPException(status_code=404, detail="音乐不存在")
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": music.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音乐详情失败: {str(e)}")


@router.get("/list")
async def list_music(
    db: Session = Depends(get_db)
):
    """
    列出所有音乐（不做复杂筛选），供前端获取实时列表
    """
    try:
        music_list = db.query(Music).order_by(Music.match_rate.desc()).all()
        data = [m.to_dict() for m in music_list]
        return {"code": 200, "msg": "获取成功", "data": {"music_list": data}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音乐列表失败: {str(e)}")


@router.post("")
async def add_music(item: dict, db: Session = Depends(get_db)):
    """
    添加音乐（简易接口，接收 json body）
    """
    try:
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
        return {"code": 200, "msg": "添加成功", "data": music.to_dict()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"添加音乐失败: {str(e)}")


@router.delete("/{music_id}")
async def delete_music(music_id: int, delete_files: Optional[bool] = Query(False, description="是否同时删除磁盘文件"), db: Session = Depends(get_db)):
    """
    删除音乐（简易权限，后续可限制为管理员）
    """
    try:
        music = db.query(Music).filter(Music.id == music_id).first()
        if not music:
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
                                    except Exception:
                                        pass
                                    return
                            except Exception:
                                pass
                    except Exception:
                        pass

                    # 支持 /static/... 或 static/...
                    rel = path.lstrip('/')
                    # 项目根目录为 routers 所在的父级的父级
                    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    file_path = os.path.join(root_dir, rel.replace('/', os.path.sep))
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass

                _remove_static_path(audio_url)
                _remove_static_path(cover_url)
            except Exception:
                # 忽略删除文件时的错误
                pass

        return {"code": 200, "msg": "删除成功", "data": {"music_id": music_id}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除音乐失败: {str(e)}")



@router.post("/upload")
async def upload_music_file(request: Request, file: UploadFile = File(...)):
    """
    接收上传的音乐文件，保存到 static/music 目录并返回可访问的 URL
    简易实现：不做复杂校验，直接保存并返回相对路径
    """
    try:
        # 先把文件写到临时文件，便于 mutagen 处理
        try:
            original_filename = file.filename
            base, ext = os.path.splitext(original_filename)
            # 生成唯一文件名以避免冲突
            import uuid
            filename = f"{base}_{uuid.uuid4().hex}{ext}"

            tmp = tempfile.NamedTemporaryFile(delete=False)
            try:
                shutil.copyfileobj(file.file, tmp)
                tmp.flush()
                tmp_path = tmp.name
            finally:
                tmp.close()

            # 优先上传到七牛
            meta = {}
            if qiniu_helper.QINIU_BUCKET:
                with open(tmp_path, 'rb') as fobj:
                    data = fobj.read()
                key = f"music/{filename}"
                ret, info = qiniu_helper.upload_bytes(data, key)
                if info.status_code == 200:
                    full_src = qiniu_helper.make_url(key)
                    src_path = f"/{key}"
                else:
                    full_src = f"/static/music/{filename}"
                    src_path = full_src
            else:
                # 回退到本地静态目录
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

            # 提取元数据与封面（如果可用）
            try:
                if HAS_MUTAGEN and tmp_path:
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
                        except Exception:
                            duration = None
                        meta.update({k: v for k, v in [('title', title), ('artist', artist), ('duration', duration)] if v})

                    try:
                        id3 = ID3(tmp_path)
                        pics = [v for k, v in id3.items() if isinstance(v, APIC)]
                        if pics:
                            pic = pics[0]
                            cover_bytes = pic.data
                            cover_key = f"music_cover/cover_{os.path.splitext(filename)[0]}.jpg"
                            if qiniu_helper.QINIU_BUCKET:
                                ret2, info2 = qiniu_helper.upload_bytes(cover_bytes, cover_key)
                                if info2.status_code == 200:
                                    meta['cover'] = qiniu_helper.make_url(cover_key)
                            else:
                                # 保存为本地静态文件（music_cover 目录）
                                root_dir = os.path.dirname(os.path.dirname(__file__))
                                static_cover_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music_cover'))
                                if not os.path.isdir(static_cover_dir):
                                    static_cover_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music_cover'))
                                cover_name = f"cover_{os.path.splitext(filename)[0]}.jpg"
                                cover_path = os.path.join(static_cover_dir, cover_name)
                                with open(cover_path, 'wb') as cf:
                                    cf.write(cover_bytes)
                                meta['cover'] = f"/static/music_cover/{cover_name}"
                    except Exception:
                        pass
            except Exception:
                pass

            # 清理临时文件（若存在）
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

            resp = {"code": 200, "msg": "上传成功", "data": {"src": full_src, "src_rel": src_path}}
            if meta:
                resp['data'].update(meta)
            return resp
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        # 上传总体失败时返回统一格式
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")



@router.post("/upload_cover")
async def upload_cover_file(request: Request, file: UploadFile = File(...)):
    """
    上传单独的封面图片，保存到 static/music_cover 并返回可访问 URL
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(__file__))
        cover_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music_cover'))
        if not os.path.isdir(cover_dir):
            cover_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music_cover'))
        os.makedirs(cover_dir, exist_ok=True)

        filename = file.filename
        save_path = os.path.join(cover_dir, filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(cover_dir, filename)
            counter += 1

        # 如果配置了七牛，优先上传到七牛
        try:
            # 读取流到内存（通常为图片，大小可控）
            file.file.seek(0)
            content = file.file.read()
            if qiniu_helper.QINIU_BUCKET:
                key = f"music_cover/{filename}"
                ret, info = qiniu_helper.upload_bytes(content, key)
                if info.status_code == 200:
                    full = qiniu_helper.make_url(key)
                    rel = f"/{key}"
                    return {"code": 200, "msg": "上传成功", "data": {"cover": full, "cover_rel": rel}}
                # 若七牛上传失败，回退到本地保存继续下面流程
        except Exception:
            # 忽略并回退到本地保存
            pass

        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)

        rel = f"/static/music_cover/{filename}"
        try:
            base = str(request.base_url).rstrip('/')
            full = f"{base}{rel}"
        except Exception:
            full = rel

        return {"code": 200, "msg": "上传成功", "data": {"cover": full, "cover_rel": rel}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传封面失败: {str(e)}")




