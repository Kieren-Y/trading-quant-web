# DataHub AI Tool 集成需求文档

本文档定义了应用平台通过 AI Tool 调用 DataHub API 的集成需求，供 AI Coding 工具参考实现。

## 概述

DataHub API 提供加密货币市场数据服务，包括：
- **市场数据**: K 线、行情、订单簿
- **账本数据**: 余额、订单、成交、转账
- **管理功能**: 交易对管理、任务监控、数据回填、日志查询

## AI Tool 定义规范

### Tool 命名规范

```
datahub_{action}_{resource}
```

示例：
- `datahub_get_klines` - 获取 K 线数据
- `datahub_list_symbols` - 列出交易对
- `datahub_backfill_orders` - 回填订单数据

### Tool 分类

| 分类 | 前缀 | 描述 |
|------|------|------|
| 查询类 | `get_` / `list_` | 只读查询操作 |
| 操作类 | `update_` / `subscribe_` | 修改操作 |
| 回填类 | `backfill_` | 数据回填任务 |
| 系统类 | `health_` | 系统状态检查 |

---

## Tool 定义列表

### 1. 市场数据 Tools

#### datahub_get_klines

获取 K 线（蜡烛图）数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol` | string | 否 | 交易对，如 `BTC_USDT.BNC` |
| `exchange` | string | 否 | 交易所代码：`BNC`, `OKX`, `GIO` |
| `interval` | string | 否 | K 线周期：`1m`, `5m`, `15m`, `1h`, `1d`，默认 `1h` |
| `limit` | int | 否 | 返回数量，默认 100，最大 10000 |
| `offset` | int | 否 | 跳过数量，默认 0 |
| `after` | string | 否 | 开始时间（ISO 8601） |
| `before` | string | 否 | 结束时间（ISO 8601） |
| `search` | string | 否 | 模糊搜索 |

**返回**: K 线数据列表，包含 OHLCV 数据

**示例调用**:
```json
{
  "tool": "datahub_get_klines",
  "parameters": {
    "symbol": "BTC_USDT.BNC",
    "interval": "1h",
    "limit": 24,
    "after": "2026-01-14T00:00:00Z"
  }
}
```

#### datahub_get_tickers

获取实时行情数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol` | string | 否 | 交易对 |
| `exchange` | string | 否 | 交易所代码 |
| `limit` | int | 否 | 返回数量，默认 100 |
| `search` | string | 否 | 模糊搜索 |

**返回**: 行情数据列表，包含最新价、买卖价、24h 变动等

#### datahub_get_orderbook

获取订单簿数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol` | string | 否 | 交易对 |
| `exchange` | string | 否 | 交易所代码 |
| `limit` | int | 否 | 返回数量，默认 20 |

**返回**: 订单簿快照列表，包含买卖盘档位

---

### 2. 账本数据 Tools

#### datahub_get_balances

获取账户余额历史。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `account` | string | 否 | 账户，如 `BNC_MM01` |
| `asset` | string | 否 | 资产代码，如 `USDT` |
| `limit` | int | 否 | 返回数量，默认 100 |
| `after` | string | 否 | 开始时间 |
| `before` | string | 否 | 结束时间 |

**返回**: 余额快照列表

#### datahub_get_balances_latest

获取账户最新余额。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `account` | string | 否 | 账户 |
| `asset` | string | 否 | 资产代码 |
| `limit` | int | 否 | 返回数量，默认 100 |

**返回**: 最新余额状态列表

#### datahub_get_orders

获取订单数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `order_id` | string | 否 | 订单 ID |
| `client_order_id` | string | 否 | 客户端订单 ID |
| `symbol` | string | 否 | 交易对 |
| `account` | string | 否 | 账户 |
| `side` | string | 否 | 方向：`buy`, `sell` |
| `status` | string | 否 | 状态：`new`, `filled`, `canceled` |
| `limit` | int | 否 | 返回数量 |
| `after` | string | 否 | 开始时间 |
| `before` | string | 否 | 结束时间 |

**返回**: 订单列表

#### datahub_get_fills

获取成交数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `order_id` | string | 否 | 订单 ID |
| `trade_id` | string | 否 | 成交 ID |
| `symbol` | string | 否 | 交易对 |
| `account` | string | 否 | 账户 |
| `side` | string | 否 | 方向 |
| `limit` | int | 否 | 返回数量 |
| `after` | string | 否 | 开始时间 |
| `before` | string | 否 | 结束时间 |

**返回**: 成交记录列表

#### datahub_get_transfers

获取转账数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `account` | string | 否 | 账户 |
| `asset` | string | 否 | 资产代码 |
| `transfer_type` | string | 否 | 类型：`deposit`, `withdraw`, `transfer` |
| `transfer_id` | string | 否 | 转账 ID |
| `tx_hash` | string | 否 | 交易哈希 |
| `limit` | int | 否 | 返回数量 |
| `after` | string | 否 | 开始时间 |
| `before` | string | 否 | 结束时间 |

**返回**: 转账记录列表

---

### 3. 交易对管理 Tools

#### datahub_list_symbols

列出交易对。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `search` | string | 否 | 搜索关键词 |
| `limit` | int | 否 | 返回数量，默认 50 |
| `offset` | int | 否 | 跳过数量 |

**返回**: 交易对列表

#### datahub_get_symbol

获取交易对详情。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol_id` | int | 是 | 交易对 ID |

