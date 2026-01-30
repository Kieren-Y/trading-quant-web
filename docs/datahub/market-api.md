# 市场数据 API

提供 K 线（蜡烛图）、行情、订单簿等市场数据的只读访问接口。

## 目录

- [K 线数据](#k-线数据)
- [行情数据](#行情数据)
- [订单簿数据](#订单簿数据)

---

## K 线数据

### 获取 K 线列表

获取指定时间周期的 K 线（蜡烛图）数据。

**端点**: `GET /api/v1/klines`

**权限**: `read:klines`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `interval` | string | 否 | `1h` | K 线周期：`1m`, `5m`, `15m`, `1h`, `1d` |
| `symbol` | string | 否 | - | 精确匹配交易对，如 `BTC_USDT.BNC` |
| `exchange` | string | 否 | - | 精确匹配交易所代码，如 `BNC`, `OKX`, `GIO` |
| `search` | string | 否 | - | 模糊搜索交易对或交易所（与精确筛选互斥） |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-10000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `datetime` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限（ISO 8601） |
| `after` | datetime | 否 | - | 时间下限（ISO 8601） |

#### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `exchange` | string | 交易所代码 |
| `symbol` | string | 交易对（含交易所后缀） |
| `datetime` | datetime | K 线时间 |
| `open` | decimal | 开盘价 |
| `high` | decimal | 最高价 |
| `low` | decimal | 最低价 |
| `close` | decimal | 收盘价 |
| `volume` | decimal | 成交量（基础货币） |
| `quote_volume` | decimal | 成交额（计价货币） |
| `num_trades` | int | 成交笔数 |
| `is_closed` | bool | K 线是否已收盘 |
| `updated_at` | datetime | 更新时间 |

#### 请求示例

```bash
# 获取 BTC/USDT 1 小时 K 线（Binance）
curl -X GET "https://api.datahub.example.com/api/v1/klines?symbol=BTC_USDT.BNC&interval=1h&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取所有交易所的 1 分钟 K 线
curl -X GET "https://api.datahub.example.com/api/v1/klines?interval=1m&limit=500" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定时间范围的 K 线
curl -X GET "https://api.datahub.example.com/api/v1/klines?symbol=BTC_USDT.BNC&interval=1h&after=2026-01-01T00:00:00Z&before=2026-01-15T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索包含 BTC 的交易对
curl -X GET "https://api.datahub.example.com/api/v1/klines?search=BTC&interval=1h&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "exchange": "BNC",
      "symbol": "BTC_USDT.BNC",
      "datetime": "2026-01-15T08:00:00Z",
      "open": "42150.50",
      "high": "42300.00",
      "low": "42100.00",
      "close": "42250.75",
      "volume": "1234.56789",
      "quote_volume": "52123456.78",
      "num_trades": 15678,
      "is_closed": true,
      "updated_at": "2026-01-15T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total": 500,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

#### AI Tool 调用示例

```json
{
  "tool": "datahub_get_klines",
  "parameters": {
    "symbol": "BTC_USDT.BNC",
    "interval": "1h",
    "limit": 100,
    "after": "2026-01-01T00:00:00Z"
  }
}
```

---

## 行情数据

### 获取行情列表

获取实时行情（Ticker）数据。

**端点**: `GET /api/v1/tickers`

**权限**: `read:tickers`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `symbol` | string | 否 | - | 精确匹配交易对 |
| `exchange` | string | 否 | - | 精确匹配交易所代码 |
| `search` | string | 否 | - | 模糊搜索交易对或交易所原始代码 |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `timestamp` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限 |
| `after` | datetime | 否 | - | 时间下限 |

#### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | int | 记录 ID |
| `exchange` | string | 交易所代码 |
| `symbol` | string | 统一交易对 |
| `exchange_symbol` | string | 交易所原始交易对 |
| `last_price` | decimal | 最新成交价 |
| `bid_price` | decimal | 买一价 |
| `ask_price` | decimal | 卖一价 |
| `volume_24h` | decimal | 24 小时成交量 |
| `change_24h` | decimal | 24 小时价格变动 |
| `change_pct_24h` | decimal | 24 小时涨跌幅（百分比） |
| `timestamp` | datetime | 行情时间 |
| `time_bucket` | datetime | 时间桶（用于聚合） |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

#### 请求示例

```bash
# 获取最新行情
curl -X GET "https://api.datahub.example.com/api/v1/tickers?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定交易对行情
curl -X GET "https://api.datahub.example.com/api/v1/tickers?symbol=BTC_USDT.BNC" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取 Binance 所有行情
curl -X GET "https://api.datahub.example.com/api/v1/tickers?exchange=BNC" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索 ETH 相关行情
curl -X GET "https://api.datahub.example.com/api/v1/tickers?search=ETH" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "id": 12345,
      "exchange": "BNC",
      "symbol": "BTC_USDT.BNC",
      "exchange_symbol": "BTCUSDT",
      "last_price": "42250.75",
      "bid_price": "42250.00",
      "ask_price": "42251.00",
      "volume_24h": "45678.12345",
      "change_24h": "1250.50",
      "change_pct_24h": "3.05",
      "timestamp": "2026-01-15T08:30:00Z",
      "time_bucket": "2026-01-15T08:00:00Z",
      "created_at": "2026-01-15T08:30:00Z",
      "updated_at": "2026-01-15T08:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total": 150,
    "total_pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

#### AI Tool 调用示例

```json
{
  "tool": "datahub_get_tickers",
  "parameters": {
    "exchange": "BNC",
    "limit": 50
  }
}
```

---

## 订单簿数据

### 获取订单簿列表

获取订单簿快照数据（每侧最多 20 档）。

**端点**: `GET /api/v1/orderbook`

**权限**: `read:orderbook`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `symbol` | string | 否 | - | 精确匹配交易对 |
| `exchange` | string | 否 | - | 精确匹配交易所代码 |
| `search` | string | 否 | - | 模糊搜索交易对或交易所原始代码 |
| `limit` | int | 否 | 20 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `timestamp` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限 |
| `after` | datetime | 否 | - | 时间下限 |

#### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | int | 记录 ID |
| `exchange` | string | 交易所代码 |
| `symbol` | string | 统一交易对 |
| `exchange_symbol` | string | 交易所原始交易对 |
| `bids` | array | 买单列表（价格降序） |
| `bids[].price` | decimal | 买单价格 |
| `bids[].quantity` | decimal | 买单数量 |
| `asks` | array | 卖单列表（价格升序） |
| `asks[].price` | decimal | 卖单价格 |
| `asks[].quantity` | decimal | 卖单数量 |
| `last_update_id` | int | 交易所更新序号 |
| `timestamp` | datetime | 快照时间 |
| `time_bucket` | datetime | 时间桶 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

#### 请求示例

```bash
# 获取最新订单簿快照
curl -X GET "https://api.datahub.example.com/api/v1/orderbook?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定交易对订单簿
curl -X GET "https://api.datahub.example.com/api/v1/orderbook?symbol=BTC_USDT.BNC" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取 OKX 所有订单簿
curl -X GET "https://api.datahub.example.com/api/v1/orderbook?exchange=OKX&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "id": 67890,
      "exchange": "BNC",
      "symbol": "BTC_USDT.BNC",
      "exchange_symbol": "BTCUSDT",
      "bids": [
        {"price": "42250.00", "quantity": "1.5"},
        {"price": "42249.50", "quantity": "2.3"},
        {"price": "42249.00", "quantity": "0.8"}
      ],
      "asks": [
        {"price": "42251.00", "quantity": "1.2"},
        {"price": "42251.50", "quantity": "3.1"},
        {"price": "42252.00", "quantity": "0.5"}
      ],
      "last_update_id": 123456789,
      "timestamp": "2026-01-15T08:30:00Z",
      "time_bucket": "2026-01-15T08:00:00Z",
      "created_at": "2026-01-15T08:30:00Z",
      "updated_at": "2026-01-15T08:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 50,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### AI Tool 调用示例

```json
{
  "tool": "datahub_get_orderbook",
  "parameters": {
    "symbol": "BTC_USDT.BNC",
    "limit": 5
  }
}
```

---

## 使用场景

### 场景 1：获取 BTC 价格走势

```python
# 获取最近 24 小时 BTC/USDT 1 小时 K 线
response = datahub.get_klines(
    symbol="BTC_USDT.BNC",
    interval="1h",
    limit=24,
    order_desc=True
)
```

### 场景 2：比较多交易所价格

```python
# 获取所有交易所的 BTC 最新行情
tickers = []
for exchange in ["BNC", "OKX", "GIO"]:
    response = datahub.get_tickers(
        symbol=f"BTC_USDT.{exchange}",
        limit=1
    )
    tickers.extend(response["data"])
```

### 场景 3：分析订单簿深度

```python
# 获取 BTC/USDT 订单簿
orderbook = datahub.get_orderbook(
    symbol="BTC_USDT.BNC",
    limit=1
)

# 计算买卖价差
if orderbook["data"]:
    ob = orderbook["data"][0]
    spread = float(ob["asks"][0]["price"]) - float(ob["bids"][0]["price"])
    print(f"Spread: {spread}")
```

## 注意事项

1. **精确筛选与模糊搜索互斥**：当提供 `symbol` 或 `exchange` 参数时，`search` 参数将被忽略
2. **K 线周期**：不同周期的 K 线存储在不同的表中，查询效率较高
3. **订单簿深度**：默认返回每侧最多 20 档，可通过 `limit` 参数调整返回的快照数量
4. **时间范围**：建议使用 `before` 和 `after` 参数限制查询范围，避免返回过多数据

