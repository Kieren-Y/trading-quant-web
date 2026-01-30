# 账本数据 API

提供账户余额、订单、成交记录、充提转账等账本数据的只读访问接口。

## 目录

- [余额数据](#余额数据)
- [订单数据](#订单数据)
- [成交数据](#成交数据)
- [转账数据](#转账数据)

---

## 余额数据

### 获取历史余额列表

获取账户余额历史快照数据。

**端点**: `GET /api/v1/balances`

**权限**: `read:balances`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `account` | string | 否 | - | 精确匹配账户，如 `BNC_MM01` |
| `asset` | string | 否 | - | 精确匹配资产代码，如 `BTC`, `USDT` |
| `search` | string | 否 | - | 模糊搜索资产（与精确筛选互斥） |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-10000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `datetime` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限 |
| `after` | datetime | 否 | - | 时间下限 |

#### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | int | 记录 ID |
| `exchange` | string | 交易所代码 |
| `account` | string | 账户标识 |
| `asset` | string | 资产代码 |
| `wallet_amount` | decimal | 钱包余额 |
| `total_amount` | decimal | 总余额 |
| `available_amount` | decimal | 可用余额 |
| `locked_amount` | decimal | 冻结余额 |
| `unrealized_pnl` | decimal | 未实现盈亏 |
| `datetime` | datetime | 快照时间 |
| `time_bucket` | datetime | 时间桶 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

#### 请求示例

```bash
# 获取最新余额快照
curl -X GET "https://api.datahub.example.com/api/v1/balances?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定账户余额
curl -X GET "https://api.datahub.example.com/api/v1/balances?account=BNC_MM01" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定资产余额
curl -X GET "https://api.datahub.example.com/api/v1/balances?asset=USDT" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定账户的 USDT 余额历史
curl -X GET "https://api.datahub.example.com/api/v1/balances?account=BNC_MM01&asset=USDT&after=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "id": 12345,
      "exchange": "BNC",
      "account": "BNC_MM01",
      "asset": "USDT",
      "wallet_amount": "100000.00",
      "total_amount": "100000.00",
      "available_amount": "85000.00",
      "locked_amount": "15000.00",
      "unrealized_pnl": "0.00",
      "datetime": "2026-01-15T08:00:00Z",
      "time_bucket": "2026-01-15T08:00:00Z",
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-01-15T08:00:00Z"
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

### 获取最新余额列表

获取账户最新余额状态（每个账户-资产对一条记录）。

**端点**: `GET /api/v1/balances/latest`

**权限**: `read:balances`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `account` | string | 否 | - | 精确匹配账户 |
| `asset` | string | 否 | - | 精确匹配资产代码 |
| `search` | string | 否 | - | 模糊搜索资产 |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `datetime` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |

#### 请求示例

```bash
# 获取所有账户最新余额
curl -X GET "https://api.datahub.example.com/api/v1/balances/latest" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定账户最新余额
curl -X GET "https://api.datahub.example.com/api/v1/balances/latest?account=BNC_MM01" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索 BTC 相关余额
curl -X GET "https://api.datahub.example.com/api/v1/balances/latest?search=BTC" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### AI Tool 调用示例

```json
{
  "tool": "datahub_get_balances_latest",
  "parameters": {
    "account": "BNC_MM01"
  }
}
```

---

## 订单数据

### 获取订单列表

获取历史订单数据（只读）。

**端点**: `GET /api/v1/orders`

**权限**: `read:orders`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `order_id` | string | 否 | - | 精确匹配订单 ID |
| `client_order_id` | string | 否 | - | 精确匹配客户端订单 ID |
| `symbol` | string | 否 | - | 精确匹配交易对，如 `BTC_USDT` |
| `account` | string | 否 | - | 精确匹配账户 |
| `side` | string | 否 | - | 订单方向：`buy`, `sell` |
| `order_type` | string | 否 | - | 订单类型：`limit`, `market`, `stop_limit` |
| `status` | string | 否 | - | 订单状态：`new`, `filled`, `canceled` 等 |
| `search` | string | 否 | - | 模糊搜索交易对 |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-10000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `created_at` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限 |
| `after` | datetime | 否 | - | 时间下限 |

#### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | int | 记录 ID |
| `exchange` | string | 交易所代码 |
| `symbol` | string | 交易对 |
| `symbol_exchange` | string | 交易所原始交易对 |
| `order_id` | string | 交易所订单 ID |
| `client_order_id` | string | 客户端订单 ID |
| `account` | string | 账户标识 |
| `side` | string | 订单方向：`buy` / `sell` |
| `type` | string | 订单类型 |
| `status` | string | 订单状态 |
| `price` | decimal | 订单价格 |
| `quantity` | decimal | 订单数量 |
| `filled_qty` | decimal | 已成交数量 |
| `filled_avg_price` | decimal | 成交均价 |
| `fee` | decimal | 手续费 |
| `fee_asset` | string | 手续费资产 |
| `datetime` | datetime | 订单时间 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

#### 订单状态说明

| 状态 | 描述 |
|------|------|
| `NEW` | 新订单，待成交 |
| `PARTIALLY_FILLED` | 部分成交 |
| `FILLED` | 完全成交 |
| `CANCELED` | 已取消 |
| `REJECTED` | 已拒绝 |
| `EXPIRED` | 已过期 |

#### 请求示例

```bash
# 获取最新订单
curl -X GET "https://api.datahub.example.com/api/v1/orders?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定订单
curl -X GET "https://api.datahub.example.com/api/v1/orders?order_id=123456789" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定账户的买单
curl -X GET "https://api.datahub.example.com/api/v1/orders?account=OKX_MM01&side=buy" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取已成交订单
curl -X GET "https://api.datahub.example.com/api/v1/orders?status=filled&after=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取 BTC 相关订单
curl -X GET "https://api.datahub.example.com/api/v1/orders?symbol=BTC_USDT&account=OKX_MM01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "id": 12345,
      "exchange": "OKX",
      "symbol": "BTC_USDT",
      "symbol_exchange": "BTC-USDT",
      "order_id": "123456789",
      "client_order_id": "my_order_001",
      "account": "OKX_MM01",
      "side": "buy",
      "type": "limit",
      "status": "FILLED",
      "price": "42000.00",
      "quantity": "0.1",
      "filled_qty": "0.1",
      "filled_avg_price": "41998.50",
      "fee": "0.00004",
      "fee_asset": "BTC",
      "datetime": "2026-01-15T08:00:00Z",
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-01-15T08:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total": 1500,
    "total_pages": 15,
    "has_next": true,
    "has_prev": false
  }
}
```

#### AI Tool 调用示例

```json
{
  "tool": "datahub_get_orders",
  "parameters": {
    "account": "OKX_MM01",
    "status": "filled",
    "limit": 50,
    "after": "2026-01-01T00:00:00Z"
  }
}
```

---

## 成交数据

### 获取成交列表

获取交易成交（Fill）记录。

**端点**: `GET /api/v1/fills`

**权限**: `read:fills`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `order_id` | string | 否 | - | 精确匹配订单 ID |
| `trade_id` | string | 否 | - | 精确匹配成交 ID |
| `symbol` | string | 否 | - | 精确匹配交易对 |
| `account` | string | 否 | - | 精确匹配账户 |
| `side` | string | 否 | - | 成交方向：`buy`, `sell` |
| `search` | string | 否 | - | 模糊搜索交易对 |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-10000 |
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
| `symbol` | string | 交易对 |
| `symbol_exchange` | string | 交易所原始交易对 |
| `order_id` | string | 关联订单 ID |
| `trade_id` | string | 成交 ID |
| `account` | string | 账户标识 |
| `side` | string | 成交方向 |
| `price` | decimal | 成交价格 |
| `quantity` | decimal | 成交数量 |
| `fee` | decimal | 手续费 |
| `fee_asset` | string | 手续费资产 |
| `is_maker` | bool | 是否为 Maker |
| `datetime` | datetime | 成交时间 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

#### 请求示例

```bash
# 获取最新成交
curl -X GET "https://api.datahub.example.com/api/v1/fills?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定订单的成交
curl -X GET "https://api.datahub.example.com/api/v1/fills?order_id=123456789" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定账户的成交
curl -X GET "https://api.datahub.example.com/api/v1/fills?account=OKX_MM01&after=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取买入成交
curl -X GET "https://api.datahub.example.com/api/v1/fills?side=buy&symbol=BTC_USDT" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "id": 67890,
      "exchange": "OKX",
      "symbol": "BTC_USDT",
      "symbol_exchange": "BTC-USDT",
      "order_id": "123456789",
      "trade_id": "987654321",
      "account": "OKX_MM01",
      "side": "buy",
      "price": "41998.50",
      "quantity": "0.05",
      "fee": "0.00002",
      "fee_asset": "BTC",
      "is_maker": true,
      "datetime": "2026-01-15T08:05:00Z",
      "created_at": "2026-01-15T08:05:00Z",
      "updated_at": "2026-01-15T08:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total": 2500,
    "total_pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

#### AI Tool 调用示例

```json
{
  "tool": "datahub_get_fills",
  "parameters": {
    "account": "OKX_MM01",
    "symbol": "BTC_USDT",
    "limit": 100,
    "after": "2026-01-01T00:00:00Z"
  }
}
```

---

## 转账数据

### 获取转账列表

获取充值、提现、内部转账记录。

**端点**: `GET /api/v1/transfers`

**权限**: `read:transfers`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `account` | string | 否 | - | 精确匹配账户 |
| `asset` | string | 否 | - | 精确匹配资产代码 |
| `transfer_type` | string | 否 | - | 转账类型：`deposit`, `withdraw`, `transfer` |
| `transfer_id` | string | 否 | - | 精确匹配转账 ID |
| `tx_hash` | string | 否 | - | 精确匹配交易哈希 |
| `search` | string | 否 | - | 模糊搜索资产 |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-10000 |
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
| `account` | string | 账户标识 |
| `asset` | string | 资产代码 |
| `transfer_id` | string | 转账 ID |
| `type` | string | 转账类型 |
| `status` | string | 转账状态 |
| `amount` | decimal | 转账金额 |
| `tx_hash` | string | 区块链交易哈希 |
| `address` | string | 目标/来源地址 |
| `fee` | decimal | 手续费 |
| `fee_asset` | string | 手续费资产 |
| `datetime` | datetime | 转账时间 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

#### 转账类型说明

| 类型 | 描述 |
|------|------|
| `DEPOSIT` | 充值 |
| `WITHDRAW` | 提现 |
| `TRANSFER` | 内部转账 |

#### 请求示例

```bash
# 获取最新转账
curl -X GET "https://api.datahub.example.com/api/v1/transfers?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定账户充值记录
curl -X GET "https://api.datahub.example.com/api/v1/transfers?account=BNC_MM01&transfer_type=deposit" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取 USDT 转账记录
curl -X GET "https://api.datahub.example.com/api/v1/transfers?asset=USDT&after=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 根据交易哈希查询
curl -X GET "https://api.datahub.example.com/api/v1/transfers?tx_hash=0xabc123..." \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应示例

```json
{
  "data": [
    {
      "id": 11111,
      "exchange": "BNC",
      "account": "BNC_MM01",
      "asset": "USDT",
      "transfer_id": "DEP123456",
      "type": "DEPOSIT",
      "status": "COMPLETED",
      "amount": "10000.00",
      "tx_hash": "0xabc123def456...",
      "address": "0x1234567890abcdef...",
      "fee": "0.00",
      "fee_asset": null,
      "datetime": "2026-01-15T08:00:00Z",
      "created_at": "2026-01-15T08:00:00Z",
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
  "tool": "datahub_get_transfers",
  "parameters": {
    "account": "BNC_MM01",
    "transfer_type": "deposit",
    "limit": 50
  }
}
```

---

## 使用场景

### 场景 1：查询账户资产概览

```python
# 获取账户所有资产最新余额
balances = datahub.get_balances_latest(account="BNC_MM01")

# 计算总资产价值
total_value = 0
for balance in balances["data"]:
    if balance["asset"] == "USDT":
        total_value += float(balance["total_amount"])
    else:
        # 获取对应 USDT 价格
        ticker = datahub.get_tickers(
            symbol=f"{balance['asset']}_USDT.BNC",
            limit=1
        )
        if ticker["data"]:
            price = float(ticker["data"][0]["last_price"])
            total_value += float(balance["total_amount"]) * price
```

### 场景 2：分析交易历史

```python
# 获取指定时间段的成交记录
fills = datahub.get_fills(
    account="OKX_MM01",
    symbol="BTC_USDT",
    after="2026-01-01T00:00:00Z",
    before="2026-01-15T00:00:00Z"
)

# 计算总成交量和手续费
total_volume = sum(float(f["quantity"]) for f in fills["data"])
total_fee = sum(float(f["fee"] or 0) for f in fills["data"])
```

### 场景 3：监控充提状态

```python
# 获取待处理的提现
pending_withdrawals = datahub.get_transfers(
    account="BNC_MM01",
    transfer_type="withdraw",
    status="PENDING"
)

for w in pending_withdrawals["data"]:
    print(f"Pending withdrawal: {w['amount']} {w['asset']}")
```

## 注意事项

1. **账本数据为只读**：API 仅提供查询功能，不支持下单或转账操作
2. **账户命名规范**：账户名格式为 `{EXCHANGE}_{NAME}`，如 `BNC_MM01`
3. **时间范围限制**：建议使用 `before` 和 `after` 参数限制查询范围
4. **订单状态大写**：查询时 `status` 参数会自动转换为大写
5. **精确筛选优先**：当提供精确筛选参数时，`search` 参数将被忽略

