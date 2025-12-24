# WaveTune 后端 API 接口文档

## 文档说明

本文档详细描述了 WaveTune 脑疲劳检测与音乐干预系统的后端 API 接口，基于 FastAPI 框架实现，支撑前端 Vue 3 项目的所有交互功能。

### 基础信息
- **API 基础路径**: `http://localhost:8000/api`
- **数据格式**: JSON
- **响应格式**: 统一为 `{"code": 状态码, "msg": "提示信息", "data": 数据对象}`
- **状态码说明**: 200-成功, 400-参数错误, 404-资源不存在, 500-服务器错误

---

## 一、用户认证接口

### 1.1 用户注册

**接口描述**: 注册新用户账户

**请求信息**:
- **URL**: `/api/auth/register`
- **方法**: `POST`
- **请求体**:
```json
{
  "username": "李同学",
  "student_id": "2022001001",
  "password": "123456",
  "email": "li.student@example.com",
  "phone": "13800138001"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "user_id": 1,
    "username": "李同学",
    "student_id": "2022001001",
    "email": "li.student@example.com"
  }
}
```

### 1.2 用户登录

**接口描述**: 用户登录并获取会话令牌

**请求信息**:
- **URL**: `/api/auth/login`
- **方法**: `POST`
- **请求体**:
```json
{
  "student_id": "2022001001",
  "password": "123456",
  "device_info": "Chrome/Windows"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "李同学",
      "student_id": "2022001001",
      "email": "li.student@example.com",
      "phone": "13800138001",
      "avatar": "/static/avatar/default.jpg",
      "detection_count": 12,
      "intervention_count": 8,
      "is_active": true,
      "create_time": "2023-09-01T00:00:00",
      "update_time": "2023-10-10T15:30:00"
    },
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expire_time": "2023-10-11T15:30:00"
  }
}
```

### 1.3 用户登出

**接口描述**: 用户登出并使会话失效

**请求信息**:
- **URL**: `/api/auth/logout`
- **方法**: `POST`
- **请求体**:
```json
{
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "登出成功",
  "data": null
}
```

### 1.4 修改密码

**接口描述**: 修改用户密码

**请求信息**:
- **URL**: `/api/auth/change-password`
- **方法**: `POST`
- **请求头**: `Authorization: Bearer <session_token>`
- **请求体**:
```json
{
  "old_password": "123456",
  "new_password": "newpassword123"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "密码修改成功",
  "data": null
}
```

### 1.5 获取用户资料

**接口描述**: 获取用户详细信息和偏好设置

**请求信息**:
- **URL**: `/api/auth/profile`
- **方法**: `GET`
- **请求头**: `Authorization: Bearer <session_token>`
- **参数**: `user_id` (Query, 必填)

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "username": "李同学",
    "student_id": "2022001001",
    "email": "li.student@example.com",
    "phone": "13800138001",
    "avatar": "/static/avatar/default.jpg",
    "detection_count": 12,
    "intervention_count": 8,
    "is_active": true,
    "create_time": "2023-09-01T00:00:00",
    "update_time": "2023-10-10T15:30:00",
    "preferences": {
      "default_fatigue_level": "medium",
      "preferred_music_type": "natural",
      "notification_enabled": "true",
      "auto_play": "false"
    }
  }
}
```

### 1.6 更新用户资料

**接口描述**: 更新用户基本信息

**请求信息**:
- **URL**: `/api/auth/profile`
- **方法**: `PUT`
- **请求头**: `Authorization: Bearer <session_token>`
- **请求体**:
```json
{
  "username": "李同学",
  "email": "li.student@example.com",
  "phone": "13800138001"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "资料更新成功",
  "data": {
    "id": 1,
    "username": "李同学",
    "student_id": "2022001001",
    "email": "li.student@example.com",
    "phone": "13800138001",
    "avatar": "/static/avatar/default.jpg",
    "detection_count": 12,
    "intervention_count": 8,
    "is_active": true,
    "create_time": "2023-09-01T00:00:00",
    "update_time": "2023-10-10T16:00:00"
  }
}
```

### 1.7 更新用户偏好

**接口描述**: 更新用户偏好设置

**请求信息**:
- **URL**: `/api/auth/preference`
- **方法**: `PUT`
- **请求头**: `Authorization: Bearer <session_token>`
- **请求体**:
```json
{
  "preference_key": "default_fatigue_level",
  "preference_value": "light"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "偏好设置更新成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "preference_key": "default_fatigue_level",
    "preference_value": "light",
    "create_time": "2023-09-01T00:00:00",
    "update_time": "2023-10-10T16:00:00"
  }
}
```

### 1.8 获取用户会话列表

**接口描述**: 获取用户的所有活跃会话

**请求信息**:
- **URL**: `/api/auth/sessions`
- **方法**: `GET`
- **请求头**: `Authorization: Bearer <session_token>`
- **参数**: `user_id` (Query, 必填)

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "sessions": [
      {
        "id": 1,
        "user_id": 1,
        "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "device_info": "Chrome/Windows",
        "ip_address": "192.168.1.100",
        "is_active": true,
        "expire_time": "2023-10-11T15:30:00",
        "create_time": "2023-10-10T15:30:00",
        "last_activity": "2023-10-10T16:00:00"
      }
    ]
  }
}
```

