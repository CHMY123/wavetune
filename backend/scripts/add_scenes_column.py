#!/usr/bin/env python3
"""
为 music 表添加 scenes 字段
"""

import sys
import os
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine

def add_scenes_column():
    """为 music 表添加 scenes 字段"""
    try:
        # 使用 SQLAlchemy 引擎执行原生 SQL
        with engine.connect() as connection:
            # 检查 music 表是否存在 scenes 字段
            result = connection.execute(text("SHOW COLUMNS FROM music LIKE 'scenes'"))
            columns = result.fetchall()
            
            if not columns:
                # 添加 scenes 字段
                connection.execute(text("ALTER TABLE music ADD COLUMN scenes VARCHAR(100) DEFAULT NULL COMMENT '适用场景，多个场景用逗号分隔'"))
                connection.commit()
                print("成功添加 scenes 字段")
            else:
                print("scenes 字段已存在，跳过")
        
    except Exception as e:
        print(f"添加字段失败: {str(e)}")

if __name__ == "__main__":
    add_scenes_column()
