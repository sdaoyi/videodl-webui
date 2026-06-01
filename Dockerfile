FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --no-cache-dir fastapi uvicorn[standard]
RUN pip install --no-cache-dir git+https://github.com/CharlesPikachu/videodl.git

# 复制项目
COPY . .

# 创建输出目录
RUN mkdir -p videodl_outputs logs

EXPOSE 8000

ENV VIDEODL_OUTPUT=/app/videodl_outputs

CMD ["python", "server.py"]
