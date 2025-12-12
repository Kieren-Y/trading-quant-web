这份技术实现文档基于之前的 PRD 编写，专注于工程落地细节。我们将构建一个模块化、高可扩展的 Python 项目 `DataHub`。

---

# DataHub 技术实现文档 (Technical Specification)

## 1. 项目结构设计 (Project Structure)

为了满足未来的扩展性（例如加入 News 采集），我们将采用**插件化（Adapter Pattern）**的目录结构。核心逻辑与具体数据源解耦。

```text
datahub/
├── pyproject.toml              # Poetry 依赖管理与工具配置
├── poetry.lock
├── README.md
├── .pre-commit-config.yaml     # Git Hook 配置
├── .env.example                # 环境变量模版
├── src/
│   └── datahub/
│       ├── __init__.py
│       ├── core/               # 核心引擎层
│       │   ├── __init__.py
│       │   ├── engine.py       # 主循环/任务调度
│       │   ├── event_bus.py    # 内部消息分发 (Observer Pattern)
│       │   └── config.py       # Pydantic Settings 配置加载
│       │
│       ├── models/             # 统一数据模型层 (Data Schema)
│       │   ├── __init__.py
│       │   ├── base.py         # 基础模型 (含 raw_data 定义)
│       │   ├── market.py       # 行情模型 (Kline, Symbol)
│       │   └── account.py      # 账户模型 (Order, Balance, Trade)
│       │
│       ├── connectors/         # 连接器层 (数据源插件)
│       │   ├── __init__.py
│       │   ├── base.py         # 抽象基类 (Abstract Base Class)
│       │   │
│       │   ├── exchanges/      # 交易所实现
│       │   │   ├── __init__.py
│       │   │   ├── binance/    # Binance 实现 (Rest + WS)
│       │   │   ├── okx/        # OKX 实现
│       │   │   └── gate/       # Gate.io 实现
│       │   │
│       │   └── news/           # [扩展预留] 新闻源实现
│       │       ├── __init__.py
│       │       ├── gpt_crawler/
│       │       └── twitter/
│       │
│       ├── storage/            # 持久化层
│       │   ├── __init__.py
│       │   ├── database.py     # TimescaleDB/Postgres 连接
│       │   └── cache.py        # Redis 连接
│       │
│       └── utils/              # 工具库
│           ├── logger.py
│           └── time_helper.py
│
└── tests/                      # 测试用例 (结构对应 src)
    ├── connectors/
    ├── models/
    └── ...
```

### 设计亮点：
*   **Connectors 分组**：将 `exchanges` 和未来的 `news` 分开，互不干扰。
*   **Models 独立**：数据定义与业务逻辑分离，便于其他微服务复用该模块（打包成 shared lib）。
*   **Core 抽象**：`engine.py` 不关心数据来自 Binance 还是 Twitter，只处理标准化的 `Event`。

---

## 2. 包管理与开发工具链 (Tooling)

### 2.1 依赖管理 (Poetry)

使用 `poetry` 进行依赖锁定和虚拟环境管理。

**`pyproject.toml` 配置示例：**

```toml
[tool.poetry]
name = "datahub"
version = "0.1.0"
description = "High-performance crypto data acquisition system"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
pydantic = "^2.5.0"          # 数据验证核心
pydantic-settings = "^2.0.0" # 配置管理
aiohttp = "^3.9.0"           # 异步 HTTP 客户端
websockets = "^12.0"         # 基础 WS 库
asyncpg = "^0.29.0"          # 异步 PostgreSQL 驱动
redis = "^5.0.0"             # Redis 客户端
# 交易所 SDK (按需固定版本)
binance-connector = "^3.0.0"
gate-api = "^4.0.0"
# 注意：OKX 官方 SDK 可能不支持最新的 asyncio，建议封装 raw requests 或使用特定 fork

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.23.0"
black = "^23.11.0"
isort = "^5.12.0"
mypy = "^1.7.0"
pre-commit = "^3.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# --- 格式化工具配置 ---
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
```

### 2.2 代码质量守门员 (Pre-commit)

在项目根目录创建 `.pre-commit-config.yaml`，确保提交前自动格式化。

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

**启用命令：**
```bash
poetry install
poetry run pre-commit install
```

---

## 3. 统一数据模型设计 (Unified Data Models)

使用 `Pydantic v2` 定义模型。为了满足需求，我们在基础模型中包含了 `raw_payload` 字段以存储原始数据。

文件：`src/datahub/models/base.py`

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

class ExchangeType(str, Enum):
    BINANCE = "BINANCE"
    OKX = "OKX"
    GATE = "GATE"

class EventType(str, Enum):
    KLINE = "KLINE"
    ORDER_UPDATE = "ORDER_UPDATE"
    BALANCE_UPDATE = "BALANCE_UPDATE"
    TRADE = "TRADE"

