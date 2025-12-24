验证 Add‑Music 弹窗与 Music 表 ID 重置（本地开发）

说明
----
该文档列出在本地验证 Add‑Music 弹窗可见性/功能及如何安全地重置 `music` 表自增（id）的方法。

前置条件
----
- 已安装 Node.js / npm
- 已安装并配置后端 Python 环境（建议虚拟环境）且已安装 requirements.txt
- 数据库（MySQL / SQLite）可访问，且 `backend/config/database.py` 中的 `DATABASE_URL` 正确指向要操作的开发库

本地启动（PowerShell）
----
1) 启动后端（在项目根）：

```powershell
# 进入 backend 文件夹
cd d:\Code\Vue\wavetune\backend
# 激活你的 Python 虚拟环境（示例）
# & C:/path/to/venv/Scripts/Activate.ps1
# 安装依赖（若尚未安装）
pip install -r requirements.txt
# 启动（依据项目启动脚本）
python start.py
# 或者使用 uvicorn（如果 start.py 不是启动入口）
# uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

2) 启动前端（在项目根）：

```powershell
cd d:\Code\Vue\wavetune
npm install # 若尚未安装依赖
npm run serve
```

验证 Add‑Music 弹窗按钮可见性和功能
----
- 访问前端页面（npm run serve 输出的本地地址），进入音乐推荐页。
- 点击顶部“添加音乐”按钮，弹窗打开后应看到：
  - 左侧“选择音频”按钮与“上传”按钮（用于上传音频）
  - 右侧“选择图片”与“上传封面”按钮
  - 底部“添加音乐”按钮
- 操作顺序建议：
  1. 点击“选择音频”，选择一个 mp3/wav 文件，然后点击“上传”。观察页面右侧表单是否自动填充标题/时长/封面（若后端能解析元数据）。
  2. 如果需要，使用“选择图片”并上传封面。
  3. 在右侧选择“音乐类型”，填写/确认其他字段，点击“添加音乐”。
  4. 在音乐列表中查看新增条目。

调试不可见问题
----
若仍看不到按钮：
- 打开浏览器 DevTools（F12）检查 DOM，确认按钮元素存在但被隐藏（display: none、visibility:hidden、opacity:0），并查看覆盖样式来自哪个 CSS 文件。
- 在 DevTools 中直接修改样式（例如 remove display: none）观察是否恢复显示。
- 请把控制台的 CSS 规则截图或把相关样式片段复制给我，我可以基于真实样式继续定位并修复。

重置 music 表 ID（风险提示）
----
如果你确定要把 `music` 表的 id 从 1 开始（开发用途），可使用我们提供的脚本 `backend/scripts/reset_music_table.py`：

```powershell
# 在项目根（或 backend 目录）运行
python backend/scripts/reset_music_table.py
```

脚本会读取 `backend/config/database.py` 中的 `DATABASE_URL`，并要求在控制台输入 `YES` 以确认操作。
- MySQL：脚本优先尝试 TRUNCATE TABLE music（会重置 AUTO_INCREMENT），如失败会尝试 DELETE + ALTER TABLE AUTO_INCREMENT = 1。
- SQLite：脚本会 DELETE FROM music 并尝试清空 sqlite_sequence 中的记录。

重要：该脚本会删除数据。请先备份生产/重要数据。

后续
----
把你在浏览器 DevTools 中看到的具体隐藏样式或控制台错误发给我，或允许我在工作区本地启动并运行 dev server (我会把输出日志贴回)。我可以根据真实运行时的样式覆盖继续修复，或把最终的修复合并到全局样式中以避免冲突。