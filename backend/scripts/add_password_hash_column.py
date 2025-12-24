"""
检查并为 SQLite 数据库的 user 表添加 password_hash 列（如有必要）。
用法: 在 backend 目录下运行： python scripts/add_password_hash_column.py
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
from config.database import DATABASE_URL


def main():
    print(f"检测数据库：{DATABASE_URL}")

    # 目前仅支持 sqlite 的自动 ALTER（其他数据库请使用迁移工具）
    if not DATABASE_URL.startswith("sqlite"):
        print("当前 DATABASE_URL 不是 SQLite。请使用数据库迁移工具为生产数据库添加缺失列（例如 Alembic）。")
        return

    # 创建 engine，使用 echo=False
    engine = create_engine(DATABASE_URL, echo=False)
    inspector = inspect(engine)

    if not inspector.has_table('user'):
        print("未发现 user 表，跳过修改。你可以运行 init_db.py 创建表。")
        return

    cols = [c['name'] for c in inspector.get_columns('user')]
    print(f"当前 user 表列: {cols}")

    if 'password_hash' in cols:
        print('password_hash 列已存在，无需修改。')
        return

    # SQLite 支持 ALTER TABLE ADD COLUMN
    alter_sql = 'ALTER TABLE "user" ADD COLUMN password_hash VARCHAR(255)'
    print(f'正在执行: {alter_sql}')
    with engine.connect() as conn:
        conn.execute(text(alter_sql))
        conn.commit()

    # 再次检查
    inspector = inspect(engine)
    cols_after = [c['name'] for c in inspector.get_columns('user')]
    print(f"修改后 user 表列: {cols_after}")
    if 'password_hash' in cols_after:
        print('已成功添加 password_hash 列。')
    else:
        print('未能添加 password_hash 列，请手动检查数据库文件或使用适当的迁移工具。')


if __name__ == '__main__':
    main()
