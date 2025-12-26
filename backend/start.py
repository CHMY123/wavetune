"""
WaveTune 后端启动脚本
"""

import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 创建必要的目录
os.makedirs("logs", exist_ok=True)
os.makedirs("static/avatar", exist_ok=True)
os.makedirs("static/music_cover", exist_ok=True)

if __name__ == "__main__":
    # 启动 FastAPI 应用
    port = int(os.getenv("PORT", 8000))

    # 可配置的 keep-alive / 上传超时（秒），默认 120s，可通过环境变量调整
    timeout_keep_alive = int(os.getenv('UVICORN_TIMEOUT_KEEP_ALIVE', os.getenv('UPLOAD_TIMEOUT', 360)))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
        access_log=True,
        timeout_keep_alive=timeout_keep_alive,
    )




