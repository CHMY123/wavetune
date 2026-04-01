# WaveTune API 接口文档

## 文档概述

本文档详细描述了 WaveTune 脑疲劳检测与音乐干预系统的所有 API 接口，包括请求参数、响应格式和错误码说明。

**基础URL**: `http://localhost:8000/api`

**认证方式**: JWT Token (Bearer Token)

## 通用规范

### 请求格式
- Content-Type: `application/json`
- 认证接口需在 Header 中携带: `Authorization: Bearer <token>`

### 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 认证接口 (Auth)

### 1. 用户注册

**接口**: `POST /auth/register`

**请求参数**:
```json
{
  "username": "string",      // 用户名，必填，2-20字符
  "student_id": "string",    // 学号，必填，唯一
  "password": "string",      // 密码，必填，6-20字符
  "email": "string",         // 邮箱，可选
  "phone": "string"          // 手机号，可选
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "张三",
    "student_id": "2024001",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### 2. 用户登录

**接口**: `POST /auth/login`

**请求参数**:
```json
{
  "student_id": "string",    // 学号，必填
  "password": "string"       // 密码，必填
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "张三",
    "student_id": "2024001",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400
  }
}
```

### 3. 用户登出

**接口**: `POST /auth/logout`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

### 4. 刷新Token

**接口**: `POST /auth/refresh`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400
  }
}
```

---

## 用户接口 (User)

### 1. 获取用户信息

**接口**: `GET /user/profile`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "张三",
    "student_id": "2024001",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "avatar": "/avatars/1.png",
    "detection_count": 10,
    "intervention_count": 5,
    "last_login_time": "2025-01-15T10:30:00",
    "create_time": "2025-01-01T08:00:00"
  }
}
```

### 2. 更新用户信息

**接口**: `PUT /user/profile`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "username": "string",      // 用户名
  "email": "string",         // 邮箱
  "phone": "string",         // 手机号
  "avatar": "string"         // 头像URL
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "username": "张三",
    "email": "zhangsan@example.com"
  }
}
```

### 3. 修改密码

**接口**: `PUT /user/password`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "old_password": "string",  // 旧密码，必填
  "new_password": "string"   // 新密码，必填，6-20字符
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

### 4. 上传头像

**接口**: `POST /user/avatar`

**请求头**: `Authorization: Bearer <token>`

**请求体**: `multipart/form-data`
- `file`: 图片文件 (jpg, png, gif, 最大2MB)

**响应示例**:
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "avatar_url": "/avatars/1_1705312800.png"
  }
}
```

---

## 疲劳检测接口 (Detection)

### 1. 执行疲劳检测

**接口**: `POST /detection/analyze`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "signal_data": [            // EEG信号数据，数组
    {
      "timestamp": 1705312800,
      "channel_1": 0.5,
      "channel_2": 0.3,
      "channel_3": 0.2,
      "channel_4": 0.4
    }
  ],
  "sampling_rate": 256,       // 采样率，默认256Hz
  "duration": 60              // 检测时长(秒)，默认60秒
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "检测成功",
  "data": {
    "detection_id": "det_123456",
    "fatigue_level": "medium",    // light/medium/heavy
    "fatigue_score": 65,          // 0-100
    "confidence": 0.85,           // 置信度
    "analysis": {
      "alpha_power": 0.3,
      "beta_power": 0.4,
      "theta_power": 0.2,
      "dominant_frequency": 10.5
    },
    "recommendations": [
      "建议休息15分钟",
      "可尝试听轻音乐放松"
    ],
    "detect_time": "2025-01-15T10:30:00"
  }
}
```

### 2. 获取检测历史

