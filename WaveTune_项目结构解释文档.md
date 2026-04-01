# WaveTune 项目结构解释文档

## 项目概述

WaveTune 是一个基于 Vue 3 + FastAPI 的脑疲劳检测与音乐干预系统。本项目采用前后端分离架构，提供用户管理、脑疲劳检测、音乐推荐、联邦学习等功能。

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表库**: ECharts
- **样式**: CSS3 + Element Plus 主题定制

### 后端
- **框架**: FastAPI (Python 3.11.14)
- **数据库**: TiDB Cloud (MySQL 兼容)
- **ORM**: SQLAlchemy 2.x
- **认证**: JWT (JSON Web Token)
- **数据验证**: Pydantic
- **机器学习**: PyTorch (用于联邦学习)
- **云存储**: 缤纷云 S3 兼容存储

## 目录结构

```
wavetune/
├── src/                          # 前端源代码
│   ├── assets/                   # 静态资源
│   │   ├── css/                  # 全局样式文件
│   │   │   ├── variables.css     # CSS变量定义
│   │   │   ├── animations.css    # 动画效果
│   │   │   └── global.css        # 全局样式
│   │   ├── images/               # 图片资源
│   │   │   ├── logo.png          # 应用Logo
│   │   │   ├── default-avatar.png # 默认头像
│   │   │   └── backgrounds/      # 背景图片
│   │   └── audio/                # 音频资源
│   │       ├── notification.mp3  # 提示音
│   │       └── sounds/           # 音效文件
│   ├── components/               # 公共组件
│   │   ├── common/               # 通用组件
│   │   │   ├── LoadingSpinner.vue    # 加载动画
│   │   │   ├── EmptyState.vue        # 空状态
│   │   │   └── ErrorBoundary.vue     # 错误边界
│   │   ├── layout/               # 布局组件
│   │   │   ├── MainLayout.vue    # 主布局
│   │   │   ├── AdminLayout.vue   # 管理后台布局
│   │   │   └── Sidebar.vue       # 侧边栏
│   │   └── charts/               # 图表组件
│   │       ├── LineChart.vue     # 折线图
│   │       ├── BarChart.vue      # 柱状图
│   │       └── PieChart.vue      # 饼图
│   ├── views/                    # 页面视图
│   │   ├── HomeView.vue          # 首页
│   │   ├── LoginView.vue         # 登录页
│   │   ├── RegisterView.vue      # 注册页
│   │   ├── DetectionView.vue     # 疲劳检测页
│   │   ├── InterventionView.vue  # 音乐干预页
│   │   ├── MusicRecommendationView.vue  # 音乐推荐页
│   │   ├── FederatedContributeView.vue  # 联邦学习贡献页
│   │   ├── SignalMonitorView.vue        # 信号监测页
│   │   ├── UserCenterView.vue           # 用户中心页
│   │   ├── TwoBackView.vue              # 2-back实验页
│   │   ├── FeedbackView.vue             # 反馈页面
│   │   └── admin/                       # 管理后台页面
│   │       ├── Dashboard.vue            # 仪表盘
│   │       ├── UserManagement.vue       # 用户管理
│   │       ├── MusicManagement.vue      # 音乐管理
│   │       ├── SystemStats.vue          # 系统统计
│   │       └── FeedbackManagement.vue   # 反馈管理
│   ├── router/                   # 路由配置
│   │   └── index.js              # 路由定义
│   ├── stores/                   # Pinia状态管理
│   │   ├── user.js               # 用户状态
│   │   ├── music.js              # 音乐状态
│   │   ├── detection.js          # 检测状态
│   │   └── settings.js           # 设置状态
│   ├── api/                      # API接口封装
│   │   ├── auth.js               # 认证相关API
│   │   ├── user.js               # 用户相关API
│   │   ├── detection.js          # 检测相关API
│   │   ├── music.js              # 音乐相关API
│   │   ├── federated.js          # 联邦学习API
│   │   └── feedback.js           # 反馈相关API
│   ├── utils/                    # 工具函数
│   │   ├── request.js            # Axios封装
│   │   ├── storage.js            # 本地存储封装
│   │   ├── format.js             # 格式化工具
│   │   └── validators.js         # 表单验证
│   ├── composables/              # Vue组合式函数
│   │   ├── useAuth.js            # 认证逻辑
│   │   ├── useDetection.js       # 检测逻辑
│   │   ├── useMusic.js           # 音乐逻辑
│   │   └── useFederated.js       # 联邦学习逻辑
│   ├── constants/                # 常量定义
│   │   ├── api.js                # API常量
│   │   ├── enums.js              # 枚举值
│   │   └── config.js             # 配置常量
│   ├── App.vue                   # 根组件
│   └── main.js                   # 入口文件
├── backend/                      # 后端源代码
│   ├── routers/                  # API路由
│   │   ├── auth.py               # 认证路由
│   │   ├── user.py               # 用户路由
│   │   ├── detection.py          # 检测路由
│   │   ├── music.py              # 音乐路由
│   │   ├── federated.py          # 联邦学习路由
│   │   ├── feedback.py           # 反馈路由
│   │   ├── stats.py              # 统计路由
│   │   └── admin.py              # 管理后台路由
│   ├── models/                   # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── detection.py          # 检测模型
│   │   ├── music.py              # 音乐模型
│   │   ├── federated.py          # 联邦学习模型
│   │   └── feedback.py           # 反馈模型
│   ├── schemas/                  # Pydantic模式
│   │   ├── user.py               # 用户模式
│   │   ├── detection.py          # 检测模式
│   │   ├── music.py              # 音乐模式
│   │   └── federated.py          # 联邦学习模式
│   ├── services/                 # 业务逻辑
│   │   ├── auth_service.py       # 认证服务
│   │   ├── user_service.py       # 用户服务
│   │   ├── detection_service.py  # 检测服务
│   │   ├── music_service.py      # 音乐服务
│   │   └── federated_service.py  # 联邦学习服务
│   ├── utils/                    # 工具函数
│   │   ├── database.py           # 数据库连接
│   │   ├── security.py           # 安全工具
│   │   ├── s3_helper.py          # 云存储工具
│   │   └── email.py              # 邮件服务
│   ├── database/                 # 数据库相关
│   │   └── create_tables.sql     # 建表SQL
│   ├── ml/                       # 机器学习模块
│   │   ├── models/               # 模型定义
│   │   │   ├── fatigue_detector.py   # 疲劳检测模型
│   │   │   └── federated_model.py    # 联邦学习模型
│   │   ├── training/             # 训练相关
│   │   │   ├── trainer.py        # 训练器
│   │   │   └── data_loader.py    # 数据加载器
│   │   └── utils/                # ML工具
│   │       ├── preprocessing.py  # 数据预处理
│   │       └── metrics.py        # 评估指标
│   ├── config.py                 # 配置文件
│   ├── main.py                   # 应用入口
│   └── requirements.txt          # Python依赖
├── public/                       # 静态资源
│   ├── favicon.ico               # 网站图标
│   └── index.html                # HTML模板
├── nginx.conf                    # Nginx配置
├── vue.config.js                 # Vue配置
├── vite.config.js                # Vite配置
├── package.json                  # Node依赖
├── .env                          # 环境变量
├── .env.development              # 开发环境变量
├── .env.production               # 生产环境变量
├── .gitignore                    # Git忽略文件
├── jsconfig.json                 # JS配置
└── README.md                     # 项目说明
```

