# """
# 数据库配置文件
# 配置 SQLAlchemy 数据库连接和会话管理
# """

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv

# # 加载环境变量
# load_dotenv()

# # 数据库配置
# # DATABASE_URL = os.getenv(
# #     "DATABASE_URL", 
# #     "sqlite:///./wavetune.db"  # 默认使用 SQLite
# # )

# # 如果是 MySQL，使用以下格式：
# DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/wavetune"

# # 创建数据库引擎
# engine = create_engine(
#     DATABASE_URL,
#     echo=True,  # 开发环境显示SQL语句
#     pool_pre_ping=True,  # 连接池预检查
#     pool_recycle=300,    # 连接回收时间
# )

# # 创建会话工厂
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 创建基础模型类
# Base = declarative_base()

# def get_db():
#     """获取数据库会话"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import ssl
import pathlib
from dotenv import load_dotenv

# 加载环境变量（优先加载 .env 文件）
load_dotenv()

# ========== 1. 数据库URL配置（兼容TiDB/本地MySQL/SQLite） ==========
DATABASE_URL = os.getenv("DATABASE_URL")
# 本地开发降级：无DATABASE_URL时用SQLite（避免强制依赖远程数据库）
if not DATABASE_URL:
    # 本地MySQL（无需安装数据库，开发/测试用）
    DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/wavetune"
    print("⚠️ 未配置DATABASE_URL，使用本地 MySQL开发模式（无SSL）")
else:
    # 强制TiDB URL格式为 mysql+pymysql://（修复格式错误）
    if "tidbcloud.com" in DATABASE_URL and not DATABASE_URL.startswith("mysql+pymysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://")
        print(f"✅ 自动修复TiDB URL格式：{DATABASE_URL}")

# ========== 2. 基础配置 ==========
Base = declarative_base()
_engine = None  # 全局引擎（避免重复初始化）
_SessionLocal = None  # 全局会话工厂

# ========== 3. 适配TiDB Cloud的SSL连接（移除pymysql不支持的参数） ==========
def get_engine():
    global _engine
    if _engine is None:
        connect_args = {}

        # ---------- 适配SQLite（本地开发） ----------
        if "sqlite" in DATABASE_URL:
            connect_args = {"check_same_thread": False}  # SQLite专属：避免线程错误

        # ---------- 适配TiDB Cloud（远程生产） ----------
        elif "tidbcloud.com" in DATABASE_URL:
            try:
                # 拼接证书路径（backend/isrgrootx1.pem）
                cert_path = pathlib.Path(__file__).parent.parent / "isrgrootx1.pem"
                cert_abs_path = cert_path.resolve()

                # 证书存在性校验
                if not cert_abs_path.exists():
                    raise FileNotFoundError(f"TiDB SSL证书缺失：{cert_abs_path}")

                # ---------- 关键修复：pymysql兼容的SSL配置 ----------
                # 移除 ssl_mode（pymysql不识别），仅保留 ssl 参数
                ssl_context = ssl.create_default_context(cafile=str(cert_abs_path))
                ssl_context.check_hostname = True  # 验证TiDB主机名（防中间人攻击）
                ssl_context.verify_mode = ssl.CERT_REQUIRED  # 强制验证证书

                # pymysql 仅支持字典格式的SSL配置（而非ssl_context对象）
                connect_args = {
                    "ssl": {
                        "ca": str(cert_abs_path),  # 证书路径
                        "check_hostname": True
                    }
                }
                print(f"✅ 加载TiDB SSL证书成功：{cert_abs_path}")

            except Exception as e:
                # 容错：SSL配置失败时打印错误，尝试无SSL连接（TiDB可能拒绝，但保留启动可能）
                print(f"❌ TiDB SSL配置失败：{str(e)}")
                print("⚠️ 尝试关闭SSL验证（仅测试用，生产环境需修复证书）")
                connect_args = {"ssl": False}

        # ---------- 适配本地MySQL（无SSL） ----------
        else:
            connect_args = {}

        # ========== 创建数据库引擎 ==========
        _engine = create_engine(
            DATABASE_URL,
            echo=True,  # 开发模式打印SQL（生产可关闭）
            pool_pre_ping=True,  # 连接前校验可用性
            pool_recycle=300,  # 5分钟回收连接（避免TiDB超时）
            connect_args=connect_args
        )
    return _engine

# 导出引擎（main.py直接导入）
engine = get_engine()

# ========== 4. 数据库会话配置 ==========
def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    return _SessionLocal

def get_db():
    """依赖注入：获取数据库会话"""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()