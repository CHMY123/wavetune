"""
初始化联邦学习相关数据库表
使用 SQLAlchemy ORM 创建联邦学习相关的表结构
"""

import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine
from models.federated import Base, FederatedTraining, FederatedDevice, FederatedStats, SignalDetectionCount

def init_federated_tables():
    """初始化联邦学习相关数据库表"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 成功创建联邦学习相关数据库表")
        
        # 导入必要的模块来初始化统计数据
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 检查是否已存在联邦学习统计数据
            existing_stats = db.query(FederatedStats).first()
            if not existing_stats:
                # 创建初始统计数据
                initial_stats = FederatedStats(
                    total_participants=0,
                    total_devices=0,
                    total_rounds=0,
                    average_accuracy=0,
                    average_loss=0
                )
                db.add(initial_stats)
                db.commit()
                print("✅ 成功初始化联邦学习统计数据")
            else:
                print("ℹ️ 联邦学习统计数据已存在，跳过初始化")
        except Exception as e:
            print(f"❌ 初始化统计数据失败: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 创建联邦学习数据库表失败: {str(e)}")

if __name__ == "__main__":
    init_federated_tables()
