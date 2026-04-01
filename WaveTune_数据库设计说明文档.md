# WaveTune 数据库设计说明文档

## 文档概述

本文档详细说明了 WaveTune 脑疲劳检测与音乐干预系统的数据库设计，包括表结构、字段说明、关系设计、索引策略和初始数据。

## 数据库基本信息

- **数据库名称**: `wavetune`
- **字符集**: `utf8mb4`
- **排序规则**: `utf8mb4_0900_ai_ci`
- **存储引擎**: `InnoDB`
- **支持外键**: 是

## 表结构设计

### 1. 用户表 (user)

**功能**: 存储用户基本信息和统计数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 用户ID |
| username | varchar(50) | NOT NULL | 用户名 |
| student_id | varchar(20) | UNIQUE, NOT NULL | 学号 |
| password_hash | varchar(255) | NULL | 密码哈希 |
| email | varchar(100) | UNIQUE | 邮箱 |
| phone | varchar(20) | NULL | 手机号 |
| avatar | varchar(255) | DEFAULT '' | 头像路径 |
| detection_count | int | DEFAULT 0 | 检测次数 |
| intervention_count | int | DEFAULT 0 | 干预次数 |
| last_login_time | datetime | NULL | 最后登录时间 |
| is_active | tinyint(1) | DEFAULT 1 | 是否激活 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 注册时间 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引设计**:
- 主键: `id`
- 唯一索引: `student_id`, `email`
- 普通索引: `username`, `create_time`

**业务规则**:
- 学号必须唯一
- 邮箱必须唯一（如果提供）
- 用户名不能为空
- 支持软删除（通过 is_active 字段）

### 2. 用户反馈表 (feedback)

**功能**: 存储用户反馈信息和管理员回复

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 反馈ID |
| user_id | int | FK, NOT NULL | 用户ID |
| feedback_type | varchar(20) | NOT NULL | 反馈类型 |
| content | text | NOT NULL | 反馈内容 |
| score | int | NOT NULL | 满意度评分 |
| status | varchar(20) | DEFAULT 'pending' | 处理状态 |
| admin_reply | text | NULL | 管理员回复 |
| submit_time | datetime | DEFAULT CURRENT_TIMESTAMP | 提交时间 |
| reply_time | datetime | NULL | 回复时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 普通索引: `feedback_type`, `submit_time`

**业务规则**:
- 反馈类型: accuracy(检测准确性), music(音乐推荐), function(功能建议)
- 满意度评分: 1-5分
- 处理状态: pending(待处理), processing(处理中), completed(已完成)

### 3. 音乐表 (music)

**功能**: 存储音乐库信息和推荐数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 音乐ID |
| title | varchar(100) | NOT NULL | 音乐标题 |
| artist | varchar(100) | NULL | 艺术家/创作者 |
| duration | varchar(10) | NULL | 时长 |
| cover | varchar(255) | NULL | 封面图URL |
| audio_url | varchar(255) | NULL | 音频文件URL |
| reason | text | NULL | 推荐理由 |
| music_type | varchar(20) | NULL | 音乐类型 |
| fatigue_level | varchar(50) | NULL | 适配疲劳等级 |
| match_rate | int | DEFAULT 0 | 匹配度 |
| play_count | int | DEFAULT 0 | 播放次数 |
| scenes | varchar(100) | DEFAULT NULL | 适用场景，多个场景用逗号分隔 |
| is_active | tinyint(1) | DEFAULT 1 | 是否启用 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引设计**:
- 主键: `id`
- 普通索引: `music_type`, `fatigue_level`, `match_rate`, `is_active`
- 普通索引: `scenes`

**业务规则**:
- 音乐类型: natural(自然音效), piano(钢琴), whitenoise(白噪音), mix(混合)
- 疲劳等级: light(轻度), medium(中度), heavy(重度)，支持多值用逗号分隔
- 匹配度: 0-100分
- 支持软删除（通过 is_active 字段）

### 4. 场景表 (scene)

**功能**: 存储用户自定义场景和系统默认场景

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 场景ID |
| user_id | int | FK, NOT NULL | 用户ID |
| scene_name | varchar(50) | NOT NULL | 场景名称 |
| music_type | varchar(20) | NOT NULL | 音乐类型 |
| description | text | NULL | 场景描述 |
| is_default | tinyint(1) | DEFAULT 0 | 是否默认场景 |
| is_active | tinyint(1) | DEFAULT 1 | 是否启用 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 普通索引: `scene_name`, `is_default`
- 唯一索引: `user_id + scene_name`

**业务规则**:
- 同一用户不能有重名的场景
- 系统默认场景不能被删除
- 场景名称不能为空

### 5. 系统统计表 (system_stats)