**接口**: `GET /detection/history`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "page": 1,
    "page_size": 10,
    "items": [
      {
        "detection_id": "det_123456",
        "fatigue_level": "medium",
        "fatigue_score": 65,
        "detect_time": "2025-01-15T10:30:00"
      }
    ]
  }
}
```

### 3. 上传CSV文件检测

**接口**: `POST /detection/upload-csv`

**请求头**: `Authorization: Bearer <token>`

**请求体**: `multipart/form-data`
- `file`: CSV文件

**响应示例**:
```json
{
  "code": 200,
  "message": "文件上传成功，正在处理",
  "data": {
    "task_id": "task_789012",
    "status": "processing"
  }
}
```

### 4. 获取CSV处理状态

**接口**: `GET /detection/csv-status/{task_id}`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "task_789012",
    "status": "completed",        // pending/processing/completed/failed
    "progress": 100,
    "result": {
      "fatigue_level": "light",
      "fatigue_score": 35,
      "signal_data": [...]
    }
  }
}
```

---

## 音乐接口 (Music)

### 1. 获取音乐列表

**接口**: `GET /music/list`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `music_type`: 音乐类型 (natural/piano/whitenoise/mix)
- `fatigue_level`: 疲劳等级 (light/medium/heavy)
- `page`: 页码，默认1
- `page_size`: 每页数量，默认20

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "title": "雨声",
        "artist": "自然音效",
        "duration": "03:45",
        "cover": "/covers/rain.jpg",
        "audio_url": "/audio/rain.mp3",
        "music_type": "natural",
        "fatigue_level": "medium",
        "match_rate": 85,
        "play_count": 1200,
        "reason": "适合中度疲劳时聆听，有助于放松身心"
      }
    ]
  }
}
```

### 2. 获取推荐音乐

**接口**: `GET /music/recommend`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `fatigue_level`: 当前疲劳等级
- `limit`: 推荐数量，默认5

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "recommendations": [
      {
        "id": 1,
        "title": "雨声",
        "artist": "自然音效",
        "match_rate": 92,
        "reason": "根据您当前的疲劳状态，推荐这首自然音效帮助您放松"
      }
    ]
  }
}
```

### 3. 记录播放

**接口**: `POST /music/play/{music_id}`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "播放记录已更新",
  "data": {
    "play_count": 1201
  }
}
```

### 4. 获取音乐详情

**接口**: `GET /music/{music_id}`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "雨声",
    "artist": "自然音效",
    "duration": "03:45",
    "cover": "/covers/rain.jpg",
    "audio_url": "/audio/rain.mp3",
    "music_type": "natural",
    "fatigue_level": "medium",
    "match_rate": 85,
    "play_count": 1200,
    "scenes": ["工作", "休息"],
    "description": "自然雨声音效，有助于放松和集中注意力"
  }
}
```

---

## 场景接口 (Scene)

### 1. 获取场景列表

**接口**: `GET /scene/list`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "scenes": [
      {
        "id": 1,
        "scene_name": "工作专注",
        "music_type": "piano",
        "description": "适合工作时的轻音乐",
        "is_default": true
      }
    ]
  }
}
```

### 2. 创建场景

**接口**: `POST /scene/create`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "scene_name": "string",    // 场景名称，必填
  "music_type": "string",    // 音乐类型，必填
  "description": "string"    // 场景描述，可选
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "场景创建成功",
  "data": {
    "id": 2,
    "scene_name": "睡前放松",
    "music_type": "whitenoise"
  }
}
```

### 3. 更新场景

**接口**: `PUT /scene/{scene_id}`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "scene_name": "string",
  "music_type": "string",
  "description": "string"
}
```

### 4. 删除场景

**接口**: `DELETE /scene/{scene_id}`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "场景删除成功",
  "data": null
}
```

---

## 联邦学习接口 (Federated)

### 1. 提交训练贡献

**接口**: `POST /federated/contribute`

**请求头**: `Authorization: Bearer <token>`

**请求体**: `multipart/form-data`
- `file`: CSV训练数据文件
- `client_id`: 客户端ID
- `round_number`: 训练轮次

**响应示例**:
```json
{
  "code": 200,
  "message": "贡献提交成功，训练任务已启动",
  "data": {
    "training_id": "train_123456",
    "status": "pending",
    "message": "训练时长较长，请耐心等待"
  }
}
```