class BaseDataModel(BaseModel):
    """所有数据模型的基类"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    exchange: ExchangeType
    symbol: str  # 统一格式，例如 BTC_USDT
    timestamp: int = Field(..., description="毫秒级时间戳")

    # --- 关键需求：保留源数据 ---
    # exclude=True 表示默认序列化时不包含，但在调试或写入RawDB时可访问
    raw_payload: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
```

文件：`src/datahub/models/market.py`

```python
from decimal import Decimal
from .base import BaseDataModel

class KlineData(BaseDataModel):
    """K线数据模型"""
    period: str  # 1m, 5m, 1h
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    amount: Decimal # 成交额 (Quote Volume)
    num_trades: int
    is_closed: bool # 核心字段：是否为已完结的Bar

class SymbolInfo(BaseDataModel):
    """交易对静态信息"""
    base_asset: str
    quote_asset: str
    min_qty: Decimal
    tick_size: Decimal
    contract_val: Optional[Decimal] = None # 合约面值 (仅合约有效)
```

文件：`src/datahub/models/account.py`

```python
from decimal import Decimal
from enum import Enum
from typing import Optional
from .base import BaseDataModel

class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"

class OrderData(BaseDataModel):
    """订单数据模型"""
    order_id: str
    client_order_id: Optional[str] = None
    side: str # BUY / SELL
    type: str # LIMIT / MARKET
    price: Decimal
    quantity: Decimal
    filled_qty: Decimal = Decimal("0")
    filled_avg_price: Optional[Decimal] = None
    status: OrderStatus

class BalanceData(BaseDataModel):
    """资产余额模型"""
    asset: str          # USDT, BTC
    wallet_balance: Decimal # 钱包余额
    available_balance: Decimal # 可用余额
    unrealized_pnl: Decimal = Decimal("0") # 未实现盈亏
```

---

## 4. 连接器抽象层实现 (Connector Abstraction)

为了方便后续添加 News 或其他交易所，必须定义严格的接口。

文件：`src/datahub/connectors/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Callable, Awaitable
from src.datahub.models.market import KlineData, SymbolInfo
from src.datahub.models.account import OrderData, BalanceData

class BaseConnector(ABC):
    def __init__(self, api_key: str, api_secret: str, passphrase: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase

    # --- REST API 方法 (同步/异步均可，推荐异步) ---

    @abstractmethod
    async def fetch_symbols(self) -> List[SymbolInfo]:
        """获取交易对规则"""
        pass

    @abstractmethod
    async def fetch_kline_history(self, symbol: str, period: str, limit: int = 100) -> List[KlineData]:
        """获取历史K线 (用于补漏)"""
        pass

    @abstractmethod
    async def fetch_balance(self) -> List[BalanceData]:
        """REST方式拉取全量资产"""
        pass

    @abstractmethod
    async def fetch_funding_history(self, symbol: str) -> List[dict]:
        """拉取资金费率/流水记录"""
        pass

    # --- WebSocket 方法 ---

    @abstractmethod
    async def connect(self):
        """建立WS连接并处理鉴权"""
        pass

    @abstractmethod
    async def subscribe_market_data(self, symbols: List[str], callback: Callable[[KlineData], Awaitable[None]]):
        """订阅公共行情"""
        pass

    @abstractmethod
    async def subscribe_account_data(self, callback: Callable[[any], Awaitable[None]]):
        """订阅私有订单/资产推送"""
        pass
```

## 5. 核心逻辑：Normalizer (示例)

以 Binance K线解析为例，展示如何将 `raw_data` 存入并标准化的过程。

文件：`src/datahub/connectors/exchanges/binance/parser.py`

```python
from decimal import Decimal
from src.datahub.models.market import KlineData, ExchangeType

def parse_binance_kline(payload: dict) -> KlineData:
    """
    Binance WS Payload Example:
    {
      "e": "kline",
      "s": "BTCUSDT",
      "k": {
        "t": 123400000,
        "o": "0.0010",
        "c": "0.0020",
        "x": true  <-- is_closed
        ...
      }
    }
    """
    k = payload['k']

    return KlineData(
        exchange=ExchangeType.BINANCE,
        symbol=k['s'], # 可以在此处调用工具函数转换为内部 symbol (BTC_USDT)
        timestamp=k['t'],
        period=k['i'],
        open=Decimal(k['o']),
        high=Decimal(k['h']),
        low=Decimal(k['l']),
        close=Decimal(k['c']),
        volume=Decimal(k['v']),
        amount=Decimal(k['q']),
        num_trades=k['n'],
        is_closed=k['x'],
        raw_payload=payload  # 将原始数据保存
    )
```

## 6. 后续扩展性规划

1.  **添加 News 采集**：
    *   在 `src/datahub/connectors/news/` 下新建 `twitter.py`。
    *   定义新的 Model: `NewsEvent(BaseDataModel)`，包含 `headline`, `content`, `sentiment_score`。
    *   由于 `BaseConnector` 定义了基础规范，News Connector 可以选择性实现 `fetch_history`，或者定义一个新的接口 `BaseStreamConnector`。

2.  **Raw Data 存储策略**：
    *   在 `storage` 层，可以将标准化的字段写入 SQL 数据库（方便查询）。
    *   同时将 `model.raw_payload` 异步写入 MongoDB 或以 Parquet 文件形式存入 S3/MinIO（用于数据回放和Debug）。 -- 先以文档的形式存放


这份技术文档规范了开发流程和代码结构，能够确保团队协作时代码风格统一，且数据模型具备高度的严谨性。
