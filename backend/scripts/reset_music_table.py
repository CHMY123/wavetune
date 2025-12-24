"""
开发用脚本：安全地清空 music 表并重置自增计数。

注意：此脚本会删除 `music` 表中所有数据。仅在开发环境或确认需要重置时使用。
操作前请务必备份生产数据（例如使用 mysqldump / sqlite3 导出）。

用法：
  python backend/scripts/reset_music_table.py

脚本行为：
  - 自动读取 backend/config/database.py 中的 DATABASE_URL（请确保文件中正确指向当前数据库）
  - 根据数据库类型执行合适的清空+重置自增语句（支持 MySQL 和 SQLite）
  - 运行前会要求用户输入确认（输入 "YES" 才会继续）

作者：自动生成 - 请在生产环境慎用
"""

import os
import sys
from sqlalchemy import create_engine, text

# 尝试读取项目的数据库配置
try:
    # 直接导入项目配置（确保 PYTHONPATH 包含项目根或在脚本中调整导入路径）
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    from config import database as db_conf
    DATABASE_URL = getattr(db_conf, 'DATABASE_URL', None)
except Exception as e:
    print('无法从 backend/config/database.py 读取 DATABASE_URL:', e)
    DATABASE_URL = None

if not DATABASE_URL:
    print('未找到 DATABASE_URL，请在 backend/config/database.py 配置 DATABASE_URL 或手动设置环境变量。')
    sys.exit(1)

print('将对数据库执行清空 music 表并重置自增计数的操作。')
print('数据库连接：', DATABASE_URL)
print('\n警告：此操作不可逆，会清空 music 表中的所有数据。')
confirm = input('若确定要执行请在此输入 YES：').strip()
if confirm != 'YES':
    print('已取消操作（未输入 YES）。')
    sys.exit(0)

engine = create_engine(DATABASE_URL)
conn = engine.connect()
trans = conn.begin()

try:
    if DATABASE_URL.startswith('sqlite'):
        # SQLite：删除数据 + 重置 sqlite_sequence
        print('检测到 SQLite，执行 DELETE FROM music；并重置 sqlite_sequence（如果存在）。')
        conn.execute(text('DELETE FROM music'))
        try:
            conn.execute(text("DELETE FROM sqlite_sequence WHERE name='music'"))
        except Exception:
            # 有些 SQLite 版本不支持 sqlite_sequence
            pass
        trans.commit()
        print('已清空 music 表并尝试重置 sqlite_sequence（如果可用）。')
    else:
        # 假定为 MySQL 或兼容数据库
        # 先尝试 TRUNCATE（会重置自增），如果权限不足改为 DELETE + ALTER TABLE
        try:
            print('尝试使用 TRUNCATE TABLE music （此操作在 MySQL 中会重置 AUTO_INCREMENT）。')
            conn.execute(text('TRUNCATE TABLE music'))
            trans.commit()
            print('TRUNCATE 成功，music 表已清空且自增已重置。')
        except Exception as e:
            print('TRUNCATE 失败（可能是权限或外键约束），尝试备用方案：DELETE + ALTER TABLE AUTO_INCREMENT = 1')
            trans.rollback()
            trans = conn.begin()
            conn.execute(text('DELETE FROM music'))
            try:
                conn.execute(text('ALTER TABLE music AUTO_INCREMENT = 1'))
            except Exception:
                print('ALTER TABLE 设置 AUTO_INCREMENT 失败，请手动在数据库中重置序列。')
            trans.commit()
            print('备用方案完成（已尝试删除数据并重置 AUTO_INCREMENT）。')

    print('\n完成：music 表已重置。请手动检查数据库备份与服务状态。')
finally:
    try:
        conn.close()
    except Exception:
        pass

print('请注意：如果你的应用有外键或其它依赖，请在操作前做好备份并在受控环境下执行。')
