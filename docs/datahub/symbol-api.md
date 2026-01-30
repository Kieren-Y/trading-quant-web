# 交易对管理 API

提供交易对（Symbol）信息查询和订阅管理功能。

## 目录

- [获取交易对列表](#获取交易对列表)
- [获取交易对详情](#获取交易对详情)
- [更新交易对](#更新交易对)
- [订阅/取消订阅](#订阅取消订阅)

---

## 获取交易对列表

获取所有交易对信息。

**端点**: `GET /api/v1/symbols`

**权限**: `read:symbols`

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `search` | string | 否 | - | 模糊搜索交易对或交易所 |
| `limit` | int | 否 | 50 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `exchange` | 排序字段 |
| `order_desc` | bool | 否 | `false` | 是否降序 |

### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | int | 交易对 ID |
| `exchange` | string | 交易所代码 |
| `symbol` | string | 统一交易对（含交易所后缀），如 `BTC_USDT.BNC` |
| `symbol_root` | string | 根交易对（不含后缀），如 `BTC_USDT` |
| `symbol_base` | string | 基础资产，如 `BTC` |
| `symbol_quote` | string | 计价资产，如 `USDT` |
| `symbol_exchange` | string | 交易所原始交易对，如 `BTCUSDT` |
| `market_type` | string | 市场类型：`spot`, `future`, `delivery`, `option` |
| `is_active` | bool | 是否活跃（交易所是否支持交易） |
| `is_subscribed` | bool | 是否已订阅 WebSocket 实时数据 |
| `timestamp` | int | 交易所时间戳 |
| `updated_at` | datetime | 更新时间 |

### 请求示例

```bash
# 获取所有交易对
curl -X GET "https://api.datahub.example.com/api/v1/symbols?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索 BTC 相关交易对
curl -X GET "https://api.datahub.example.com/api/v1/symbols?search=BTC" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取 Binance 交易对
curl -X GET "https://api.datahub.example.com/api/v1/symbols?search=BNC&order_by=symbol" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按交易对名称排序
curl -X GET "https://api.datahub.example.com/api/v1/symbols?order_by=symbol&order_desc=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "data": [
    {
      "id": 1,
      "exchange": "BNC",
      "symbol": "BTC_USDT.BNC",
      "symbol_root": "BTC_USDT",
      "symbol_base": "BTC",
      "symbol_quote": "USDT",
      "symbol_exchange": "BTCUSDT",
      "market_type": "spot",
      "is_active": true,
      "is_subscribed": true,
      "timestamp": 1705315200000,
      "updated_at": "2026-01-15T08:00:00Z"
    },
    {
      "id": 2,
      "exchange": "BNC",
      "symbol": "ETH_USDT.BNC",
      "symbol_root": "ETH_USDT",
      "symbol_base": "ETH",
      "symbol_quote": "USDT",
      "symbol_exchange": "ETHUSDT",
      "market_type": "spot",
      "is_active": true,
      "is_subscribed": true,
      "timestamp": 1705315200000,
      "updated_at": "2026-01-15T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 500,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_list_symbols",
  "parameters": {
    "search": "BTC",
    "limit": 50
  }
}
```

---

## 获取交易对详情

根据 ID 获取单个交易对详细信息。

**端点**: `GET /api/v1/symbols/{symbol_id}`

**权限**: `read:symbols`

### 路径参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol_id` | int | 是 | 交易对 ID |

### 请求示例

```bash
# 获取 ID 为 42 的交易对
curl -X GET "https://api.datahub.example.com/api/v1/symbols/42" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "id": 42,
  "exchange": "BNC",
  "symbol": "BTC_USDT.BNC",
  "symbol_root": "BTC_USDT",
  "symbol_base": "BTC",
  "symbol_quote": "USDT",
  "symbol_exchange": "BTCUSDT",
  "market_type": "spot",
  "is_active": true,
  "is_subscribed": true,
  "timestamp": 1705315200000,
  "updated_at": "2026-01-15T08:00:00Z"
}
```

### 错误响应

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Symbol not found: 42"
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_get_symbol",
  "parameters": {
    "symbol_id": 42
  }
}
```

---

## 更新交易对

更新交易对的活跃状态或订阅状态。

**端点**: `PUT /api/v1/symbols/{symbol_id}`

**权限**: `write:symbols`

### 路径参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol_id` | int | 是 | 交易对 ID |

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `is_active` | bool | 否 | 是否活跃 |
| `is_subscribed` | bool | 否 | 是否订阅实时数据 |

> **注意**: 仅提供需要更新的字段，未提供的字段保持不变（部分更新）。

### 请求示例

```bash
# 更新交易对状态
curl -X PUT "https://api.datahub.example.com/api/v1/symbols/42" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": true,
    "is_subscribed": true
  }'

# 仅更新订阅状态
curl -X PUT "https://api.datahub.example.com/api/v1/symbols/42" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_subscribed": false
  }'
```

### 响应示例

```json
{
  "id": 42,
  "exchange": "BNC",
  "symbol": "BTC_USDT.BNC",
  "symbol_root": "BTC_USDT",
  "symbol_base": "BTC",
  "symbol_quote": "USDT",
  "symbol_exchange": "BTCUSDT",
  "market_type": "spot",
  "is_active": true,
  "is_subscribed": true,
  "timestamp": 1705315200000,
  "updated_at": "2026-01-15T08:30:00Z"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_update_symbol",
  "parameters": {
    "symbol_id": 42,
    "is_active": true,
    "is_subscribed": true
  }
}
```

---

## 订阅/取消订阅

快速订阅或取消订阅交易对的实时数据。

**端点**: `PATCH /api/v1/symbols/{symbol_id}/subscribe`

**权限**: `write:symbols`

### 路径参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `symbol_id` | int | 是 | 交易对 ID |

### 请求体

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `is_subscribed` | bool | 是 | `true` 订阅，`false` 取消订阅 |

### 请求示例

```bash
# 订阅交易对
curl -X PATCH "https://api.datahub.example.com/api/v1/symbols/42/subscribe" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_subscribed": true}'

# 取消订阅
curl -X PATCH "https://api.datahub.example.com/api/v1/symbols/42/subscribe" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_subscribed": false}'
```

### 响应示例

```json
{
  "id": 42,
  "exchange": "BNC",
  "symbol": "BTC_USDT.BNC",
  "symbol_root": "BTC_USDT",
  "symbol_base": "BTC",
  "symbol_quote": "USDT",
  "symbol_exchange": "BTCUSDT",
  "market_type": "spot",
  "is_active": true,
  "is_subscribed": true,
  "timestamp": 1705315200000,
  "updated_at": "2026-01-15T08:35:00Z"
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_subscribe_symbol",
  "parameters": {
    "symbol_id": 42,
    "is_subscribed": true
  }
}
```

---

## 使用场景

### 场景 1：查找并订阅新交易对

```python
# 1. 搜索 SOL 相关交易对
symbols = datahub.list_symbols(search="SOL_USDT")

# 2. 找到目标交易对
target = None
for s in symbols["data"]:
    if s["symbol"] == "SOL_USDT.BNC" and not s["is_subscribed"]:
        target = s
        break

# 3. 订阅该交易对
if target:
    datahub.subscribe_symbol(
        symbol_id=target["id"],
        is_subscribed=True
    )
```

### 场景 2：批量管理订阅

```python
# 获取所有已订阅的交易对
symbols = datahub.list_symbols(limit=1000)

subscribed = [s for s in symbols["data"] if s["is_subscribed"]]
print(f"当前已订阅 {len(subscribed)} 个交易对")

# 取消订阅非主流交易对
main_pairs = {"BTC_USDT", "ETH_USDT", "BNB_USDT"}
for s in subscribed:
    if s["symbol_root"] not in main_pairs:
        datahub.subscribe_symbol(
            symbol_id=s["id"],
            is_subscribed=False
        )
```

### 场景 3：检查交易对状态

```python
# 获取特定交易对
symbol = datahub.get_symbol(symbol_id=42)

if not symbol["is_active"]:
    print(f"警告: {symbol['symbol']} 已停止交易")
elif not symbol["is_subscribed"]:
    print(f"提示: {symbol['symbol']} 未订阅实时数据")
```

---

## 交易对命名规范

### 统一交易对格式

```
{BASE}_{QUOTE}.{EXCHANGE}
```

- **BASE**: 基础资产代码（大写）
- **QUOTE**: 计价资产代码（大写）
- **EXCHANGE**: 交易所代码

### 示例

| 统一格式 | 交易所原始格式 | 说明 |
|----------|---------------|------|
| `BTC_USDT.BNC` | `BTCUSDT` | Binance BTC/USDT |
| `ETH_USDT.OKX` | `ETH-USDT` | OKX ETH/USDT |
| `BTC_USDT.GIO` | `BTC_USDT` | Gate.io BTC/USDT |

### 市场类型

| 类型 | 描述 |
|------|------|
| `spot` | 现货市场 |
| `future` | 永续合约 |
| `delivery` | 交割合约 |
| `option` | 期权 |

---

## 注意事项

1. **订阅生效时间**: 订阅状态变更后，WebSocket 数据流会在下一个心跳周期内更新
2. **活跃状态**: `is_active` 由交易所决定，表示该交易对是否可交易
3. **订阅状态**: `is_subscribed` 由用户控制，决定是否收集该交易对的实时数据
4. **批量操作**: 当前 API 不支持批量订阅，需逐个调用
5. **ID 查询**: 建议先通过列表接口获取交易对 ID，再进行详情查询或更新操作

