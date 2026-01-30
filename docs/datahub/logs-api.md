# 日志查询 API

提供应用日志的结构化查询接口。日志存储为按日期和命名空间组织的文件，支持多维度过滤。

## 目录

- [获取日志列表](#获取日志列表)
- [日志文件结构](#日志文件结构)
- [使用场景](#使用场景)

---

## 获取日志列表

查询应用日志，支持按日期、级别、命名空间、任务 ID 等条件过滤。

**端点**: `GET /api/v1/logs`

**权限**: `read:logs`

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `date` | string | 否 | 最新日期 | 日志日期，格式 `YYYY-MM-DD` |
| `level` | string | 否 | - | 日志级别：`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `namespace` | string | 否 | - | 命名空间，如 `kline`, `symbol`, `balance` |
| `mode` | string | 否 | - | 运行模式，如 `batch`, `streamer` |
| `log_type` | string | 否 | - | 日志类型：`batch`, `streamer`, `scheduler`, `error`, `app` |
| `job_id` | string | 否 | - | 任务 ID / Trace ID |
| `message__icontains` | string | 否 | - | 消息内容模糊搜索（不区分大小写） |
| `limit` | int | 否 | 100 | 返回记录数，范围 1-10000 |
| `offset` | int | 否 | 0 | 跳过记录数 |

### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | int | 日志序号 |
| `timestamp` | datetime | 日志时间 |
| `level` | string | 日志级别 |
| `message` | string | 日志消息 |
| `trace_id` | string | 追踪 ID |
| `job_id` | string | 任务 ID（与 trace_id 相同） |
| `namespace` | string | 命名空间 |
| `mode` | string | 运行模式 |
| `business` | string | 业务标识 |
| `log_type` | string | 日志类型 |
| `exception` | string | 异常信息 |
| `stack_trace` | string | 堆栈跟踪 |
| `extra` | object | 额外数据 |

### 日志级别说明

| 级别 | 描述 |
|------|------|
| `DEBUG` | 调试信息 |
| `INFO` | 一般信息 |
| `WARNING` | 警告信息 |
| `ERROR` | 错误信息 |
| `CRITICAL` | 严重错误 |

### 日志类型说明

| 类型 | 描述 | 对应文件 |
|------|------|----------|
| `batch` | 批处理任务日志 | `{namespace}_batch.log` |
| `streamer` | 流处理任务日志 | `{namespace}_streamer.log` |
| `scheduler` | 调度器日志 | `scheduler.log` |
| `error` | 错误汇总日志 | `error.log` |
| `app` | 应用通用日志 | `app.log` |

### 请求示例

```bash
# 获取最新日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定日期的日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?date=2026-01-15" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取错误日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?level=ERROR" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取错误汇总日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?log_type=error" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取调度器日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?log_type=scheduler" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取 kline 批处理日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?namespace=kline&mode=batch" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按任务 ID 查询
curl -X GET "https://api.datahub.example.com/api/v1/logs?job_id=backfill_kline_abc12345" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索包含 timeout 的日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?message__icontains=timeout" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取警告及以上级别的日志
curl -X GET "https://api.datahub.example.com/api/v1/logs?level=WARNING&limit=500" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "data": [
    {
      "id": 1,
      "timestamp": "2026-01-15T08:30:15.123Z",
      "level": "INFO",
      "message": "Kline backfill started | exchanges=2 | symbols=10",
      "trace_id": "backfill_kline_abc12345",
      "job_id": "backfill_kline_abc12345",
      "namespace": "kline",
      "mode": "batch",
      "business": null,
      "log_type": "batch",
      "exception": null,
      "stack_trace": null,
      "extra": null
    },
    {
      "id": 2,
      "timestamp": "2026-01-15T08:30:16.456Z",
      "level": "INFO",
      "message": "Processing BTC_USDT.BNC | interval=1h | records=500",
      "trace_id": "backfill_kline_abc12345",
      "job_id": "backfill_kline_abc12345",
      "namespace": "kline",
      "mode": "batch",
      "business": null,
      "log_type": "batch",
      "exception": null,
      "stack_trace": null,
      "extra": null
    },
    {
      "id": 3,
      "timestamp": "2026-01-15T08:30:20.789Z",
      "level": "ERROR",
      "message": "Failed to fetch klines from OKX | error=Connection timeout",
      "trace_id": "backfill_kline_abc12345",
      "job_id": "backfill_kline_abc12345",
      "namespace": "kline",
      "mode": "batch",
      "business": null,
      "log_type": "batch",
      "exception": "ConnectionError",
      "stack_trace": "Traceback (most recent call last):\n  File ...",
      "extra": null
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

### AI Tool 调用示例

```json
{
  "tool": "datahub_list_logs",
  "parameters": {
    "job_id": "backfill_kline_abc12345",
    "limit": 100
  }
}
```

---

## 日志文件结构

### 目录结构

```
logs/
├── 2026-01-15/
│   ├── kline_batch.log
│   ├── kline_streamer.log
│   ├── symbol_batch.log
│   ├── balance_batch.log
│   ├── order_batch.log
│   ├── ticker_streamer.log
│   ├── orderbook_streamer.log
│   ├── scheduler.log
│   ├── error.log
│   └── app.log
├── 2026-01-14/
│   └── ...
└── ...
```

### 日志格式

```
{timestamp} | {level} | {namespace}.{mode} [{trace_id}] | {message}
```

示例：
```
2026-01-15 08:30:15.123 | INFO     | kline.batch [backfill_kline_abc12345] | Kline backfill started | exchanges=2 | symbols=10
2026-01-15 08:30:20.789 | ERROR    | kline.batch [backfill_kline_abc12345] | Failed to fetch klines from OKX | error=Connection timeout
```

### 命名空间说明

| 命名空间 | 描述 |
|----------|------|
| `kline` | K 线数据处理 |
| `symbol` | 交易对处理 |
| `balance` | 余额处理 |
| `order` | 订单处理 |
| `fill` | 成交处理 |
| `transfer` | 转账处理 |
| `ticker` | 行情处理 |
| `orderbook` | 订单簿处理 |

### 运行模式说明

| 模式 | 描述 |
|------|------|
| `batch` | 批处理模式（定时任务、回填任务） |
| `streamer` | 流处理模式（WebSocket 实时数据） |

---

## 使用场景

### 场景 1：追踪回填任务执行

```python
# 触发回填任务
response = datahub.backfill_klines(
    symbols=["BTC_USDT.BNC"],
    intervals=["1h"],
    start_time="2026-01-01T00:00:00Z"
)

trace_id = response["trace_id"]

# 查询任务执行日志
logs = datahub.list_logs(
    job_id=trace_id,
    limit=100
)

# 分析执行过程
for log in logs["data"]:
    if log["level"] == "ERROR":
        print(f"错误: {log['message']}")
    elif "completed" in log["message"].lower():
        print(f"完成: {log['message']}")
```

### 场景 2：监控系统错误

```python
# 获取今日所有错误
errors = datahub.list_logs(
    level="ERROR",
    limit=500
)

# 按命名空间分组统计
from collections import Counter
error_counts = Counter(log["namespace"] for log in errors["data"])

print("错误统计:")
for namespace, count in error_counts.most_common():
    print(f"  {namespace}: {count}")
```

### 场景 3：分析调度器状态

```python
# 获取调度器日志
scheduler_logs = datahub.list_logs(
    log_type="scheduler",
    limit=200
)

# 查找任务执行记录
for log in scheduler_logs["data"]:
    if "started" in log["message"].lower():
        print(f"任务启动: {log['message']}")
    elif "completed" in log["message"].lower():
        print(f"任务完成: {log['message']}")
    elif "failed" in log["message"].lower():
        print(f"任务失败: {log['message']}")
```

### 场景 4：搜索特定问题

```python
# 搜索连接超时相关日志
timeout_logs = datahub.list_logs(
    message__icontains="timeout",
    limit=100
)

# 搜索 OKX 相关错误
okx_errors = datahub.list_logs(
    message__icontains="OKX",
    level="ERROR",
    limit=100
)
```

### 场景 5：查看历史日志

```python
# 获取指定日期的 kline 批处理日志
historical_logs = datahub.list_logs(
    date="2026-01-10",
    namespace="kline",
    mode="batch",
    limit=500
)
```

---

## 注意事项

1. **日志保留**: 日志按日期目录存储，历史日志可能会定期清理
2. **默认日期**: 不指定日期时，返回最新日期目录的日志
3. **日志类型优先**: 指定 `log_type` 时会读取特定日志文件（如 `error.log`）
4. **命名空间与模式**: `namespace` 和 `mode` 组合确定具体日志文件
5. **大小写**: `level` 参数会自动转换为大写
6. **Trace ID**: 回填任务的 `trace_id` 可用于追踪完整执行过程
7. **性能考虑**: 大量日志查询可能较慢，建议使用过滤条件缩小范围