### 1.9 撤销会话

**接口描述**: 使指定会话失效

**请求信息**:
- **URL**: `/api/auth/session/{session_id}`
- **方法**: `DELETE`
- **请求头**: `Authorization: Bearer <session_token>`
- **参数**: `session_id` (Path, 必填), `user_id` (Query, 必填)

**响应示例**:
```json
{
  "code": 200,
  "msg": "会话已撤销",
  "data": null
}
```

---

## 二、系统统计接口

### 1.1 获取系统统计数据

**接口描述**: 获取首页展示的系统统计数据

**请求信息**:
- **URL**: `/api/system/stats`
- **方法**: `GET`
- **参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "stats": [
      {
        "id": 1,
        "value": "1,234",
        "label": "检测次数",
        "icon": "DataAnalysis",
        "iconClass": "detection"
      },
      {
        "id": 2,
        "value": "856",
        "label": "干预次数",
        "icon": "Headphones",
        "iconClass": "music"
      },
      {
        "id": 3,
        "value": "12",
        "label": "参与设备",
        "icon": "Monitor",
        "iconClass": "devices"
      },
      {
        "id": 4,
        "value": "89.2%",
        "label": "模型准确率",
        "icon": "TrendCharts",
        "iconClass": "accuracy"
      }
    ]
  }
}
```

---

## 二、用户信息管理接口

### 2.1 获取用户信息

**接口描述**: 根据用户ID获取用户详细信息

**请求信息**:
- **URL**: `/api/user/info`
- **方法**: `GET`
- **参数**: 
  - `user_id` (Query, 必填): 用户ID

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "username": "李同学",
    "student_id": "2022001001",
    "avatar": "/static/avatar/1.jpg",
    "detection_count": 12,
    "intervention_count": 8,
    "create_time": "2023-09-01T00:00:00",
    "update_time": "2023-10-10T15:30:00"
  }
}
```

### 2.2 更新用户信息

**接口描述**: 更新用户基本信息

**请求信息**:
- **URL**: `/api/user/update`
- **方法**: `PUT`
- **请求体**:
```json
{
  "user_id": 1,
  "username": "李同学",
  "student_id": "2022001001"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "信息修改成功",
  "data": {
    "id": 1,
    "username": "李同学",
    "student_id": "2022001001",
    "avatar": "/static/avatar/1.jpg",
    "detection_count": 12,
    "intervention_count": 8,
    "update_time": "2023-10-10T16:00:00"
  }
}
```

### 2.3 上传用户头像

**接口描述**: 上传用户头像文件

**请求信息**:
- **URL**: `/api/user/avatar/upload`
- **方法**: `POST`
- **参数**: 
  - `user_id` (Form): 用户ID
  - `avatar` (File): 头像文件 (支持 jpg/png)

**响应示例**:
```json
{
  "code": 200,
  "msg": "头像上传成功",
  "data": {
    "avatar_url": "/static/avatar/1_20231010.jpg"
  }
}
```

### 2.4 更新用户统计次数

**接口描述**: 更新用户的检测或干预次数

**请求信息**:
- **URL**: `/api/user/count/update`
- **方法**: `PUT`
- **请求体**:
```json
{
  "user_id": 1,
  "type": "detection",
  "count": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "次数更新成功",
  "data": {
    "detection_count": 13,
    "intervention_count": 8
  }
}
```

---

## 三、用户反馈接口

### 3.1 提交用户反馈

**接口描述**: 提交用户反馈信息

