# WaveTune 系统启动指南

> 推荐 Python 版本：Python 3.11.14（下面的步骤基于该版本）

## 系统概述

WaveTune 是一个基于 Vue 3 + FastAPI 的脑疲劳检测与音乐干预系统，包含前端可视化界面和后端API服务，集成了AI助手、2-back实验、联邦学习等功能。

## 环境要求

### 必需环境
- **Node.js**: >= 16.0.0
- **Python**: 3.11.14 (推荐)
- **MySQL**: 8.0+ 或 TiDB Cloud

### 可选工具
- **Git**: 版本控制
- **VS Code**: 推荐IDE
- **Postman**: API测试

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
│   ├── views/                             # 页面视图
│   │   ├── admin/                         # 管理员页面
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
│   ├── store/                             # 状态管理
│   ├── stores/                            # 模块化状态管理
│   ├── assets/                            # 静态资源
│   ├── utils/                             # 工具函数
│   ├── composables/                       # 组合式函数
│   ├── App.vue                            # 根组件
│   └── main.js                            # 应用入口
├── backend/                               # FastAPI 后端项目
│   ├── main.py                            # 主入口文件
│   ├── start.py                           # 启动脚本
│   ├── requirements.txt                   # Python 依赖
│   ├── config/                            # 配置文件
│   ├── models/                            # 数据模型
│   ├── routers/                           # API 路由
│   ├── schemas/                           # 数据验证模型
│   ├── middleware/                        # 中间件
│   ├── database/                          # 数据库脚本
│   │   └── create_tables.sql              # 建表SQL
│   ├── utils/                             # 工具函数
│   │   └── s3_helper.py                   # 云存储工具
│   ├── static/                            # 静态文件目录
│   └── logs/                              # 日志文件目录
├── public/                                # 公共静态资源
├── WaveTune_API接口文档.md                # API 接口文档
├── WaveTune_启动指南.md                   # 启动指南
├── WaveTune_数据库设计说明文档.md         # 数据库设计文档
├── WaveTune_项目结构解释文档.md           # 项目结构文档
├── package.json                           # 前端依赖配置
├── vite.config.js                         # Vite配置
├── vue.config.js                          # Vue配置
└── nginx.conf                             # Nginx配置
```

## 启动步骤

### 第一步：数据库初始化

1. **创建数据库**
   ```sql
   CREATE DATABASE wavetune CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **导入表结构**
   ```bash
   mysql -u root -p wavetune < backend/database/create_tables.sql
   ```

3. **配置数据库连接**
   - 编辑 `backend/config.py` 或创建 `.env` 文件
   - 设置数据库连接信息：
     ```
     DATABASE_URL=mysql+pymysql://user:password@localhost:3306/wavetune
     ```

### 第二步：配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/wavetune

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 云存储配置（缤纷云）
S3_ENDPOINT=https://s3.bitiful.net
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=wavetune
S3_REGION=cn-north-1

# 邮件配置（可选）
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-password
```

### 第三步：启动后端服务

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **创建并激活虚拟环境**

   Windows (PowerShell)：
   ```powershell
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
   ```bash
   pip install -r requirements.txt
   ```

   注意：`torch` 的 GPU 版本需要根据操作系统与 CUDA 版本单独安装。例如仅安装 CPU 版本：
   ```bash
   pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu
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
   - 访问 http://localhost:8000/docs 查看API文档（Swagger UI）
   - 访问 http://localhost:8000/redoc 查看API文档（ReDoc）
   - 访问 http://localhost:8000/health 进行健康检查

### 第四步：启动前端服务

1. **进入项目根目录**
   ```bash
   cd ..  # 如果还在backend目录
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

## 功能模块说明

### 前端功能模块

1. **首页 (HomeView)**
   - 系统介绍和功能导航
   - 系统统计数据展示
   - 联邦学习状态概览
   - 快速操作入口

2. **用户认证 (LoginView/RegisterView)**
   - 用户注册和登录
   - JWT Token管理
   - 会话保持

3. **个人中心 (UserCenterView)**
   - 用户信息展示和编辑
   - 头像上传功能
   - 用户反馈提交
   - 历史反馈查询

4. **音乐推荐 (MusicRecommendationView)**
   - 基于疲劳等级的音乐推荐
   - 音乐卡片展示
   - 推荐理由说明
   - 匹配度显示
   - 音乐播放器集成

5. **疲劳检测 (DetectionView)**
   - EEG信号采集
   - 疲劳状态检测
   - 结果可视化展示

6. **信号监测 (SignalMonitorView)**
   - 多模态信号实时监测
   - CSV文件上传分析
   - 波形图展示
   - 数据导出功能

7. **联邦学习 (FederatedContributeView)**
   - 数据贡献上传
   - 训练进度实时监控
   - 训练历史记录
   - 隐私保护说明
   - 云存储文件管理

8. **AI 助手 (AIAssistantSidebar)**
   - 智能问答
   - 系统操作指导
   - 个性化建议
   - 对话历史记录

9. **2-back 实验 (TwoBackExperimentView)**
   - 认知能力测试
   - 实时反馈
   - 实验结果分析
   - 历史数据对比

10. **管理员功能 (AdminLayout)**
    - 用户管理
    - 音乐库管理
    - 反馈管理
    - 系统配置
    - 联邦学习管理

### 后端API模块

1. **认证接口 (auth)**
   - 用户注册/登录/登出
   - Token刷新
   - 密码修改

