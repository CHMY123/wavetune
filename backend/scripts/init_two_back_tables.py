#!/usr/bin/env python3
# 初始化 2-Back 实验数据表
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import engine, Base
from models.two_back import TwoBackSession, TwoBackTrial, TwoBackKSSScore, TwoBackPerformanceMetric, TwoBackExperimentData

def init_two_back_tables():
    """初始化 2-Back 实验相关数据表"""
    print("开始初始化 2-Back 实验数据表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 2-Back 实验数据表初始化成功！")
        print("创建的表：")
        print("  - two_back_sessions (实验会话表)")
        print("  - two_back_trials (实验试次表)")
        print("  - two_back_kss_scores (KSS 评分表)")
        print("  - two_back_performance_metrics (表现指标表)")
        print("  - two_back_experiment_data (实验数据汇总表)")
    except Exception as e:
        print(f"❌ 初始化数据表失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_two_back_tables()
