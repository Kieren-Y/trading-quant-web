# OMS REST API 接口文档

> 版本: v1.0.0
> 更新日期: 2026-01-30
> 适用对象: App应用平台前端开发者

---

## 目录

- [概述](#概述)
- [认证方式](#认证方式)
- [通用规范](#通用规范)
- [订单管理 API](#订单管理-api)
- [组合单 API](#组合单-api)
- [账户 API](#账户-api)
- [交易记录 API](#交易记录-api)
- [健康检查 API](#健康检查-api)
- [日志查询 API](#日志查询-api)
- [错误码参考](#错误码参考)
- [枚举值参考](#枚举值参考)

---

## 概述

### 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `http://{host}:{port}/api/v1` |
| 协议 | HTTP/HTTPS |
| 数据格式 | JSON |
| 编码 | UTF-8 |

### 环境配置

| 环境 | Base URL | 说明 |
|-----|---------|------|
| 开发环境 | `http://localhost:8080/api/v1` | 本地开发 |
| 测试环境 | `http://oms-test.internal:8080/api/v1` | 集成测试 |
| 生产环境 | `https://oms.internal:8080/api/v1` | 生产环境 |

---

## 认证方式

### Bearer Token 认证

所有 API 请求（除健康检查外）需在 Header 中携带 Bearer Token。

```http
Authorization: Bearer <your-token>
```

**示例:**
```bash
curl -X GET "http://localhost:8080/api/v1/orders" \
  -H "Authorization: Bearer your-api-token"
```

### 认证豁免端点

以下端点无需认证：
- `GET /health`
- `GET /health/ready`
- `GET /health/detailed`
- `GET /docs` (仅调试模式)
- `GET /redoc` (仅调试模式)

### IP 白名单（可选）

当启用 IP 白名单时，仅允许指定 IP/CIDR 范围的请求。

---

## 通用规范

### 请求头

| Header | 必填 | 说明 |
|--------|-----|------|
| `Authorization` | 是 | Bearer Token 认证 |
| `Content-Type` | 是 | `application/json` |
| `X-Request-ID` | 否 | 客户端请求ID（用于幂等性） |

### 响应头

| Header | 说明 |
|--------|------|
| `X-Trace-ID` | 分布式追踪ID，用于问题排查 |

### 分页响应格式

列表接口统一使用以下分页格式：

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 150,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### 错误响应格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

---

## 订单管理 API

### 1. 创建订单

创建标准订单或带止损/止盈的组合单(Bracket Order)。

**请求**

```http
POST /api/v1/orders
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 - 标准订单**

```json
{
  "account": "BNC_MM01",
  "symbol": "BTC_USDT.BNC",
  "side": "BUY",
  "order_type": "LIMIT",
  "quantity": "0.1",
  "price": "42000",
  "strategy": "ALGO_01",
  "book": "MS01",
  "trader_id": "KY01",
  "timestamp": 1706620800000,
  "trace_id": "optional-trace-id",
  "request_id": "optional-request-id"
}
```

**请求体 - 组合单(含止损/止盈)**

```json
{
  "account": "OKX_MM01",
  "symbol": "ETH_USDT.OKX",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": "1.5",
  "strategy": "MOMENTUM_01",
  "book": "MS01",
  "trader_id": "KY01",
  "timestamp": 1706620800000,
  "stop_loss": {
    "order_type": "STOP_MARKET",
    "trigger_type": "PERCENT",
    "percent": "5",
    "price_trigger": "MARK_PRICE"
  },
  "take_profit": {
    "order_type": "TAKE_PROFIT_LIMIT",
    "trigger_type": "FIXED",
    "price": "2800",
    "limit_price": "2795",
    "price_trigger": "LAST_PRICE"
  }
}
```

**请求参数说明**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `account` | string | 是 | 账户标识 (如: BNC_MM01, OKX_MM01) |
| `symbol` | string | 是 | 交易对 + 交易所后缀 (如: BTC_USDT.BNC) |
| `side` | string | 是 | 买卖方向: `BUY` / `SELL` |
| `order_type` | string | 是 | 订单类型: `LIMIT` / `MARKET` |
| `quantity` | decimal | 条件 | 基础资产数量 (与 quote_quantity 二选一) |
| `quote_quantity` | decimal | 条件 | 报价资产数量 (仅 BUY 订单) |
| `price` | decimal | 条件 | 订单价格 (LIMIT 订单必填) |
| `strategy` | string | 是 | 策略标识 |
| `book` | string | 否 | 账本标识，默认 "MS01" |
| `trader_id` | string | 否 | 交易员标识，默认 "KY01" |
| `timestamp` | integer | 是 | 请求时间戳 (毫秒) |
| `trace_id` | string | 否 | 分布式追踪ID (自动生成若未提供) |
| `request_id` | string | 否 | 外部请求ID (用于幂等性) |
| `leverage` | integer | 否 | 杠杆倍数 (1-125，合约交易) |
| `margin_mode` | string | 否 | 保证金模式: `ISOLATED` / `CROSS` |
| `position_side` | string | 否 | 持仓方向: `LONG` / `SHORT` |
| `stop_loss` | object | 否 | 止损配置 |
| `take_profit` | object | 否 | 止盈配置 |

**止损/止盈配置**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `order_type` | string | 是 | 止损: `STOP_MARKET` / `STOP_LIMIT`<br>止盈: `TAKE_PROFIT_MARKET` / `TAKE_PROFIT_LIMIT` |
| `trigger_type` | string | 是 | 触发类型: `FIXED` (固定价格) / `PERCENT` (百分比) |
| `price` | decimal | 条件 | 固定触发价格 (trigger_type=FIXED 时必填) |
| `percent` | decimal | 条件 | 触发百分比 (trigger_type=PERCENT 时必填)<br>止损: 0.1-50%，止盈: 0.1-1000% |
| `limit_price` | decimal | 否 | 限价单执行价 (STOP_LIMIT/TAKE_PROFIT_LIMIT) |
| `price_trigger` | string | 否 | 触发价格类型: `LAST_PRICE` / `MARK_PRICE`<br>止损默认 MARK_PRICE，止盈默认 LAST_PRICE |

**响应 - 标准订单**

```json
{
  "order": {
    "client_order_id": "ORD_20260130_abc123",
    "exchange_order_id": "123456789",
    "account": "BNC_MM01",
    "book": "MS01",
    "trader_id": "KY01",
    "strategy": "ALGO_01",
    "exchange": "BNC",
    "symbol": "BTC_USDT",
    "symbol_exchange": "BTCUSDT",
    "side": "BUY",
    "order_type": "LIMIT",
    "price": "42000",
    "quantity": "0.1",
    "filled_qty": "0",
    "average_price": null,
    "fee": null,
    "fee_asset": null,
    "status": "NEW",
    "market_type": "SPOT",
    "leverage": null,
    "margin_mode": null,
    "position_side": null,
    "trace_id": "trace-abc123",
    "error_message": null,
    "created_at": "2026-01-30T10:30:00Z",
    "updated_at": "2026-01-30T10:30:00Z",
    "remaining_qty": "0.1",
    "fill_percentage": "0",
    "notional_value": "4200",
    "is_terminal": false,
    "is_active": true,
    "can_cancel": true
  },
  "bracket_id": null,
  "bracket_status": null,
  "stop_loss_order": null,
  "take_profit_order": null
}
```

**响应 - 组合单**

```json
{
  "order": {
    "client_order_id": "ORD_20260130_xyz789",
    "exchange_order_id": "987654321",
    "account": "OKX_MM01",
    "symbol": "ETH_USDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": "1.5",
    "status": "NEW",
    ...
  },
  "bracket_id": "BRK_20260130_xyz789",
  "bracket_status": "PENDING",
  "stop_loss_order": {
    "client_order_id": "ORD_20260130_sl001",
    "exchange_order_id": "111222333",
    "side": "SELL",
    "order_type": "STOP_MARKET",
    "status": "NEW",
    ...
  },
  "take_profit_order": {
    "client_order_id": "ORD_20260130_tp001",
    "exchange_order_id": "444555666",
    "side": "SELL",
    "order_type": "TAKE_PROFIT_LIMIT",
    "status": "NEW",
    ...
  }
}
```

**状态码**

| 状态码 | 说明 |
|-------|------|
| 200 | 订单创建成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 500 | 服务器内部错误 |

---

### 2. 查询订单列表

查询订单列表，支持多条件过滤和分页。

**请求**

```http
GET /api/v1/orders
Authorization: Bearer <token>
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `account` | string | 否 | 账户筛选 |
| `symbol` | string | 否 | 交易对筛选 |
| `exchange` | string | 否 | 交易所筛选 (BNC/OKX/GIO) |
| `side` | string | 否 | 方向筛选 (BUY/SELL) |
| `strategy` | string | 否 | 策略筛选 |
| `status` | string | 否 | 单状态筛选 (已废弃，请用 statuses) |
| `statuses` | string | 否 | 多状态筛选，逗号分隔 (如: NEW,FILLED,CANCELED) |
| `client_order_id` | string | 否 | 客户端订单ID精确匹配 |
| `exchange_order_id` | string | 否 | 交易所订单ID精确匹配 |
| `trace_id` | string | 否 | 追踪ID精确匹配 |
| `bracket_id` | string | 否 | 组合单ID精确匹配 |
| `created_after` | string | 否 | 创建时间起点 (ISO 8601) |
| `created_before` | string | 否 | 创建时间终点 (ISO 8601) |
| `page` | integer | 否 | 页码，从1开始，默认1 |
| `page_size` | integer | 否 | 每页数量，默认50，最大200 |
| `sort_by` | string | 否 | 排序字段，默认 created_at |
| `sort_order` | string | 否 | 排序方向: asc/desc，默认 desc |

**可用排序字段**
- `created_at` - 创建时间
- `updated_at` - 更新时间
- `quantity` - 数量
- `price` - 价格
- `filled_qty` - 已成交数量
- `average_price` - 平均成交价
- `exchange_order_id` - 交易所订单ID

**示例请求**

```bash
# 查询指定账户的活跃订单
GET /api/v1/orders?account=BNC_MM01&statuses=NEW,PARTIALLY_FILLED

# 查询指定时间范围内的订单
GET /api/v1/orders?created_after=2026-01-01T00:00:00Z&created_before=2026-01-31T23:59:59Z

# 查询指定交易对，按价格升序
GET /api/v1/orders?symbol=BTC_USDT.BNC&sort_by=price&sort_order=asc
```

**响应**

```json
{
  "data": [
    {
      "client_order_id": "ORD_20260130_001",
      "exchange_order_id": "123456789",
      "account": "BNC_MM01",
      "symbol": "BTC_USDT",
      "side": "BUY",
      "order_type": "LIMIT",
      "price": "42000",
      "quantity": "0.1",
      "filled_qty": "0.05",
      "average_price": "41980",
      "status": "PARTIALLY_FILLED",
      ...
    },
    ...
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 128,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### 3. 查询单个订单

根据 client_order_id 查询订单详情。

**请求**

```http
GET /api/v1/orders/{client_order_id}
Authorization: Bearer <token>
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `client_order_id` | string | 是 | 客户端订单ID |

**响应**

```json
{
  "client_order_id": "ORD_20260130_001",
  "exchange_order_id": "123456789",
  "account": "BNC_MM01",
  "book": "MS01",
  "trader_id": "KY01",
  "strategy": "ALGO_01",
  "exchange": "BNC",
  "symbol": "BTC_USDT",
  "symbol_exchange": "BTCUSDT",
  "side": "BUY",
  "order_type": "LIMIT",
  "price": "42000",
  "quantity": "0.1",
  "filled_qty": "0.1",
  "average_price": "41950",
  "fee": "0.00004",
  "fee_asset": "BTC",
  "status": "FILLED",
  "market_type": "SPOT",
  "trace_id": "trace-001",
  "created_at": "2026-01-30T10:30:00Z",
  "updated_at": "2026-01-30T10:31:15Z",
  "remaining_qty": "0",
  "fill_percentage": "100",
  "notional_value": "4195",
  "is_terminal": true,
  "is_active": false,
  "can_cancel": false
}
```

**特殊情况说明**

对于 OKX 顺序模式(Sequential)的止损/止盈订单，可能暂时没有 `exchange_order_id`：

```json
{
  "client_order_id": "ORD_20260130_sl001",
  "exchange_order_id": null,
  "status": "PENDING_NEW",
  ...
  "note": "Algo order pending submission to exchange. Will be created when entry order fills."
}
```

---

### 4. 取消订单

取消指定的活跃订单。

**请求**

```http
POST /api/v1/orders/{client_order_id}/cancel
Authorization: Bearer <token>
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `client_order_id` | string | 是 | 客户端订单ID |

> **注意**: 使用 POST 而非 DELETE，因为取消是状态转换操作，订单记录会保留为 CANCELED 状态。

**响应**

```json
{
  "client_order_id": "ORD_20260130_001",
  "exchange_order_id": "123456789",
  "status": "CANCELED",
  "account": "BNC_MM01",
  "symbol": "BTC_USDT",
  ...
}
```

**状态码**

| 状态码 | 说明 |
|-------|------|
| 200 | 取消成功 |
| 400 | 取消失败 (订单不存在或不可取消) |

---

## 组合单 API

### 1. 附加止损/止盈

为已成交订单附加止损/止盈保护。

**请求**

```http
POST /api/v1/brackets/attach
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**

```json
{
  "entry_order_id": "ORD_20260130_001",
  "stop_loss_percent": "3.5",
  "stop_loss_limit_price": "40000",
  "take_profit_price": "48000",
  "take_profit_limit_price": "47900"
}
```

**请求参数**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `entry_order_id` | string | 是 | 已成交订单的 client_order_id |
| `stop_loss_percent` | decimal | 条件 | 止损百分比 (0.1-50) |
| `stop_loss_price` | decimal | 条件 | 止损固定价格 |
| `stop_loss_limit_price` | decimal | 否 | 止损限价 |
| `take_profit_percent` | decimal | 条件 | 止盈百分比 (0.1-1000) |
| `take_profit_price` | decimal | 条件 | 止盈固定价格 |
| `take_profit_limit_price` | decimal | 否 | 止盈限价 |

> 至少提供 stop_loss 或 take_profit 其中之一。

**响应**

```json
{
  "bracket_id": "BRK_20260130_attach001",
  "status": "ACTIVE",
  "entry_order": {
    "client_order_id": "ORD_20260130_001",
    "status": "FILLED",
    ...
  },
  "sl_order": {
    "client_order_id": "ORD_20260130_sl001",
    "status": "NEW",
    ...
  },
  "tp_order": {
    "client_order_id": "ORD_20260130_tp001",
    "status": "NEW",
    ...
  }
}
```

---

### 2. 查询组合单

查询组合单详情及其关联订单。

**请求**

```http
GET /api/v1/brackets/{bracket_id}
Authorization: Bearer <token>
```

**响应**

```json
{
  "bracket_group": {
    "group_id": "BRK_20260130_001",
    "status": "ACTIVE",
    "mode": "NATIVE",
    "mode_description": "Entry + SL/TP submitted together to exchange",
    "account": "OKX_MM01",
    "exchange": "OKX",
    "symbol": "ETH_USDT",
    "entry_order_id": "ORD_20260130_entry001",
    "entry_price": "2500",
    "sl_order_id": "ORD_20260130_sl001",
    "tp_order_id": "ORD_20260130_tp001",
    "trace_id": "trace-001"
  },
  "orders": {
    "entry": {
      "client_order_id": "ORD_20260130_entry001",
      "status": "FILLED",
      ...
    },
    "stop_loss": {
      "client_order_id": "ORD_20260130_sl001",
      "status": "NEW",
      ...
    },
    "take_profit": {
      "client_order_id": "ORD_20260130_tp001",
      "status": "NEW",
      ...
    }
  }
}
```

**组合单模式说明**

| 模式 | 说明 |
|-----|------|
| `NATIVE` | 入场单 + 止损/止盈同时提交到交易所 |
| `SEQUENTIAL` | 先提交入场单，成交后再提交止损/止盈 |
| `ATTACH` | 止损/止盈附加到已成交的入场单 |

---

### 3. 取消组合单腿

取消组合单的单个腿(止损或止盈)。

**请求**

```http
DELETE /api/v1/brackets/{bracket_id}/legs/{leg_type}
Authorization: Bearer <token>
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `bracket_id` | string | 是 | 组合单ID |
| `leg_type` | string | 是 | 腿类型: `SL` (止损) / `TP` (止盈) |

**响应**

```json
{
  "bracket_id": "BRK_20260130_001",
  "status": "ACTIVE",
  "cancelled_order_id": "ORD_20260130_sl001"
}
```

---

## 账户 API

### 1. 查询余额

**请求**

```http
GET /api/v1/balances
Authorization: Bearer <token>
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `account` | string | 否 | 账户筛选 |
| `asset` | string | 否 | 资产筛选 (如: BTC, USDT) |
| `exchange` | string | 否 | 交易所筛选 |

**响应**

```json
{
  "data": [
    {
      "account": "BNC_MM01",
      "asset": "USDT",
      "exchange": "BNC",
      "balance": "10000.5",
      "available": "8500.5",
      "locked": "1500",
      "exchange_locked": "1500",
      "last_sync_at": "2026-01-30T10:00:00Z",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-30T10:00:00Z"
    },
    ...
  ]
}
```

---

### 2. 查询持仓

**请求**

```http
GET /api/v1/positions
Authorization: Bearer <token>
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `account` | string | 否 | 账户筛选 |
| `symbol` | string | 否 | 交易对筛选 |
| `exchange` | string | 否 | 交易所筛选 |
| `side` | string | 否 | 持仓方向 (LONG/SHORT) |

**响应**

```json
{
  "data": [
    {
      "account": "OKX_MM01",
      "exchange": "OKX",
      "symbol": "BTC_USDT.OKX",
      "side": "LONG",
      "quantity": "0.5",
      "entry_price": "42000",
      "leverage": 10,
      "margin_mode": "CROSS",
      "unrealized_pnl": "250.5",
      "updated_at": "2026-01-30T10:30:00Z"
    },
    ...
  ]
}
```

---

## 交易记录 API

### 查询成交记录

**请求**

```http
GET /api/v1/trades
Authorization: Bearer <token>
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `client_order_id` | string | 否 | 客户端订单ID |
| `exchange_order_id` | string | 否 | 交易所订单ID |
| `account` | string | 否 | 账户筛选 |
| `symbol` | string | 否 | 交易对筛选 |
| `exchange` | string | 否 | 交易所筛选 |
| `strategy` | string | 否 | 策略筛选 |
| `side` | string | 否 | 方向筛选 (BUY/SELL) |

**响应**

```json
{
  "data": [
    {
      "trade_id": "TRD_001",
      "client_order_id": "ORD_20260130_001",
      "exchange_order_id": "123456789",
      "account": "BNC_MM01",
      "book": "MS01",
      "trader_id": "KY01",
      "strategy": "ALGO_01",
      "exchange": "BNC",
      "symbol": "BTC_USDT",
      "side": "BUY",
      "filled_prx": "41950",
      "filled_qty": "0.1",
      "fee": "0.00004",
      "fee_asset": "BTC",
      "is_maker": false,
      "timestamp": "2026-01-30T10:31:15Z",
      "trace_id": "trace-001",
      "notional_value": "4195",
      "quote_quantity": "4195"
    },
    ...
  ]
}
```

---

## 健康检查 API

### 1. 基础健康检查

**请求**

```http
GET /health
```

**响应**

```json
{
  "status": "healthy",
  "timestamp": 1706617800.123
}
```

---

### 2. 就绪检查

检查数据库和 Redis 连接状态。

**请求**

```http
GET /health/ready
```

**响应**

```json
{
  "status": "ready",
  "components": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

---

### 3. 详细健康检查

包含 OMS Worker 和 WebSocket 状态。

**请求**

```http
GET /health/detailed
```

**响应**

```json
{
  "status": "healthy",
  "components": {
    "database": { "status": "healthy" },
    "redis": { "status": "healthy" },
    "oms_worker": {
      "status": "online",
      "last_heartbeat_age_s": 5.2,
      "active_orders": 15,
      "websocket": {
        "BNC_MM01": "connected",
        "OKX_MM01": "connected"
      }
    }
  }
}
```

**整体状态说明**

| 状态 | 说明 |
|-----|------|
| `healthy` | 所有组件正常 |
| `degraded` | OMS Worker 离线或状态过期 |
| `unhealthy` | 数据库或 Redis 不可用 |

---

## 日志查询 API

### 查询日志

**请求**

```http
GET /api/v1/logs
Authorization: Bearer <token>
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `trace_id` | string | 否 | 追踪ID过滤 |
| `log_date` | date | 否 | 日志日期 (YYYY-MM-DD)，默认今天 |
| `level` | string | 否 | 日志级别: DEBUG/INFO/WARNING/ERROR |
| `keyword` | string | 否 | 关键词搜索 |
| `log_file` | string | 否 | 日志文件名，默认 app.log |
| `limit` | integer | 否 | 返回条数，默认100，最大1000 |

**可用日志文件**
- `app.log` - 主日志
- `oms.log` - OMS 业务日志
- `order_events.log` - 订单生命周期事件
- `error.log` - 错误日志
- `gateway.log` - 网关日志
- `tasks.log` - 后台任务日志
- `mq.log` - 消息队列日志

**响应**

```json
{
  "entries": [
    {
      "timestamp": "2026-01-30 10:30:00.123",
      "level": "INFO",
      "trace_id": "trace-001",
      "message": "src.app.handlers.order:handle_create:45 - Order created successfully",
      "extra": {
        "client_order_id": "ORD_001",
        "account": "BNC_MM01"
      }
    },
    ...
  ],
  "total": 25,
  "file": "logs/2026-01-30/app.log",
  "date": "2026-01-30"
}
```

---

## 错误码参考

### 通用错误码

| 错误码 | HTTP状态码 | 说明 |
|-------|-----------|------|
| `UNAUTHORIZED` | 401 | 认证失败 |
| `FORBIDDEN` | 403 | IP 不在白名单 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

### 订单错误码

| 错误码 | 说明 |
|-------|------|
| `ORDER_CREATION_FAILED` | 订单创建失败 |
| `CANCEL_FAILED` | 订单取消失败 |
| `ATTACH_FAILED` | 附加止损/止盈失败 |
| `CANCEL_LEG_FAILED` | 取消组合单腿失败 |

### 日志错误码

| 错误码 | 说明 |
|-------|------|
| `INVALID_LOG_FILE` | 无效的日志文件名 |
| `INVALID_PATH` | 无效的日志路径 |
| `PERMISSION_DENIED` | 日志文件无法读取 |

---

## 枚举值参考

### 订单状态 (OrderStatus)

| 值 | 说明 |
|---|------|
| `PENDING_NEW` | 订单已发送，等待交易所确认 |
| `NEW` | 订单已在交易所生效 |
| `PARTIALLY_FILLED` | 部分成交 |
| `FILLED` | 完全成交 |
| `PENDING_CANCEL` | 取消请求已发送，等待确认 |
| `CANCELED` | 已取消 |
| `REJECTED` | 被拒绝 |
| `EXPIRED` | 已过期 |
| `FAILED` | 失败 |

### 订单类型 (OrderType)

| 值 | 说明 |
|---|------|
| `LIMIT` | 限价单 |
| `MARKET` | 市价单 |
| `STOP_MARKET` | 止损市价单 |
| `STOP_LIMIT` | 止损限价单 |
| `TAKE_PROFIT_MARKET` | 止盈市价单 |
| `TAKE_PROFIT_LIMIT` | 止盈限价单 |

### 订单方向 (OrderSide)

| 值 | 说明 |
|---|------|
| `BUY` | 买入 |
| `SELL` | 卖出 |

### 交易所 (ExchangeType)

| 值 | 全称 |
|---|------|
| `BNC` | Binance |
| `OKX` | OKX |
| `GIO` | Gate.io |

### 市场类型 (MarketType)

| 值 | 说明 |
|---|------|
| `SPOT` | 现货 |
| `FUTURES` | 期货 |
| `MARGIN` | 杠杆 |
| `SWAP` | 永续合约 |

### 组合单状态 (BracketStatus)

| 值 | 说明 |
|---|------|
| `PENDING` | 等待入场单成交 |
| `ACTIVE` | 入场单已成交，保护订单生效中 |
| `CLOSED` | 组合单已结束 |

### 组合单角色 (BracketRole)

| 值 | 说明 |
|---|------|
| `ENTRY` | 入场单 |
| `SL` | 止损单 |
| `TP` | 止盈单 |

---

## 附录

### SDK 示例

**Python**

```python
import requests

class OMSClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def create_order(self, **kwargs):
        resp = requests.post(
            f"{self.base_url}/orders",
            json=kwargs,
            headers=self.headers
        )
        return resp.json()

    def get_order(self, client_order_id: str):
        resp = requests.get(
            f"{self.base_url}/orders/{client_order_id}",
            headers=self.headers
        )
        return resp.json()

    def cancel_order(self, client_order_id: str):
        resp = requests.post(
            f"{self.base_url}/orders/{client_order_id}/cancel",
            headers=self.headers
        )
        return resp.json()

    def list_orders(self, **filters):
        resp = requests.get(
            f"{self.base_url}/orders",
            params=filters,
            headers=self.headers
        )
        return resp.json()

# Usage
client = OMSClient("http://localhost:8080/api/v1", "your-token")

# Create a limit order
order = client.create_order(
    account="BNC_MM01",
    symbol="BTC_USDT.BNC",
    side="BUY",
    order_type="LIMIT",
    quantity="0.1",
    price="42000",
    strategy="ALGO_01",
    timestamp=1706620800000
)
print(order)
```

**TypeScript/JavaScript**

```typescript
interface OrderParams {
  account: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  order_type: 'LIMIT' | 'MARKET';
  quantity?: string;
  quote_quantity?: string;
  price?: string;
  strategy: string;
  timestamp: number;
  stop_loss?: StopLossConfig;
  take_profit?: TakeProfitConfig;
}

class OMSClient {
  constructor(
    private baseUrl: string,
    private token: string
  ) {}

  private get headers() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async createOrder(params: OrderParams) {
    const resp = await fetch(`${this.baseUrl}/orders`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(params)
    });
    return resp.json();
  }

  async getOrder(clientOrderId: string) {
    const resp = await fetch(
      `${this.baseUrl}/orders/${clientOrderId}`,
      { headers: this.headers }
    );
    return resp.json();
  }

  async cancelOrder(clientOrderId: string) {
    const resp = await fetch(
      `${this.baseUrl}/orders/${clientOrderId}/cancel`,
      { method: 'POST', headers: this.headers }
    );
    return resp.json();
  }

  async listOrders(filters: Record<string, string>) {
    const params = new URLSearchParams(filters);
    const resp = await fetch(
      `${this.baseUrl}/orders?${params}`,
      { headers: this.headers }
    );
    return resp.json();
  }
}

// Usage
const client = new OMSClient('http://localhost:8080/api/v1', 'your-token');

const order = await client.createOrder({
  account: 'BNC_MM01',
  symbol: 'BTC_USDT.BNC',
  side: 'BUY',
  order_type: 'LIMIT',
  quantity: '0.1',
  price: '42000',
  strategy: 'ALGO_01',
  timestamp: Date.now()
});
```

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| 1.0.0 | 2026-01-30 | 初始版本发布 |