**请求信息**:
- **URL**: `/api/feedback/submit`
- **方法**: `POST`
- **请求体**:
```json
{
  "user_id": 1,
  "feedback_type": "accuracy",
  "content": "检测结果比较准确，希望能增加更多疲劳等级的分类",
  "score": 4
}
```

**参数说明**:
- `feedback_type`: 反馈类型 (accuracy-脑疲劳检测准确性, music-轻音乐推荐效果, function-系统功能建议)
- `content`: 反馈内容 (10-500字)
- `score`: 满意度评分 (1-5)

**响应示例**:
```json
{
  "code": 200,
  "msg": "反馈提交成功",
  "data": {
    "feedback_id": 1,
    "submit_time": "2023-10-10T16:00:00"
  }
}
```

### 3.2 查询历史反馈

**接口描述**: 分页查询用户历史反馈记录

**请求信息**:
- **URL**: `/api/feedback/history`
- **方法**: `GET`
- **参数**: 
  - `user_id` (Query, 必填): 用户ID
  - `page` (Query, 可选): 页码，默认1
  - `page_size` (Query, 可选): 每页条数，默认5

**响应示例**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "total": 3,
    "list": [
      {
        "id": 1,
        "feedback_type": "accuracy",
        "feedback_type_name": "脑疲劳检测准确性",
        "content": "检测结果比较准确，希望能增加更多疲劳等级的分类",
        "score": 4,
        "submit_time": "2023-10-10T16:00:00"
      }
    ],
    "page": 1,
    "page_size": 5
  }
}
```

### 3.3 删除历史反馈

**接口描述**: 删除指定用户的一条反馈记录（仅允许删除本人提交的反馈）

**请求信息**:
- **URL**: `/api/feedback/{feedback_id}`
- **方法**: `DELETE`
- **参数**:
  - `feedback_id` (Path, 必填): 反馈 ID
  - `user_id` (Query, 必填): 请求方用户 ID（用于校验是否为本人）

**响应示例**:
```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

**常见错误**:
- 400: 参数缺失或格式错误
- 403: 非反馈所有者尝试删除
- 404: 反馈不存在


---

## 四、音乐推荐接口

### 4.1 获取音乐推荐列表

**接口描述**: 根据疲劳等级和音乐类型获取推荐音乐列表

**请求信息**:
- **URL**: `/api/music/recommend`
- **方法**: `GET`
- **参数**: 
  - `fatigue_level` (Query, 必填): 疲劳等级 (light/medium/heavy)
  - `music_type` (Query, 可选): 音乐类型 (natural/piano/whitenoise/mix)

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "music_list": [
      {
        "id": 1,
        "title": "森林雨声与钢琴",
        "artist": "自然白噪音工作室",
        "duration": "05:30",
        "cover": "/static/music_cover/1.jpg",
        "reason": "帮助中度疲劳放松，降低 β 波活跃度",
        "music_type": "natural",
        "fatigue_level": "light,medium",
        "match_rate": 98
      }
    ]
  }
}
```

### 4.2 获取音乐详情

**接口描述**: 根据音乐ID获取音乐详细信息

**请求信息**:
- **URL**: `/api/music/detail`
- **方法**: `GET`
- **参数**: 
  - `music_id` (Query, 必填): 音乐ID

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "title": "森林雨声与钢琴",
    "artist": "自然白噪音工作室",
    "duration": "05:30",
    "cover": "/static/music_cover/1.jpg",
    "reason": "帮助中度疲劳放松，降低 β 波活跃度",
    "music_type": "natural",
    "fatigue_level": "light,medium",
    "match_rate": 98
  }
}
```

### 4.3 获取音乐列表（管理/展示通用）

**接口描述**: 获取系统内的音乐列表（用于前端展示与管理）

**请求信息**:
- **URL**: `/api/music/list`
- **方法**: `GET`
- **参数**: 可选分页/筛选参数
  - `page` (Query, 可选)
  - `page_size` (Query, 可选)
  - `music_type` (Query, 可选)
  - `fatigue_level` (Query, 可选)

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total": 12,
    "list": [
      {
        "id": 1,
        "title": "森林雨声与钢琴",
        "artist": "自然白噪音工作室",
        "duration": "05:30",
        "cover": "/static/music_cover/1.jpg",
        "src": "http://localhost:8000/static/music/forest_rain_piano.mp3",
        "reason": "帮助中度疲劳放松",
        "music_type": "natural",
        "fatigue_level": "light,medium",
        "match_rate": 98
      }
    ],
    "page": 1,
    "page_size": 10
  }
}
```

> 注意: 返回的 `src` 字段通常为后端生成的可直接访问的完整 URL（例如 `http://<host>:<port>/static/music/xxx.mp3`），前端播放时应使用该字段以避免跨主机路径错误。

