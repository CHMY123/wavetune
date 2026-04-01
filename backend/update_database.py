#!/usr/bin/env python3
"""
数据库更新脚本
用于为federated_training表添加fatigue_status字段
"""

import os
import sys
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine

def update_database():
    """
    更新数据库结构，为federated_training表添加fatigue_status字段
    """
    try:
        print("开始更新数据库结构...")
        
        # 使用SQLAlchemy执行原生SQL来添加字段
        with engine.connect() as connection:
            # 检查字段是否已存在
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'wavetune' 
                AND table_name = 'federated_training' 
                AND column_name = 'fatigue_status'
            """)
            
            result = connection.execute(check_query)
            column_exists = result.fetchone() is not None
            
            if column_exists:
                print("fatigue_status字段已存在，跳过更新")
            else:
                # 添加fatigue_status字段
                alter_query = text("""
                    ALTER TABLE federated_training 
                    ADD COLUMN fatigue_status VARCHAR(50)
                """)
                
                connection.execute(alter_query)
                connection.commit()
                print("成功添加fatigue_status字段")
        
        print("数据库更新完成！")
        return True
        
    except Exception as e:
        print(f"数据库更新失败: {str(e)}")
        return False

if __name__ == "__main__":
    update_database()
