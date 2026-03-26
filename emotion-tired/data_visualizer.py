import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import glob
import os
from scipy import signal
from processing_fNIRS_new import get_processing_from_origin_data_48_ch, process_origin_to_fNIRS

class DataVisualizer:
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        sns.set(style="whitegrid")

    def load_csv(self, csv_path):
        print(f"📁 加载文件: {csv_path}")
        try:
            raw_data = np.loadtxt(csv_path, delimiter=',').T
        except ValueError:
            raw_data = np.loadtxt(csv_path).T
        print(f"   数据形状: {raw_data.shape}")
        return raw_data

    def extract_data(self, raw_data):
        eeg_data = raw_data[1:33, :]
        fnirs_raw = raw_data[33:57, :]
        marker_data = raw_data[56, :]
        label_data = raw_data[-1, :]
        
        marker_col_index = 56
        fNIRS_channels, data_780, data_850, _ = get_processing_from_origin_data_48_ch(raw_data, marker_col_index)
        
        hbo, hbr = [], []
        if len(data_780) > 0 and len(data_780[0]) > 0:
            hbo, hbr = process_origin_to_fNIRS(
                np.array(data_850).T, 
                np.array(data_780).T, 
                [850, 780]
            )
            hbo = hbo.T
            hbr = hbr.T
        
        return {
            'eeg': eeg_data,
            'fnirs_raw': fnirs_raw,
            'hbo': hbo,
            'hbr': hbr,
            'marker': marker_data,
            'label': label_data,
            'fNIRS_channels': fNIRS_channels
        }

    def plot_eeg_channels(self, eeg_data, duration=10, channels=[0, 1, 2, 3]):
        plt.figure(figsize=(15, 8))
        sample_rate = 1000
        time = np.arange(eeg_data.shape[1]) / sample_rate
        end_sample = int(duration * sample_rate)
        
        for i, ch in enumerate(channels):
            plt.subplot(len(channels), 1, i+1)
            plt.plot(time[:end_sample], eeg_data[ch, :end_sample])
            plt.title(f'EEG Channel {ch+1}')
            plt.ylabel('Amplitude')
            if i == len(channels)-1:
                plt.xlabel('Time (s)')
            plt.grid(True)
        
        plt.tight_layout()
        plt.suptitle('EEG Signals', y=1.02, fontsize=16)
        return plt

    def plot_fnirs_channels(self, hbo, hbr, duration=60, channels=[0, 1, 2, 3]):
        if len(hbo) == 0:
            return None
            
        plt.figure(figsize=(15, 8))
        sample_rate = 5
        time = np.arange(hbo.shape[1]) / sample_rate
        end_sample = min(int(duration * sample_rate), hbo.shape[1])
        
        for i, ch in enumerate(channels):
            plt.subplot(len(channels), 1, i+1)
            plt.plot(time[:end_sample], hbo[ch, :end_sample], label='HbO')
            plt.plot(time[:end_sample], hbr[ch, :end_sample], label='HbR')
            plt.title(f'fNIRS Channel {ch+1}')
            plt.ylabel('Concentration')
            if i == len(channels)-1:
                plt.xlabel('Time (s)')
            plt.legend()
            plt.grid(True)
        
        plt.tight_layout()
        plt.suptitle('fNIRS Signals (HbO/HbR)', y=1.02, fontsize=16)
        return plt

    def plot_power_spectrum(self, eeg_data, channel=0):
        sample_rate = 1000
        nperseg = 1024
        
        f, Pxx = signal.welch(eeg_data[channel, :], fs=sample_rate, nperseg=nperseg)
        
        plt.figure(figsize=(12, 6))
        plt.semilogy(f, Pxx)
        plt.title(f'Power Spectrum - EEG Channel {channel+1}')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (μV²/Hz)')
        plt.xlim([0, 50])
        plt.grid(True)
        return plt

    def plot_labels(self, label_data, duration=60):
        sample_rate = 1000
        time = np.arange(label_data.shape[0]) / sample_rate
        end_sample = int(duration * sample_rate)
        
        plt.figure(figsize=(15, 4))
        plt.step(time[:end_sample], label_data[:end_sample])
        plt.title('Fatigue Labels Over Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Label')
        plt.yticks([0, 1, 2], ['Normal', 'Mild Fatigue', 'Severe Fatigue'])
        plt.grid(True)
        return plt

    def plot_heatmap(self, data, title):
        plt.figure(figsize=(12, 8))
        sns.heatmap(data, cmap='viridis')
        plt.title(title)
        plt.tight_layout()
        return plt

    def plot_summary(self, data_dict):
        fig, axes = plt.subplots(2, 2, figsize=(20, 12))
        fig.suptitle('Data Summary', fontsize=16)
        
        eeg_data = data_dict['eeg']
        hbo = data_dict['hbo']
        label_data = data_dict['label']
        
        # EEG 信号
        ax = axes[0, 0]
        time = np.arange(2000) / 1000
        ax.plot(time, eeg_data[0, :2000])
        ax.set_title('EEG Signal (Channel 1)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        
        # fNIRS 信号
        if len(hbo) > 0:
            ax = axes[0, 1]
            time = np.arange(min(100, hbo.shape[1])) / 5
            ax.plot(time, hbo[0, :min(100, hbo.shape[1])], label='HbO')
            ax.plot(time, data_dict['hbr'][0, :min(100, hbo.shape[1])], label='HbR')
            ax.set_title('fNIRS Signal (Channel 1)')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Concentration')
            ax.legend()
        
        # 标签分布
        ax = axes[1, 0]
        unique, counts = np.unique(label_data[label_data != 0], return_counts=True)
        ax.bar(unique, counts)
        ax.set_title('Label Distribution')
        ax.set_xlabel('Label')
        ax.set_ylabel('Count')
        ax.set_xticks([1, 2], ['Mild Fatigue', 'Severe Fatigue'])
        
        # 数据统计
        ax = axes[1, 1]
        stats = {
            'EEG Channels': eeg_data.shape[0],
            'fNIRS Channels': len(hbo) if len(hbo) > 0 else 0,
            'Total Samples': eeg_data.shape[1],
            'Duration': eeg_data.shape[1] / 1000,
            'Non-zero Labels': len(label_data[label_data != 0])
        }
        ax.axis('off')
        table_data = [[k, v] for k, v in stats.items()]
        table = ax.table(cellText=table_data, colLabels=['Metric', 'Value'], loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        return plt

    def process_file(self, csv_path, output_dir=None):
        raw_data = self.load_csv(csv_path)
        data_dict = self.extract_data(raw_data)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 生成各种图表
        plots = {
            'eeg_channels': self.plot_eeg_channels(data_dict['eeg']),
            'fnirs_channels': self.plot_fnirs_channels(data_dict['hbo'], data_dict['hbr']),
            'power_spectrum': self.plot_power_spectrum(data_dict['eeg']),
            'labels': self.plot_labels(data_dict['label']),
            'summary': self.plot_summary(data_dict)
        }
        
        # 保存或显示
        if output_dir:
            base_name = os.path.splitext(os.path.basename(csv_path))[0]
            for name, plot in plots.items():
                if plot:
                    plot.savefig(os.path.join(output_dir, f'{base_name}_{name}.png'), dpi=150, bbox_inches='tight')
                    plot.close()
            print(f"📊 图表已保存到: {output_dir}")
        else:
            for name, plot in plots.items():
                if plot:
                    plot.show()
                    plt.pause(2)
                    plt.close()

def main():
    parser = argparse.ArgumentParser(description="CSV数据可视化工具")
    parser.add_argument("--csv", type=str, default=None, help="CSV文件路径")
    parser.add_argument("--output", type=str, default=None, help="输出目录")
    parser.add_argument("--batch", action="store_true", help="批量处理当前目录下所有CSV文件")
    parser.add_argument("--duration", type=float, default=10, help="显示时长(秒)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 CSV数据可视化工具")
    print("=" * 60)
    
    visualizer = DataVisualizer()
    
    if args.batch:
        csv_files = glob.glob("*.csv")
        if not csv_files:
            print("❌ 当前目录下没有找到CSV文件")
            return
        
        print(f"\n📂 找到 {len(csv_files)} 个CSV文件，开始批量处理...\n")
        
        for csv_file in csv_files:
            print(f"\n处理: {csv_file}")
            visualizer.process_file(csv_file, args.output)
        
    else:
        csv_path = args.csv
        if not csv_path:
            candidates = glob.glob("*.csv")
            if not candidates:
                print("❌ 请指定CSV文件路径或使用--batch批量处理")
                return
            csv_path = candidates[0]
            print(f"📂 自动选择文件: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"❌ 文件不存在: {csv_path}")
            return
        
        visualizer.process_file(csv_path, args.output)

if __name__ == "__main__":
    main()