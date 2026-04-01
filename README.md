# WaveTune - 基于多模态生理信号的脑疲劳检测和轻音乐个性化干预系统

## 项目简介

WaveTune 是一个基于 Vue 3 + FastAPI 开发的完整系统，专注于多模态生理信号的脑疲劳检测和轻音乐个性化干预。系统采用前后端分离架构，结合联邦学习技术保护用户隐私，通过 EEG、EOG、HRV 等多模态生理信号实时监测脑疲劳状态，并提供个性化轻音乐干预方案。

## 技术栈

### 前端技术栈
- **前端框架**: Vue 3 (组合式 API)
- **UI 组件库**: Element Plus 2.0+
- **图表工具**: ECharts 5.x
- **路由管理**: Vue Router 4.x
- **状态管理**: Pinia
- **样式预处理**: SCSS
- **构建工具**: Vue CLI 5.0

### 后端技术栈
- **后端框架**: FastAPI
- **数据库 ORM**: SQLAlchemy
- **数据验证**: Pydantic
- **服务器**: Uvicorn
- **数据库**: MySQL / SQLite
- **认证**: JWT

## 项目结构

```
wavetune/
├── src/                                    # Vue 3 前端项目
│   ├── components/                         # 组件目录
│   │   ├── global/                        # 全局通用组件
│   │   │   ├── AIAssistantSidebar.vue     # AI 助手侧边栏
│   │   │   ├── CardContainer.vue          # 卡片容器组件
│   │   │   ├── Footer.vue                 # 页脚组件
│   │   │   ├── MusicPlayer.vue            # 音乐播放器
│   │   │   └── Navbar.vue                 # 导航栏组件
│   │   └── HelloWorld.vue                 # 示例组件
│   ├── views/                             # 页面视图
│   │   ├── admin/                         # 管理员页面
│   │   │   ├── AdminLayout.vue            # 管理员布局
│   │   │   ├── DashboardView.vue          # 管理员仪表盘
│   │   │   ├── FederatedManagementView.vue # 联邦学习管理
│   │   │   ├── FeedbackManagementView.vue # 反馈管理
│   │   │   ├── MusicManagementView.vue    # 音乐管理
│   │   │   ├── SystemConfigView.vue       # 系统配置
│   │   │   └── UserManagementView.vue     # 用户管理
│   │   ├── AboutView.vue                  # 关于页面
│   │   ├── FederatedContributeView.vue    # 联邦学习贡献
│   │   ├── HomeView.vue                   # 首页
│   │   ├── LoginView.vue                  # 登录页面
│   │   ├── MusicRecommendationView.vue    # 音乐推荐页面
│   │   ├── QuickDetectionChoiceView.vue   # 快速检测选择
│   │   ├── RegisterView.vue               # 注册页面
│   │   ├── SignalMonitorView.vue          # 信号监测页面
│   │   ├── TwoBackExperimentView.vue      # 2-back 实验页面
│   │   ├── UserCenterView.vue             # 用户中心
│   │   └── UserFeedbackView.vue           # 用户反馈页面
│   ├── router/                            # 路由配置
│   │   └── index.js                       # 路由定义
│   ├── store/                             # 状态管理
│   │   └── index.js                       # Pinia 状态定义
│   ├── stores/                            # 模块化状态管理
│   │   ├── adminStore.js                  # 管理员状态
│   │   ├── analyticsStore.js              # 分析状态
│   │   └── playerStore.js                 # 播放器状态
│   ├── assets/                            # 静态资源
│   │   ├── styles/                        # 样式文件
│   │   │   ├── _design_tokens.scss        # 设计令牌
│   │   │   ├── _variables.scss            # 变量定义
│   │   │   ├── breakpoints.scss           # 响应式断点
│   │   │   ├── element-variables.scss     # Element Plus 变量
│   │   │   └── global.scss                # 全局样式
│   │   └── logo.png                       # 项目 Logo
│   ├── utils/                             # 工具函数
│   │   ├── errorHandler.js                # 错误处理工具
│   │   ├── media.js                       # 媒体处理
│   │   └── request.js                     # 请求封装
│   ├── composables/                       # 组合式函数
│   │   └── useTheme.js                    # 主题管理
│   ├── App.vue                            # 根组件
│   └── main.js                            # 应用入口
├── backend/                               # FastAPI 后端项目
│   ├── main.py                            # 主入口文件
│   ├── start.py                           # 启动脚本
│   ├── requirements.txt                   # Python 依赖
│   ├── config/                            # 配置文件
│   │   └── database.py                    # 数据库配置
│   ├── models/                            # 数据模型
│   │   ├── __init__.py                    # 模型初始化
│   │   ├── federated.py                   # 联邦学习模型
│   │   ├── feedback.py                    # 反馈模型
│   │   ├── music.py                       # 音乐模型
│   │   ├── operation_log.py               # 操作日志模型
│   │   ├── scene.py                       # 场景模型
│   │   ├── system_config.py               # 系统配置模型
│   │   ├── two_back.py                    # 2-back 实验模型
│   │   ├── user.py                        # 用户模型
│   │   ├── user_preference.py             # 用户偏好模型
│   │   └── user_session.py                # 用户会话模型
│   ├── routers/                           # API 路由
│   │   ├── __init__.py                    # 路由初始化
│   │   ├── admin.py                       # 管理员路由
│   │   ├── ai.py                          # AI 助手路由
│   │   ├── auth.py                        # 认证路由
│   │   ├── detection.py                   # 检测路由
│   │   ├── federated.py                   # 联邦学习路由
│   │   ├── feedback.py                    # 反馈路由
│   │   ├── music.py                       # 音乐推荐路由
│   │   └── scene.py                       # 场景配置路由
│   ├── schemas/                           # 数据验证模型
│   │   ├── admin.py                       # 管理员验证模型
│   │   ├── analytics.py                   # 分析验证模型
│   │   ├── auth.py                        # 认证验证模型
│   │   ├── feedback.py                    # 反馈验证模型
│   │   ├── scene.py                       # 场景验证模型
│   │   ├── token.py                       # 令牌验证模型
│   │   └── user.py                        # 用户验证模型
│   ├── middleware/                        # 中间件
│   │   ├── __init__.py                    # 中间件初始化
│   │   └── auth.py                        # 认证中间件
│   ├── federated/                         # 联邦学习相关
│   │   ├── README.md                      # 联邦学习说明
│   │   ├── data_loader.py                 # 数据加载器
│   │   ├── federated_client.py            # 联邦学习客户端
│   │   ├── federated_client_supernode.py  # 超级节点客户端
│   │   ├── federated_server.py            # 联邦学习服务器
│   │   ├── federated_server_superlink.py  # 超级链接服务器
│   │   └── federated_trainer.py           # 联邦学习训练器
│   ├── services/                          # 服务
│   │   ├── data_storage.py                # 数据存储服务
│   │   └── two_back_service.py            # 2-back 实验服务
│   ├── utils/                             # 工具
│   │   ├── boardInfo.json                 # 板卡信息
│   │   ├── models.py                      # 模型工具
│   │   ├── multimodal_fatigue_model.pth   # 多模态疲劳模型
│   │   ├── processing_fNIRS_new.py        # fNIRS 处理
│   │   ├── procutil_get_extinctions.py    # 消光处理
│   │   ├── quick_detect.py                # 快速检测
│   │   └── s3_helper.py                   # S3 云存储助手
│   ├── database/                          # 数据库脚本
│   │   ├── create_tables.sql              # 建表 SQL 脚本
│   │   └── federated_tables.sql           # 联邦学习表脚本
│   ├── static/                            # 静态文件目录
│   │   ├── avatar/                        # 用户头像
│   │   └── music/                         # 音乐文件
│   └── logs/                              # 日志文件目录
├── public/                                # 公共静态资源
│   ├── favicon.ico                        # 网站图标
│   ├── index.html                         # HTML 模板
│   └── static/                            # 静态资源
│       ├── avatar/                        # 默认头像
│       ├── icon/                          # 图标
│       └── logo/                          #  Logo
├── WaveTune_API接口文档.md                # API 接口文档
├── WaveTune_启动指南.md                   # 启动指南
├── WaveTune_数据库设计说明文档.md         # 数据库设计文档
├── WaveTune_项目结构解释文档.md           # 项目结构文档
├── moviemate.sql                          # 数据库备份
├── package.json                           # 前端依赖配置
├── vue.config.js                          # Vue 配置
└── README.md                              # 项目说明文档
```