**功能**: 存储系统运行统计数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 统计ID |
| stat_name | varchar(50) | UNIQUE, NOT NULL | 统计名称 |
| stat_value | varchar(20) | NOT NULL | 统计值 |
| stat_unit | varchar(10) | NULL | 单位 |
| description | varchar(255) | NULL | 描述 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引设计**:
- 主键: `id`
- 唯一索引: `stat_name`

**业务规则**:
- 统计名称必须唯一
- 支持实时更新统计数据

### 6. 用户会话表 (user_session)

**功能**: 管理用户登录会话和令牌

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 会话ID |
| user_id | int | FK, NOT NULL | 用户ID |
| session_token | varchar(255) | UNIQUE, NOT NULL | 会话令牌 |
| device_info | varchar(255) | NULL | 设备信息 |
| ip_address | varchar(45) | NULL | IP地址 |
| user_agent | text | NULL | 用户代理 |
| is_active | tinyint(1) | DEFAULT 1 | 是否活跃 |
| expire_time | datetime | NOT NULL | 过期时间 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| last_activity | datetime | DEFAULT CURRENT_TIMESTAMP | 最后活动时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 唯一索引: `session_token`
- 外键索引: `user_id`
- 普通索引: `expire_time`, `is_active`

**业务规则**:
- 会话令牌必须唯一
- 支持会话过期管理
- 记录用户登录设备信息

### 7. 用户偏好表 (user_preference)

**功能**: 存储用户个性化偏好设置

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 偏好ID |
| user_id | int | FK, NOT NULL | 用户ID |
| preference_key | varchar(50) | NOT NULL | 偏好键 |
| preference_value | text | NULL | 偏好值 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 唯一索引: `user_id + preference_key`

**业务规则**:
- 同一用户的偏好键必须唯一
- 支持键值对形式的偏好设置

### 8. 操作日志表 (operation_log)

**功能**: 记录系统操作日志和审计信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 日志ID |
| user_id | int | FK, NULL | 用户ID |
| operation_type | varchar(50) | NOT NULL | 操作类型 |
| operation_desc | varchar(255) | NULL | 操作描述 |
| request_method | varchar(10) | NULL | 请求方法 |
| request_url | varchar(255) | NULL | 请求URL |
| request_params | text | NULL | 请求参数 |
| response_status | int | NULL | 响应状态码 |
| ip_address | varchar(45) | NULL | IP地址 |
| user_agent | text | NULL | 用户代理 |
| execution_time | int | NULL | 执行时间(ms) |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**外键关系**:
- `user_id` → `user.id` (SET NULL)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 普通索引: `operation_type`, `create_time`

**业务规则**:
- 支持匿名操作记录
- 记录详细的请求和响应信息
- 用于系统审计和性能分析

### 9. 2-back 实验表 (two_back)

**功能**: 存储2-back实验相关数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 实验ID |
| user_id | int | FK, NOT NULL | 用户ID |
| experiment_config | json | NULL | 实验配置 |
| experiment_data | json | NULL | 实验数据 |
| result_score | int | NULL | 实验得分 |
| result_analysis | text | NULL | 结果分析 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 普通索引: `create_time`

**业务规则**:
- 存储用户的2-back实验数据
- 支持实验配置和结果分析

### 10. 联邦学习训练表 (federated_training)

**功能**: 存储联邦学习训练任务信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 训练ID |
| user_id | int | FK, NOT NULL | 用户ID |
| client_id | varchar(100) | NOT NULL | 客户端ID |
| round_number | int | DEFAULT 1 | 训练轮次 |
| status | varchar(20) | DEFAULT 'pending' | 训练状态 |
| fatigue_status | varchar(50) | NULL | 疲劳状态 |
| accuracy | float | NULL | 训练准确率 |
| loss | float | NULL | 训练损失 |
| training_time | datetime | DEFAULT CURRENT_TIMESTAMP | 训练时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 普通索引: `client_id`, `status`, `training_time`

**业务规则**:
- 训练状态: pending(等待中), training(训练中), completed(已完成), failed(失败)
- 记录每次联邦学习训练的详细信息和结果

### 11. 联邦学习设备表 (federated_device)

**功能**: 存储联邦学习参与设备信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 设备ID |
| user_id | int | FK, NOT NULL | 用户ID |
| device_id | varchar(100) | NOT NULL | 设备标识 |
| device_type | varchar(20) | DEFAULT 'local' | 设备类型 |
| status | varchar(20) | DEFAULT 'online' | 设备状态 |
| training_count | int | DEFAULT 0 | 训练次数 |
| contribution | float | DEFAULT 0 | 贡献值 |
| last_participate | datetime | NULL | 最后参与时间 |
| create_time | datetime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**外键关系**:
- `user_id` → `user.id` (CASCADE DELETE)

