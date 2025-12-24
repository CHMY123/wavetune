"""
WaveTune 后端主入口文件
基于 FastAPI 框架实现脑疲劳检测与音乐干预系统的后端服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

# 导入路由
from routers import system, user, feedback, music, scene, auth, detection

# 导入数据库配置
from config.database import engine, Base

# 创建 FastAPI 应用实例
app = FastAPI(
    title="WaveTune API",
    description="脑疲劳检测与音乐干预系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue 开发服务器
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # 备用端口
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

# 创建数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logging.info("数据库表创建完成")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


