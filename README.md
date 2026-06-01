# videodl WebUI 🎬✨

基于 [CharlesPikachu/videodl](https://github.com/CharlesPikachu/videodl) 的 Web 面板，
支持 65+ 视频平台一键下载。

![screenshot]

## 特性

- 🖥️ **Web 界面** — 粘贴链接即可下载，无需命令行
- 📊 **实时进度** — WebSocket 推送下载状态
- 🎞️ **在线播放** — 下载后直接在浏览器播放
- 🌙 **深色/亮色** — 支持主题切换
- 🐳 **Docker 部署** — 一键启动
- 🎀 **二次元风 UI** — 好看又好用

## 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python server.py
```

打开 http://localhost:8000

### Docker 部署

```bash
docker compose up -d
```

打开 http://localhost:8000

## 支持的平台

抖音、快手、B站、小红书、YouTube、腾讯视频、优酷、爱奇艺、
A站、微博、知乎、虎牙、搜狐、皮皮虾、西瓜视频、芒果TV、
央视网、梨视频、TED、Reddit、DailyMotion 等 65+ 平台。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VIDEODL_OUTPUT` | `./videodl_outputs` | 下载文件输出目录 |
