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
from contextlib import asynccontextmanager  # 导入生命周期上下文管理器

# 导入路由
from routers import system, user, feedback, music, scene, auth, detection

# 导入数据库配置
from config.database import engine, Base

# ========== 核心：路径配置（适配 dist 在项目根目录） ==========
# 获取当前文件（main.py）所在目录（backend）
BACKEND_DIR = pathlib.Path(__file__).parent
# 项目根目录（backend 的上级目录）
PROJECT_ROOT_DIR = BACKEND_DIR.parent
# Vue 打包后的静态文件目录（项目根目录下的 dist）
FRONTEND_DIR = PROJECT_ROOT_DIR / "dist"

# ========== 生命周期函数（替代废弃的 on_event） ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期函数
    - 启动时：尝试创建数据库表
    - 关闭时：可选清理逻辑
    """
    # 数据库表创建（容错处理，失败不影响服务启动）
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("✅ 数据库表创建完成")
    except Exception as e:
        logging.error(f"❌ 数据库表创建失败：{str(e)}")
        logging.warning("⚠️ 服务将继续运行，数据库相关功能暂不可用")
    
    yield  # 应用运行中
    
    # 应用关闭时的清理逻辑（可选）
    logging.info("🔌 WaveTune API 服务已关闭")

# ========== 创建 FastAPI 应用实例 ==========
app = FastAPI(
    title="WaveTune API",
    description="脑疲劳检测与音乐干预系统后端API",
    version="1.0.0",
    docs_url="/docs",          # API 文档地址（调试用）
    redoc_url="/redoc",        # 备用文档地址
    lifespan=lifespan          # 绑定生命周期函数
)

# ========== 配置 CORS 跨域（适配前端请求） ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 生产环境建议替换为前端域名（如 https://xxx.onrender.com）
    allow_credentials=True,
    allow_methods=["*"],       # 允许所有请求方法（GET/POST/PUT/DELETE 等）
    allow_headers=["*"],       # 允许所有请求头
)

# ========== 挂载静态文件 ==========
# 1. 优先挂载 Vue 前端静态文件（覆盖根路径 /）
if FRONTEND_DIR.exists():
    app.mount(
        "/", 
        StaticFiles(directory=FRONTEND_DIR, html=True),  # html=True 支持前端路由 history 模式
        name="frontend"
    )
    logging.info(f"✅ 成功挂载前端静态文件：{FRONTEND_DIR}")
else:
    logging.error(f"❌ 前端目录不存在：{FRONTEND_DIR}")
    logging.warning("⚠️ 请确认 Vue 打包后的 dist 文件夹在项目根目录下")

# 2. 挂载后端静态文件（如上传的图片/音频，路径：/backend-static/xxx）
app.mount(
    "/backend-static", 
    StaticFiles(directory=BACKEND_DIR / "static"),  # 后端 static 文件夹在 backend 目录下
    name="backend_static"
)

# ========== 注册后端 API 路由（统一前缀 /api，避免和前端路由冲突） ==========
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
    """处理 HTTP 异常（如 404/405/401 等）"""
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
    """处理未捕获的全局异常"""
    logging.error(f"未处理的异常: {str(exc)}", exc_info=True)  # 打印完整异常栈
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误，请稍后重试",
            "data": None
        }
    )

# ========== 健康检查接口（路径 /api/health，避免和前端路由冲突） ==========
@app.get("/api/health", tags=["健康检查"])
async def health_check():
    """服务健康检查接口，用于验证后端是否正常运行"""
    return {
        "code": 200,
        "msg": "服务健康",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "WaveTune API"
        }
    }

# ========== 启动服务 ==========
if __name__ == "__main__":
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 从环境变量获取端口（适配 Render 自动分配端口）
    port = int(os.getenv("PORT", 8000))

    # 启动 Uvicorn 服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",    # 允许外部访问
        port=port,         # 端口（Render 会自动映射）
        reload=False,      # 生产环境关闭热重载
        log_level="info"   # 日志级别
    )