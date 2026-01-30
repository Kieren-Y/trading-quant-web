# DataHub API 文档

## 概述

DataHub API 是一个加密货币市场数据收集与分发系统，提供 RESTful API 接口用于查询市场数据、账户信息、任务管理等功能。

## 基础信息

| 属性 | 值 |
|------|-----|
| Base URL | `https://api.datahub.example.com/api/v1` |
| API 版本 | v1.0.0 |
| 协议 | HTTPS |
| 数据格式 | JSON |

## 认证

所有 API 请求（除健康检查外）都需要通过 JWT Bearer Token 进行认证。

### 请求头

```http
Authorization: Bearer <your_jwt_token>
```

### Token 结构

JWT Token 需包含以下 claims：

| Claim | 类型 | 必需 | 描述 |
|-------|------|------|------|
| `user_id` | int | 是 | 用户唯一标识 |
| `username` | string | 否 | 用户名 |
| `scopes` | list[string] | 否 | 权限范围列表 |
| `jti` | string | 否 | Token 唯一标识 |
| `exp` | int | 是 | 过期时间戳 |

### 权限范围 (Scopes)

| Scope | 描述 |
|-------|------|
| `read:klines` | 读取K线数据 |
| `read:tickers` | 读取行情数据 |
| `read:orderbook` | 读取订单簿数据 |
| `read:symbols` | 读取交易对信息 |
| `write:symbols` | 修改交易对信息 |
| `read:orders` | 读取订单数据 |
| `read:fills` | 读取成交数据 |
| `read:balances` | 读取余额数据 |
| `read:transfers` | 读取转账数据 |
| `read:jobs` | 读取任务信息 |
| `write:jobs` | 修改任务配置 |
| `trigger:jobs` | 触发任务执行 |
| `delete:jobs` | 删除任务 |
| `read:logs` | 读取日志 |
| `write:backfill` | 触发数据回填 |
| `*` | 全部权限 |

## 通用响应格式

### 分页响应

所有列表查询接口返回统一的分页响应格式：

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 1000,
    "total_pages": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

### 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "detail": "详细信息（可选）"
  }
}
```

### 错误码

| HTTP 状态码 | 错误码 | 描述 |
|-------------|--------|------|
| 400 | `BAD_REQUEST` | 请求参数错误 |
| 401 | `UNAUTHORIZED` | 未认证或 Token 无效 |
| 403 | `FORBIDDEN` | 权限不足 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | 资源冲突 |
| 422 | `VALIDATION_ERROR` | 数据验证失败 |
| 429 | `RATE_LIMIT_EXCEEDED` | 请求频率超限 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 |
| 503 | `SERVICE_UNAVAILABLE` | 服务不可用 |

## 通用查询参数

大多数列表接口支持以下通用查询参数：

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `limit` | int | 50/100 | 返回记录数量，最大 1000-10000 |
| `offset` | int | 0 | 跳过记录数量 |
| `search` | string | - | 模糊搜索关键词 |
| `order_by` | string | 因接口而异 | 排序字段 |
| `order_desc` | bool | false/true | 是否降序排序 |
| `before` | datetime | - | 时间范围上限（ISO 8601） |
| `after` | datetime | - | 时间范围下限（ISO 8601） |

### 时间格式

所有时间参数使用 ISO 8601 格式：

```
2026-01-15T00:00:00Z
2026-01-15T08:30:00+08:00
```

## 交易所代码

系统支持以下交易所：

| 代码 | 交易所名称 |
|------|----------|
| `BNC` | Binance |
| `OKX` | OKX |
| `GIO` | Gate.io |

## 交易对命名规范

- **统一格式**: `{BASE}_{QUOTE}.{EXCHANGE}`
- **示例**: `BTC_USDT.BNC`, `ETH_USDT.OKX`
- **根交易对**: `BTC_USDT`（不含交易所后缀）

## 账户命名规范

- **格式**: `{EXCHANGE}_{ACCOUNT_NAME}`
- **示例**: `BNC_MM01`, `OKX_TRADE01`

## API 模块

| 模块 | 文档 | 描述 |
|------|------|------|
| 市场数据 | [market-api.md](./market-api.md) | K线、行情、订单簿数据 |
| 账本数据 | [ledger-api.md](./ledger-api.md) | 余额、订单、成交、转账 |
| 交易对管理 | [symbol-api.md](./symbol-api.md) | 交易对查询与订阅管理 |
| 任务管理 | [jobs-api.md](./jobs-api.md) | 定时任务查询与执行记录 |
| 数据回填 | [backfill-api.md](./backfill-api.md) | 历史数据回填任务 |
| 日志查询 | [logs-api.md](./logs-api.md) | 应用日志查询 |
| 健康检查 | [health-api.md](./health-api.md) | 系统健康状态 |

## 速率限制

| 限制类型 | 限制值 |
|----------|--------|
| 每分钟请求数 | 60 |
| 每小时请求数 | 1000 |

超过限制将返回 `429 Too Many Requests` 响应。

## SDK & 工具

### cURL 示例

```bash
# 获取 K 线数据
curl -X GET "https://api.datahub.example.com/api/v1/klines?symbol=BTC_USDT.BNC&interval=1h&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Python 示例

```python
import requests

BASE_URL = "https://api.datahub.example.com/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 获取 K 线数据
response = requests.get(
    f"{BASE_URL}/klines",
    headers=headers,
    params={
        "symbol": "BTC_USDT.BNC",
        "interval": "1h",
        "limit": 100
    }
)
data = response.json()
```

## 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-01-30 | 初始版本发布 |

