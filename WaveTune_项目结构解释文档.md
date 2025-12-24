# WaveTune 项目结构解释文档

## 项目概述

WaveTune 是一个基于 Vue 3 + FastAPI 的脑疲劳检测与音乐干预系统，采用前后端分离架构，提供完整的用户认证、音乐推荐、场景配置、反馈管理等功能。

## 整体架构

```
WaveTune 系统架构
├── 前端层 (Vue 3 + Element Plus)
│   ├── 用户界面
│   ├── 状态管理 (Pinia)
│   └── 路由管理 (Vue Router)
├── 后端层 (FastAPI + SQLAlchemy)
│   ├── API 接口层
│   ├── 业务逻辑层
│   └── 数据访问层
└── 数据层 (MySQL/SQLite)
    ├── 用户数据
    ├── 音乐数据
    └── 系统数据
```

## 项目目录结构

```
wavetune/
├── src/                                    # Vue 3 前端项目
│   ├── components/                         # 组件目录
│   │   ├── business/                      # 业务组件
│   │   │   ├── fatigue/                   # 疲劳检测相关组件
│   │   │   ├── federated/                 # 联邦学习相关组件
│   │   │   └── music/                     # 音乐推荐相关组件
│   │   └── global/                        # 全局通用组件
│   │       ├── CardContainer.vue          # 卡片容器组件
│   │       ├── Footer.vue                 # 页脚组件
│   │       └── Navbar.vue                 # 导航栏组件
│   ├── views/                             # 页面视图
│   │   ├── federated/                     # 联邦学习页面
│   │   │   ├── FederatedDevicesView.vue   # 设备管理页面
│   │   │   ├── FederatedProgressView.vue  # 训练进度页面
│   │   │   └── FederatedStatusView.vue    # 参与状态页面
│   │   ├── AboutView.vue                  # 关于页面
│   │   ├── FatigueResultView.vue          # 疲劳检测结果页面
│   │   ├── HomeView.vue                   # 首页
│   │   ├── MusicRecommendationView.vue    # 音乐推荐页面
│   │   ├── SignalMonitorView.vue          # 信号监测页面
│   │   └── UserFeedbackView.vue           # 用户反馈页面
│   ├── router/                            # 路由配置
│   │   └── index.js                       # 路由定义
│   ├── store/                             # 状态管理
│   │   └── index.js                       # Pinia 状态定义
│   ├── assets/                            # 静态资源
│   │   ├── styles/                        # 样式文件
│   │   │   ├── breakpoints.scss           # 响应式断点
│   │   │   ├── element-variables.scss     # Element Plus 变量
│   │   │   └── global.scss                # 全局样式
│   │   └── logo.png                       # 项目 Logo
│   ├── utils/                             # 工具函数
│   │   └── errorHandler.js                # 错误处理工具
│   ├── App.vue                            # 根组件
│   └── main.js                            # 应用入口
├── backend/                               # FastAPI 后端项目
│   ├── main.py                            # 主入口文件
│   ├── start.py                           # 启动脚本
│   ├── init_db.py                         # 数据库初始化脚本
│   ├── test_api.py                        # API 测试脚本
│   ├── requirements.txt                   # Python 依赖
│   ├── env.example                        # 环境配置示例
│   ├── README.md                          # 后端说明文档
│   ├── config/                            # 配置文件
│   │   └── database.py                    # 数据库配置
│   ├── models/                            # 数据模型
│   │   ├── __init__.py                    # 模型初始化
│   │   ├── user.py                        # 用户模型
│   │   ├── feedback.py                    # 反馈模型
│   │   ├── music.py                       # 音乐模型
│   │   ├── scene.py                       # 场景模型
│   │   ├── system_stats.py                # 系统统计模型
│   │   ├── user_session.py                # 用户会话模型
│   │   ├── user_preference.py             # 用户偏好模型
│   │   └── operation_log.py               # 操作日志模型
│   ├── schemas/                           # 数据验证模型
│   │   ├── user.py                        # 用户验证模型
│   │   ├── feedback.py                    # 反馈验证模型
│   │   ├── scene.py                       # 场景验证模型
│   │   └── auth.py                        # 认证验证模型
│   ├── routers/                           # API 路由
│   │   ├── __init__.py                    # 路由初始化
│   │   ├── auth.py                        # 认证路由
│   │   ├── system.py                      # 系统统计路由
│   │   ├── user.py                        # 用户管理路由
│   │   ├── feedback.py                    # 反馈路由
│   │   ├── music.py                       # 音乐推荐路由
│   │   └── scene.py                       # 场景配置路由
│   ├── middleware/                        # 中间件
│   │   ├── __init__.py                    # 中间件初始化
│   │   └── auth.py                        # 认证中间件
│   ├── database/                          # 数据库脚本
│   │   └── create_tables.sql              # 建表 SQL 脚本
│   ├── static/                            # 静态文件目录
│   │   ├── avatar/                        # 用户头像
│   │   └── music_cover/                   # 音乐封面
│   └── logs/                              # 日志文件目录
├── public/                                # 公共静态资源
│   ├── favicon.ico                        # 网站图标
│   └── index.html                         # HTML 模板
├── 大创项目后端功能实现提示词文档（聚焦非核心检测类功能）.md  # 功能实现文档
├── WaveTune_API接口文档.md                # API 接口文档
├── WaveTune_数据库设计说明文档.md         # 数据库设计文档
├── WaveTune_启动指南.md                   # 启动指南
├── WaveTune_项目结构解释文档.md           # 项目结构文档
├── package.json                           # 前端依赖配置
├── vue.config.js                          # Vue 配置
├── babel.config.js                        # Babel 配置
├── jsconfig.json                          # JavaScript 配置
└── README.md                              # 项目说明文档
```

