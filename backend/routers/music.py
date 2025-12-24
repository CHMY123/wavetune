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
        # 确保静态目录存在（基于项目根目录的 static/music）
        root_dir = os.path.dirname(os.path.dirname(__file__))
        # try backend/../static/music then project root static/music
        static_music_dir = os.path.abspath(os.path.join(root_dir, '..', 'static', 'music'))
        if not os.path.isdir(static_music_dir):
            static_music_dir = os.path.abspath(os.path.join(root_dir, '..', '..', 'static', 'music'))
        os.makedirs(static_music_dir, exist_ok=True)

        filename = file.filename
        # 生成安全的文件名（简单处理，实际可加入 uuid 防重名）
        save_path = os.path.join(static_music_dir, filename)
        # 如果存在，尝试添加后缀
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(static_music_dir, filename)
            counter += 1

        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)

        # 返回客户端可访问的相对路径（前端通过 baseURL 拼接）
        src_path = f"/static/music/{filename}"
        # 构造可访问的完整 URL（使用请求的 base_url）
        try:
            base = str(request.base_url).rstrip('/')
            full_src = f"{base}{src_path}"
        except Exception:
            full_src = src_path

        # 尝试使用 mutagen 提取一些元数据（如果可用）
        meta = {}
        try:
            if HAS_MUTAGEN:
                m = MutagenFile(save_path, easy=True)
                if m:
                    # title/artist
                    title = None
                    artist = None
                    if 'title' in m and m['title']:
                        title = m['title'][0]
                    if 'artist' in m and m['artist']:
                        artist = m['artist'][0]
                    # duration
                    duration = None
                    try:
                        d = int(m.info.length)
                        mm = str(d // 60).zfill(2)
                        ss = str(d % 60).zfill(2)
                        duration = f"{mm}:{ss}"
                    except Exception:
                        duration = None
                    meta.update({k: v for k, v in [('title', title), ('artist', artist), ('duration', duration)] if v})

                # 尝试读取封面（ID3 APIC）
                try:
                    id3 = ID3(save_path)
                    pics = [v for k, v in id3.items() if isinstance(v, APIC)]
                    if pics:
                        pic = pics[0]
                        cover_name = f"cover_{os.path.splitext(filename)[0]}.jpg"
                        cover_path = os.path.join(static_music_dir, cover_name)
                        with open(cover_path, 'wb') as cf:
                            cf.write(pic.data)
                        meta['cover'] = f"/static/music/{cover_name}"
                except Exception:
                    pass
        except Exception:
            # 如果 mutagen 抛出错误，忽略，不影响上传成功
            pass

        resp = {"code": 200, "msg": "上传成功", "data": {"src": full_src, "src_rel": src_path}}
        if meta:
            resp['data'].update(meta)
        return resp
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




