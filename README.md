# WaveTune - 基于多模态生理信号的脑疲劳检测和轻音乐个性化干预系统

## 项目简介

WaveTune 是一个基于 Vue 3 开发的前端可视化系统，专注于多模态生理信号的脑疲劳检测和轻音乐个性化干预。系统采用联邦学习技术保护用户隐私，通过 EEG、EOG、HRV 等多模态生理信号实时监测脑疲劳状态，并提供个性化轻音乐干预方案。

## 技术栈

- **前端框架**: Vue 3 (组合式 API)
- **UI 组件库**: Element Plus 2.0+
- **图表工具**: ECharts 5.x
- **路由管理**: Vue Router 4.x
- **状态管理**: Pinia
- **样式预处理**: SCSS
- **构建工具**: Vue CLI 5.0

## 项目结构

```
src/
├── assets/                    # 静态资源
│   ├── styles/               # 样式文件
│   │   ├── global.scss       # 全局样式
│   │   ├── breakpoints.scss  # 响应式断点
│   │   └── element-variables.scss # Element Plus 主题变量
│   └── logo.png              # 项目logo
├── components/               # 组件目录
│   ├── global/              # 全局通用组件
│   │   ├── Navbar.vue       # 导航栏组件
│   │   ├── CardContainer.vue # 通用卡片容器
│   │   └── Footer.vue       # 页脚组件
│   └── business/            # 业务组件
│       ├── fatigue/         # 脑疲劳相关组件
│       ├── music/           # 音乐推荐相关组件
│       └── federated/       # 联邦学习相关组件
├── views/                   # 页面组件
│   ├── HomeView.vue         # 首页
│   ├── FatigueResultView.vue # 脑疲劳检测结果页
│   ├── MusicRecommendationView.vue # 音乐推荐页
│   ├── SignalMonitorView.vue # 信号监测页
│   ├── UserFeedbackView.vue # 用户反馈页
│   ├── AboutView.vue        # 关于页面
│   └── federated/           # 联邦学习相关页面
│       ├── FederatedStatusView.vue # 联邦学习状态页
│       ├── FederatedProgressView.vue # 联邦学习进度页
│       └── FederatedDevicesView.vue # 联邦学习设备管理页
├── router/                  # 路由配置
│   └── index.js            # 路由定义
├── store/                   # 状态管理
│   └── index.js            # Pinia store
├── App.vue                  # 根组件
└── main.js                  # 应用入口
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

### 4. 多模态信号实时监测
- EEG、EOG、HRV 信号监测
- 实时数值展示
- 简化波形图
- 监测状态指示
- 时间轴显示

### 5. 联邦学习相关界面
- 参与状态展示
- 训练进度监控
- 设备管理
- 隐私保护说明

### 6. 用户信息管理与反馈
- 个人信息展示
- 系统使用反馈
- 满意度评分
- 反馈类型选择

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
- **全局通用组件**: 导航栏、卡片容器、页脚
- **业务组件**: 按功能模块分类，命名格式为 `XxxComponent.vue`
- **页面组件**: 命名格式为 `XxxView.vue`

## 安装和运行

### 环境要求
- Node.js >= 14.0.0
- npm >= 6.0.0

### 安装依赖
```bash
npm install
```

### 开发运行
```bash
npm run serve
```

### 生产构建
```bash
npm run build
```

## 开发说明

### 代码规范
- 使用 Vue 3 组合式 API
- 组件命名采用 PascalCase
- 样式使用 SCSS 预处理器
- 遵循 Element Plus 组件使用规范

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

1. **仅前端可视化**: 本项目仅实现前端可视化展示，不涉及具体功能逻辑实现
2. **静态数据**: 所有数据均为静态模拟值，用于展示界面效果
3. **隐私保护**: 联邦学习相关界面重点展示隐私保护机制
4. **响应式设计**: 所有页面均适配不同屏幕尺寸

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址: [GitHub Repository]
- 邮箱: [Your Email]