**返回**: 交易对详细信息

#### datahub_update_symbol

更新交易对。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol_id` | int | 是 | 交易对 ID |
| `is_active` | bool | 否 | 是否活跃 |
| `is_subscribed` | bool | 否 | 是否订阅 |

**返回**: 更新后的交易对信息

#### datahub_subscribe_symbol

订阅/取消订阅交易对。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol_id` | int | 是 | 交易对 ID |
| `is_subscribed` | bool | 是 | 是否订阅 |

**返回**: 更新后的交易对信息

---

### 4. 任务管理 Tools

#### datahub_list_jobs

列出定时任务。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `search` | string | 否 | 搜索关键词 |
| `limit` | int | 否 | 返回数量 |

**返回**: 任务配置列表

#### datahub_get_job

获取任务详情。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | string | 是 | 任务 ID 或名称 |

**返回**: 任务详细信息

#### datahub_list_job_executions

列出所有任务执行记录。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `search` | string | 否 | 搜索关键词 |
| `limit` | int | 否 | 返回数量 |
| `after` | string | 否 | 开始时间 |
| `before` | string | 否 | 结束时间 |

**返回**: 执行记录列表

#### datahub_get_job_executions

获取指定任务的执行记录。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | string | 是 | 任务 ID 或名称 |
| `search` | string | 否 | 搜索关键词 |
| `limit` | int | 否 | 返回数量 |
| `after` | string | 否 | 开始时间 |
| `before` | string | 否 | 结束时间 |

**返回**: 执行记录列表

---

### 5. 数据回填 Tools

#### datahub_backfill_klines

回填 K 线数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbols` | list[string] | 否 | 交易对列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |
| `intervals` | list[string] | 是 | K 线周期列表 |
| `start_time` | string | 是 | 开始时间（ISO 8601） |
| `end_time` | string | 否 | 结束时间 |

**返回**: 任务提交结果，包含 trace_id

#### datahub_backfill_symbols

回填交易对数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 是 | 交易所列表 |

**返回**: 任务提交结果

#### datahub_backfill_balances

回填余额数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `accounts` | list[string] | 是 | 账户列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |

**返回**: 任务提交结果

#### datahub_backfill_orders

回填订单数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `accounts` | list[string] | 否 | 账户列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |
| `symbols` | list[string] | 否 | 交易对列表 |
| `start_time` | string | 否 | 开始时间 |
| `end_time` | string | 否 | 结束时间 |

**返回**: 任务提交结果

#### datahub_backfill_fills

回填成交数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `accounts` | list[string] | 否 | 账户列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |
| `symbols` | list[string] | 否 | 交易对列表 |
| `start_time` | string | 否 | 开始时间 |
| `end_time` | string | 否 | 结束时间 |

**返回**: 任务提交结果

#### datahub_backfill_transfers

回填转账数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `accounts` | list[string] | 否 | 账户列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |
| `start_time` | string | 否 | 开始时间 |
| `end_time` | string | 否 | 结束时间 |

**返回**: 任务提交结果

#### datahub_backfill_orderbook

回填订单簿数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbols` | list[string] | 否 | 交易对列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |
| `limit` | int | 否 | 订单簿深度 |

**返回**: 任务提交结果

#### datahub_backfill_ticker

回填行情数据。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbols` | list[string] | 否 | 交易对列表 |
| `exchanges` | list[string] | 否 | 交易所列表 |

**返回**: 任务提交结果

---

### 6. 日志查询 Tools

#### datahub_list_logs

查询应用日志。

**参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `date` | string | 否 | 日期（YYYY-MM-DD） |
| `level` | string | 否 | 级别：`DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `namespace` | string | 否 | 命名空间 |
| `mode` | string | 否 | 模式：`batch`, `streamer` |
| `log_type` | string | 否 | 类型：`batch`, `streamer`, `scheduler`, `error`, `app` |
| `job_id` | string | 否 | 任务 ID / Trace ID |
| `message_contains` | string | 否 | 消息包含内容 |
| `limit` | int | 否 | 返回数量 |

**返回**: 日志记录列表

---

### 7. 系统 Tools

#### datahub_health_check

检查系统健康状态。

**参数**: 无

**返回**: 系统健康状态，包含各组件详情

---

## 实现指南

### 1. HTTP 客户端封装

```python
class DataHubClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, url, headers=self.headers, **kwargs
            )
            response.raise_for_status()
            return response.json()
    
    async def get_klines(self, **params):
        return await self._request("GET", "/api/v1/klines", params=params)
    
    async def backfill_klines(self, **data):
        return await self._request("POST", "/api/v1/backfill/klines", json=data)
```

### 2. Tool 注册示例

