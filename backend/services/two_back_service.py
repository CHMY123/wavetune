# 2-Back 疲劳诱发实验后端服务
import random
import time
import json
import uuid
import socket
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------- Trigger Server 配置 -------------------
TRIGGER_SERVER_IP = '192.168.3.25'  # 根据实验室网络修改
TRIGGER_SERVER_PORT = 9986
TRIGGER_BUFFER_SIZE = 2048

# 全局触发器套接字与最后客户端地址（由监听线程更新）
server_socket = None
last_client_address = None
trigger_lock = threading.Lock()

class TwoBackService:
    def __init__(self):
        # 初始化实验数据存储
        self.experiments = {}
        # 初始化触发器服务器
        self.init_trigger_server()
    
    def init_trigger_server(self, server_ip=TRIGGER_SERVER_IP, server_port=TRIGGER_SERVER_PORT):
        """初始化 UDP 触发服务器套接字并启动监听线程"""
        global server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            server_socket.bind((server_ip, server_port))
            logger.info(f"✅ Trigger server bound on {server_ip}:{server_port}")
        except Exception as e:
            logger.error(f"❌ 绑定触发服务器失败: {e}")
            server_socket = None
            return

        t = threading.Thread(target=self.trigger_listen_thread, daemon=True)
        t.start()
    
    def trigger_listen_thread(self):
        """后台线程：接收来自 EEG 设备/采集端的 UDP 消息并记录客户端地址"""
        global server_socket, last_client_address
        if server_socket is None:
            return
        logger.info("🔁 Trigger listen thread started, waiting for client messages...")
        while True:
            try:
                data, addr = server_socket.recvfrom(TRIGGER_BUFFER_SIZE)
                last_client_address = addr
                logger.info(f"🛰 Received from {addr}: {data[:200]!r}")
                # 可选：回复确认
                try:
                    ack = json.dumps({"action": "ack", "timestamp": datetime.now().isoformat()})
                    server_socket.sendto((ack + "\r\n").encode('utf-8'), addr)
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"Trigger listen error: {e}")
                time.sleep(0.5)
    
    def trigger(self, marker: int, port: int = 12345, ip: str = '127.0.0.1'):
        """发送 marker 给最后连接的客户端（非阻塞、线程安全）"""
        global server_socket, last_client_address
        with trigger_lock:
            if server_socket is None:
                logger.warning(f"⚠️ trigger({marker}) 未发送：server_socket 未初始化")
                return {"success": False, "message": "Server socket not initialized"}
            
            # 优先使用传入的 IP 和端口
            target_address = (ip, port)
            
            # 如果没有传入 IP 和端口，使用最后连接的客户端地址
            if ip == '127.0.0.1' and port == 12345 and last_client_address:
                target_address = last_client_address
                logger.info(f"➡️ Using last client address: {target_address}")
            
            try:
                payload = json.dumps({"action": "trigger", "marker": int(marker)})
                server_socket.sendto((payload + "\r\n").encode('utf-8'), target_address)
                logger.info(f"➡️ Sent marker {marker} to {target_address}")
                return {"success": True, "message": f"Marker {marker} sent to {target_address}"}
            except Exception as e:
                logger.error(f"❌ 发送 marker {marker} 失败: {e}")
                return {"success": False, "message": f"Failed to send marker: {str(e)}"}
    
    def generate_id(self, prefix: str = "P") -> str:
        """生成唯一 ID"""
        return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    
    def init_experiment(self, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """初始化 2-Back 实验"""
        # 默认设置
        default_settings = {
            "duration": 10,
            "trialsPerBlock": 20,
            "blockCount": 2,
            "stimulusDuration": 1000,
            "intervalDuration": 1000,
            "breakDuration": 60,
            "letters": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        }
        
        # 更新设置
        if settings:
            default_settings.update(settings)
        
        # 生成会话 ID 和参与者 ID
        participant_id = self.generate_id("P")
        session_id = self.generate_id("S")
        
        # 创建实验数据
        experiment_data = {
            "session_id": session_id,
            "participant_id": participant_id,
            "settings": default_settings,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "initialized",
            "completed_blocks": 0,
            "overall_hit_rate": None,
            "total_trials": 0,
            "trials": [],
            "kss_scores": [],
            "performance_metrics": []
        }
        
        # 存储实验数据
        self.experiments[session_id] = experiment_data
        
        # 发送实验开始 marker
        self.trigger(100)
        
        logger.info(f"✅ 实验初始化成功: {session_id}")
        return experiment_data
    
    def generate_2back_sequence(self, length: int, match_rate: float = 0.28, 
                              letters: list = ["A", "B", "C", "D", "E"]) -> Tuple[List[str], List[bool]]:
        """生成 2-Back 实验刺激序列"""
        if length < 3:
            raise ValueError("序列长度必须≥3")
        
        seq = [random.choice(letters), random.choice(letters)]
        is_target = [False, False]
        consecutive_matches = 0
        max_consecutive_matches = 2
        
        for i in range(2, length):
            place_match = (random.random() < match_rate and
                           consecutive_matches < max_consecutive_matches)
            if place_match:
                seq.append(seq[i - 2])
                is_target.append(True)
                consecutive_matches += 1
            else:
                exclude = {seq[i - 2]}
                candidates = [L for L in letters if L not in exclude]
                choice = random.choice(candidates)
                if choice == seq[i - 1]:
                    choice = random.choice(candidates)
                seq.append(choice)
                is_target.append(False)
                consecutive_matches = 0
        
        logger.info(f"✅ 生成刺激序列成功: {length} 个试次")
        return seq, is_target
    
    def record_trial(self, session_id: str, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """记录试次数据"""
        if session_id not in self.experiments:
            raise ValueError(f"实验会话不存在: {session_id}")
        
        # 获取实验数据
        experiment = self.experiments[session_id]
        
        # 计算试次结果
        is_target = trial_data.get("is_target", False)
        key_pressed = trial_data.get("key_pressed", False)
        
        trial_result = {
            "is_hit": is_target and key_pressed,
            "is_false_alarm": not is_target and key_pressed,
            "is_miss": is_target and not key_pressed,
            "is_correct_reject": not is_target and not key_pressed
        }
        
        # 更新试次数据
        trial_data.update(trial_result)
        
        # 存储试次数据
        experiment["trials"].append(trial_data)
        
        # 发送试次标记
        if is_target:
            self.trigger(10)  # 目标刺激标记
        else:
            self.trigger(11)  # 非目标刺激标记
        
        # 如果按键响应，发送响应标记
        if key_pressed:
            self.trigger(20)  # 响应标记
        
        logger.info(f"✅ 记录试次成功: {trial_data.get('trial_id')}")
        return {"success": True, "message": "Trial recorded successfully"}
    
    def record_kss(self, session_id: str, round: int, score: int) -> Dict[str, Any]:
        """记录 KSS 评分"""
        if session_id not in self.experiments:
            raise ValueError(f"实验会话不存在: {session_id}")
        
        if score < 1 or score > 9:
            raise ValueError("KSS 评分必须在 1-9 之间")
        
        # 获取实验数据
        experiment = self.experiments[session_id]
        
        # 创建 KSS 评分数据
        kss_data = {
            "round": round,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
        
        # 存储 KSS 评分
        experiment["kss_scores"].append(kss_data)
        
        # 发送 KSS 标记
        self.trigger(120)  # KSS 开始标记
        self.trigger(121)  # KSS 评分标记
        
        logger.info(f"✅ 记录 KSS 评分成功: {score}")
        return kss_data
    
    def complete_experiment(self, session_id: str) -> Dict[str, Any]:
        """完成实验，返回分析结果"""
        if session_id not in self.experiments:
            raise ValueError(f"实验会话不存在: {session_id}")
        
        # 获取实验数据
        experiment = self.experiments[session_id]
        
        # 更新实验状态
        experiment["end_time"] = datetime.now().isoformat()
        experiment["status"] = "completed"
        
        # 计算实验结果
        trials = experiment["trials"]
        total_trials = len(trials)
        experiment["total_trials"] = total_trials
        
        # 计算总体命中率
        if total_trials > 0:
            hits = sum(1 for trial in trials if trial.get("is_hit", False))
            targets = sum(1 for trial in trials if trial.get("is_target", False))
            overall_hit_rate = hits / targets if targets > 0 else 0
            experiment["overall_hit_rate"] = overall_hit_rate
        
        # 计算每轮表现
        block_count = experiment["settings"].get("blockCount", 1)
        trials_per_block = experiment["settings"].get("trialsPerBlock", 20)
        
        for block in range(block_count):
            start_index = block * trials_per_block
            end_index = (block + 1) * trials_per_block
            block_trials = trials[start_index:end_index]
            
            if block_trials:
                hits = sum(1 for trial in block_trials if trial.get("is_hit", False))
                fas = sum(1 for trial in block_trials if trial.get("is_false_alarm", False))
                targets = sum(1 for trial in block_trials if trial.get("is_target", False))
                correct_rejects = sum(1 for trial in block_trials if trial.get("is_correct_reject", False))
                misses = sum(1 for trial in block_trials if trial.get("is_miss", False))
                
                hit_rate = hits / targets if targets > 0 else 0
                fa_rate = fas / (len(block_trials) - targets) if (len(block_trials) - targets) > 0 else 0
                
                # 计算平均反应时
                response_times = [trial.get("response_time", 0) for trial in block_trials 
                                if trial.get("response_time")]
                avg_response_time = sum(response_times) / len(response_times) * 1000 if response_times else 0
                
                # 存储表现指标
                performance_metric = {
                    "round": block + 1,
                    "hit_rate": hit_rate,
                    "false_alarm_rate": fa_rate,
                    "avg_response_time": avg_response_time,
                    "hits": hits,
                    "false_alarms": fas,
                    "misses": misses,
                    "correct_rejects": correct_rejects,
                    "total_trials": len(block_trials)
                }
                experiment["performance_metrics"].append(performance_metric)
        
        # 发送实验结束 marker
        self.trigger(199)
        
        logger.info(f"✅ 实验完成成功: {session_id}")
        return {
            "session_id": session_id,
            "participant_id": experiment["participant_id"],
            "start_time": experiment["start_time"],
            "end_time": experiment["end_time"],
            "status": experiment["status"],
            "total_trials": total_trials,
            "overall_hit_rate": experiment["overall_hit_rate"],
            "kss_scores": experiment["kss_scores"],
            "performance_metrics": experiment["performance_metrics"]
        }

# 创建服务实例
two_back_service = TwoBackService()
