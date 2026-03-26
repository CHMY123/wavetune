# 联邦学习系统使用指南

## 🚀 快速开始

### 1. 准备数据

在 `data` 目录下创建客户端数据文件夹：

```bash
mkdir data\client1
data\client2
data\client3
```

将 CSV 数据文件复制到各个客户端目录：

```bash
copy "2025_10_27_15_11_59_fnris 洋1.csv" data\client1\
copy "2025_10_27_15_11_59_fnris 洋1.csv" data\client2\
copy "2025_10_27_15_11_59_fnris 洋1.csv" data\client3\
```

### 2. 启动服务器

**标准版服务器**：

```bash
python federated/federated_server.py --clients 3 --rounds 2 --port 8080
```

**SuperLink 服务器**（推荐，Flower 最新版本）：

```bash
python federated/federated_server_superlink.py --clients 3 --rounds 5 --port 8080
```

**使用 Flower CLI**（推荐，官方推荐方式）：

```bash
# 首先启动 SuperLink 服务器
flower-superlink --insecure --port 8080
```

### 3. 启动客户端

在多个终端中分别运行：

**标准版客户端**：

```bash
# 客户端1
python federated/federated_client.py --client-id 1 --data-path ./data/client1/ --server 127.0.0.1:8080

# 客户端2
python federated/federated_client.py --client-id 2 --data-path ./data/client2/ --server 127.0.0.1:8080

# 客户端3
python federated/federated_client.py --client-id 3 --data-path ./data/client3/ --server 127.0.0.1:8080
```

**SuperNode 客户端**（推荐，Flower 最新版本）：

```bash
# 客户端1
python federated/federated_client_supernode.py --client-id 1 --data-path ./data/client1/ --server 127.0.0.1:8080 --sample-rate 0.3

# 客户端2
python federated/federated_client_supernode.py --client-id 2 --data-path ./data/client2/ --server 127.0.0.1:8080 --sample-rate 0.3

# 客户端3
python federated/federated_client_supernode.py --client-id 3 --data-path ./data/client3/ --server 127.0.0.1:8080 --sample-rate 0.3
```

**使用 Flower CLI**（官方推荐方式）：

```bash
# 客户端1
flower-supernode --insecure --superlink='127.0.0.1:8080'

# 客户端2
flower-supernode --insecure --superlink='127.0.0.1:8080'

# 客户端3
flower-supernode --insecure --superlink='127.0.0.1:8080'
```

## ⚡ SuperNode 客户端特性

### 核心优化

1. **数据采样**：通过 `--sample-rate` 参数控制训练数据采样率，默认 30%
2. **GPU 加速**：自动检测并使用 GPU 进行训练
3. **数据缓存**：缓存处理后的数据，避免重复处理
4. **批量优化**：默认批量大小为 32
5. **早停机制**：当损失不再下降时自动停止训练
6. **进度条**：实时显示训练和评估进度
7. **并行处理**：使用批量并行处理加速训练

### 服务器特性

1. **SuperLink 架构**：支持 Flower 最新的 SuperLink 架构
2. **性能监控**：记录每轮训练的耗时
3. **历史记录**：保存详细的训练历史
4. **参数优化**：默认配置更适合快速训练

## 🎯 性能对比

| 版本 | 训练速度 | 内存使用 | 准确率 | 适用场景 |
|------|---------|---------|--------|----------|
| 标准版 | 较慢 | 高 | 高 | 数据量小，追求精度 |
| SuperNode版 | 快3-5倍 | 低 | 中等 | 大规模部署，生产环境 |

## 📊 训练结果

训练完成后，会生成以下文件：

- `federated_global_model.pth` - 全局模型
- `federated_history.json` - 训练历史

## 🔧 调参建议

### SuperNode 客户端参数

- `--sample-rate`：数据采样率，推荐 0.2-0.5
- `--batch-size`：批量大小，推荐 32-64
- `--epochs`：本地训练轮数，推荐 1-3
- `--no-gpu`：禁用 GPU（如果内存不足）