```python
from typing import Any

def register_datahub_tools(tool_registry):
    """注册 DataHub AI Tools"""
    
    @tool_registry.register(
        name="datahub_get_klines",
        description="获取加密货币 K 线数据",
        parameters={
            "symbol": {"type": "string", "description": "交易对，如 BTC_USDT.BNC"},
            "interval": {"type": "string", "description": "K 线周期", "default": "1h"},
            "limit": {"type": "integer", "description": "返回数量", "default": 100},
            "after": {"type": "string", "description": "开始时间（ISO 8601）"},
            "before": {"type": "string", "description": "结束时间（ISO 8601）"},
        }
    )
    async def get_klines(**params) -> dict[str, Any]:
        client = get_datahub_client()
        return await client.get_klines(**params)
    
    @tool_registry.register(
        name="datahub_backfill_klines",
        description="触发 K 线数据回填任务",
        parameters={
            "symbols": {"type": "array", "items": {"type": "string"}},
            "intervals": {"type": "array", "items": {"type": "string"}, "required": True},
            "start_time": {"type": "string", "required": True},
            "end_time": {"type": "string"},
        }
    )
    async def backfill_klines(**params) -> dict[str, Any]:
        client = get_datahub_client()
        return await client.backfill_klines(**params)
```

### 3. 错误处理

```python
class DataHubError(Exception):
    def __init__(self, code: str, message: str, detail: str = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)

async def handle_response(response):
    if response.status_code >= 400:
        error = response.json().get("error", {})
        raise DataHubError(
            code=error.get("code", "UNKNOWN"),
            message=error.get("message", "Unknown error"),
            detail=error.get("detail")
        )
    return response.json()
```

### 4. 分页处理

```python
async def fetch_all_pages(client, method, **params):
    """获取所有分页数据"""
    all_data = []
    offset = 0
    limit = params.get("limit", 100)
    
    while True:
        params["offset"] = offset
        result = await method(**params)
        all_data.extend(result["data"])
        
        if not result["pagination"]["has_next"]:
            break
        offset += limit
    
    return all_data
```

---

## 使用场景示例

### 场景 1：查询 BTC 价格走势

```
用户: 帮我查看 BTC 最近 24 小时的价格走势

AI Tool 调用:
{
  "tool": "datahub_get_klines",
  "parameters": {
    "symbol": "BTC_USDT.BNC",
    "interval": "1h",
    "limit": 24
  }
}

返回数据后，AI 可以分析价格趋势并生成图表描述。
```

### 场景 2：检查账户余额

```
用户: 查看我的 Binance 账户余额

AI Tool 调用:
{
  "tool": "datahub_get_balances_latest",
  "parameters": {
    "account": "BNC_MM01"
  }
}

返回数据后，AI 可以汇总各资产余额并计算总价值。
```

### 场景 3：回填历史数据

```
用户: 帮我回填 ETH 上个月的 K 线数据

AI Tool 调用:
{
  "tool": "datahub_backfill_klines",
  "parameters": {
    "symbols": ["ETH_USDT.BNC", "ETH_USDT.OKX"],
    "intervals": ["1h", "1d"],
    "start_time": "2025-12-01T00:00:00Z",
    "end_time": "2025-12-31T23:59:59Z"
  }
}

返回 trace_id 后，AI 可以告知用户任务已提交并提供追踪方式。
```

### 场景 4：监控系统状态

```
用户: 检查 DataHub 系统状态

AI Tool 调用:
{
  "tool": "datahub_health_check",
  "parameters": {}
}

返回数据后，AI 可以解读各组件状态并给出建议。
```

---

## 权限矩阵

| Tool | 所需权限 |
|------|----------|
| `datahub_get_klines` | `read:klines` |
| `datahub_get_tickers` | `read:tickers` |
| `datahub_get_orderbook` | `read:orderbook` |
| `datahub_get_balances` | `read:balances` |
| `datahub_get_balances_latest` | `read:balances` |
| `datahub_get_orders` | `read:orders` |
| `datahub_get_fills` | `read:fills` |
| `datahub_get_transfers` | `read:transfers` |
| `datahub_list_symbols` | `read:symbols` |
| `datahub_get_symbol` | `read:symbols` |
| `datahub_update_symbol` | `write:symbols` |
| `datahub_subscribe_symbol` | `write:symbols` |
| `datahub_list_jobs` | `read:jobs` |
| `datahub_get_job` | `read:jobs` |
| `datahub_list_job_executions` | `read:jobs` |
| `datahub_get_job_executions` | `read:jobs` |
| `datahub_backfill_*` | `write:backfill` |
| `datahub_list_logs` | `read:logs` |
| `datahub_health_check` | 无需权限 |

---

## 最佳实践

1. **缓存策略**: 对于不频繁变化的数据（如交易对列表），建议实现本地缓存
2. **批量查询**: 尽量使用批量查询减少 API 调用次数
3. **时间范围**: 查询历史数据时，建议限制时间范围避免返回过多数据
4. **错误重试**: 对于网络错误，建议实现指数退避重试机制
5. **日志追踪**: 回填任务返回的 `trace_id` 可用于后续日志查询
6. **健康检查**: 在执行关键操作前，建议先检查系统健康状态