## 功能模块

### 1. 首页总览
- 系统介绍和功能导航
- 核心功能模块展示
- 系统运行统计
- 联邦学习状态概览
- 快速操作入口

### 2. 脑疲劳检测结果展示
- 检测基本信息展示
- 疲劳等级可视化
- 关键指标数值展示
- 历史趋势图表
- 详细指标表格

### 3. 轻音乐个性化推荐
- 基于疲劳等级的推荐
- 音乐卡片展示
- 推荐理由说明
- 个性化匹配度显示
- 音乐播放器集成

### 4. 多模态信号实时监测
- EEG、EOG、HRV 信号监测
- 实时数值展示
- 简化波形图
- 监测状态指示
- 时间轴显示

### 5. 联邦学习相关功能
- 参与状态展示
- 训练进度监控
- 设备管理
- 隐私保护说明
- 贡献数据管理

### 6. 用户信息管理与反馈
- 个人信息展示和编辑
- 系统使用反馈
- 满意度评分
- 反馈类型选择
- 反馈历史查询

### 7. AI 助手
- 智能问答
- 系统操作指导
- 个性化建议
- 对话历史记录

### 8. 2-back 实验
- 认知能力测试
- 实时反馈
- 实验结果分析
- 历史数据对比

### 9. 管理员功能
- 用户管理
- 音乐库管理
- 反馈管理
- 系统配置
- 联邦学习管理