### 4.4 添加音乐（元数据入库）

**接口描述**: 将一条音乐记录添加到数据库（若已上传文件则使用 `audio_url` / `src`）

**请求信息**:
- **URL**: `/api/music`
- **方法**: `POST`
- **请求体** (JSON):
```json
{
  "title": "森林雨声与钢琴",
  "artist": "自然白噪音工作室",
  "duration": "05:30",
  "cover": "/static/music_cover/1.jpg",
  "audio_url": "http://localhost:8000/static/music/forest_rain_piano.mp3",
  "music_type": "natural",
  "fatigue_level": "light,medium",
  "reason": "帮助中度疲劳放松",
  "match_rate": 98
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "添加成功",
  "data": {
    "id": 13,
    "title": "森林雨声与钢琴",
    "audio_url": "http://localhost:8000/static/music/forest_rain_piano.mp3"
  }
}
```

### 4.5 删除音乐

**接口描述**: 根据音乐 ID 删除音乐记录（以及可选的静态文件）

**请求信息**:
- **URL**: `/api/music/{music_id}`
- **方法**: `DELETE`
- **参数**:
  - `music_id` (Path, 必填)
  - `delete_files` (Query, 可选, 布尔): 是否同时删除存储的音频/封面文件，默认为 false

**响应示例**:
```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 4.6 上传音频文件（multipart/form-data）

**接口描述**: 上传音频文件到后端静态目录，后端会尝试解析元数据（如标题、艺术家、时长）并返回可直接访问的 `src` URL 与解析到的元信息。

**请求信息**:
- **URL**: `/api/music/upload`
- **方法**: `POST`
- **请求体**: multipart/form-data（FormData）
  - `file` (File): 音频文件 (支持 mp3, wav 等)

**前端注意**:
- 使用 `FormData` 上传时，不要在请求头手动设置 `Content-Type`（让浏览器/axios 自动设置 boundary）。
- 上传完成后，后端返回的 `src` 字段为完整可访问URL，可直接用于 `<audio>` 播放器。

**响应示例**:
```json
{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "src": "http://localhost:8000/static/music/forest_rain_piano.mp3",
    "src_rel": "/static/music/forest_rain_piano.mp3",
    "metadata": {
      "title": "森林雨声与钢琴",
      "artist": "自然白噪音工作室",
      "duration": "05:30"
    }
  }
}
```

**可选依赖**:
- 后端若安装 `mutagen` 库，将尝试从音频文件解析更多元数据；若未安装，上传仍会成功，但 `metadata` 可能为空或只包含时长（后端可通过 HTML5 audio 解析时长并返回）。

### 4.7 上传封面图片（multipart/form-data）

**接口描述**: 上传音乐封面图片并返回可直接访问的 URL

**请求信息**:
- **URL**: `/api/music/upload_cover`
- **方法**: `POST`
- **请求体**: multipart/form-data
  - `file` (File): 封面图片 (jpg/png/webp)

**响应示例**:
```json
{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "cover": "http://localhost:8000/static/music_cover/cover_20251118_1234.jpg",
    "cover_rel": "/static/music_cover/cover_20251118_1234.jpg"
  }
}
```

**前端建议**:
- 上传封面后，使用返回的 `cover`(完整 URL) 填充表单并显示预览。
- 对图片大小与格式做客户端校验（例如限制 < 5MB, 仅允许 jpg/png/webp）。


---

## 五、场景配置接口

### 5.1 获取场景列表

**接口描述**: 获取用户的所有场景配置（包括系统默认场景）

**请求信息**:
- **URL**: `/api/scene/list`
- **方法**: `GET`
- **参数**: 
  - `user_id` (Query, 必填): 用户ID

**响应示例**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "scene_list": [
      {
        "id": 1,
        "scene_name": "学习场景",
        "music_type": "piano",
        "is_default": 1,
        "create_time": "2023-09-01T00:00:00"
      },
      {
        "id": 2,
        "scene_name": "我的专注场景",
        "music_type": "natural",
        "is_default": 0,
        "create_time": "2023-10-01T10:00:00"
      }
    ]
  }
}
```

### 5.2 创建场景