2. **用户接口 (user)**
   - 用户信息管理
   - 头像上传
   - 统计信息

3. **检测接口 (detection)**
   - 疲劳检测分析
   - 检测历史查询
   - CSV文件处理

4. **音乐接口 (music)**
   - 音乐库管理
   - 推荐算法
   - 播放统计

5. **场景接口 (scene)**
   - 场景配置管理
   - 用户自定义场景

6. **联邦学习接口 (federated)**
   - 训练任务管理
   - 设备管理
   - 进度监控
   - 云存储集成

7. **反馈接口 (feedback)**
   - 反馈提交
   - 历史查询
   - 管理员回复

8. **统计接口 (stats)**
   - 系统统计
   - 用户统计

9. **2-back接口 (twoback)**
   - 实验管理
   - 结果存储

10. **管理后台接口 (admin)**
    - 用户管理
    - 音乐管理
    - 系统配置

## 数据库说明

### 数据表结构

1. **user** - 用户信息
2. **feedback** - 用户反馈
3. **music** - 音乐数据
4. **scene** - 场景配置
5. **system_stats** - 系统统计
6. **user_session** - 用户会话
7. **user_preference** - 用户偏好
8. **operation_log** - 操作日志
9. **two_back** - 2-back 实验数据
10. **federated_training** - 联邦学习训练记录
11. **federated_device** - 联邦学习设备
12. **federated_stats** - 联邦学习统计

### 初始数据

系统初始化时会自动创建：
- 测试用户数据
- 多条音乐数据（覆盖不同疲劳等级和音乐类型）
- 系统默认场景
- 系统统计数据

## 配置说明

### 后端配置 (backend/config.py)

- **数据库**: TiDB Cloud 或 MySQL
- **端口**: 8000
- **CORS**: 允许 localhost:8080 和内网穿透域名访问
- **文件上传**: 支持头像上传，大文件使用云存储
- **云存储**: 缤纷云 S3 兼容存储

### 前端配置

- **开发端口**: 8080
- **API基础URL**: /api (相对路径，支持动态域名)
- **路由模式**: History 模式
- **代理配置**: vite.config.js 中配置开发代理

## 常见问题

### 1. 后端启动失败

**问题**: 端口被占用
**解决**: 修改端口或关闭占用端口的进程
```bash
# 查看端口占用 (Windows)
netstat -ano | findstr :8000
# 杀死进程
taskkill /PID <进程ID> /F

# 查看端口占用 (Linux/Mac)
lsof -i :8000
# 杀死进程
kill -9 <进程ID>
```

### 2. 数据库连接失败

**问题**: 数据库配置错误
**解决**: 
1. 检查 `.env` 或 `config.py` 中的数据库连接字符串
2. 确认数据库服务已启动
3. 检查用户名和密码是否正确
4. 确认数据库 `wavetune` 已创建

### 3. 前端无法连接后端

**问题**: CORS 跨域问题
**解决**: 
1. 检查后端 `main.py` 中的 CORS 配置
2. 确认前端域名已添加到允许列表
3. 检查前端 `vite.config.js` 中的代理配置

### 4. 文件上传失败

**问题**: 云存储配置错误
**解决**: 
1. 检查 `.env` 中的 S3 配置信息
2. 确认云存储服务可用
3. 检查 Access Key 和 Secret Key 是否正确
4. 确认存储桶 `wavetune` 已创建

### 5. 联邦学习训练失败

**问题**: 数据格式不正确
**解决**: 
1. 确保 CSV 文件格式正确
2. 检查数据列名是否符合要求
3. 确认文件大小在限制范围内
4. 查看后端日志获取详细错误信息

### 6. 内网穿透访问失败

**问题**: 域名未添加到 CORS 配置
**解决**: 
1. 检查 `backend/main.py` 中的 CORS 配置
2. 在 `vue.config.js` 中添加允许的域名
3. 重启前后端服务

## 开发建议

### 后端开发
1. 使用 FastAPI 自动生成的文档进行接口测试
2. 修改模型后需要重新启动服务
3. 日志文件保存在 `logs/app.log`
4. 使用 `pytest` 进行单元测试

### 前端开发
1. 使用 Vue DevTools 进行调试
2. 修改路由后检查导航菜单
3. 注意 Element Plus 组件的响应式设计
4. 使用 ESLint 保持代码规范

### 集成测试
1. 先启动后端服务，再启动前端
2. 使用浏览器开发者工具查看网络请求
3. 检查控制台错误信息
4. 测试各种边界条件

## 部署说明

### 开发环境
- 后端：http://localhost:8000
- 前端：http://localhost:8080
- 数据库：TiDB Cloud / MySQL

### 生产环境部署

#### 前端部署
1. 构建生产版本：
   ```bash
   npm run build
   ```
2. 输出目录：`dist/`
3. 使用 Nginx 托管静态文件

#### 后端部署
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置生产环境变量
3. 使用 Gunicorn 运行：
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

#### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/wavetune/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 技术支持

如有问题，请参考：
1. API接口文档：`WaveTune_API接口文档.md`
2. 数据库设计文档：`WaveTune_数据库设计说明文档.md`
3. 项目结构文档：`WaveTune_项目结构解释文档.md`
4. FastAPI官方文档：https://fastapi.tiangolo.com/
5. Vue 3官方文档：https://vuejs.org/
6. Element Plus文档：https://element-plus.org/
