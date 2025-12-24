#!/usr/bin/env python3
"""
脑疲劳可视化检测工具（Tkinter GUI）
依赖：Python 标准库 + torch + pandas + numpy
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import torch
import joblib
import os
import sys

# ---------------- 模型加载（零依赖） ----------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
scaler = joblib.load('scaler.pkl')
model = None


def _load_model():
    global model
    if model is None:
        spec = {}
        exec(open('model.py', encoding='utf-8').read(), spec)
        # 根据 model.py 中的类名实例化；若类名不同请修改下方字符串
        model = spec['FatigueDetectionModel'](time_steps=20, num_classes=3).to(device)
        model.load_state_dict(torch.load('best_model.pth', map_location=device))
        model.eval()
    return model


def detect(x_raw):
    """输入: (20, 20)  输出: (label, prob)"""
    x = np.array(x_raw, dtype=np.float32)
    if x.shape != (20, 20):
        raise ValueError("必须是 20×20")
    x_flat = x.reshape(-1, 20)
    x_flat = scaler.transform(x_flat)
    x = x_flat.reshape(20, 20)
    seq = x[:15, :].reshape(15, 1, 4, 5)
    x_tensor = torch.FloatTensor(seq).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x_tensor)
        prob = torch.softmax(logits, dim=1).cpu().numpy().flatten()
    label = int(np.argmax(prob))
    return label, prob


# ---------------- GUI 构建 ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("脑疲劳快速检测")
        self.geometry("500x600")
        self.resizable(False, False)
        _load_model()  # 预加载模型
        self.create_widgets()

    def create_widgets(self):
        # 标题
        tk.Label(self, text="脑疲劳检测", font=("微软雅黑", 18, "bold")).pack(pady=10)

        # 输入选择
        self.method = tk.StringVar(value="csv")
        frame_method = tk.Frame(self)
        frame_method.pack(pady=5)
        tk.Radiobutton(frame_method, text="上传 CSV", variable=self.method, value="csv",
                       command=self.switch_input).pack(side="left", padx=10)
        tk.Radiobutton(frame_method, text="粘贴数值", variable=self.method, value="vec",
                       command=self.switch_input).pack(side="left", padx=10)

        # 输入区域
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)
        self.switch_input()

        # 检测按钮
        tk.Button(self, text="开始检测", command=self.detect, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 12)).pack(pady=10)

        # 结果区域
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(pady=10, fill='both', expand=True)

    def switch_input(self):
        """切换输入方式"""
        for w in self.input_frame.winfo_children():
            w.destroy()

        if self.method.get() == "csv":
            tk.Button(self.input_frame, text="选择 CSV 文件", command=self.load_csv).pack()
            self.csv_path = tk.StringVar()
            tk.Entry(self.input_frame, textvariable=self.csv_path, width=40,
                     state='readonly').pack(pady=5)
        else:
            tk.Label(self.input_frame, text="粘贴 400 个数值（逗号分隔）:").pack()
            self.text_vec = tk.Text(self.input_frame, width=50, height=8)
            self.text_vec.pack()

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path.set(path)

    def detect(self):
        # 获取输入
        try:
            if self.method.get() == "csv":
                path = self.csv_path.get()
                if not path:
                    raise ValueError("未选择 CSV 文件")
                df = pd.read_csv(path, header=None)
                if df.shape != (20, 20):
                    raise ValueError("CSV 必须是 20×20")
                x_raw = df.values
            else:
                vec = self.text_vec.get("1.0", "end-1c").strip()
                if not vec:
                    raise ValueError("未粘贴数值")
                nums = list(map(float, vec.split(',')))
                if len(nums) != 400:
                    raise ValueError("必须是 400 个数值")
                x_raw = np.array(nums).reshape(20, 20)

            # 推理
            label, prob = detect(x_raw)
            label_map = {0: 'Low', 1: 'Medium', 2: 'High'}
            advice = {0: "状态良好，继续保持！", 1: "轻度疲劳，建议短暂休息。", 2: "中度疲劳，建议立即休息 10-15 分钟并补充水分。"}

            # 清空旧结果
            for w in self.result_frame.winfo_children():
                w.destroy()

            # 结果展示
            tk.Label(self.result_frame, text=f"预测类别: {label_map[label]}", font=("微软雅黑", 16, "bold")).pack()
            tk.Label(self.result_frame, text=f"置信度: {prob[label]:.3f}", font=("微软雅黑", 12)).pack()
            tk.Label(self.result_frame, text=f"三类别概率: Low={prob[0]:.3f}  Medium={prob[1]:.3f}  High={prob[2]:.3f}", font=("微软雅黑", 10)).pack()
            tk.Label(self.result_frame, text=f"建议: {advice[label]}", font=("微软雅黑", 11), fg="blue").pack(pady=5)

            # 柱状图
            self.plot_bar(prob)

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def plot_bar(self, prob):
        fig = plt.Figure(figsize=(4, 2), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(['Low', 'Medium', 'High'], prob, color=['#4CAF50', '#FFC107', '#F44336'])
        ax.set_ylim(0, 1)
        ax.set_ylabel('Probability')
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


# ---------------- 入口 ----------------
if __name__ == '__main__':
    App().mainloop()