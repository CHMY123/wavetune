"""
数据库初始化脚本
创建数据库表并插入初始数据
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import engine, SessionLocal
from models import User, Feedback, Music, Scene, SystemStats, UserSession, UserPreference, OperationLog

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建数据库表
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(User).first():
            print("数据库已有数据，跳过初始化")
            return
        
        # 插入测试用户数据
        test_user = User(
            username="李同学",
            student_id="2022001001",
            email="li.student@example.com",
            phone="13800138001",
            avatar="/static/avatar/default.jpg",
            detection_count=12,
            intervention_count=8,
            is_active=True,
            create_time=datetime(2023, 9, 1),
            update_time=datetime.now()
        )
        test_user.set_password("123456")  # 设置默认密码
        db.add(test_user)
        db.flush()  # 获取用户ID
        
        # 插入音乐数据
        music_data = [
            {
                "title": "森林雨声与钢琴",
                "artist": "自然白噪音工作室",
                "duration": "05:30",
                "cover": "/static/music_cover/1.jpg",
                "reason": "帮助中度疲劳放松，降低 β 波活跃度",
                "music_type": "natural",
                "fatigue_level": "light,medium",
                "match_rate": 98
            },
            {
                "title": "海浪轻拍沙滩",
                "artist": "海洋之声",
                "duration": "08:45",
                "cover": "/static/music_cover/2.jpg",
                "reason": "舒缓的海浪声有助于缓解眼部疲劳",
                "music_type": "natural",
                "fatigue_level": "light,medium",
                "match_rate": 95
            },
            {
                "title": "溪流潺潺",
                "artist": "山水音韵",
                "duration": "06:15",
                "cover": "/static/music_cover/3.jpg",
                "reason": "自然水流声促进 α 波产生，提升专注力",
                "music_type": "natural",
                "fatigue_level": "light,medium",
                "match_rate": 92
            },
            {
                "title": "鸟鸣晨曦",
                "artist": "晨光音乐",
                "duration": "07:20",
                "cover": "/static/music_cover/4.jpg",
                "reason": "清晨鸟鸣有助于调节生物钟，缓解疲劳",
                "music_type": "natural",
                "fatigue_level": "light,medium",
                "match_rate": 89
            },
            {
                "title": "古筝流水",
                "artist": "古典雅韵",
                "duration": "09:10",
                "cover": "/static/music_cover/5.jpg",
                "reason": "传统乐器演奏，具有深度放松效果",
                "music_type": "piano",
                "fatigue_level": "medium,heavy",
                "match_rate": 87
            },
            {
                "title": "微风轻抚竹林",
                "artist": "竹韵清风",
                "duration": "06:55",
                "cover": "/static/music_cover/6.jpg",
                "reason": "竹叶摩擦声有助缓解压力，改善情绪",
                "music_type": "natural",
                "fatigue_level": "light,medium",
                "match_rate": 85
            },
            {
                "title": "星空下的冥想",
                "artist": "冥想音乐社",
                "duration": "12:30",
                "cover": "/static/music_cover/7.jpg",
                "reason": "长时间冥想音乐，适合深度放松",
                "music_type": "whitenoise",
                "fatigue_level": "heavy",
                "match_rate": 83
            },
            {
                "title": "山间云雾",
                "artist": "云山音画",
                "duration": "05:45",
                "cover": "/static/music_cover/8.jpg",
                "reason": "空灵音效有助于大脑进入放松状态",
                "music_type": "natural",
                "fatigue_level": "light,medium",
                "match_rate": 81
            }
        ]
        
        for music_info in music_data:
            music = Music(**music_info)
            db.add(music)
        
        # 插入系统默认场景
        default_scenes = [
            {
                "user_id": test_user.id,
                "scene_name": "学习场景",
                "music_type": "piano",
                "is_default": 1,
                "create_time": datetime(2023, 9, 1)
            },
            {
                "user_id": test_user.id,
                "scene_name": "办公场景",
                "music_type": "whitenoise",
                "is_default": 1,
                "create_time": datetime(2023, 9, 1)
            },
            {
                "user_id": test_user.id,
                "scene_name": "休息场景",
                "music_type": "natural",
                "is_default": 1,
                "create_time": datetime(2023, 9, 1)
            }
        ]
        
        for scene_info in default_scenes:
            scene = Scene(**scene_info)
            db.add(scene)
        
        # 插入系统统计数据
        system_stats_data = [
            {
                "stat_name": "detection_count",
                "stat_value": "1,234",
                "stat_unit": "次",
                "update_time": datetime.now()
            },
            {
                "stat_name": "intervention_count", 
                "stat_value": "856",
                "stat_unit": "次",
                "update_time": datetime.now()
            },
            {
                "stat_name": "device_count",
                "stat_value": "12",
                "stat_unit": "台",
                "update_time": datetime.now()
            },
            {
                "stat_name": "model_accuracy",
                "stat_value": "89.2",
                "stat_unit": "%",
                "update_time": datetime.now()
            }
        ]
        
        for stats_info in system_stats_data:
            stats = SystemStats(**stats_info)
            db.add(stats)
        
        # 提交事务
        db.commit()
        print("初始数据插入完成")
        
    except Exception as e:
        print(f"初始化数据库时发生错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("数据库初始化完成！")


