# videodl WebUI 🎬✨

基于 [CharlesPikachu/videodl](https://github.com/CharlesPikachu/videodl) 的 Web 面板，
支持 **65+ 视频平台**一键下载。抖音图文 / 视频均支持。

🖼️ 图片分组浏览 · ⬅️➡️ 前后切换 · 🖱️ 滚轮翻阅 · 🎀 初音未来网页宠物

## ✨ 特性

| 功能 | 说明 |
|------|------|
| 🔗 粘贴即下 | 支持抖音分享链接直接粘贴（含自动提取 URL） |
| 🖼️ 图文下载 | 抖音图集/图文帖子自动识别，图片自动归组 |
| 🎞️ 在线播放 | 视频 + 图片弹窗预览，← → 键盘 / 滚轮 / 滑动切换 |
| 📊 实时进度 | WebSocket 推送下载状态，状态指示灯 |
| 🌗 双主题 | 深色/亮色一键切换，紫粉樱花配色 |
| 🎀 网页宠物 | 初音未来在页面散步（Miku shimeji），可拖可摸 |
| 🐳 Docker | 一键部署，docker compose up -d |
| 📱 移动端 | 手机浏览器访问适配，触控 + 滑动手势 |

## 🚀 快速开始

### 本地运行

```bash
# 安装依赖（videodl 需从 GitHub 安装）
pip install fastapi uvicorn
pip install git+https://github.com/CharlesPikachu/videodl.git

# 启动
python server.py
```

打开 http://localhost:8000

### Docker 部署

```bash
docker compose up -d
```

## ⚙️ 配置

### 修改端口

`server.py` 最底部：

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # 改这里
```

或者在启动时指定：

```bash
uvicorn server:app --host 0.0.0.0 --port 9000
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VIDEODL_OUTPUT` | `./videodl_outputs` | 下载文件输出目录 |

### 反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";  # WebSocket 必须
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

⚠️ WebSocket 需要 `Upgrade` + `Connection` 头，否则下载进度不推送。

### systemd 服务（Linux 服务器）

```ini
# /etc/systemd/system/videodl-webui.service
[Unit]
Description=videodl WebUI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/videodl-webui
ExecStart=/opt/videodl-webui/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now videodl-webui
```

## 📦 支持的平台

抖音、快手、B站、小红书、YouTube、腾讯视频、优酷、爱奇艺、
A站、微博、知乎、虎牙、搜狐、皮皮虾、西瓜视频、芒果TV、
央视网、梨视频、TED、Reddit、DailyMotion 等 65+ 平台。

## 🖼️ 图集对比

| | 视频帖子 | 图文帖子 |
|--|---------|---------|
| 自动识别 | ✅ | ✅ |
| 文件展示 | 🎬 单文件 | 🖼️ 分组折叠 |
| 预览方式 | ▶ 播放器 | 👁️ 图片弹窗 |
| 前后切换 | ⬅️➡️ | ⬅️➡️ + 滚轮 |