## 核心模块说明

### 前端核心模块

#### 1. 用户认证模块 (Auth)
- **文件**: `src/views/LoginView.vue`, `src/views/RegisterView.vue`
- **功能**: 用户登录、注册、密码重置
- **状态管理**: `src/stores/user.js`
- **API**: `src/api/auth.js`

#### 2. 疲劳检测模块 (Detection)
- **文件**: `src/views/DetectionView.vue`
- **功能**: EEG信号采集、疲劳状态检测、结果展示
- **状态管理**: `src/stores/detection.js`
- **API**: `src/api/detection.js`

#### 3. 音乐干预模块 (Intervention)
- **文件**: `src/views/InterventionView.vue`, `src/views/MusicRecommendationView.vue`
- **功能**: 音乐播放、疲劳干预、推荐算法
- **状态管理**: `src/stores/music.js`
- **API**: `src/api/music.js`

#### 4. 联邦学习模块 (Federated Learning)
- **文件**: `src/views/FederatedContributeView.vue`
- **功能**: 数据贡献、模型训练、进度监控
- **状态管理**: 使用本地存储持久化训练状态
- **API**: `src/api/federated.js`

#### 5. 信号监测模块 (Signal Monitor)
- **文件**: `src/views/SignalMonitorView.vue`
- **功能**: EEG信号可视化、实时监测、CSV文件上传分析
- **API**: `src/api/detection.js`

