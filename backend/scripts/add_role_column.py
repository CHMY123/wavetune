"""
数据库迁移脚本
为user表添加role字段
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine
import sqlalchemy as sa

def add_role_column():
    """为user表添加role字段"""
    print("开始为user表添加role字段...")
    
    try:
        # 连接到数据库
        with engine.connect() as conn:
            # 检查user表是否存在
            inspector = sa.inspect(engine)
            if 'user' not in inspector.get_table_names():
                print("user表不存在，跳过迁移")
                return
            
            # 检查role字段是否已存在
            columns = [col['name'] for col in inspector.get_columns('user')]
            if 'role' in columns:
                print("role字段已存在，跳过迁移")
                return
            
            # 为user表添加role字段
            conn.execute(
                sa.text("ALTER TABLE user ADD COLUMN `role` VARCHAR(20) DEFAULT 'user' COMMENT '用户角色'")
            )
            conn.commit()
            print("成功为user表添加role字段")
            
            # 更新现有用户的role字段为默认值
            conn.execute(
                sa.text("UPDATE user SET `role` = 'user' WHERE `role` IS NULL")
            )
            conn.commit()
            print("成功更新现有用户的role字段")
            
            # 为管理员用户设置admin角色
            conn.execute(
                sa.text("UPDATE user SET `role` = 'admin' WHERE id = 1")
            )
            conn.commit()
            print("成功设置管理员角色")
            
    except Exception as e:
        print(f"添加role字段时发生错误: {e}")
        raise

if __name__ == "__main__":
    add_role_column()
    print("数据库迁移完成！")
