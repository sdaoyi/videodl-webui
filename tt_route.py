# TT WebUI — 对接 TikTokDownloader API (port 5555)
# 需要先运行 TikTokDownloader 的 API 服务器

@app.get("/tt")
async def tt_index():
    return HTMLResponse(Path(__file__).parent.joinpath("templates", "tt.html").read_text(encoding="utf-8"))