## 前端项目结构详解

### 1. 组件架构 (components/)

#### 全局组件 (global/)
- **CardContainer.vue**: 通用卡片容器组件，提供统一的卡片样式和布局
- **Navbar.vue**: 顶部导航栏组件，包含系统 Logo、导航菜单和用户头像
- **Footer.vue**: 页脚组件，显示版权信息和系统状态

#### 业务组件 (business/)
- **fatigue/**: 疲劳检测相关组件
- **federated/**: 联邦学习相关组件  
- **music/**: 音乐推荐相关组件

### 2. 页面视图 (views/)

#### 核心功能页面
- **HomeView.vue**: 系统首页，展示功能模块、统计数据、联邦学习状态
- **FatigueResultView.vue**: 脑疲劳检测结果页面，显示检测数据和图表
- **MusicRecommendationView.vue**: 音乐推荐页面，基于疲劳等级推荐音乐
- **SignalMonitorView.vue**: 信号监测页面，实时监测多模态生理信号
- **UserFeedbackView.vue**: 用户反馈页面，包含用户信息展示和反馈提交

#### 联邦学习页面 (federated/)
- **FederatedStatusView.vue**: 联邦学习参与状态页面
- **FederatedProgressView.vue**: 训练进度页面
- **FederatedDevicesView.vue**: 设备管理页面

### 3. 路由配置 (router/)

- **index.js**: 定义所有页面路由，包括路由守卫和懒加载配置

### 4. 状态管理 (store/)

- **index.js**: 使用 Pinia 进行全局状态管理，管理用户信息、系统状态等

### 5. 样式系统 (assets/styles/)

- **global.scss**: 全局样式定义，包含 CSS 变量、通用类等
- **element-variables.scss**: Element Plus 组件库的样式定制
- **breakpoints.scss**: 响应式设计的断点定义

## 后端项目结构详解

### 1. 应用入口 (main.py)

- **FastAPI 应用实例**: 创建 FastAPI 应用，配置中间件、路由、异常处理
- **CORS 配置**: 允许前端跨域访问
- **静态文件服务**: 提供头像、音乐封面等静态文件访问
- **全局异常处理**: 统一处理 HTTP 异常和通用异常

### 2. 数据模型层 (models/)

#### 核心业务模型
- **User**: 用户信息模型，包含认证、个人信息、统计数据
- **Feedback**: 用户反馈模型，支持反馈类型、评分、状态管理
- **Music**: 音乐数据模型，包含音乐信息、推荐参数、播放统计
- **Scene**: 场景配置模型，支持用户自定义场景和系统默认场景
- **SystemStats**: 系统统计模型，存储系统运行统计数据

#### 认证和会话模型
- **UserSession**: 用户会话模型，管理登录会话和令牌
- **UserPreference**: 用户偏好模型，存储个性化设置
- **OperationLog**: 操作日志模型，记录系统操作和审计信息

### 3. 数据验证层 (schemas/)

使用 Pydantic 进行请求参数验证：
- **auth.py**: 认证相关验证（注册、登录、密码修改等）
- **user.py**: 用户信息验证
- **feedback.py**: 反馈数据验证
- **scene.py**: 场景配置验证

### 4. API 路由层 (routers/)

#### 认证路由 (auth.py)
- `POST /api/auth/register`: 用户注册
- `POST /api/auth/login`: 用户登录
- `POST /api/auth/logout`: 用户登出
- `POST /api/auth/change-password`: 修改密码
- `GET /api/auth/profile`: 获取用户资料
- `PUT /api/auth/profile`: 更新用户资料
- `PUT /api/auth/preference`: 更新用户偏好
- `GET /api/auth/sessions`: 获取用户会话列表
- `DELETE /api/auth/session/{id}`: 撤销会话

#### 系统统计路由 (system.py)
- `GET /api/system/stats`: 获取系统统计数据

#### 用户管理路由 (user.py)
- `GET /api/user/info`: 获取用户信息
- `PUT /api/user/update`: 更新用户信息
- `POST /api/user/avatar/upload`: 上传用户头像
- `PUT /api/user/count/update`: 更新用户统计次数

#### 反馈管理路由 (feedback.py)
- `POST /api/feedback/submit`: 提交用户反馈
- `GET /api/feedback/history`: 查询历史反馈

#### 音乐推荐路由 (music.py)
- `GET /api/music/recommend`: 获取音乐推荐列表
- `GET /api/music/detail`: 获取音乐详情

#### 场景配置路由 (scene.py)
- `GET /api/scene/list`: 获取场景列表
- `POST /api/scene/create`: 创建场景
- `GET /api/scene/apply`: 应用场景
- `DELETE /api/scene/delete`: 删除场景

### 5. 中间件层 (middleware/)

#### 认证中间件 (auth.py)
- **AuthManager**: 认证管理器，处理用户身份验证
- **get_current_user**: 获取当前用户（必需认证）
- **get_current_user_optional**: 获取当前用户（可选认证）
- **require_auth**: 要求认证的依赖注入
- **require_admin**: 要求管理员权限的依赖注入

### 6. 配置层 (config/)

#### 数据库配置 (database.py)
- **数据库连接**: 支持 SQLite 和 MySQL
- **会话管理**: SQLAlchemy 会话工厂
- **连接池**: 数据库连接池配置

### 7. 数据库脚本 (database/)

#### 建表脚本 (create_tables.sql)
- 完整的数据库表结构定义
- 索引和外键约束
- 初始数据插入
- 支持 MySQL 和 SQLite

## 数据流架构

### 1. 用户认证流程

```
用户登录 → 验证凭据 → 创建会话 → 返回令牌 → 前端存储令牌
```

### 2. API 请求流程

```
前端请求 → 认证中间件 → 路由处理 → 业务逻辑 → 数据库操作 → 返回响应
```

### 3. 数据持久化流程

```
业务数据 → 数据验证 → 数据模型 → SQLAlchemy ORM → 数据库存储
```

## 技术栈说明

### 前端技术栈
- **Vue 3**: 渐进式 JavaScript 框架
- **Element Plus**: Vue 3 组件库
- **Pinia**: Vue 3 状态管理
- **Vue Router**: Vue 3 路由管理
- **SCSS**: CSS 预处理器
- **ECharts**: 数据可视化图表库

### 后端技术栈
- **FastAPI**: 现代、快速的 Python Web 框架
- **SQLAlchemy**: Python SQL 工具包和对象关系映射
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI 服务器
- **Python-multipart**: 文件上传支持

### 数据库技术
- **MySQL**: 生产环境关系型数据库
- **SQLite**: 开发环境轻量级数据库
- **数据库连接池**: 提高数据库访问性能

## 安全机制

### 1. 认证安全
- **密码加密**: 使用 PBKDF2 算法加密存储密码
- **会话管理**: 基于令牌的会话管理，支持过期控制
- **设备绑定**: 记录登录设备信息，支持多设备管理

### 2. 数据安全
- **参数验证**: 使用 Pydantic 严格验证请求参数
- **SQL 注入防护**: 使用 ORM 防止 SQL 注入攻击
- **CORS 配置**: 限制跨域访问来源

### 3. 操作审计
- **操作日志**: 记录所有重要操作和访问日志
- **错误追踪**: 详细的错误日志和异常处理
- **性能监控**: 记录请求执行时间和性能指标

## 部署架构

### 开发环境
```
前端 (Vue Dev Server) ←→ 后端 (FastAPI) ←→ 数据库 (SQLite)
```

### 生产环境建议
```
前端 (Nginx) ←→ 后端 (Gunicorn + FastAPI) ←→ 数据库 (MySQL)
```

## 扩展性设计

### 1. 水平扩展
- **无状态设计**: 后端服务无状态，支持负载均衡
- **数据库分离**: 支持读写分离和分库分表
- **缓存层**: 可集成 Redis 缓存

### 2. 功能扩展
- **插件化架构**: 支持功能模块插件化
- **API 版本控制**: 支持 API 版本管理
- **微服务拆分**: 可拆分为多个微服务

### 3. 数据扩展
- **数据迁移**: 支持数据库结构升级
- **数据备份**: 完整的备份和恢复机制
- **数据分析**: 支持数据分析和报表功能

## 开发规范

### 1. 代码规范
- **Python**: 遵循 PEP 8 编码规范
- **JavaScript**: 使用 ESLint 代码检查
- **Git**: 使用语义化提交信息

### 2. 文档规范
- **API 文档**: 使用 FastAPI 自动生成
- **代码注释**: 详细的函数和类注释
- **README**: 完整的项目说明文档

### 3. 测试规范
- **单元测试**: 核心业务逻辑单元测试
- **集成测试**: API 接口集成测试
- **端到端测试**: 完整业务流程测试

这个项目结构为 WaveTune 系统提供了完整的技术架构，支持用户认证、音乐推荐、场景配置等核心功能，同时具备良好的可维护性、可扩展性和安全性。


