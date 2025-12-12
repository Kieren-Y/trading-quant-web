针对 **DataHub** 这种后台常驻型（Long-running）的数据采集系统，最推荐的部署方式是 **Docker 容器化部署**，配合 **Docker Compose** 进行编排。这种方式能确保运行环境与开发环境一致，且易于管理依赖服务（Redis, TimescaleDB）。

以下是详细的启动与部署方案：

---

# DataHub 启动与部署指南

## 1. 准备工作：环境配置

在任何部署开始前，必须先配置敏感信息。项目根目录下创建 `.env` 文件（不要提交到 Git）：

```bash
# .env
ENV=production
LOG_LEVEL=INFO

# 数据库连接
DATABASE_URL=postgresql://user:password@timescaledb:5432/datahub
REDIS_URL=redis://redis:6379/0

# 交易所 API Keys (严禁硬编码在代码中)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_secret

OKX_API_KEY=your_okx_key
OKX_SECRET=your_okx_secret
OKX_PASSPHRASE=your_okx_pass

GATE_KEY=your_gate_key
GATE_SECRET=your_gate_secret
```

---

## 2. 方式一：Docker 容器化部署（推荐）

这是生产环境的标准做法。我们将 DataHub 打包成镜像，并使用 Docker Compose 一键拉起所有服务。

### 2.1 编写 `Dockerfile`
在项目根目录创建 `Dockerfile`：

```dockerfile
# 使用轻量级 Python 3.10 镜像
FROM python:3.10-slim as builder

# 设置环境变量，防止生成 pyc 文件，并在 stdout 输出日志
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.0

# 安装系统依赖 (如果有需要编译的库，如 asyncpg 可能需要 gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install "poetry==$POETRY_VERSION"

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 配置 poetry 不创建虚拟环境（在容器内直接装在系统 Python）
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 复制源代码
COPY src ./src
COPY README.md ./

# 定义启动命令
# 假设入口文件是 src/datahub/core/engine.py 中的 main 函数
CMD ["python", "-m", "src.datahub.core.engine"]
```

### 2.2 编写 `docker-compose.yml`
编排 DataHub、Redis 和 TimescaleDB。

```yaml
version: '3.8'

services:
  # 核心采集服务
  datahub:
    build: .
    container_name: datahub_core
    restart: always  # 崩溃自动重启
    env_file:
      - .env
    depends_on:
      - redis
      - timescaledb
    networks:
      - trading_net
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

  # 消息队列 / 实时缓存
  redis:
    image: redis:7.2-alpine
    container_name: trading_redis
    restart: always
    ports:
      - "6379:6379"
    networks:
      - trading_net

  # 时序数据库 (存储 K线 / Trade / OrderLog)
  timescaledb:
    image: timescale/timescaledb:latest-pg14
    container_name: trading_db
    restart: always
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=datahub
    ports:
      - "5432:5432"
    volumes:
      - ./data/pgdata:/var/lib/postgresql/data
    networks:
      - trading_net

networks:
  trading_net:
    driver: bridge
```

### 2.3 启动与管理命令

```bash
# 1. 启动所有服务 (后台运行)
docker-compose up -d --build

# 2. 查看实时日志
docker-compose logs -f datahub

# 3. 停止服务
docker-compose down

# 4. 更新代码后重新部署
git pull
docker-compose up -d --build datahub
```

---

## 3. 方式二：本地开发/调试启动 (Poetry)

在开发阶段，不使用 Docker，直接在本地运行。

### 3.1 安装依赖
确保本地已安装 Python 3.10+ 和 Poetry。

```bash
# 安装依赖
poetry install

# 激活虚拟环境 (可选，也可以直接用 poetry run)
poetry shell
```

### 3.2 启动 Redis 和 DB (本地开发版)
可以使用 Docker 快速拉起基础服务，但本地运行 Python 代码。

```bash
# 只启动 redis 和 db，不启动 datahub 容器
docker-compose up -d redis timescaledb
```

### 3.3 运行代码
确保你已经定义了入口脚本（例如在 `src/datahub/core/engine.py` 中有 `if __name__ == "__main__":` 块）。

```bash
# 加载 .env 环境变量并运行
# 建议安装 python-dotenv 来让 python 自动读取 .env，或者手动 export
export $(cat .env | xargs) && poetry run python -m src.datahub.core.engine
```

---

## 4. 方式三：传统服务器部署 (Systemd)

如果你不想用 Docker 运行 Python 代码，可以使用 Systemd 将其注册为 Linux 服务。

### 4.1 安装环境
```bash
cd /opt/datahub
poetry install --no-dev
```

### 4.2 创建 Systemd 配置文件
创建文件 `/etc/systemd/system/datahub.service`：

```ini
[Unit]
Description=DataHub Crypto Collector Service
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/datahub
# 加载环境变量
EnvironmentFile=/opt/datahub/.env
# 使用 poetry 的虚拟环境 Python 路径
ExecStart=/root/.cache/pypoetry/virtualenvs/datahub-xyz/bin/python -m src.datahub.core.engine
Restart=on-failure
RestartSec=5s
# 输出日志到 Syslog
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=datahub

[Install]
WantedBy=multi-user.target
```

### 4.3 管理服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable datahub
sudo systemctl start datahub
sudo systemctl status datahub
```

---

## 5. 启动流程代码实现 (Entry Point)

为了让上述命令生效，你需要一个健壮的入口文件。
文件：`src/datahub/core/engine.py`

```python
import asyncio
import logging
import signal
import sys
from src.datahub.core.config import settings
from src.datahub.connectors.exchanges.binance import BinanceConnector
# from src.datahub.connectors.exchanges.okx import OKXConnector

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DataHub")

class DataHubEngine:
    def __init__(self):
        self.running = True
        self.connectors = []

        # 初始化连接器
        if settings.BINANCE_API_KEY:
            self.connectors.append(BinanceConnector(settings.BINANCE_API_KEY, settings.BINANCE_SECRET))
        # if settings.OKX_API_KEY: ...

    async def start(self):
        logger.info("Starting DataHub Engine...")

        # 1. 建立数据库/Redis连接
        # await db.connect()

        # 2. 启动所有连接器
        tasks = [c.connect() for c in self.connectors]

        # 3. 订阅数据
        # await self.connectors[0].subscribe_market_data(...)

        logger.info("DataHub Engine Started. Press Ctrl+C to stop.")

        # 保持运行
        await asyncio.gather(*tasks)

    async def shutdown(self):
        logger.info("Shutting down...")
        self.running = False
        # 关闭连接逻辑
        # await db.disconnect()

def main():
    engine = DataHubEngine()

    loop = asyncio.get_event_loop()

    # 优雅退出信号处理 (Docker stop 发送 SIGTERM)
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(engine.shutdown()))

    try:
        loop.run_until_complete(engine.start())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        logger.info("Exited gracefully.")

if __name__ == "__main__":
    main()
```

## 6. 总结建议

1.  **首选 Docker Compose**：它解决了依赖管理、日志轮转和自动重启问题，且易于迁移。
2.  **日志管理**：不要将日志写入本地文件（容易写满磁盘），建议直接输出到标准输出（Stdout），由 Docker logs 管理，或通过 Filebeat 采集到 ELK。
3.  **健康检查**：建议在 `DataHubEngine` 中开启一个极简的 HTTP Server (使用 `aiohttp`) 暴露 `/health` 接口，供 Docker Healthcheck 探测进程是否假死。
