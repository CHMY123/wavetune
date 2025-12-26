"""
音乐模型
定义轻音乐数据相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, Text
from config.database import Base

class Music(Base):
    """音乐表模型"""
    __tablename__ = "music"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False, comment="音乐标题")
    artist = Column(String(100), comment="艺术家/创作者")
    duration = Column(String(10), comment="时长")
    cover = Column(Text, comment="封面图URL")
    audio_url = Column(Text, comment="音频文件URL或路径")
    reason = Column(Text, comment="推荐理由")
    music_type = Column(String(20), comment="音乐类型")
    fatigue_level = Column(String(50), comment="适配疲劳等级")
    match_rate = Column(Integer, default=0, comment="匹配度")
    
    def __repr__(self):
        return f"<Music(id={self.id}, title='{self.title}', artist='{self.artist}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "cover": self.cover,
            "src": self.audio_url or (f"/static/music/sample{self.id}.mp3" if self.id else None),
            "reason": self.reason,
            "music_type": self.music_type,
            "fatigue_level": self.fatigue_level,
            "match_rate": self.match_rate
        }




