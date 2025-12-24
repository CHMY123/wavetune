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

# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量读取 DATABASE_URL（Render 会注入）
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required!")

# TiDB Cloud 必须使用 SSL
# SQLAlchemy + PyMySQL 的 SSL 配置方式
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "ssl": {
            "ssl_mode": "VERIFY_IDENTITY",  # 或 "REQUIRED"（若证书验证失败可降级）
            # 注意：PyMySQL 不支持 ssl_ca 直接传路径（Render 是 Linux 环境，系统信任根证书）
        }
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()