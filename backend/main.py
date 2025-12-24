"""
WaveTune 后端主入口文件
基于 FastAPI 框架实现脑疲劳检测与音乐干预系统的后端服务
"""
import pymysql
pymysql.install_as_MySQLdb()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager  # 新增：导入生命周期上下文管理器

# 导入路由
from routers import system, user, feedback, music, scene, auth, detection

# 导入数据库配置
from config.database import engine, Base

# ========== 核心修改：替换 on_event 为 lifespan ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期函数（替代废弃的 on_event）
    - 启动时：创建数据库表
    - 关闭时：可添加清理逻辑（如关闭连接池）
    """
    # 启动逻辑（原 startup_event 内容）
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("数据库表创建完成")
    except Exception as e:
        logging.error(f"数据库表创建失败：{str(e)}")
    
    yield  # 应用运行中（yield 之前是启动逻辑，之后是关闭逻辑）
    
    # 可选：应用关闭时的清理逻辑（如关闭数据库连接池、释放资源等）
    logging.info("WaveTune API 服务已关闭")

# 创建 FastAPI 应用实例（绑定 lifespan）
app = FastAPI(
    title="WaveTune API",
    description="脑疲劳检测与音乐干预系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # 新增：绑定生命周期函数，消除警告
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue 开发服务器
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # 备用端口
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])
app.include_router(system.router, prefix="/api/system", tags=["系统统计"])
app.include_router(user.router, prefix="/api/user", tags=["用户管理"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["用户反馈"])
app.include_router(music.router, prefix="/api/music", tags=["音乐推荐"])
app.include_router(scene.router, prefix="/api/scene", tags=["场景配置"])
app.include_router(detection.router, prefix="/api/detection", tags=["快速检测"])

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
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
    """通用异常处理器"""
    logging.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误，请稍后重试",
            "data": None
        }
    )

# 根路径
@app.get("/")
async def root():
    """根路径，返回API基本信息"""
    return {
        "code": 200,
        "msg": "WaveTune API 服务运行正常",
        "data": {
            "service": "WaveTune Backend API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "docs": "/docs"
        }
    }

# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "code": 200,
        "msg": "服务健康",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    port = int(os.getenv("PORT", 8000))

    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )