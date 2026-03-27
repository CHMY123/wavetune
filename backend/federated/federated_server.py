import torch
import flwr as fl
import argparse
import os
import sys
import json
from datetime import datetime

# 添加backend目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.models import MultimodalFatigueModel

def get_parameters():
    """获取初始模型参数"""
    model = MultimodalFatigueModel(num_classes=3)
    if os.path.exists("federated_global_model.pth"):
        model.load_state_dict(torch.load("federated_global_model.pth"))
    return [val.cpu().numpy() for val in model.state_dict().values()]

def fit_round(server_round, parameters, config):
    """每轮训练的聚合逻辑"""
    print(f"\n📊 第 {server_round} 轮训练开始")
    print(f"   收到 {len(parameters)} 个客户端的模型更新")
    
    # 提取客户端模型参数和权重
    client_params = []
    client_weights = []
    
    for param in parameters:
        client_params.append(param.parameters)
        client_weights.append(param.num_examples)
    
    # 聚合参数（FedAvg）
    aggregated_params = aggregate_parameters(client_params, client_weights)
    
    # 保存模型
    model = MultimodalFatigueModel(num_classes=3)
    state_dict = {}
    for k, v in zip(model.state_dict().keys(), aggregated_params):
        state_dict[k] = torch.tensor(v)
    model.load_state_dict(state_dict)
    torch.save(model.state_dict(), "federated_global_model.pth")
    print("   模型已保存至: federated_global_model.pth")
    
    # 记录历史
    history = []
    if os.path.exists("federated_history.json"):
        with open("federated_history.json", "r") as f:
            history = json.load(f)
    
    history.append({
        "round": server_round,
        "clients": len(parameters),
        "timestamp": datetime.now().isoformat()
    })
    
    with open("federated_history.json", "w") as f:
        json.dump(history, f, indent=2)
    
    return aggregated_params, {"round": server_round, "clients": len(parameters)}

def evaluate_round(server_round, parameters, config):
    """每轮评估的聚合逻辑"""
    print(f"\n📋 第 {server_round} 轮评估开始")
    print(f"   收到 {len(parameters)} 个客户端的评估结果")
    
    total_loss = 0
    total_accuracy = 0
    total_samples = 0
    
    for param in parameters:
        total_loss += param.loss * param.num_examples
        total_accuracy += param.accuracy * param.num_examples
        total_samples += param.num_examples
    
    if total_samples > 0:
        avg_loss = total_loss / total_samples
        avg_accuracy = total_accuracy / total_samples
        print(f"   平均损失: {avg_loss:.4f}, 平均准确率: {avg_accuracy:.4f}")
    
    return 0.0, {"round": server_round, "clients": len(parameters)}

def aggregate_parameters(client_params, client_weights):
    """FedAvg 聚合策略"""
    total_weight = sum(client_weights)
    weighted_params = []
    
    for params, weight in zip(client_params, client_weights):
        weighted = [w * (weight / total_weight) for w in params]
        weighted_params.append(weighted)
    
    aggregated = []
    for param_idx in range(len(weighted_params[0])):
        param_sum = sum(params[param_idx] for params in weighted_params)
        aggregated.append(param_sum)
    
    return aggregated

def main():
    parser = argparse.ArgumentParser(description="联邦学习服务器")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8090, help="服务器端口")
    parser.add_argument("--clients", type=int, default=5, help="客户端数量")
    parser.add_argument("--rounds", type=int, default=10, help="训练轮数")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 联邦学习服务器启动")
    print("=" * 60)
    print(f"服务器地址: {args.host}:{args.port}")
    print(f"客户端数量: {args.clients}")
    print(f"训练轮数: {args.rounds}")
    
    # 配置 Flower 服务器策略
    strategy = fl.server.strategy.FedAvg(
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