### 后端核心模块

#### 1. 认证服务 (Auth Service)
- **文件**: `backend/routers/auth.py`, `backend/services/auth_service.py`
- **功能**: JWT认证、用户注册登录、会话管理
- **安全**: 密码哈希、Token刷新、权限验证

#### 2. 检测服务 (Detection Service)
- **文件**: `backend/routers/detection.py`, `backend/services/detection_service.py`
- **功能**: 疲劳检测算法、信号处理、结果分析
- **ML模块**: `backend/ml/models/fatigue_detector.py`

#### 3. 联邦学习服务 (Federated Service)
- **文件**: `backend/routers/federated.py`, `backend/services/federated_service.py`
- **功能**: 模型训练、参数聚合、设备管理
- **ML模块**: `backend/ml/models/federated_model.py`
- **云存储**: 使用缤纷云S3存储训练数据

#### 4. 音乐服务 (Music Service)
- **文件**: `backend/routers/music.py`, `backend/services/music_service.py`
- **功能**: 音乐库管理、推荐算法、播放统计

#### 5. 云存储服务 (Cloud Storage)
- **文件**: `backend/utils/s3_helper.py`
- **功能**: 文件上传下载、预签名URL生成
- **存储桶**: 缤纷云 wavetune 存储桶

## 数据流说明

### 1. 用户认证流程
```
用户输入 → 前端验证 → API请求 → 后端验证 → JWT生成 → 返回Token → 前端存储 → 路由跳转
```

### 2. 疲劳检测流程
```
采集数据 → 前端展示 → 发送检测请求 → 后端处理 → ML模型推理 → 返回结果 → 前端展示
```

### 3. 联邦学习流程
```
选择文件 → 上传至云存储 → 后端下载 → 数据预处理 → 模型训练 → 进度更新 → 结果返回
```

### 4. 信号监测流程
```
上传CSV → 云存储 → 后端下载 → 信号解析 → 可视化数据 → 疲劳检测 → 结果展示
```

## 配置文件说明

### 前端配置

#### vite.config.js
- 开发服务器配置
- 代理设置
- 构建优化
- 插件配置

#### vue.config.js
- 允许的内网穿透地址
- 构建输出配置

### 后端配置

#### backend/config.py
- 数据库连接配置
- JWT密钥配置
- 云存储配置
- 邮件服务配置

#### backend/.env
- 环境变量
- 敏感信息（数据库密码、API密钥等）

## 开发规范

### 前端规范
- 使用 Composition API
- 组件名使用 PascalCase
- 文件名使用 camelCase
- 使用 Pinia 进行状态管理
- API 请求统一封装

### 后端规范
- 使用 FastAPI 异步路由
- Pydantic 进行数据验证
- SQLAlchemy 2.x 进行数据库操作
- 统一响应格式
- 异常处理封装

## 部署说明

### 前端部署
1. 构建生产版本: `npm run build`
2. 输出目录: `dist/`
3. 使用 Nginx 或类似服务器托管

### 后端部署
1. 安装依赖: `pip install -r requirements.txt`
2. 配置环境变量
3. 启动服务: `uvicorn main:app --host 0.0.0.0 --port 8000`

### 数据库部署
- 使用 TiDB Cloud 托管服务
- 执行 `backend/database/create_tables.sql` 初始化表结构

## 注意事项

1. **环境变量**: 确保 `.env` 文件中的敏感信息不被提交到版本控制
2. **数据库连接**: 生产环境使用连接池管理
3. **文件上传**: 大文件使用分片上传
4. **跨域配置**: 开发环境配置代理，生产环境配置 CORS
5. **错误处理**: 统一错误处理和日志记录
