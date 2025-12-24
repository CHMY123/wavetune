# WaveTune 系统启动指南

> 推荐 Python 版本：Python 3.11.14（下面的步骤基于该版本）

## 系统概述

WaveTune 是一个基于 Vue 3 + FastAPI 的脑疲劳检测与音乐干预系统，包含前端可视化界面和后端API服务。

## 项目结构

```
wavetune/
├── src/                    # Vue 3 前端项目
│   ├── views/             # 页面组件
│   ├── components/        # 通用组件
│   ├── router/           # 路由配置
│   └── assets/           # 静态资源
├── backend/              # FastAPI 后端项目
│   ├── main.py          # 主入口文件
│   ├── models/          # 数据模型
│   ├── routers/         # API路由
│   ├── schemas/         # 数据验证
│   └── config/          # 配置文件
├── WaveTune_API接口文档.md    # API接口文档
└── 大创项目后端功能实现提示词文档.md  # 功能实现文档
```

## 启动步骤

### 第一步：启动后端服务

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **创建并激活虚拟环境（推荐在项目根目录执行）**

   Windows (PowerShell)：

   ```powershell
   # 在项目根目录执行一次
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Windows (cmd)：

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

   macOS / Linux：

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **安装 Python 依赖**

   - 本项目在项目根目录提供了 `requirements.txt`（包含后端依赖及检测模型相关库）。

   ```bash
   pip install -r requirements.txt
   ```

   - 注意：`torch` 的 GPU 版本需要根据操作系统与 CUDA 版本单独安装。
     例如仅安装 CPU 版本的常见方法：

   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **初始化数据库**
   ```bash
   python init_db.py
   ```

4. **启动后端服务**
   ```bash
   python start.py
   ```

   或者使用 uvicorn：
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **验证后端服务**
   - 访问 http://localhost:8000 查看服务状态
   - 访问 http://localhost:8000/docs 查看API文档
   - 访问 http://localhost:8000/health 进行健康检查

### 第二步：启动前端服务

1. **进入项目根目录**
   ```bash
   cd ..  # 回到项目根目录
   ```

2. **安装前端依赖**
   ```bash
   npm install
   ```

3. **启动前端开发服务器**
   ```bash
   npm run serve
   ```

4. **访问前端应用**
   - 访问 http://localhost:8080 查看前端界面

### 第三步：测试系统功能

1. **运行API测试脚本**
   ```bash
   cd backend
   python test_api.py
   ```

2. **手动测试前端功能**
   - 首页：查看系统统计和功能导航
   - 个人中心：查看用户信息和提交反馈
   - 音乐推荐：查看基于疲劳等级的音乐推荐
   - 检测结果：查看脑疲劳检测数据展示
   - 信号监测：查看多模态生理信号监测
   - 联邦学习：查看联邦学习参与状态

## 功能模块说明

### 前端功能模块

1. **首页 (HomeView)**
   - 系统介绍和功能导航
   - 系统统计数据展示
   - 联邦学习状态概览
   - 快速操作入口

2. **个人中心 (UserFeedbackView)**
   - 用户信息展示和编辑
   - 头像上传功能
   - 用户反馈提交
   - 历史反馈查询

3. **音乐推荐 (MusicRecommendationView)**
   - 基于疲劳等级的音乐推荐
   - 音乐卡片展示
   - 推荐理由说明
   - 匹配度显示

4. **检测结果 (FatigueResultView)**
   - 疲劳等级展示
   - 关键指标数值
   - 趋势图表占位
   - 详细指标表格

5. **信号监测 (SignalMonitorView)**
   - 多模态信号实时监测
   - 波形图展示
   - 监测时间轴
   - 数据导出功能

6. **联邦学习 (FederatedStatusView)**
   - 参与设备统计
   - 训练进度展示
   - 隐私保护说明
   - 参与状态管理

### 后端API模块

1. **系统统计接口**
   - 获取首页统计数据
   - 支持检测次数、干预次数、参与设备、模型准确率

2. **用户管理接口**
   - 用户信息查询和更新
   - 头像上传功能
   - 统计次数更新

3. **反馈管理接口**
   - 反馈提交功能
   - 历史反馈查询
   - 分页支持

4. **音乐推荐接口**
   - 基于疲劳等级的音乐筛选
   - 音乐详情查询
   - 多条件筛选支持

5. **场景配置接口**
   - 场景列表查询
   - 场景创建和删除
   - 场景应用功能

## 数据库说明

### 数据表结构

1. **user 表** - 用户信息
2. **feedback 表** - 用户反馈
3. **music 表** - 音乐数据
4. **scene 表** - 场景配置
5. **system_stats 表** - 系统统计

### 初始数据

系统初始化时会自动创建：
- 测试用户：李同学 (ID: 1, 学号: 2022001001)
- 8条音乐数据（覆盖不同疲劳等级和音乐类型）
- 3个系统默认场景
- 系统统计数据

## 配置说明

### 后端配置

- **数据库**: 默认使用 MySQL
- **端口**: 8000
- **CORS**: 允许 localhost:5173 和 localhost:8080 访问
- **文件上传**: 支持头像上传到 static/avatar/ 目录

### 前端配置

- **开发端口**: 8080
- **API基础URL**: http://localhost:8000/api
- **路由模式**: Hash 模式

## 常见问题

### 1. 后端启动失败

**问题**: 端口被占用
**解决**: 修改端口或关闭占用端口的进程
```bash
# 查看端口占用
netstat -ano | findstr :8000
# 杀死进程
taskkill /PID <进程ID> /F
```

### 2. 数据库连接失败

**问题**: SQLite 文件权限问题
**解决**: 确保 backend 目录有写入权限

### 3. 前端无法连接后端

**问题**: CORS 跨域问题
**解决**: 检查后端 CORS 配置，确保允许前端域名访问

### 4. 文件上传失败

**问题**: 静态文件目录不存在
**解决**: 确保 static/avatar/ 目录存在且有写入权限

## 开发建议

1. **后端开发**
   - 使用 FastAPI 自动生成的文档进行接口测试
   - 修改模型后需要重新初始化数据库
   - 日志文件保存在 logs/app.log

2. **前端开发**
   - 使用 Vue DevTools 进行调试
   - 修改路由后检查导航菜单
   - 注意 Element Plus 组件的响应式设计

3. **集成测试**
   - 先启动后端服务，再启动前端
   - 使用浏览器开发者工具查看网络请求
   - 检查控制台错误信息

## 部署说明

### 开发环境
- 后端：http://localhost:8000
- 前端：http://localhost:8080
- 数据库：SQLite

### 生产环境建议
- 使用 Nginx 作为反向代理
- 使用 Gunicorn 运行 FastAPI
- 使用 MySQL 作为生产数据库
- 配置 HTTPS 证书
- 设置环境变量和配置文件

## 技术支持

如有问题，请参考：
1. API接口文档：`WaveTune_API接口文档.md`
2. 功能实现文档：`大创项目后端功能实现提示词文档.md`
3. 后端README：`backend/README.md`
4. FastAPI官方文档：https://fastapi.tiangolo.com/
5. Vue 3官方文档：https://vuejs.org/