### 2. 获取训练状态

**接口**: `GET /federated/training-status/{training_id}`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "training_id": "train_123456",
    "status": "training",         // pending/training/completed/failed
    "progress": 65,               // 进度百分比
    "current_step": "模型训练中",  // 当前步骤描述
    "logs": [
      {
        "time": "10:30:00",
        "content": "数据上传完成"
      },
      {
        "time": "10:30:05",
        "content": "开始模型训练"
      }
    ],
    "result": {
      "accuracy": 0.85,
      "loss": 0.15,
      "training_time": 300
    }
  }
}
```

### 3. 获取训练历史

**接口**: `GET /federated/history`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 20,
    "page": 1,
    "page_size": 10,
    "items": [
      {
        "training_id": "train_123456",
        "status": "completed",
        "accuracy": 0.85,
        "loss": 0.15,
        "training_time": "2025-01-15T10:30:00"
      }
    ]
  }
}
```

### 4. 获取联邦学习统计

**接口**: `GET /federated/stats`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_participants": 50,
    "total_rounds": 100,
    "total_devices": 30,
    "average_accuracy": 0.82,
    "average_loss": 0.18,
    "my_contributions": 5,
    "my_rank": 10
  }
}
```

### 5. 获取设备列表

**接口**: `GET /federated/devices`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "devices": [
      {
        "device_id": "dev_001",
        "device_type": "local",
        "status": "online",
        "training_count": 10,
        "contribution": 0.85,
        "last_participate": "2025-01-15T10:00:00"
      }
    ]
  }
}
```

---

## 反馈接口 (Feedback)

### 1. 提交反馈

**接口**: `POST /feedback/submit`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "feedback_type": "string",   // accuracy/music/function
  "content": "string",         // 反馈内容，必填
  "score": 5                   // 满意度评分，1-5
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "反馈提交成功",
  "data": {
    "feedback_id": 1,
    "status": "pending"
  }
}
```

### 2. 获取反馈列表

**接口**: `GET /feedback/list`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "items": [
      {
        "id": 1,
        "feedback_type": "accuracy",
        "content": "检测结果很准确",
        "score": 5,
        "status": "completed",
        "admin_reply": "感谢您的反馈！",
        "submit_time": "2025-01-15T10:00:00"
      }
    ]
  }
}
```

---

## 统计接口 (Stats)

### 1. 获取系统统计

**接口**: `GET /stats/system`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 1000,
    "total_detections": 5000,
    "total_interventions": 3000,
    "online_users": 50,
    "detection_accuracy": 0.88
  }
}
```

### 2. 获取用户统计

**接口**: `GET /stats/user`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "detection_count": 20,
    "intervention_count": 15,
    "detection_trend": [
      {"date": "2025-01-01", "count": 2},
      {"date": "2025-01-02", "count": 3}
    ],
    "fatigue_distribution": {
      "light": 10,
      "medium": 8,
      "heavy": 2
    }
  }
}
```

---

## 2-back实验接口 (TwoBack)

### 1. 开始实验

**接口**: `POST /twoback/start`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "difficulty": "medium",      // easy/medium/hard
  "duration": 300              // 实验时长(秒)
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "实验开始",
  "data": {
    "experiment_id": "exp_123456",
    "start_time": "2025-01-15T10:30:00",
    "sequence": ["A", "B", "A", "C", "B"]
  }
}
```

### 2. 提交实验结果

**接口**: `POST /twoback/submit`

**请求头**: `Authorization: Bearer <token>`

**请求参数**:
```json
{
  "experiment_id": "exp_123456",
  "responses": [
    {"stimulus": "A", "response": "match", "reaction_time": 500},
    {"stimulus": "B", "response": "no_match", "reaction_time": 450}
  ]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "实验完成",
  "data": {
    "score": 85,
    "accuracy": 0.9,
    "average_reaction_time": 480,
    "analysis": "您的反应速度和准确率都表现良好"
  }
}
```

---

## 管理后台接口 (Admin)

### 1. 获取仪表盘数据

**接口**: `GET /admin/dashboard`

**请求头**: `Authorization: Bearer <token>` (需要管理员权限)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 1000,
    "today_new_users": 10,
    "total_detections": 5000,
    "today_detections": 50,
    "system_health": "good",
    "recent_activities": [...]
  }
}
```