**接口描述**: 创建用户自定义场景

**请求信息**:
- **URL**: `/api/scene/create`
- **方法**: `POST`
- **请求体**:
```json
{
  "user_id": 1,
  "scene_name": "我的专注场景",
  "music_type": "natural"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "场景创建成功",
  "data": {
    "id": 2,
    "scene_name": "我的专注场景",
    "music_type": "natural",
    "is_default": 0,
    "create_time": "2023-10-10T16:00:00"
  }
}
```

### 5.3 应用场景

**接口描述**: 应用指定场景，返回场景配置信息

**请求信息**:
- **URL**: `/api/scene/apply`
- **方法**: `GET`
- **参数**: 
  - `scene_id` (Query, 必填): 场景ID
  - `user_id` (Query, 必填): 用户ID

**响应示例**:
```json
{
  "code": 200,
  "msg": "应用成功",
  "data": {
    "scene_name": "学习场景",
    "music_type": "piano"
  }
}
```

### 5.4 删除场景

**接口描述**: 删除用户自定义场景（不允许删除系统默认场景）

**请求信息**:
- **URL**: `/api/scene/delete`
- **方法**: `DELETE`
- **参数**: 
  - `scene_id` (Query, 必填): 场景ID
  - `user_id` (Query, 必填): 用户ID

**响应示例**:
```json
{
  "code": 200,
  "msg": "场景删除成功",
  "data": null
}
```

---

## 六、错误响应格式

### 6.1 参数错误 (400)
```json
{
  "code": 400,
  "msg": "参数缺失或格式错误",
  "data": null
}
```

### 6.2 资源不存在 (404)
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

### 6.3 服务器错误 (500)
```json
{
  "code": 500,
  "msg": "数据库操作失败，请重试",
  "data": null
}
```

### 6.4 业务逻辑错误
```json
{
  "code": 400,
  "msg": "场景名称已存在",
  "data": null
}
```

---

## 七、数据模型说明

### 7.1 用户模型 (User)
```json
{
  "id": "integer, 主键",
  "username": "string, 用户名",
  "student_id": "string, 学号(唯一)",
  "avatar": "string, 头像路径",
  "detection_count": "integer, 检测次数",
  "intervention_count": "integer, 干预次数",
  "create_time": "datetime, 创建时间",
  "update_time": "datetime, 更新时间"
}
```

### 7.2 音乐模型 (Music)
```json
{
  "id": "integer, 主键",
  "title": "string, 音乐标题",
  "artist": "string, 艺术家",
  "duration": "string, 时长(如05:30)",
  "cover": "string, 封面图URL",
  "reason": "string, 推荐理由",
  "music_type": "string, 音乐类型",
  "fatigue_level": "string, 适配疲劳等级(逗号分隔)",
  "match_rate": "integer, 匹配度(1-100)"
}
```

### 7.3 反馈模型 (Feedback)
```json
{
  "id": "integer, 主键",
  "user_id": "integer, 用户ID(外键)",
  "feedback_type": "string, 反馈类型",
  "content": "string, 反馈内容",
  "score": "integer, 满意度评分(1-5)",
  "submit_time": "datetime, 提交时间"
}
```

### 7.4 场景模型 (Scene)
```json
{
  "id": "integer, 主键",
  "user_id": "integer, 用户ID(外键)",
  "scene_name": "string, 场景名称",
  "music_type": "string, 音乐类型",
  "create_time": "datetime, 创建时间",
  "is_default": "integer, 是否默认场景(0/1)"
}
```

---

## 八、接口测试说明

### 8.1 测试环境
- **开发环境**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs` (FastAPI自动生成)
- **测试工具**: Postman 或 curl

### 8.2 测试数据
系统初始化时会自动创建以下测试数据：
- 测试用户: 李同学 (ID: 1, 学号: 2022001001)
- 8-10条音乐数据 (覆盖不同疲劳等级和音乐类型)
- 3个系统默认场景
- 系统统计数据

### 8.3 跨域配置
后端已配置CORS，允许前端 `http://localhost:5173` 访问所有接口。

---

## 九、部署说明

### 9.1 环境要求
- Python 3.8+
- MySQL 8.0+ 或 SQLite
- FastAPI
- SQLAlchemy
- 其他依赖见 requirements.txt

### 9.2 启动命令
```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 9.3 生产环境
建议使用 Gunicorn + Nginx 部署，并配置HTTPS和数据库连接池。


