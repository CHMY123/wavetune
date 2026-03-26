# 整合版：2-Back 疲劳诱发实验 + EEG UDP Trigger
import random
import time
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import threading
import socket
from matplotlib import font_manager

# ------------------- Trigger Server 配置 -------------------
TRIGGER_SERVER_IP = '192.168.32.136'  # 根据实验室网络修改
TRIGGER_SERVER_PORT = 9986
TRIGGER_BUFFER_SIZE = 2048

# 全局触发器套接字与最后客户端地址（由监听线程更新）
server_socket = None
last_client_address = None
trigger_lock = threading.Lock()

def init_trigger_server(server_ip=TRIGGER_SERVER_IP, server_port=TRIGGER_SERVER_PORT):
    """初始化 UDP 触发服务器套接字并启动监听线程"""
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.bind((server_ip, server_port))
        print(f"✅ Trigger server bound on {server_ip}:{server_port}")
    except Exception as e:
        print(f"❌ 绑定触发服务器失败: {e}")
        server_socket = None
        return

    t = threading.Thread(target=trigger_listen_thread, daemon=True)
    t.start()

def trigger_listen_thread():
    """后台线程：接收来自 EEG 设备/采集端的 UDP 消息并记录客户端地址"""
    global server_socket, last_client_address
    if server_socket is None:
        return
    print("🔁 Trigger listen thread started, waiting for client messages...")
    while True:
        try:
            data, addr = server_socket.recvfrom(TRIGGER_BUFFER_SIZE)
            last_client_address = addr
            print(f"🛰 Received from {addr}: {data[:200]!r}")
            # 可选：回复确认
            try:
                ack = json.dumps({"action": "ack", "timestamp": datetime.now().isoformat()})
                server_socket.sendto((ack + "\r\n").encode('utf-8'), addr)
            except Exception:
                pass
        except Exception as e:
            print(f"Trigger listen error: {e}")
            time.sleep(0.5)

def trigger(marker: int):
    """发送 marker 给最后连接的客户端（非阻塞、线程安全）"""
    global server_socket, last_client_address
    with trigger_lock:
        if server_socket is None:
            print(f"⚠️ trigger({marker}) 未发送：server_socket 未初始化")
            return False
        if last_client_address is None:
            print(f"⚠️ trigger({marker}) 未发送：尚无客户端地址（请确保 EEG 端已发送一次 UDP 消息到本脚本）")
            return False
        try:
            payload = json.dumps({"action": "trigger", "marker": int(marker)})
            server_socket.sendto((payload + "\r\n").encode('utf-8'), last_client_address)
            # 打印日志便于线下校验
            print(f"➡️ Sent marker {marker} to {last_client_address}")
            return True
        except Exception as e:
            print(f"❌ 发送 marker {marker} 失败: {e}")
            return False

# ------------------- 字体设置 -------------------
def setup_chinese_font():
    """设置matplotlib中文字体"""
    try:
        font_list = [
            'Microsoft YaHei', 'SimHei', 'KaiTi', 'SimSun',
            'Arial Unicode MS', 'DejaVu Sans'
        ]

        for font_name in font_list:
            try:
                plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
                test_font = font_manager.FontProperties(family=font_name)
                if test_font.get_name():
                    print(f"✅ 使用字体: {font_name}")
                    return True
            except Exception:
                continue

        print("⚠️ 未找到合适的中文字体，使用默认字体")
        return False
    except Exception as e:
        print(f"字体设置失败: {e}")
        return False

setup_chinese_font()