### 2. 用户管理

#### 获取用户列表
**接口**: `GET /admin/users`

**查询参数**:
- `page`: 页码
- `page_size`: 每页数量
- `search`: 搜索关键词

#### 禁用/启用用户
**接口**: `PUT /admin/users/{user_id}/status`

**请求参数**:
```json
{
  "is_active": false
}
```

### 3. 音乐管理

#### 添加音乐
**接口**: `POST /admin/music`

**请求参数**:
```json
{
  "title": "string",
  "artist": "string",
  "music_type": "string",
  "fatigue_level": "string",
  "audio_url": "string",
  "cover": "string"
}
```

#### 更新音乐
**接口**: `PUT /admin/music/{music_id}`

#### 删除音乐
**接口**: `DELETE /admin/music/{music_id}`

### 4. 反馈管理

#### 获取反馈列表
**接口**: `GET /admin/feedback`

#### 回复反馈
**接口**: `POST /admin/feedback/{feedback_id}/reply`

**请求参数**:
```json
{
  "reply": "感谢您的反馈，我们会持续改进！"
}
```

---

## 错误码说明

### 通用错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400001 | 参数校验失败 | 检查请求参数格式和必填项 |
| 400002 | JSON解析错误 | 检查请求体格式 |
| 401001 | Token无效或过期 | 重新登录获取新Token |
| 401002 | 权限不足 | 检查用户权限 |
| 403001 | 访问被拒绝 | 联系管理员获取权限 |
| 404001 | 资源不存在 | 检查资源ID是否正确 |
| 500001 | 服务器内部错误 | 稍后重试或联系管理员 |

### 认证相关错误

| 错误码 | 说明 |
|--------|------|
| 400100 | 用户名已存在 |
| 400101 | 学号已存在 |
| 400102 | 邮箱已存在 |
| 400103 | 密码强度不足 |
| 401100 | 用户名或密码错误 |
| 401101 | 用户已被禁用 |

### 文件上传错误

| 错误码 | 说明 |
|--------|------|
| 400200 | 文件类型不支持 |
| 400201 | 文件大小超过限制 |
| 400202 | 文件上传失败 |
| 400203 | 文件解析失败 |

---

## 限流说明

为防止API滥用，系统实施以下限流策略：

| 接口类型 | 限流策略 |
|----------|----------|
| 认证接口 | 每分钟5次 |
| 普通接口 | 每分钟100次 |
| 文件上传 | 每分钟10次 |
| 检测接口 | 每分钟20次 |

超过限流将返回 `429 Too Many Requests` 状态码。

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2025-01-15 | 初始版本，包含基础功能 |
| v1.1.0 | 2025-02-01 | 新增联邦学习接口 |
| v1.2.0 | 2025-03-01 | 新增云存储文件上传 |

---

## 附录

### 音乐类型枚举

```javascript
const MusicType = {
  NATURAL: 'natural',     // 自然音效
  PIANO: 'piano',         // 钢琴
  WHITENOISE: 'whitenoise', // 白噪音
  MIX: 'mix'              // 混合
}
```

### 疲劳等级枚举

```javascript
const FatigueLevel = {
  LIGHT: 'light',         // 轻度
  MEDIUM: 'medium',       // 中度
  HEAVY: 'heavy'          // 重度
}
```

### 反馈类型枚举

```javascript
const FeedbackType = {
  ACCURACY: 'accuracy',   // 检测准确性
  MUSIC: 'music',         // 音乐推荐
  FUNCTION: 'function'    // 功能建议
}
```
