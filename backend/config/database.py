"""
数据库配置文件
配置 SQLAlchemy 数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
# DATABASE_URL = os.getenv(
#     "DATABASE_URL", 
#     "sqlite:///./wavetune.db"  # 默认使用 SQLite
# )

# 如果是 MySQL，使用以下格式：
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/wavetune"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 开发环境显示SQL语句
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=300,    # 连接回收时间
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




