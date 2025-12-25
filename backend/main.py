"""
WaveTune 后端主入口文件
基于 FastAPI 框架实现脑疲劳检测与音乐干预系统的后端服务
"""
import pymysql
pymysql.install_as_MySQLdb()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import logging
import os
import pathlib
from datetime import datetime
from contextlib import asynccontextmanager

# ========== 第一步：配置日志 ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入路由（如果缺少这些文件，需要先创建或注释掉）
try:
    from routers import system, user, feedback, music, scene, auth, detection
except ImportError as e:
    logging.warning(f"⚠️ 部分路由模块导入失败：{e}，请确保routers目录存在并包含对应文件")
    # 临时创建空路由避免启动报错（实际使用时需补全routers代码）
    from fastapi import APIRouter
    system = user = feedback = music = scene = auth = detection = APIRouter()

# 导入数据库配置（如果缺少，临时注释避免报错）
try:
    from config.database import engine, Base
except ImportError as e:
    logging.warning(f"⚠️ 数据库配置导入失败：{e}，请确保config/database.py存在")
    # 临时创建空对象避免报错
    class MockBase:
        class metadata:
            @staticmethod
            def create_all(bind=None):
                pass
    Base = MockBase()
    engine = None

# ========== 核心：路径配置 ==========
# 获取当前文件（main.py）所在目录
BACKEND_DIR = pathlib.Path(__file__).resolve().parent
# 项目根目录（backend的上级目录）
PROJECT_ROOT_DIR = BACKEND_DIR.parent
# Vue打包后的静态文件目录
FRONTEND_DIR = PROJECT_ROOT_DIR / "dist"

# ========== 生命周期函数 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI生命周期函数"""
    # 数据库表创建（容错处理）
    try:
        if engine:
            Base.metadata.create_all(bind=engine)
            logging.info("✅ 数据库表创建完成")
        else:
            logging.warning("⚠️ 未配置数据库引擎，跳过表创建")
    except Exception as e:
        logging.error(f"❌ 数据库表创建失败：{str(e)}")
        logging.warning("⚠️ 服务将继续运行，数据库相关功能暂不可用")
    
    yield
    
    # 应用关闭时的清理逻辑
    logging.info("🔌 WaveTune API 服务已关闭")

# ========== 创建FastAPI应用实例 ==========
app = FastAPI(
    title="WaveTune API",
    description="脑疲劳检测与音乐干预系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ========== 配置CORS跨域 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://wavetune-6xb1.onrender.com", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 注册后端API路由 ==========
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])
app.include_router(system.router, prefix="/api/system", tags=["系统统计"])
app.include_router(user.router, prefix="/api/user", tags=["用户管理"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["用户反馈"])
app.include_router(music.router, prefix="/api/music", tags=["音乐推荐"])
app.include_router(scene.router, prefix="/api/scene", tags=["场景配置"])
app.include_router(detection.router, prefix="/api/detection", tags=["快速检测"])

# ========== 全局异常处理器 ==========
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "msg": exc.detail,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logging.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误，请稍后重试",
            "data": None
        }
    )

# ========== 健康检查接口 ==========
@app.get("/api/health", tags=["健康检查"])
async def health_check():
    return {
        "code": 200,
        "msg": "服务健康",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "WaveTune API"
        }
    }

# ========== 挂载静态文件（关键修复） ==========
# 1. 第一优先级：前端静态资源（/static路径，解决404核心）
STATIC_ROOT = PROJECT_ROOT_DIR / 'static'
# 强制检查目录是否存在，给出明确提示
if STATIC_ROOT.exists():
    app.mount(
        "/static",
        StaticFiles(directory=STATIC_ROOT),
        name="static_root"
    )
    logging.info(f"✅ 成功挂载前端静态资源：{STATIC_ROOT}")
    # 额外检查子目录是否存在
    icon_dir = STATIC_ROOT / "icon"
    logo_dir = STATIC_ROOT / "logo"
    if not icon_dir.exists():
        logging.error(f"❌ static/icon 目录不存在：{icon_dir}")
    if not logo_dir.exists():
        logging.error(f"❌ static/logo 目录不存在：{logo_dir}")
else:
    logging.error(f"❌ 项目根目录static不存在：{STATIC_ROOT}")
    # 自动创建空目录避免完全无法访问
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
    logging.info(f"✅ 已自动创建static目录：{STATIC_ROOT}，请手动放入icon、logo等文件夹")

# 2. 第二优先级：Vue前端应用（挂载到根路径/）
if FRONTEND_DIR.exists():
    app.mount(
        "/", 
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend"
    )
    logging.info(f"✅ 成功挂载前端应用：{FRONTEND_DIR}")
else:
    logging.error(f"❌ 前端目录不存在：{FRONTEND_DIR}")

# 3. 第三优先级：后端上传文件（/uploads路径）
UPLOADS_DIR = BACKEND_DIR / "static"
(UPLOADS_DIR / "avatar").mkdir(parents=True, exist_ok=True)
(UPLOADS_DIR / "music").mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
    name="uploads"
)
logging.info(f"✅ 成功挂载上传文件目录：{UPLOADS_DIR}")

# 4. 后端静态文件（备用）
app.mount(
    "/backend-static", 
    StaticFiles(directory=BACKEND_DIR / "static"),
    name="backend_static"
)

# ========== 启动服务 ==========
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )