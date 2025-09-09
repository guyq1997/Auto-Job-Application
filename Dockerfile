# 使用Python 3.13官方镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（浏览器运行所需）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Node.js（Playwright需要）
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制项目文件
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# 创建结果目录
RUN mkdir -p /app/results

# 设置权限
RUN chmod +x /app/scripts/*.py

# 默认命令
CMD ["python", "-m", "scripts.docker_runner"]
