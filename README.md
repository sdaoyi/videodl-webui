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

## 🚀 部署（服务器）

```bash
# 1. 克隆项目
git clone https://github.com/liangyu-love/videodl-webui.git
cd videodl-webui

# 2. 启动
docker compose up -d --build
```

打开 **http://你的服务器IP:9999**

> 需要安装 [Docker](https://docs.docker.com/engine/install/) 和 Docker Compose

### 本地运行（开发）

```bash
pip install fastapi uvicorn
pip install git+https://github.com/CharlesPikachu/videodl.git
python server.py
```

打开 http://localhost:9999

## ⚙️ 配置

### 修改端口

`docker-compose.yml` 里改端口映射：

```yaml
ports:
  - "8080:9999"   # 把 8080 换成你想要的公网端口
```

### 环境变量

在 `docker-compose.yml` 的 `environment` 下添加：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VIDEODL_OUTPUT` | `/app/videodl_outputs` | 下载文件输出目录 |
| `TZ` | `Asia/Shanghai` | 时区 |

### 下载文件位置

默认保存在项目目录下的 `videodl_outputs/`，通过 Docker volume 持久化。

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
