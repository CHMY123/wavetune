import numpy as np
import argparse
import glob
import os

def _load_csv(path: str):
    try:
        return np.loadtxt(path, delimiter=',').T
    except ValueError:
        return np.loadtxt(path).T

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default=None)
    args = parser.parse_args()

    csv_path = args.csv
    if not csv_path:
        candidates = glob.glob("*.csv")
        if not candidates:
            raise FileNotFoundError("当前目录未找到 .csv，请用 --csv 指定文件路径。")
        csv_path = candidates[0]

    csv_path = os.path.abspath(csv_path)
    data = _load_csv(csv_path)
    print(f"csv: {csv_path}")
    print("shape:", data.shape)
    label = data[-1].astype(int)
    nonzero = [int(i) for i in label[label != 0]]
    print("nonzero labels:", nonzero)
    print("unique nonzero labels:", sorted(set(nonzero)))

if __name__ == "__main__":
    main()

