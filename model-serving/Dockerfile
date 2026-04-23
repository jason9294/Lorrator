# ---- Base: NVIDIA CUDA 12.6 + Ubuntu 22.04 ----
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_PYTHON=3.14

# 安裝系統依賴（MSSQL ODBC + build tools）
# 不透過 OS 套件安裝 Python，改由 uv 管理 Python 版本
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
        https://packages.microsoft.com/ubuntu/22.04/prod jammy main" \
        > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv（從官方映像複製二進制檔）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# 由 uv 自行下載並管理 Python 3.14
RUN uv python install 3.14

# 先複製依賴描述檔（利用 Docker layer cache）
COPY pyproject.toml uv.lock* ./

# 安裝所有 production 依賴（torch 會從 pytorch-cu126 index 安裝 CUDA 版本）
RUN uv sync --no-dev --no-cache

# 複製應用程式原始碼
COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