# ------------------- 实验类 -------------------
class TwoBackFatigueExperiment:
    def __init__(self):
        # ------------------- 实验参数 -------------------
        self.LETTERS = ["A", "B", "C", "D", "E"]
        self.MATCH_RATE = 0.28
        self.TRIALS_PER_MINUTE = 24
        self.MINUTES_PER_BLOCK = 10
        self.TRIALS_PER_BLOCK = self.TRIALS_PER_MINUTE * self.MINUTES_PER_BLOCK
        self.BLOCK_COUNT = 3
        self.STIMULUS_DURATION_MS = 500
        self.ISI_MS = 2000
        self.TRIAL_DURATION_MS = self.STIMULUS_DURATION_MS + self.ISI_MS
        self.MAX_CONSECUTIVE_MATCHES = 2

        # ------------------- 量表与静息采集 -------------------
        self.KSS_SCALE_DURATION = 30  # 秒
        self.REST_EEG_DURATION = 120  # 秒

        # ------------------- 数据 -------------------
        self.participant_id = self.generate_id("P")
        self.session_id = self.generate_id("S")
        self.data = []
        self.eeg_data = []
        self.kss_scores = []
        self.performance_metrics = []

        # ------------------- GUI -------------------
        self.root = None
        self.canvas = None
        self.stimulus_text = None
        self.feedback_text = None
        self.status_text = None
        self.progress_text = None

        # ------------------- 状态 -------------------
        self.is_running = True
        self.waiting_for_key = False
        self._waiting_kss_input = False
        self._current_kss_score = None
        self.current_trial_data = None
        self.trial_start_time = None
        self.stimulus_end_time = None
        self.trial_end_time = None

        # ------------------- 字体 -------------------
        self.font_large = ("Microsoft YaHei", 80, "bold")
        self.font_medium = ("Microsoft YaHei", 28)
        self.font_small = ("Microsoft YaHei", 20)
        self.font_tiny = ("Microsoft YaHei", 16)

    def generate_id(self, prefix: str = "P") -> str:
        import uuid
        return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    def generate_2back_sequence(self, length: int, match_rate: float = None):
        if match_rate is None:
            match_rate = self.MATCH_RATE
        if length < 3:
            raise ValueError("序列长度必须≥3")

        seq = [random.choice(self.LETTERS), random.choice(self.LETTERS)]
        is_target = [False, False]
        consecutive_matches = 0

        for i in range(2, length):
            place_match = (random.random() < match_rate and
                           consecutive_matches < self.MAX_CONSECUTIVE_MATCHES)
            if place_match:
                seq.append(seq[i - 2])
                is_target.append(True)
                consecutive_matches += 1
            else:
                exclude = {seq[i - 2]}
                candidates = [L for L in self.LETTERS if L not in exclude]
                choice = random.choice(candidates)
                if choice == seq[i - 1]:
                    choice = random.choice(candidates)
                seq.append(choice)
                is_target.append(False)
                consecutive_matches = 0

        return seq, is_target

    # ------------------- GUI -------------------
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("2-Back 疲劳诱发实验 + EEG采集")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)

        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.stimulus_text = self.canvas.create_text(
            w // 2, h // 2 - 50, text="", font=self.font_large, fill="white", anchor="center"
        )
        self.feedback_text = self.canvas.create_text(
            w // 2, h // 2 + 100, text="", font=self.font_medium, fill="yellow", anchor="center"
        )
        self.status_text = self.canvas.create_text(
            w // 2, 80, text="", font=self.font_small, fill="lightgray", anchor="center"
        )
        self.progress_text = self.canvas.create_text(
            w // 2, 120, text="", font=self.font_tiny, fill="lightblue", anchor="center"
        )

        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<Escape>', lambda e: self.exit_experiment())

    def on_key_press(self, event):
        """处理按键事件 - 优化反应时记录并发送 response trigger"""
        if self._waiting_kss_input:
            try:
                score = int(event.char)
                if 1 <= score <= 9:
                    self._current_kss_score = score
                    print(f"KSS评分记录: {score}")
            except Exception:
                pass

        # 空格键响应 - 在刺激呈现期间和ISI期间都记录
        if event.keysym == 'space' and self.current_trial_data is not None:
            current_time = time.time()
            if current_time <= self.trial_end_time:
                response_time = current_time - self.trial_start_time
                if not self.current_trial_data['key_pressed']:
                    self.current_trial_data['key_pressed'] = True
                    self.current_trial_data['response_time'] = response_time
                    print(f"按键记录: 反应时 {response_time:.3f}s")
                    # 发送 response marker（20）
                    trigger(20)

        elif event.keysym == 'q':
            self.exit_experiment()

    def record_response(self, pressed: bool):
        """记录响应 - 保持向后兼容"""
        if self.current_trial_data is not None:
            current_time = time.time()
            if current_time <= self.trial_end_time:
                response_time = current_time - self.trial_start_time
                if not self.current_trial_data['key_pressed'] and pressed:
                    # 只在第一次标记时发送 trigger
                    self.current_trial_data['key_pressed'] = pressed
                    self.current_trial_data['response_time'] = response_time
                    trigger(20)

    # ------------------- 实验流程 -------------------
    def show_stimulus(self, letter: str, is_target: bool, trial_index: int, round_index: int):
        """展示单个刺激 - 在刺激出现时发送 marker（target:10, non-target:11）"""
        status_text = f"第 {round_index} 轮 | 试次 {trial_index}/{self.TRIALS_PER_BLOCK}"
        progress_text = f"总进度: {round_index}/{self.BLOCK_COUNT} 轮"

        self.canvas.itemconfig(self.status_text, text=status_text)
        self.canvas.itemconfig(self.progress_text, text=progress_text)
        self.canvas.itemconfig(self.stimulus_text, text=letter)
        self.canvas.itemconfig(self.feedback_text, text="")
        self.root.update()

        # 初始化试次数据
        self.current_trial_data = {
            'participant_id': self.participant_id,
            'session_id': self.session_id,
            'round_index': round_index,
            'trial_index': trial_index,
            'stimulus_letter': letter,
            'is_target': is_target,
            'task': '2back',
            'key_pressed': False,
            'response_time': None,
            'timestamp': datetime.now().isoformat()
        }

        # 设置时间点
        self.trial_start_time = time.time()
        self.stimulus_end_time = self.trial_start_time + (self.STIMULUS_DURATION_MS / 1000.0)
        self.trial_end_time = self.trial_start_time + (self.TRIAL_DURATION_MS / 1000.0)

        # 在刺激出现瞬间发送 marker
        if is_target:
            trigger(10)  # 目标刺激 marker
        else:
            trigger(11)  # 非目标刺激 marker

        # 刺激呈现阶段 (0-500ms)
        current_time = time.time()
        while current_time < self.stimulus_end_time and self.is_running:
            self.root.update()
            time.sleep(0.001)
            current_time = time.time()

        # 清空刺激，进入 ISI 阶段
        self.canvas.itemconfig(self.stimulus_text, text="")
        self.root.update()

        current_time = time.time()
        while current_time < self.trial_end_time and self.is_running:
            self.root.update()
            time.sleep(0.001)
            current_time = time.time()

        # 试次结束，计算结果并保存
        pressed = self.current_trial_data['key_pressed']
        response_time = self.current_trial_data['response_time']

        self.current_trial_data.update({
            'is_hit': is_target and pressed,
            'is_false_alarm': not is_target and pressed,
            'is_miss': is_target and not pressed,
            'is_correct_reject': not is_target and not pressed
        })

        self.current_trial_data.update({
            'stimulus_duration': self.STIMULUS_DURATION_MS,
            'isi_duration': self.ISI_MS,
            'trial_duration': self.TRIAL_DURATION_MS,
            'response_within_stimulus': response_time is not None and response_time <= (self.STIMULUS_DURATION_MS / 1000.0),
            'response_within_isi': response_time is not None and response_time > (self.STIMULUS_DURATION_MS / 1000.0)
        })

        if pressed:
            rt_ms = response_time * 1000 if response_time else 0
            response_type = "刺激呈现期间" if rt_ms <= self.STIMULUS_DURATION_MS else "ISI期间"
            print(f"试次 {trial_index}: 反应时 {rt_ms:.1f}ms ({response_type})")
        else:
            print(f"试次 {trial_index}: 无响应")

        self.data.append(self.current_trial_data.copy())
        self.current_trial_data = None

    def run_2back_task(self, round_index=1):
        """运行2-Back任务，发送 block start/end marker"""
        print(f"开始第 {round_index} 轮 2-Back 任务")
        # 发送 block start marker (110)
        trigger(110)

        seq, targets = self.generate_2back_sequence(self.TRIALS_PER_BLOCK)

        for i, (letter, t) in enumerate(zip(seq, targets)):
            if not self.is_running:
                break
            self.show_stimulus(letter, t, i + 1, round_index)

        # 发送 block end marker (111)
        trigger(111)

        # 计算本轮表现
        round_data = [d for d in self.data if d['round_index'] == round_index]
        if round_data:
            hits = sum(1 for d in round_data if d['is_hit'])
            fas = sum(1 for d in round_data if d['is_false_alarm'])
            targets_count = sum(1 for d in round_data if d['is_target'])
            correct_rejects = sum(1 for d in round_data if d['is_correct_reject'])
            misses = sum(1 for d in round_data if d['is_miss'])

            hit_rate = hits / targets_count if targets_count > 0 else 0
            fa_rate = fas / (len(round_data) - targets_count) if (len(round_data) - targets_count) > 0 else 0

            hit_rts = [d['response_time'] for d in round_data if d['is_hit'] and d['response_time'] is not None]
            avg_rt = np.mean(hit_rts) * 1000 if hit_rts else 0

            self.performance_metrics.append({
                'round': round_index,
                'hit_rate': hit_rate,
                'fa_rate': fa_rate,
                'avg_rt_ms': avg_rt,
                'hits': hits,
                'false_alarms': fas,
                'misses': misses,
                'correct_rejects': correct_rejects,
                'total_trials': len(round_data)
            })

            print(f"第 {round_index} 轮表现 - 命中率: {hit_rate:.2%}, 虚报率: {fa_rate:.2%}, 平均反应时: {avg_rt:.1f}ms")

        self.canvas.itemconfig(self.feedback_text, text="2-Back 任务完成！")
        self.root.update()
        time.sleep(2)

    def run_kss_scale(self):
        """KSS 主观量表 - 发送 kss start (120) 与 kss score (121) marker"""
        # 发送 KSS 开始 marker
        trigger(120)

        self._waiting_kss_input = True
        self._current_kss_score = None

        scale_text = ("KSS疲劳量表\n\n"
                     "请根据当前疲劳程度选择数字 (1-9)\n\n"
                     "1=非常清醒   5=中等疲劳   9=极度困倦")

        self.canvas.itemconfig(self.stimulus_text, text=scale_text, font=self.font_medium)
        self.canvas.itemconfig(self.feedback_text, text="请在30秒内输入1-9", font=self.font_small)
        self.root.update()

        start = time.time()
        while time.time() - start < self.KSS_SCALE_DURATION and self._current_kss_score is None and self.is_running:
            self.root.update()
            time.sleep(0.1)

        if self._current_kss_score is None:
            self._current_kss_score = random.randint(4, 7)
            print(f"未检测到输入，使用随机KSS评分: {self._current_kss_score}")

        # 发送 KSS 评分 marker（121），把分数放到 data 里
        trigger(121)

        self.kss_scores.append({
            'round': len(self.kss_scores) + 1,
            'kss_score': self._current_kss_score,
            'timestamp': datetime.now().isoformat()
        })

        self._waiting_kss_input = False
        self.canvas.itemconfig(self.stimulus_text, text=f"KSS评分记录: {self._current_kss_score}", font=self.font_medium)
        self.canvas.itemconfig(self.feedback_text, text="", font=self.font_small)
        self.root.update()
        time.sleep(2)

    def run_rest_eeg(self):
        """静息脑电采集（此处为模拟） - 发送 rest start (130) 与 rest end (131) marker"""
        trigger(130)  # rest start

        self.canvas.itemconfig(self.stimulus_text, text="静息脑电采集中...\n请放松并保持静止", font=self.font_medium)
        self.canvas.itemconfig(self.feedback_text, text=f"剩余时间: {self.REST_EEG_DURATION}秒", font=self.font_small)
        self.root.update()

        start = time.time()
        sample_count = 0
        while time.time() - start < self.REST_EEG_DURATION and self.is_running:
            remaining = int(self.REST_EEG_DURATION - (time.time() - start))
            self.canvas.itemconfig(self.feedback_text, text=f"剩余时间: {remaining}秒")
            self.root.update()

            # 模拟EEG数据采集（上线时请替换为实际采集API）
            self.eeg_data.append({
                'timestamp': datetime.now().isoformat(),
                'eeg_signal': np.random.randn() * 10 + 5 * np.sin(2 * np.pi * 0.1 * sample_count),
                'sample_index': sample_count
            })
            sample_count += 1
            time.sleep(0.1)

        trigger(131)  # rest end

        self.canvas.itemconfig(self.stimulus_text, text="静息脑电采集结束", font=self.font_medium)
        self.canvas.itemconfig(self.feedback_text, text="", font=self.font_small)
        self.root.update()
        time.sleep(2)

    # ------------------- 数据与绘图 -------------------
    def save_data(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"experiment_data_{self.participant_id}_{timestamp}.json"

        data_package = {
            'participant_id': self.participant_id,
            'session_id': self.session_id,
            'experiment_info': {
                'block_count': self.BLOCK_COUNT,
                'trials_per_block': self.TRIALS_PER_BLOCK,
                'stimulus_duration_ms': self.STIMULUS_DURATION_MS,
                'isi_duration_ms': self.ISI_MS,
                'trial_duration_ms': self.TRIAL_DURATION_MS
            },
            'trials': self.data,
            'kss_scores': self.kss_scores,
            'performance_metrics': self.performance_metrics,
            'eeg_samples': len(self.eeg_data)
        }

        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(data_package, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存至 {fname}")
        return fname

    def plot_results(self):
        if not self.kss_scores:
            print("⚠️ 没有KSS评分数据可绘制")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('2-Back 疲劳诱发实验结果分析', fontsize=16, fontweight='bold')

        rounds = [score['round'] for score in self.kss_scores]
        kss_scores = [score['kss_score'] for score in self.kss_scores]

        ax1.plot(rounds, kss_scores, 'o-', linewidth=2, markersize=8)
        ax1.set_xlabel('实验轮次', fontsize=12)
        ax1.set_ylabel('KSS评分', fontsize=12)
        ax1.set_title('主观疲劳程度变化趋势', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(1, 9)

        if self.performance_metrics:
            perf_rounds = [m['round'] for m in self.performance_metrics]
            hit_rates = [m['hit_rate'] for m in self.performance_metrics]
            fa_rates = [m['fa_rate'] for m in self.performance_metrics]
            avg_rts = [m['avg_rt_ms'] for m in self.performance_metrics]

            ax2a = ax2
            line1 = ax2a.plot(perf_rounds, hit_rates, 'o-', linewidth=2, markersize=8, label='命中率')
            line2 = ax2a.plot(perf_rounds, fa_rates, 'o-', linewidth=2, markersize=8, label='虚报率')
            ax2a.set_xlabel('实验轮次', fontsize=12)
            ax2a.set_ylabel('比例', fontsize=12)
            ax2a.set_ylim(0, 1)

            ax2b = ax2a.twinx()
            line3 = ax2b.plot(perf_rounds, avg_rts, 's-', linewidth=2, markersize=6, label='反应时(ms)')
            ax2b.set_ylabel('平均反应时 (ms)', fontsize=12)

            lines = line1 + line2 + line3
            labels = [l.get_label() for l in lines]
            ax2a.legend(lines, labels, loc='upper left')

            ax2a.set_title('任务表现与反应时变化', fontsize=14, fontweight='bold')
            ax2a.grid(True, alpha=0.3)

        if self.data:
            response_times = [d['response_time'] * 1000 for d in self.data
                            if d['response_time'] is not None and d['is_hit']]
            if response_times:
                ax3.hist(response_times, bins=20, alpha=0.7, edgecolor='black')
                ax3.set_xlabel('反应时 (ms)', fontsize=12)
                ax3.set_ylabel('频次', fontsize=12)
                ax3.set_title('命中试次反应时分布', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3)

        if self.performance_metrics and len(self.performance_metrics) >= 2:
            first_round = self.performance_metrics[0]
            last_round = self.performance_metrics[-1]

            categories = ['命中率', '虚报率', '反应时(ms)']
            first_values = [first_round['hit_rate'], first_round['fa_rate'], first_round['avg_rt_ms']]
            last_values = [last_round['hit_rate'], last_round['fa_rate'], last_round['avg_rt_ms']]

            x = np.arange(len(categories))
            width = 0.35

            ax4.bar(x - width/2, first_values, width, label='第一轮', alpha=0.8)
            ax4.bar(x + width/2, last_values, width, label='最后一轮', alpha=0.8)
            ax4.set_xlabel('指标', fontsize=12)
            ax4.set_ylabel('数值', fontsize=12)
            ax4.set_title('首尾轮次表现对比', fontsize=14, fontweight='bold')
            ax4.set_xticks(x)
            ax4.set_xticklabels(categories)
            ax4.legend()
            ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_filename = f"results_plot_{self.participant_id}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"📊 结果图表已保存: {plot_filename}")
        plt.show()

    # ------------------- 主控制 -------------------
    def run(self):
        """运行完整实验"""
        try:
            # 初始化 Trigger Server（非阻塞，后台线程会等待客户端发包以建立地址）
            init_trigger_server()

            # 发送实验开始 marker (100)
            trigger(100)

            self.setup_gui()

            welcome_text = ("2-Back 疲劳诱发实验\n\n"
                          "实验说明:\n"
                          "• 当当前字母与前两个位置相同时按空格键\n"
                          "• 反应时从刺激出现开始计算\n"
                          "• 每轮包含2-Back任务、疲劳评分和静息采集\n"
                          "• 按Q键可提前退出实验")

            self.canvas.itemconfig(self.stimulus_text, text=welcome_text, font=self.font_medium)
            self.canvas.itemconfig(self.feedback_text, text="按 Enter 键开始实验", font=self.font_small)
            self.root.update()

            # 等待开始
            self.wait_for_key('Return')

            # 运行实验
            for round_index in range(1, self.BLOCK_COUNT + 1):
                if not self.is_running:
                    break

                print(f"\n=== 开始第 {round_index}/{self.BLOCK_COUNT} 轮实验 ===")

                self.run_2back_task(round_index)
                self.run_kss_scale()
                self.run_rest_eeg()

                if round_index < self.BLOCK_COUNT:
                    self.canvas.itemconfig(self.stimulus_text, text=f"第 {round_index} 轮完成", font=self.font_medium)
                    self.canvas.itemconfig(self.feedback_text, text="短暂休息，按 Enter 键继续", font=self.font_small)
                    self.root.update()
                    self.wait_for_key('Return')

            # 实验结束
            if self.is_running:
                # 发送实验结束 marker (199)
                trigger(199)

                fname = self.save_data()
                self.plot_results()

                self.canvas.itemconfig(self.stimulus_text, text="实验完成！", font=self.font_large)
                self.canvas.itemconfig(self.feedback_text, text="感谢参与！数据已保存分析", font=self.font_medium)
                self.root.update()

                messagebox.showinfo("实验结束", "实验已全部完成，感谢参与！\n数据文件和图表已自动保存。")

        except Exception as e:
            print(f"实验出错: {e}")
            messagebox.showerror("错误", f"实验出现错误: {e}")
        finally:
            self.exit_experiment()

    def wait_for_key(self, key='Return'):
        """等待特定按键"""
        self.waiting_for_key = True
        self.root.bind(f'<{key}>', lambda e: self.root.quit())
        self.root.mainloop()
        self.root.unbind(f'<{key}>')
        self.waiting_for_key = False

    def exit_experiment(self):
        """退出实验"""
        self.is_running = False
        # 发送退出 marker（可选）
        try:
            trigger(199)
        except Exception:
            pass
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass

if __name__ == "__main__":
    print("=" * 60)
    print("2-Back 疲劳诱发实验系统（含 EEG Trigger）")
    print("=" * 60)
    print("Marker 约定（示例，可与采集端确认）:")
    print("100: 实验开始")
    print("110: 本轮（block）开始")
    print("111: 本轮（block）结束")
    print("10 : 目标刺激（target）")
    print("11 : 非目标刺激（non-target）")
    print("20 : 受试按键（response）")
    print("120: KSS 开始")
    print("121: KSS 评分")
    print("130: 静息采集开始")
    print("131: 静息采集结束")
    print("199: 实验结束/退出")
    print("=" * 60)

    exp = TwoBackFatigueExperiment()
    exp.run()