## 设计规范

### 响应式断点
- **大屏** (≥1200px): 多列布局，2-4列卡片
- **中屏** (768px~1199px): 2列布局或上下堆叠
- **小屏** (≤767px): 单列布局，表格横向滚动

### 主题色配置
- **主色调**: 蓝色系 (#1890ff)
- **成功色**: 绿色 (#52c41a)
- **警告色**: 橙色 (#fa8c16)
- **危险色**: 红色 (#f56c6c)

### 组件规范
- **全局通用组件**: 导航栏、卡片容器、页脚、音乐播放器、AI 助手
- **业务组件**: 按功能模块分类，命名格式为 `XxxComponent.vue`
- **页面组件**: 命名格式为 `XxxView.vue`

## 安装和运行

### 环境要求
- **前端**: Node.js >= 14.0.0, npm >= 6.0.0
- **后端**: Python >= 3.8.0, pip >= 20.0.0

### 前端安装和运行
```bash
# 安装依赖
npm install

# 开发运行
npm run serve

# 生产构建
npm run build
```

### 后端安装和运行
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python start.py
# 或使用 uvicorn
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 开发说明

### 代码规范
- **前端**: 使用 Vue 3 组合式 API，组件命名采用 PascalCase，样式使用 SCSS 预处理器
- **后端**: 遵循 PEP 8 编码规范，使用 FastAPI 标准结构

### 样式规范
- 统一使用 CSS 变量定义主题色
- 响应式设计遵循断点规范
- 组件样式使用 scoped 作用域
- 全局样式放在 `assets/styles/global.scss`

### 路由规范
- 路由路径全小写
- 子路由采用 `/父路由/子路由` 格式
- 使用懒加载优化性能

## 注意事项

1. **完整系统**: 本项目包含完整的前后端实现，支持实际功能逻辑
2. **数据存储**: 使用 TiDB Cloud 存储数据，文件上传采用 S3 兼容云存储（缤纷云）
3. **隐私保护**: 联邦学习技术保护用户隐私
4. **响应式设计**: 所有页面均适配不同屏幕尺寸
5. **AI 集成**: 集成了 AI 助手功能，提供智能交互
6. **云存储流程**: 文件上传采用先上传到云存储，再下载到后端处理的流程，提高存储可靠性

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址: [GitHub Repository]
- 邮箱: 924157960@qq.com