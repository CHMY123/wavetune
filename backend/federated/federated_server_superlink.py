import torch
import flwr as fl
import argparse
import os
import sys
import json
from datetime import datetime
import time

# 添加backend目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.models import MultimodalFatigueModel

# 获取项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 模型保存路径
MODEL_PATH = os.path.join(PROJECT_ROOT, "federated_global_model.pth")
# 历史记录路径
HISTORY_PATH = os.path.join(PROJECT_ROOT, "federated_history.json")

def get_parameters():
    """获取初始模型参数"""
    model = MultimodalFatigueModel(num_classes=3)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH))
        print(f"✅ 加载了现有模型: {MODEL_PATH}")
    else:
        print("⚠️  未找到现有模型，使用新模型")
    return [val.cpu().numpy() for val in model.state_dict().values()]

class CustomFedAvgStrategy(fl.server.strategy.FedAvg):
    """自定义 FedAvg 策略"""
    def aggregate_fit(
        self,
        server_round,
        results,
        failures,
    ):
        """聚合客户端模型参数"""
        start_time = time.time()
        print(f"\n📊 第 {server_round} 轮训练开始")
        print(f"   收到 {len(results)} 个客户端的模型更新")
        print(f"   失败: {len(failures)}")
        
        # 调用父类的聚合方法
        aggregated_parameters, metrics = super().aggregate_fit(server_round, results, failures)
        
        # 保存模型
        try:
            # 转换聚合参数为ndarrays
            if isinstance(aggregated_parameters, tuple):
                # 对于旧版本的Flower
                aggregated_params = aggregated_parameters[0]
            else:
                # 对于新版本的Flower
                try:
                    aggregated_params = fl.common.parameters_to_ndarrays(aggregated_parameters)
                except:
                    try:
                        aggregated_params = aggregated_parameters.ndarrays
                    except:
                        aggregated_params = aggregated_parameters
            
            # 保存模型
            model = MultimodalFatigueModel(num_classes=3)
            state_dict = {}
            for k, v in zip(model.state_dict().keys(), aggregated_params):
                state_dict[k] = torch.tensor(v)
            model.load_state_dict(state_dict)
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"   模型已保存至: {MODEL_PATH}")
            
            # 记录历史
            history = []
            if os.path.exists(HISTORY_PATH):
                with open(HISTORY_PATH, "r") as f:
                    history = json.load(f)
            
            # 计算轮次时间
            round_time = time.time() - start_time
            
            history.append({
                "round": server_round,
                "clients": len(results),
                "time": round(round_time, 2),
                "timestamp": datetime.now().isoformat()
            })
            
            with open(HISTORY_PATH, "w") as f:
                json.dump(history, f, indent=2)
            print(f"   历史记录已保存至: {HISTORY_PATH}")
            print(f"   轮次耗时: {round_time:.2f} 秒")
        except Exception as e:
            print(f"   保存模型时出错: {e}")
        
        return aggregated_parameters, metrics

def main():
    parser = argparse.ArgumentParser(description="SuperLink 联邦学习服务器")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8090, help="服务器端口")
    parser.add_argument("--clients", type=int, default=1, help="客户端数量")
    parser.add_argument("--rounds", type=int, default=1, help="训练轮数")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 联邦学习服务器 【标准兼容版】 启动")
    print("=" * 60)
    print(f"服务器地址: {args.host}:{args.port}")
    print(f"所需客户端数量: {args.clients}")
    print(f"训练轮数: {args.rounds}")
    print(f"模型保存路径: {MODEL_PATH}")
    print(f"历史记录路径: {HISTORY_PATH}")
    print()
    print("✅ 服务器已准备就绪，等待客户端连接...")
    
    # 配置 Flower 服务器策略
    strategy = CustomFedAvgStrategy(
        min_fit_clients=args.clients,
        min_evaluate_clients=args.clients,
        min_available_clients=args.clients,
        initial_parameters=fl.common.ndarrays_to_parameters(get_parameters())
    )
    
    # 启动服务器
    fl.server.start_server(
        server_address=f"{args.host}:{args.port}",
        config=fl.server.ServerConfig(num_rounds=args.rounds),
        strategy=strategy
    )

if __name__ == "__main__":
    main()