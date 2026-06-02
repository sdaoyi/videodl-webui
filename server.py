"""
videodl WebUI — 视频下载 Web 面板
FastAPI + WebSocket 进度推送
"""

import io
import asyncio
import json
import os
import sys
import threading
import time
import logging
from datetime import datetime
from pathlib import Path

# fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import re

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from videodl.videodl import VideoClient

# ── 配置 ──────────────────────────────────────────────
_BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = Path(os.environ.get("VIDEODL_OUTPUT", str(_BASE_DIR / "videodl_outputs"))).resolve()
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR = _BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 文件日志
logging.basicConfig(
    filename=str(LOG_DIR / "server.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("videodl-webui")

app = FastAPI(title="videodl WebUI")

# 挂载静态文件（webmeji 精灵 sprite 等）
app.mount("/static", StaticFiles(directory=str(_BASE_DIR / "static")), name="static")

# ── 全局状态 ──────────────────────────────────────────
downloads: list[dict] = []
download_lock = threading.Lock()
ws_clients: set[WebSocket] = set()


# ── 已知平台列表 ──────────────────────────────────────
KNOWN_PLATFORMS = [
    ("", "自动检测"),
    ("DouyinVideoClient", "抖音 (Douyin)"),
    ("KuaishouVideoClient", "快手 (Kuaishou)"),
    ("BilibiliVideoClient", "B站 (Bilibili)"),
    ("RednoteVideoClient", "小红书 (RedNote)"),
    ("YouTubeVideoClient", "YouTube"),
    ("TencentVideoClient", "腾讯视频"),
    ("YoukuVideoClient", "优酷"),
    ("IQiyiVideoClient", "爱奇艺"),
    ("AcFunVideoClient", "A站 (AcFun)"),
    ("WeiboVideoClient", "微博"),
    ("ZhihuVideoClient", "知乎"),
    ("HuyaVideoClient", "虎牙"),
    ("SohuVideoClient", "搜狐"),
    ("PipixVideoClient", "皮皮虾"),
    ("XiguaVideoClient", "西瓜视频"),
    ("MGTVVideoClient", "芒果TV"),
    ("CCTVVideoClient", "央视网"),
    ("PearVideoClient", "梨视频"),
    ("TedVideoClient", "TED"),
    ("RedditVideoClient", "Reddit"),
    ("DailyMotionVideoClient", "DailyMotion"),
]


def _default_cfg():
    return {"work_dir": str(OUTPUT_DIR), "disable_print": False}


# ── WebSocket 广播 ────────────────────────────────────
async def broadcast(msg: dict):
    global ws_clients
    dead = set()
    for ws in ws_clients:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.add(ws)
    ws_clients -= dead


# ── 写下载日志 ────────────────────────────────────────
def _write_log(task_id: str, text: str):
    log_path = LOG_DIR / f"download_{task_id}.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(text)
    return str(log_path)


# ── 图片下载工具 ──────────────────────────────────────
import urllib.request
import re as _re
import hashlib

def _extract_image_urls(info) -> list[str] | None:
    """从解析结果中提取图集 URL 列表（抖音图文等），失败返回 None"""
    try:
        raw = info.raw_data.get("loaderData", {})
        for key in raw:
            if "page" in key or "video" in key:
                page = raw[key]
                if isinstance(page, dict):
                    item_list = page.get("videoInfoRes", {}).get("item_list", [])
                    if item_list:
                        item = item_list[0]
                        images = item.get("images")
                        if images and isinstance(images, list) and len(images) > 0:
                            urls = []
                            for img in images:
                                # 优先用 download_url_list（无水印高清版）
                                dl = img.get("download_url_list", [])
                                ul = img.get("url_list", [])
                                u = None
                                if dl: u = dl[0]
                                elif ul: u = ul[0]
                                if u: urls.append(u)
                            if urls:
                                return urls
    except Exception:
        pass
    return None


def _download_images(title: str, urls: list[str], info) -> list[str]:
    """下载图片到以标题命名的子目录，返回保存路径列表"""
    import uuid, http.cookiejar
    safe_title = _re.sub(r'[\\/*?:"<>|#\s]', '_', title)[:80]
    save_dir = OUTPUT_DIR / safe_title
    save_dir.mkdir(parents=True, exist_ok=True)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    saved = []
    for i, url in enumerate(urls):
        try:
            ext = ".webp"
            fname = f"{i+1:02d}_{uuid.uuid4().hex[:6]}{ext}"
            fpath = save_dir / fname
            req = urllib.request.Request(
                url,
                headers={
                    "Referer": "https://www.douyin.com/",
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                    "Accept": "image/webp,image/*,*/*",
                },
            )
            with opener.open(req) as resp:
                fpath.write_bytes(resp.read())
            if fpath.exists() and fpath.stat().st_size > 0:
                saved.append(str(fpath))
                log.info(f"downloaded image {i+1}/{len(urls)}: {fpath}")
        except Exception as e:
            log.error(f"image {i+1}/{len(urls)} failed: {e}")
    return saved


# ── 后台下载任务 ──────────────────────────────────────
def _run_download(task_id: str, url: str, platform: str | None):
    global downloads
    log_text = ""

    def _status(status: str, message: str, **extra):
        """线程安全的状态更新"""
        with download_lock:
            for d in downloads:
                if d["id"] == task_id:
                    d["status"] = status
                    d["message"] = message
                    d["updated_at"] = time.time()
                    d.update(extra)
                    break
        # 异步推送
        data = {"id": task_id, "status": status, "message": message, "updated_at": time.time(), **extra}
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            asyncio.ensure_future(broadcast(data))
        else:
            loop.run_until_complete(broadcast(data))

    _status("parsing", "正在解析链接...")
    log.info(f"[{task_id}] parsing: {url}")

    try:
        # videodl 0.8.9 bug: allowed_video_sources=None → TypeError
        # workaround: 传空列表让 videodl 自己填充所有平台
        allowed = []
        if platform:
            allowed = [p.strip() for p in platform.split(",") if p.strip()]
        client_kwargs = {
            "init_video_clients_cfg": {"*": _default_cfg()},
            "allowed_video_sources": allowed,
        }

        client = VideoClient(**client_kwargs)

        # 捕获标准输出作为日志
        old_stdout, old_stderr = sys.stdout, sys.stderr
        capture = io.StringIO()
        sys.stdout = capture
        sys.stderr = capture

        try:
            video_infos = client.parsefromurl(url)
            log_text = capture.getvalue()

            if not video_infos:
                msg = "无法解析该视频链接，请检查 URL 或尝试指定平台"
                _status("failed", msg)
                log.info(f"[{task_id}] failed: {msg}")
                return

            info = video_infos[0]
            title = (info.title or url).strip()

            # ── 检查是否为图集（抖音图文 / 图片帖子）──
            image_urls = _extract_image_urls(info)
            if image_urls:
                _status("downloading", f"正在下载 {len(image_urls)} 张图片: {title}",
                        title=title, source=info.source or "unknown", ext="jpg",
                        image_count=len(image_urls))
                saved = _download_images(title, image_urls, info)
                log_text += capture.getvalue()
                if saved:
                    _status("completed", f"已下载 {len(saved)} 张图片",
                            save_path=str(saved[0]), size=os.path.getsize(saved[0]),
                            size_str=f"{len(saved)} 张",
                            images=[str(p) for p in saved])
                    log.info(f"[{task_id}] images completed: {len(saved)} pics")
                else:
                    _status("failed", "图片下载失败")
                if log_text.strip():
                    _write_log(task_id, log_text)
                return

            # ── 普通视频下载 ──
            _status("downloading", f"正在下载: {title}",
                    title=title,
                    source=info.source or "unknown",
                    ext=info.ext or "mp4")

            client.download(video_infos)
            log_text = capture.getvalue()

            save_path = info.save_path
            if save_path and os.path.exists(save_path):
                size = os.path.getsize(save_path)
                _status("completed", "下载完成!",
                        save_path=str(save_path),
                        size=size,
                        size_str=_fmt_size(size))
                log.info(f"[{task_id}] completed: {save_path} ({_fmt_size(size)})")
            else:
                _status("failed", f"下载未产出文件，检查 {OUTPUT_DIR}")
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log.error(f"[{task_id}] error: {e}\n{tb}")
        _status("failed", f"{type(e).__name__}: {e}")

    # 保存日志文件
    if log_text.strip():
        log_file = _write_log(task_id, log_text)
        with download_lock:
            for d in downloads:
                if d["id"] == task_id:
                    d["log_file"] = log_file
                    d["log_preview"] = log_text[-2000:]
                    break


def _extract_url(text: str) -> str:
    """从分享文案中提取视频链接"""
    # 匹配 http/https URL
    urls = re.findall(r'https?://[^\s]+', text)
    if urls:
        # 取最后一个 URL（通常是视频链接）
        url = urls[-1].rstrip('.,;:!?）)')
        # 去掉抖音短链接后面跟的乱码参数
        url = re.sub(r'[\u4e00-\u9fff].*$', '', url)
        return url.strip()
    return text


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ── API 路由 ──────────────────────────────────────────

@app.post("/api/download")
async def api_download(data: dict):
    raw = data.get("url", "").strip()
    platform = data.get("platform", "").strip() or None

    if not raw:
        return {"ok": False, "error": "请输入视频链接"}

    # 自动从分享文案提取 URL
    url = _extract_url(raw)
    if not url.startswith("http"):
        return {"ok": False, "error": f"未识别到有效链接: {url[:60]}"}

    log.info(f"extracted URL: {url} (raw: {raw[:50]}...)")

    task_id = f"{int(time.time() * 1000)}"
    task = {
        "id": task_id,
        "url": url,
        "platform": platform,
        "status": "queued",
        "message": "排队中...",
        "title": "",
        "source": "",
        "ext": "",
        "save_path": "",
        "size": 0,
        "size_str": "",
        "created_at": time.time(),
        "updated_at": time.time(),
    }
    with download_lock:
        downloads.insert(0, task)

    threading.Thread(target=_run_download, args=(task_id, url, platform), daemon=True).start()

    return {"ok": True, "task": task}


@app.get("/api/history")
async def api_history():
    return {"downloads": downloads}


@app.get("/api/files")
async def api_files():
    files = []
    if OUTPUT_DIR.exists():
        # 扫描 OUTPUT_DIR 及其一级子目录（每个平台一个子目录）
        dirs_to_scan = [OUTPUT_DIR] + [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
        for scan_dir in dirs_to_scan:
            for f in scan_dir.iterdir():
                if f.is_file():
                    rel = str(f.relative_to(OUTPUT_DIR)).replace("\\", "/")
                    # 查询参数格式避免 # 等特殊字符问题
                    from urllib.parse import quote
                    video_url = f"/api/video?p={quote(rel, safe='')}"
                    files.append({
                        "name": f.name,
                        "path": str(f),
                        "rel_path": rel,
                        "video_url": video_url,
                        "size": f.stat().st_size,
                        "size_str": _fmt_size(f.stat().st_size),
                        "mtime": f.stat().st_mtime,
                    })
        files.sort(key=lambda x: x["mtime"], reverse=True)
    return {"files": files, "output_dir": str(OUTPUT_DIR)}


@app.delete("/api/files")
async def api_delete_file(data: dict):
    """删除已下载的文件"""
    rel_path = data.get("path", "").strip()
    if not rel_path:
        return {"ok": False, "error": "未指定文件路径"}
    full_path = OUTPUT_DIR / rel_path
    # 安全检查：防止路径穿越
    try:
        full_path.resolve().relative_to(OUTPUT_DIR.resolve())
    except ValueError:
        return {"ok": False, "error": "非法的文件路径"}
    if not full_path.exists() or not full_path.is_file():
        return {"ok": False, "error": "文件不存在"}
    try:
        os.remove(full_path)
        log.info(f"deleted file: {full_path}")
        return {"ok": True}
    except Exception as e:
        log.error(f"delete failed: {full_path} — {e}")
        return {"ok": False, "error": str(e)}


@app.get("/api/platforms")
async def api_platforms():
    return {"platforms": [{"value": v, "label": l} for v, l in KNOWN_PLATFORMS]}


@app.get("/api/log/{task_id}")
async def api_log(task_id: str):
    log_path = LOG_DIR / f"download_{task_id}.log"
    if log_path.exists():
        return {"ok": True, "log": log_path.read_text(encoding="utf-8")}
    return {"ok": False, "error": "日志不存在"}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    global ws_clients
    await ws.accept()
    ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)


@app.get("/api/video")
async def serve_video(p: str = ""):
    """提供视频文件播放 — 用查询参数避免 # 等特殊字符问题"""
    full_path = OUTPUT_DIR / p
    if not p or not full_path.exists() or not full_path.is_file():
        return HTMLResponse("file not found", status_code=404)
    # 根据扩展名判断 MIME 类型
    ext = full_path.suffix.lower()
    mime_map = {
        ".mp4": "video/mp4", ".webm": "video/webm", ".mkv": "video/x-matroska",
        ".mov": "video/quicktime", ".avi": "video/x-msvideo", ".flv": "video/x-flv",
        ".ts": "video/mp2t",
        ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".bmp": "image/bmp",
    }
    return FileResponse(full_path, media_type=mime_map.get(ext, "video/mp4"))


@app.get("/")
async def index():
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(
        html_path.read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


if __name__ == "__main__":
    import uvicorn
    os.chdir(str(_BASE_DIR))  # 确保 videodl 输出到项目目录
    print(f"Download dir: {OUTPUT_DIR}")
    print(f"Log dir:     {LOG_DIR}")
    print(f"Open:        http://localhost:9999")
    uvicorn.run(app, host="0.0.0.0", port=9999, log_level="info")
