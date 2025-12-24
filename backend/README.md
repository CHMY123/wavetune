# WaveTune 后端服务

基于 FastAPI 的脑疲劳检测与音乐干预系统后端服务。

## 功能特性

- 🧠 用户信息管理
- 📝 用户反馈系统
- 🎵 音乐推荐服务
- ⚙️ 场景配置管理
- 📊 系统统计展示
- 🔒 统一错误处理
- 📝 请求日志记录

## 技术栈

- **Web框架**: FastAPI
- **数据库**: SQLAlchemy + SQLite/MySQL
- **数据验证**: Pydantic
- **文件上传**: python-multipart
- **API文档**: 自动生成 (Swagger UI)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

### 3. 启动服务

```bash
python start.py
```

或者使用 uvicorn 直接启动：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问服务

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 项目结构

```
backend/
├── main.py                 # 主入口文件
├── start.py               # 启动脚本
├── init_db.py             # 数据库初始化
├── requirements.txt       # 项目依赖
├── config/                # 配置文件
│   └── database.py        # 数据库配置
├── models/                # 数据模型
│   ├── __init__.py
│   ├── user.py           # 用户模型
│   ├── feedback.py       # 反馈模型
│   ├── music.py          # 音乐模型
│   ├── scene.py          # 场景模型
│   └── system_stats.py   # 系统统计模型
├── schemas/               # 数据验证模型
│   ├── user.py
│   ├── feedback.py
│   └── scene.py
├── routers/               # 路由模块
│   ├── __init__.py
│   ├── system.py         # 系统统计路由
│   ├── user.py           # 用户管理路由
│   ├── feedback.py       # 反馈路由
│   ├── music.py          # 音乐推荐路由
│   └── scene.py          # 场景配置路由
├── static/                # 静态文件目录
│   ├── avatar/           # 用户头像
│   └── music_cover/      # 音乐封面
└── logs/                  # 日志文件目录
```

## API 接口

### 系统统计
- `GET /api/system/stats` - 获取系统统计数据

### 用户管理
- `GET /api/user/info` - 获取用户信息
- `PUT /api/user/update` - 更新用户信息
- `POST /api/user/avatar/upload` - 上传用户头像
- `PUT /api/user/count/update` - 更新用户统计次数

### 用户反馈
- `POST /api/feedback/submit` - 提交用户反馈
- `GET /api/feedback/history` - 查询历史反馈

### 音乐推荐
- `GET /api/music/recommend` - 获取音乐推荐列表
- `GET /api/music/detail` - 获取音乐详情

### 场景配置
- `GET /api/scene/list` - 获取场景列表
- `POST /api/scene/create` - 创建场景
- `GET /api/scene/apply` - 应用场景
- `DELETE /api/scene/delete` - 删除场景

## 数据库配置

### SQLite (开发环境)
```python
DATABASE_URL = "sqlite:///./wavetune.db"
```

### MySQL (生产环境)
```python
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/wavetune"
```

## 环境变量

复制 `env.example` 为 `.env` 并修改相应配置：

```bash
cp env.example .env
```

## 开发说明

### 添加新的API接口

1. 在 `models/` 中定义数据模型
2. 在 `schemas/` 中定义请求验证模型
3. 在 `routers/` 中实现路由逻辑
4. 在 `main.py` 中注册路由

### 数据库迁移

修改模型后需要重新初始化数据库：

```bash
python init_db.py
```

### 日志查看

日志文件保存在 `logs/app.log`，包含请求记录和错误信息。

## 部署说明

### 生产环境部署

1. 使用 Gunicorn 作为 WSGI 服务器
2. 配置 Nginx 作为反向代理
3. 使用 MySQL 作为生产数据库
4. 配置 HTTPS 证书

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 测试

运行测试：

```bash
pytest
```

## 许可证

MIT License




