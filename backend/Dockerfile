FROM ghcr.io/astral-sh/uv:0.9.25-python3.14-bookworm-slim

WORKDIR /app
ENV TZ=Asia/Taipei

# 讓 Python 可以直接把 /app 當成模組搜尋路徑，方便 import app.main 這類結構
# ENV PYTHONPATH=/app

# 要求 uv 在安裝套件時先編譯 .pyc
# 可稍微改善啟動與首次匯入速度，官方也有建議這種容器場景可開啟
ENV UV_COMPILE_BYTECODE=1

# 在 Docker 建置環境中使用 copy 而非 hardlink
# 這對 cache mount / bind mount 場景較穩定，避免檔案系統連結問題
ENV UV_LINK_MODE=copy

# 不安裝 dev dependencies, 只包含 production 需要的套件
ENV UV_NO_DEV=1

# 把專案虛擬環境的執行檔放到 PATH 前面
# 之後可直接執行 uvicorn，而不用寫完整路徑
ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*
# 安裝系統相依套件：
# - ca-certificates: HTTPS 憑證
# - curl: 下載金鑰與外部資源
# - gnupg: 驗證 / 匯入 repo 金鑰
# - unixodbc / unixodbc-dev: ODBC runtime 與開發標頭，常見於 pyodbc 場景
# 最後清掉 apt 索引，減少 image 體積

RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
# 加入 Microsoft 官方 Debian 12 套件來源並安裝 msodbcsql18
# 因為目前 base image 是 bookworm-slim，所以這裡要用 Debian 12 的 repo，不是 Ubuntu 22.04 的 repo
# ACCEPT_EULA=Y 是 Microsoft ODBC driver 安裝時必需條件
# 最後同樣清理 apt 快取以縮小映像

COPY pyproject.toml uv.lock ./
# 先只複製依賴描述檔
# 這樣只要依賴沒變，下面的 uv sync layer 就可以直接吃快取

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project
# 先安裝「第三方依賴」，但不安裝目前專案本身
# 這是官方推薦的分層方式：專案程式碼常變，但依賴通常不常變
# --locked 代表嚴格依照 uv.lock 安裝，避免 build 時重新解析版本
# cache mount 可保留 uv 的下載快取，提升重建速度

COPY . .
# 再把整個專案程式碼複製進容器
# 放在依賴安裝之後，可以最大化 Docker layer cache 效益

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
# 第二次同步：把目前專案本身也安裝進虛擬環境
# 因為前面的第三方套件通常已經裝好了，這層只需要補專案本身與少量變更

# 建立非 root 使用者並把 /app 權限交給它, 正式環境不建議用 root 跑 API 服務, 這是基本安全最佳實務
RUN groupadd --system --gid 1001 appuser \
    && useradd --system --uid 1001 --gid 1001 --create-home --home-dir /home/appuser appuser \
    && chown -R appuser:appuser /app

# 後續執行容器時，改用非 root 身份運行
USER appuser

EXPOSE 8000

# 清空 base image 可能預設帶的 entrypoint
# 避免啟動時被自動包一層 uv 指令，讓 CMD 行為更可預期
ENTRYPOINT []

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
