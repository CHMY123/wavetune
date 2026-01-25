# 实验数据存储服务
from sqlalchemy.orm import Session
from config.database import engine
from models.two_back import (
    TwoBackSession as TwoBackSessionModel,
    TwoBackTrial as TwoBackTrialModel,
    TwoBackKSSScore as TwoBackKSSScoreModel,
    TwoBackPerformanceMetric as TwoBackPerformanceMetricModel,
    TwoBackExperimentData as TwoBackExperimentDataModel
)
from datetime import datetime
from typing import Dict, Any, Optional

class DataStorageService:
    """实验数据存储服务"""
    
    def __init__(self):
        pass
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """保存实验会话"""
        try:
            with Session(engine) as db:
                # 创建会话模型
                db_session = TwoBackSessionModel(
                    session_id=session_data["session_id"],
                    participant_id=session_data["participant_id"],
                    settings=session_data["settings"],
                    start_time=datetime.fromisoformat(session_data["start_time"]),
                    end_time=datetime.fromisoformat(session_data["end_time"]) if session_data.get("end_time") else None,
                    status=session_data["status"],
                    completed_blocks=session_data.get("completed_blocks", 0),
                    overall_hit_rate=session_data.get("overall_hit_rate"),
                    total_trials=session_data.get("total_trials")
                )
                db.add(db_session)
                db.commit()
                return True
        except Exception as e:
            print(f"保存会话失败: {e}")
            return False
    
    def save_trial(self, session_id: str, trial_data: Dict[str, Any]) -> bool:
        """保存试次数据"""
        try:
            with Session(engine) as db:
                # 创建试次模型
                db_trial = TwoBackTrialModel(
                    trial_id=trial_data["trial_id"],
                    session_id=session_id,
                    block_num=trial_data.get("block_num", 1),
                    trial_index=trial_data["trial_index"],
                    stimulus=trial_data["stimulus"],
                    is_target=1 if trial_data["is_target"] else 0,
                    key_pressed=1 if trial_data["key_pressed"] else 0,
                    response_time=trial_data.get("response_time"),
                    is_hit=1 if trial_data.get("is_hit") else 0 if trial_data.get("is_hit") is not None else None,
                    is_false_alarm=1 if trial_data.get("is_false_alarm") else 0 if trial_data.get("is_false_alarm") is not None else None,
                    is_miss=1 if trial_data.get("is_miss") else 0 if trial_data.get("is_miss") is not None else None,
                    is_correct_reject=1 if trial_data.get("is_correct_reject") else 0 if trial_data.get("is_correct_reject") is not None else None,
                    timestamp=datetime.fromisoformat(trial_data["timestamp"])
                )
                db.add(db_trial)
                db.commit()
                return True
        except Exception as e:
            print(f"保存试次数据失败: {e}")
            return False
    
    def save_kss_score(self, session_id: str, kss_data: Dict[str, Any]) -> bool:
        """保存 KSS 评分"""
        try:
            with Session(engine) as db:
                # 创建 KSS 评分模型
                db_kss = TwoBackKSSScoreModel(
                    session_id=session_id,
                    round_num=kss_data["round"],
                    score=kss_data["score"],
                    timestamp=datetime.fromisoformat(kss_data["timestamp"])
                )
                db.add(db_kss)
                db.commit()
                return True
        except Exception as e:
            print(f"保存 KSS 评分失败: {e}")
            return False
    
    def save_performance_metric(self, session_id: str, metric_data: Dict[str, Any]) -> bool:
        """保存表现指标"""
        try:
            with Session(engine) as db:
                # 创建表现指标模型
                db_metric = TwoBackPerformanceMetricModel(
                    session_id=session_id,
                    round_num=metric_data["round"],
                    hit_rate=metric_data["hit_rate"],
                    false_alarm_rate=metric_data["false_alarm_rate"],
                    avg_response_time=metric_data["avg_response_time"],
                    hits=metric_data["hits"],
                    false_alarms=metric_data["false_alarms"],
                    misses=metric_data["misses"],
                    correct_rejects=metric_data["correct_rejects"],
                    total_trials=metric_data["total_trials"]
                )
                db.add(db_metric)
                db.commit()
                return True
        except Exception as e:
            print(f"保存表现指标失败: {e}")
            return False
    
    def save_experiment_data(self, session_id: str, experiment_data: Dict[str, Any]) -> bool:
        """保存完整的实验数据"""
        try:
            with Session(engine) as db:
                # 创建实验数据汇总模型
                db_experiment_data = TwoBackExperimentDataModel(
                    session_id=session_id,
                    participant_id=experiment_data["participant_id"],
                    experiment_data=experiment_data,
                    analysis_result=experiment_data.get("analysis_result"),
                    created_at=datetime.now()
                )
                db.add(db_experiment_data)
                db.commit()
                return True
        except Exception as e:
            print(f"保存实验数据失败: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        try:
            with Session(engine) as db:
                db_session = db.query(TwoBackSessionModel).filter(
                    TwoBackSessionModel.session_id == session_id
                ).first()
                
                if not db_session:
                    return None
                
                # 转换为字典
                session_data = {
                    "session_id": db_session.session_id,
                    "participant_id": db_session.participant_id,
                    "settings": db_session.settings,
                    "start_time": db_session.start_time.isoformat(),
                    "end_time": db_session.end_time.isoformat() if db_session.end_time else None,
                    "status": db_session.status,
                    "completed_blocks": db_session.completed_blocks,
                    "overall_hit_rate": db_session.overall_hit_rate,
                    "total_trials": db_session.total_trials
                }
                
                return session_data
        except Exception as e:
            print(f"获取会话失败: {e}")
            return None
    
    def get_all_sessions(self) -> list:
        """获取所有会话"""
        try:
            with Session(engine) as db:
                db_sessions = db.query(TwoBackSessionModel).all()
                
                sessions = []
                for db_session in db_sessions:
                    session_data = {
                        "session_id": db_session.session_id,
                        "participant_id": db_session.participant_id,
                        "status": db_session.status,
                        "start_time": db_session.start_time.isoformat(),
                        "end_time": db_session.end_time.isoformat() if db_session.end_time else None,
                        "completed_blocks": db_session.completed_blocks,
                        "total_trials": db_session.total_trials
                    }
                    sessions.append(session_data)
                
                return sessions
        except Exception as e:
            print(f"获取所有会话失败: {e}")
            return []
    
    def get_session_trials(self, session_id: str) -> list:
        """获取会话的所有试次"""
        try:
            with Session(engine) as db:
                db_trials = db.query(TwoBackTrialModel).filter(
                    TwoBackTrialModel.session_id == session_id
                ).order_by(TwoBackTrialModel.trial_index).all()
                
                trials = []
                for db_trial in db_trials:
                    trial_data = {
                        "trial_id": db_trial.trial_id,
                        "block_num": db_trial.block_num,
                        "trial_index": db_trial.trial_index,
                        "stimulus": db_trial.stimulus,
                        "is_target": bool(db_trial.is_target),
                        "key_pressed": bool(db_trial.key_pressed),
                        "response_time": db_trial.response_time,
                        "is_hit": bool(db_trial.is_hit) if db_trial.is_hit is not None else None,
                        "is_false_alarm": bool(db_trial.is_false_alarm) if db_trial.is_false_alarm is not None else None,
                        "is_miss": bool(db_trial.is_miss) if db_trial.is_miss is not None else None,
                        "is_correct_reject": bool(db_trial.is_correct_reject) if db_trial.is_correct_reject is not None else None,
                        "timestamp": db_trial.timestamp.isoformat()
                    }
                    trials.append(trial_data)
                
                return trials
        except Exception as e:
            print(f"获取会话试次失败: {e}")
            return []
    
    def get_session_kss_scores(self, session_id: str) -> list:
        """获取会话的所有 KSS 评分"""
        try:
            with Session(engine) as db:
                db_kss_scores = db.query(TwoBackKSSScoreModel).filter(
                    TwoBackKSSScoreModel.session_id == session_id
                ).order_by(TwoBackKSSScoreModel.round_num).all()
                
                kss_scores = []
                for db_kss in db_kss_scores:
                    kss_data = {
                        "round": db_kss.round_num,
                        "score": db_kss.score,
                        "timestamp": db_kss.timestamp.isoformat()
                    }
                    kss_scores.append(kss_data)
                
                return kss_scores
        except Exception as e:
            print(f"获取会话 KSS 评分失败: {e}")
            return []
    
    def get_session_performance_metrics(self, session_id: str) -> list:
        """获取会话的所有表现指标"""
        try:
            with Session(engine) as db:
                db_metrics = db.query(TwoBackPerformanceMetricModel).filter(
                    TwoBackPerformanceMetricModel.session_id == session_id
                ).order_by(TwoBackPerformanceMetricModel.round_num).all()
                
                metrics = []
                for db_metric in db_metrics:
                    metric_data = {
                        "round": db_metric.round_num,
                        "hit_rate": db_metric.hit_rate,
                        "false_alarm_rate": db_metric.false_alarm_rate,
                        "avg_response_time": db_metric.avg_response_time,
                        "hits": db_metric.hits,
                        "false_alarms": db_metric.false_alarms,
                        "misses": db_metric.misses,
                        "correct_rejects": db_metric.correct_rejects,
                        "total_trials": db_metric.total_trials
                    }
                    metrics.append(metric_data)
                
                return metrics
        except Exception as e:
            print(f"获取会话表现指标失败: {e}")
            return []

# 单例实例
data_storage_service = DataStorageService()