### 服务器参数

- `--clients`：客户端数量，根据实际设备数量设置
- `--rounds`：训练轮数，推荐 5-10
- `--port`：服务器端口，默认 8080

## 🚨 常见问题

### 1. 内存不足

**解决方案**：
- 降低 `--sample-rate` 值
- 减小 `--batch-size`
- 使用 `--no-gpu` 禁用 GPU

### 2. 训练速度慢

**解决方案**：
- 使用 SuperNode 客户端
- 增加 `--sample-rate` 值
- 确保使用 GPU 加速
- 使用 SuperLink 服务器

### 3. 准确率低

**解决方案**：
- 增加 `--sample-rate` 值
- 增加 `--epochs` 训练轮数
- 增加服务器 `--rounds` 轮数

### 4. Flower 版本兼容性

**解决方案**：
- 使用 SuperLink 服务器和 SuperNode 客户端
- 运行 `pip install --upgrade flwr` 更新 Flower
- 参考官方文档：https://flower.dev/docs/

## 📈 预期输出

**SuperLink 服务器**：
```
============================================================
🚀 SuperLink 联邦学习服务器启动
============================================================
服务器地址: 0.0.0.0:8080
客户端数量: 3
训练轮数: 5
📡 启动 SuperLink 服务器...
   注意: 请在新的终端中运行客户端
INFO :      Starting Flower server, config: num_rounds=5, no round_timeout
INFO :      Flower ECE: gRPC server running (5 rounds), SSL is disabled
```

**SuperNode 客户端**：
```
============================================================
🚀 SuperNode 联邦学习客户端 1 启动
============================================================
服务器地址: 127.0.0.1:8080
数据路径: ./data/client1/
批量大小: 32
本地训练轮数: 1
数据采样率: 0.3
使用GPU: True
使用设备: cuda
客户端 1 加载了 1 个数据文件
使用缓存的数据...
采样后的数据量: 443 / 1479

📈 客户端 1 Epoch 1/1
训练进度: 100%|██████████| 443/443 [00:10<00:00, 42.34batch/s, loss=1.1023, acc=0.3386]
✅ 客户端 1 Epoch 1 完成: 损失=1.1023, 准确率=0.3386

🏆 客户端 1 训练完成: 损失=1.1023, 准确率=0.3386
```

## 🎉 最佳实践

1. **快速验证**：使用 SuperNode 客户端，设置 `--sample-rate 0.1` 快速验证系统
2. **生产环境**：使用 SuperLink 服务器 + SuperNode 客户端，设置 `--sample-rate 0.5`
3. **资源受限**：使用 `--no-gpu --sample-rate 0.2` 减少资源消耗
4. **精度优先**：使用标准版客户端，完整训练所有数据
5. **大规模部署**：使用 Flower CLI 启动 SuperLink 服务器和 SuperNode 客户端

## 🔄 迁移到 SuperLink/SuperNode

如果您看到以下警告：

```
WARNING :   DEPRECATED FEATURE: flwr.server.start_server() is deprecated.
        Instead, use the `flower-superlink` CLI command to start a SuperLink as shown below:
                $ flower-superlink --insecure
```

或

```
WARNING :   DEPRECATED FEATURE: flwr.client.start_client() is deprecated.
        Instead, use the `flower-supernode` CLI command to start a SuperNode as shown below:
                $ flower-supernode --insecure --superlink='<IP>:<PORT>'
```

**解决方案**：
1. 安装最新版 Flower：`pip install --upgrade flwr`
2. 使用 `flower-superlink` CLI 启动服务器
3. 使用 `flower-supernode` CLI 启动客户端
4. 或者使用我们提供的 `federated_server_superlink.py` 和 `federated_client_supernode.py` 脚本

现在您的联邦学习系统已经准备就绪！