# 数据回填 API

提供历史数据回填任务的触发接口。每个请求会创建一个后台任务，返回 `trace_id` 用于追踪执行状态。

## 目录

- [K 线回填](#k-线回填)
- [交易对回填](#交易对回填)
- [余额回填](#余额回填)
- [订单回填](#订单回填)
- [成交回填](#成交回填)
- [转账回填](#转账回填)
- [订单簿回填](#订单簿回填)
- [行情回填](#行情回填)

---

## 通用响应格式

所有回填接口返回统一的响应格式：

```json
{
  "execution_id": 0,
  "trace_id": "backfill_kline_abc12345",
  "status": "queued",
  "message": "Kline backfill queued | exchanges=2 | symbols=3"
}
```

### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `execution_id` | int | 执行记录 ID（后台任务创建后更新） |
| `trace_id` | string | 追踪 ID，用于查询日志和执行状态 |
| `status` | string | 任务状态：`queued`, `running`, `completed`, `failed` |
| `message` | string | 任务描述信息 |

### 支持的交易所

| 代码 | 交易所 | 支持的回填类型 |
|------|--------|---------------|
| `BNC` | Binance | kline, symbol, balance, orderbook, ticker |
| `OKX` | OKX | kline, symbol, balance, order, fill, transfer, orderbook, ticker |
| `GIO` | Gate.io | kline, symbol, orderbook, ticker |

---

## K 线回填

触发 K 线（蜡烛图）历史数据回填。

**端点**: `POST /api/v1/backfill/klines`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表，如 `["BNC", "OKX"]` |
| `symbols` | list[string] | 否 | 交易对列表，如 `["BTC_USDT.BNC", "ETH_USDT.OKX"]` |
| `intervals` | list[string] | 是 | K 线周期：`1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` |
| `start_time` | datetime | 是 | 开始时间（ISO 8601） |
| `end_time` | datetime | 否 | 结束时间，默认为当前时间 |

### 参数优先级

1. 如果提供 `symbols`，会自动从交易对中提取交易所（如 `BTC_USDT.BNC` → `BNC`）
2. 如果仅提供 `exchanges`，会回填该交易所所有已订阅的交易对
3. 如果都不提供，会回填所有交易所的所有已订阅交易对

### 请求示例

```bash
# 回填指定交易对的 K 线
curl -X POST "https://api.datahub.example.com/api/v1/backfill/klines" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC_USDT.BNC", "BTC_USDT.OKX", "ETH_USDT.BNC"],
    "intervals": ["1m", "1h"],
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-15T00:00:00Z"
  }'

# 回填指定交易所的所有交易对
curl -X POST "https://api.datahub.example.com/api/v1/backfill/klines" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchanges": ["BNC", "OKX"],
    "intervals": ["1h"],
    "start_time": "2026-01-01T00:00:00Z"
  }'

# 回填所有交易所
curl -X POST "https://api.datahub.example.com/api/v1/backfill/klines" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "intervals": ["1h"],
    "start_time": "2026-01-01T00:00:00Z"
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_kline_a1b2c3d4",
  "status": "queued",
  "message": "Kline backfill queued | exchanges=2 | symbols=3"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_klines",
  "parameters": {
    "symbols": ["BTC_USDT.BNC", "ETH_USDT.BNC"],
    "intervals": ["1h", "1d"],
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-15T00:00:00Z"
  }
}
```

---

## 交易对回填

同步交易所的完整交易对列表。

**端点**: `POST /api/v1/backfill/symbols`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 是 | 交易所列表 |

### 请求示例

```bash
curl -X POST "https://api.datahub.example.com/api/v1/backfill/symbols" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchanges": ["BNC", "OKX", "GIO"]
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_symbol_e5f6g7h8",
  "status": "queued",
  "message": "Symbol backfill queued | exchanges=3"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_symbols",
  "parameters": {
    "exchanges": ["BNC", "OKX", "GIO"]
  }
}
```

---

## 余额回填

获取账户当前余额快照。

**端点**: `POST /api/v1/backfill/balances`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表（支持 `BNC`, `OKX`） |
| `accounts` | list[string] | 是 | 账户列表，如 `["BNC_MM01", "OKX_MM01"]` |

### 参数说明

- 如果仅提供 `accounts`，会自动从账户名提取交易所（如 `BNC_MM01` → `BNC`）
- 支持的交易所：`BNC`（Binance）、`OKX`

### 请求示例

```bash
# 通过账户列表回填
curl -X POST "https://api.datahub.example.com/api/v1/backfill/balances" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["BNC_MM01", "OKX_MM01"]
  }'

# 显式指定交易所
curl -X POST "https://api.datahub.example.com/api/v1/backfill/balances" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchanges": ["BNC", "OKX"],
    "accounts": ["BNC_MM01", "OKX_MM01"]
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_balance_i9j0k1l2",
  "status": "queued",
  "message": "Balance backfill queued | exchanges=2 | accounts=2"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_balances",
  "parameters": {
    "accounts": ["BNC_MM01", "OKX_MM01"]
  }
}
```

---

## 订单回填

获取历史订单数据。

**端点**: `POST /api/v1/backfill/orders`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表（仅支持 `OKX`） |
| `accounts` | list[string] | 否 | 账户列表 |
| `symbols` | list[string] | 否 | 交易对列表（根交易对格式） |
| `start_time` | datetime | 否 | 开始时间 |
| `end_time` | datetime | 否 | 结束时间 |

### 参数说明

- 必须提供 `exchanges` 或 `accounts` 之一
- 如果仅提供 `accounts`，会自动提取交易所
- 当前仅支持 `OKX` 交易所

### 请求示例

```bash
# 回填指定账户的订单
curl -X POST "https://api.datahub.example.com/api/v1/backfill/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["OKX_MM01"]
  }'

# 回填指定时间范围的订单
curl -X POST "https://api.datahub.example.com/api/v1/backfill/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["OKX_MM01"],
    "symbols": ["BTC_USDT", "ETH_USDT"],
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-15T00:00:00Z"
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_order_m3n4o5p6",
  "status": "queued",
  "message": "Order backfill queued | exchanges=1 | accounts=1 | symbols=2"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_orders",
  "parameters": {
    "accounts": ["OKX_MM01"],
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-15T00:00:00Z"
  }
}
```

---

## 成交回填

获取历史成交（Fill）数据。

**端点**: `POST /api/v1/backfill/fills`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表（仅支持 `OKX`） |
| `accounts` | list[string] | 否 | 账户列表 |
| `symbols` | list[string] | 否 | 交易对列表 |
| `start_time` | datetime | 否 | 开始时间 |
| `end_time` | datetime | 否 | 结束时间 |

### 请求示例

```bash
# 回填指定账户的成交
curl -X POST "https://api.datahub.example.com/api/v1/backfill/fills" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["OKX_MM01"]
  }'

# 回填指定交易对和时间范围
curl -X POST "https://api.datahub.example.com/api/v1/backfill/fills" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["OKX_MM01"],
    "symbols": ["BTC_USDT", "ETH_USDT"],
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-15T00:00:00Z"
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_fill_q7r8s9t0",
  "status": "queued",
  "message": "Fill backfill queued | exchanges=1 | accounts=1 | symbols=2"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_fills",
  "parameters": {
    "accounts": ["OKX_MM01"],
    "symbols": ["BTC_USDT"],
    "start_time": "2026-01-01T00:00:00Z"
  }
}
```

---

## 转账回填

获取历史充提转账数据。

**端点**: `POST /api/v1/backfill/transfers`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表（仅支持 `OKX`） |
| `accounts` | list[string] | 否 | 账户列表 |
| `start_time` | datetime | 否 | 开始时间 |
| `end_time` | datetime | 否 | 结束时间 |

### 请求示例

```bash
# 回填指定账户的转账
curl -X POST "https://api.datahub.example.com/api/v1/backfill/transfers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["OKX_MM01"]
  }'

# 回填指定时间范围
curl -X POST "https://api.datahub.example.com/api/v1/backfill/transfers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": ["OKX_MM01"],
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-15T00:00:00Z"
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_transfer_u1v2w3x4",
  "status": "queued",
  "message": "Transfer backfill queued | exchanges=1 | accounts=1"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_transfers",
  "parameters": {
    "accounts": ["OKX_MM01"],
    "start_time": "2026-01-01T00:00:00Z"
  }
}
```

---

## 订单簿回填

获取当前订单簿快照。

**端点**: `POST /api/v1/backfill/orderbook`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表 |
| `symbols` | list[string] | 否 | 交易对列表 |
| `limit` | int | 否 | 订单簿深度，范围 1-1000，默认 20 |

### 请求示例

```bash
# 回填指定交易对的订单簿
curl -X POST "https://api.datahub.example.com/api/v1/backfill/orderbook" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC_USDT.BNC", "BTC_USDT.OKX"],
    "limit": 20
  }'

# 回填指定交易所的所有订单簿
curl -X POST "https://api.datahub.example.com/api/v1/backfill/orderbook" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchanges": ["BNC", "OKX"],
    "limit": 50
  }'

# 回填所有交易所
curl -X POST "https://api.datahub.example.com/api/v1/backfill/orderbook" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 20
  }'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_orderbook_y5z6a7b8",
  "status": "queued",
  "message": "Orderbook backfill queued | exchanges=2 | symbols=2 | limit=20"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_orderbook",
  "parameters": {
    "symbols": ["BTC_USDT.BNC", "ETH_USDT.BNC"],
    "limit": 20
  }
}
```

---

## 行情回填

获取当前行情（Ticker）快照。

**端点**: `POST /api/v1/backfill/ticker`

**权限**: `write:backfill`

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `exchanges` | list[string] | 否 | 交易所列表 |
| `symbols` | list[string] | 否 | 交易对列表 |

### 请求示例

```bash
# 回填指定交易对的行情
curl -X POST "https://api.datahub.example.com/api/v1/backfill/ticker" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC_USDT.BNC", "BTC_USDT.OKX", "ETH_USDT.BNC"]
  }'

# 回填指定交易所的所有行情
curl -X POST "https://api.datahub.example.com/api/v1/backfill/ticker" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchanges": ["BNC", "OKX"]
  }'

# 回填所有交易所
curl -X POST "https://api.datahub.example.com/api/v1/backfill/ticker" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 响应示例

```json
{
  "execution_id": 0,
  "trace_id": "backfill_ticker_c9d0e1f2",
  "status": "queued",
  "message": "Ticker backfill queued | exchanges=2 | symbols=3"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_backfill_ticker",
  "parameters": {
    "exchanges": ["BNC", "OKX"]
  }
}
```

---

## 使用场景

### 场景 1：初始化新交易对数据

```python
# 1. 先同步交易对列表
datahub.backfill_symbols(exchanges=["BNC"])

# 2. 回填 K 线历史数据
datahub.backfill_klines(
    symbols=["SOL_USDT.BNC"],
    intervals=["1h", "1d"],
    start_time="2026-01-01T00:00:00Z"
)

# 3. 获取当前订单簿和行情
datahub.backfill_orderbook(symbols=["SOL_USDT.BNC"])
datahub.backfill_ticker(symbols=["SOL_USDT.BNC"])
```

### 场景 2：补充缺失的账户数据

```python
# 回填账户余额
datahub.backfill_balances(accounts=["OKX_MM01"])

# 回填历史订单和成交
datahub.backfill_orders(
    accounts=["OKX_MM01"],
    start_time="2026-01-01T00:00:00Z"
)
datahub.backfill_fills(
    accounts=["OKX_MM01"],
    start_time="2026-01-01T00:00:00Z"
)

# 回填转账记录
datahub.backfill_transfers(
    accounts=["OKX_MM01"],
    start_time="2026-01-01T00:00:00Z"
)
```

### 场景 3：追踪回填任务状态

```python
# 触发回填任务
response = datahub.backfill_klines(
    symbols=["BTC_USDT.BNC"],
    intervals=["1h"],
    start_time="2026-01-01T00:00:00Z"
)

trace_id = response["trace_id"]
print(f"任务已提交，Trace ID: {trace_id}")

# 通过日志 API 查询执行状态
logs = datahub.list_logs(
    job_id=trace_id,
    limit=100
)

for log in logs["data"]:
    print(f"[{log['level']}] {log['message']}")
```

---

## 注意事项

1. **异步执行**: 所有回填任务都是异步执行的，API 会立即返回 `trace_id`
2. **任务追踪**: 使用 `trace_id` 可以在日志 API 中查询任务执行详情
3. **交易所限制**: 不同数据类型支持的交易所不同，请参考各接口说明
4. **时间范围**: K 线回填建议分批进行，避免单次回填时间跨度过大
5. **交易对格式**: 
   - 市场数据（kline, orderbook, ticker）使用完整格式：`BTC_USDT.BNC`
   - 账本数据（order, fill）使用根交易对格式：`BTC_USDT`
6. **账户命名**: 账户名格式为 `{EXCHANGE}_{NAME}`，会自动提取交易所代码
7. **速率限制**: 回填任务会受到交易所 API 速率限制，大量数据回填可能需要较长时间

