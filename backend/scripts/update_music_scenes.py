#!/usr/bin/env python3
"""
为现有音乐数据添加场景信息
根据音乐的疲劳等级和类型，为它们分配合适的场景
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.music import Music
from config.database import DATABASE_URL, get_engine

def update_music_scenes():
    """为现有音乐数据添加场景信息"""
    # 创建数据库连接
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 获取所有音乐数据
        music_list = db.query(Music).all()
        print(f"找到 {len(music_list)} 首音乐")
        
        updated_count = 0
        
        for music in music_list:
            # 如果已经有场景信息，跳过
            if music.scenes:
                print(f"音乐 {music.id} ({music.title}) 已有场景信息，跳过")
                continue
            
            # 根据疲劳等级和类型分配场景
            scenes = []
            
            # 基于疲劳等级的场景分配
            if music.fatigue_level == 'light':
                # 轻度疲劳适合所有场景
                scenes.extend(['work', 'study', 'drive'])
            elif music.fatigue_level == 'medium':
                # 中度疲劳适合工作和学习，驾驶需要更清醒
                scenes.extend(['work', 'study'])
            elif music.fatigue_level == 'heavy':
                # 重度疲劳适合放松，不适合驾驶
                scenes.extend(['work', 'study'])
            
            # 基于音乐类型的场景分配
            if music.music_type in ['natural', 'ambient', 'piano']:
                # 自然、环境、钢琴音乐适合所有场景
                if 'work' not in scenes:
                    scenes.append('work')
                if 'study' not in scenes:
                    scenes.append('study')
                if 'drive' not in scenes:
                    scenes.append('drive')
            elif music.music_type in ['whitenoise', 'classical']:
                # 白噪音和古典音乐适合工作和学习
                if 'work' not in scenes:
                    scenes.append('work')
                if 'study' not in scenes:
                    scenes.append('study')
            elif music.music_type in ['pop', 'rock', 'electronic']:
                # 流行、摇滚、电子音乐适合工作和驾驶
                if 'work' not in scenes:
                    scenes.append('work')
                if 'drive' not in scenes:
                    scenes.append('drive')
            
            # 去重并排序
            scenes = sorted(list(set(scenes)))
            
            # 更新场景信息
            music.scenes = ','.join(scenes)
            updated_count += 1
            print(f"更新音乐 {music.id} ({music.title}) 的场景: {music.scenes}")
        
        # 提交更改
        db.commit()
        print(f"成功更新 {updated_count} 首音乐的场景信息")
        
    except Exception as e:
        print(f"更新场景信息失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_music_scenes()