**索引设计**:
- 主键: `id`
- 外键索引: `user_id`
- 普通索引: `device_id`, `status`

**业务规则**:
- 设备类型: local(本地), remote(远程)
- 设备状态: online(在线), offline(离线), busy(忙碌)
- 记录设备的训练贡献和参与情况

### 12. 联邦学习统计表 (federated_stats)

**功能**: 存储联邦学习全局统计数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK, AUTO_INCREMENT | 统计ID |
| total_participants | int | DEFAULT 0 | 总参与人数 |
| total_rounds | int | DEFAULT 0 | 总训练轮次 |
| total_devices | int | DEFAULT 0 | 总设备数 |
| average_accuracy | float | DEFAULT 0 | 平均准确率 |
| average_loss | float | DEFAULT 0 | 平均损失 |
| update_time | datetime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引设计**:
- 主键: `id`

**业务规则**:
- 记录联邦学习的全局统计数据
- 支持实时更新统计信息

## 关系设计

### 主要关系图

```
user (1) ←→ (N) feedback
user (1) ←→ (N) scene
user (1) ←→ (N) user_session
user (1) ←→ (N) user_preference
user (1) ←→ (N) operation_log
user (1) ←→ (N) two_back
user (1) ←→ (N) federated_training
user (1) ←→ (N) federated_device
```

### 关系说明

1. **用户与反馈**: 一对多关系，一个用户可以有多个反馈
2. **用户与场景**: 一对多关系，一个用户可以创建多个场景
3. **用户与会话**: 一对多关系，一个用户可以同时有多个活跃会话
4. **用户与偏好**: 一对多关系，一个用户可以有多个偏好设置
5. **用户与日志**: 一对多关系，一个用户的操作会生成多条日志记录
6. **用户与2-back实验**: 一对多关系，一个用户可以进行多次2-back实验
7. **用户与联邦学习训练**: 一对多关系，一个用户可以参与多次联邦学习训练
8. **用户与联邦学习设备**: 一对多关系，一个用户可以使用多个设备参与联邦学习

## 索引策略

### 主键索引
- 所有表都使用自增整数作为主键
- 提供最佳的性能和存储效率

### 唯一索引
- `user.student_id`: 确保学号唯一性
- `user.email`: 确保邮箱唯一性
- `user_session.session_token`: 确保会话令牌唯一性
- `system_stats.stat_name`: 确保统计名称唯一性
- `user_preference(user_id, preference_key)`: 确保用户偏好键唯一性
- `scene(user_id, scene_name)`: 确保用户场景名称唯一性

### 外键索引
- 所有外键字段都建立索引，提高关联查询性能

### 业务索引
- 时间字段索引: 支持时间范围查询
- 状态字段索引: 支持状态筛选
- 分类字段索引: 支持分类查询

## 视图设计

### 1. 音乐统计视图 (music_stats_view)

**功能**: 提供音乐库的统计信息

**字段**:
- id: 音乐ID
- title: 音乐标题
- artist: 艺术家
- music_type: 音乐类型
- fatigue_level: 疲劳等级
- match_rate: 匹配度
- play_count: 播放次数
- is_active: 是否启用
- scene_usage_count: 场景使用次数

**用途**: 用于音乐管理页面的数据统计和展示

## 存储过程和触发器

### 1. 音乐更新时间触发器 (update_music_time)

**触发时机**: BEFORE UPDATE ON music
**功能**: 自动更新音乐的 update_time 字段

```sql
CREATE TRIGGER `update_music_time` 
BEFORE UPDATE ON `music` 
FOR EACH ROW 
BEGIN
    SET NEW.`update_time` = CURRENT_TIMESTAMP;
END
```

## 数据备份策略

### 备份方式
- **完全备份**: 每周日凌晨2点执行
- **增量备份**: 每天凌晨2点执行
- **实时备份**: 关键表使用TiDB Cloud的自动备份功能

### 备份内容
- 所有表结构和数据
- 存储过程和触发器
- 用户权限和配置

### 备份保留
- 完全备份: 保留4周
- 增量备份: 保留7天
- 实时备份: 由TiDB Cloud管理

## 性能优化

### 查询优化
- 使用EXPLAIN分析慢查询
- 为常用查询字段建立复合索引
- 避免全表扫描

### 写入优化
- 批量插入代替单条插入
- 使用事务保证数据一致性
- 合理设置连接池大小

### 存储优化
- 定期清理过期数据
- 归档历史数据
- 优化大字段存储

## 安全设计

### 数据加密
- 敏感字段使用加密存储
- 传输过程使用SSL/TLS
- 数据库连接使用SSL证书

### 访问控制
- 最小权限原则
- 角色基础的访问控制
- 操作日志记录

### 审计追踪
- 记录所有数据变更
- 保留操作历史
- 支持数据恢复
