# 任务管理 API

提供定时任务（Scheduled Jobs）及其执行历史的只读查询接口。任务由调度器管理，此 API 仅暴露状态和历史记录。

## 目录

- [获取任务列表](#获取任务列表)
- [获取任务详情](#获取任务详情)
- [获取所有执行记录](#获取所有执行记录)
- [获取任务执行记录](#获取任务执行记录)

---

## 获取任务列表

获取所有定时任务配置。

**端点**: `GET /api/v1/jobs`

**权限**: `read:jobs`

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `search` | string | 否 | - | 搜索任务名称或任务类型 |
| `limit` | int | 否 | 50 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `name` | 排序字段 |
| `order_desc` | bool | 否 | `false` | 是否降序 |

### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | string | 任务 ID（与 name 相同） |
| `job_type` | string | 任务类型：`kline`, `symbol`, `balance` 等 |
| `name` | string | 任务名称 |
| `job_category` | string | 任务分类：`backfill`, `sync`, `monitor`, `cleanup` |
| `description` | string | 任务描述 |
| `schedule_type` | string | 调度类型：`cron`, `interval` |
| `schedule` | string | Cron 表达式（当 schedule_type 为 cron 时） |
| `interval_seconds` | int | 间隔秒数（当 schedule_type 为 interval 时） |
| `parameters` | object | 任务参数 |
| `timeout_seconds` | int | 超时时间（秒） |
| `max_instances` | int | 最大并发实例数 |
| `enabled` | bool | 是否启用 |
| `last_run_at` | datetime | 上次执行时间 |
| `next_run_at` | datetime | 下次执行时间 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### 任务类型说明

| 类型 | 描述 |
|------|------|
| `kline` | K 线数据同步 |
| `symbol` | 交易对同步 |
| `balance` | 余额同步 |
| `order` | 订单同步 |
| `fill` | 成交同步 |
| `transfer` | 转账同步 |
| `ticker` | 行情同步 |
| `orderbook` | 订单簿同步 |

### 任务分类说明

| 分类 | 描述 |
|------|------|
| `backfill` | 历史数据回填 |
| `sync` | 实时数据同步 |
| `monitor` | 监控任务 |
| `cleanup` | 数据清理 |

### 请求示例

```bash
# 获取所有任务
curl -X GET "https://api.datahub.example.com/api/v1/jobs" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索 kline 相关任务
curl -X GET "https://api.datahub.example.com/api/v1/jobs?search=kline" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按名称倒序排列
curl -X GET "https://api.datahub.example.com/api/v1/jobs?order_by=name&order_desc=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "data": [
    {
      "id": "sync_klines_1h",
      "job_type": "kline",
      "name": "sync_klines_1h",
      "job_category": "sync",
      "description": "Sync 1-hour klines from all exchanges",
      "schedule_type": "cron",
      "schedule": "0 * * * *",
      "interval_seconds": null,
      "parameters": {
        "intervals": ["1h"],
        "exchanges": ["BNC", "OKX", "GIO"]
      },
      "timeout_seconds": 300,
      "max_instances": 1,
      "enabled": true,
      "last_run_at": "2026-01-15T08:00:00Z",
      "next_run_at": "2026-01-15T09:00:00Z",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-15T08:00:00Z"
    },
    {
      "id": "sync_symbols_all",
      "job_type": "symbol",
      "name": "sync_symbols_all",
      "job_category": "sync",
      "description": "Sync trading symbols from all exchanges",
      "schedule_type": "cron",
      "schedule": "0 0 * * *",
      "interval_seconds": null,
      "parameters": {
        "exchanges": ["BNC", "OKX", "GIO"]
      },
      "timeout_seconds": 600,
      "max_instances": 1,
      "enabled": true,
      "last_run_at": "2026-01-15T00:00:00Z",
      "next_run_at": "2026-01-16T00:00:00Z",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-15T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 15,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_list_jobs",
  "parameters": {
    "search": "kline",
    "limit": 20
  }
}
```

---

## 获取任务详情

根据 ID 或名称获取单个任务详细信息。

**端点**: `GET /api/v1/jobs/{job_id}`

**权限**: `read:jobs`

### 路径参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | string | 是 | 任务 ID 或任务名称 |

### 请求示例

```bash
# 通过数字 ID 获取
curl -X GET "https://api.datahub.example.com/api/v1/jobs/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 通过任务名称获取
curl -X GET "https://api.datahub.example.com/api/v1/jobs/sync_klines_1h" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "id": "sync_klines_1h",
  "job_type": "kline",
  "name": "sync_klines_1h",
  "job_category": "sync",
  "description": "Sync 1-hour klines from all exchanges",
  "schedule_type": "cron",
  "schedule": "0 * * * *",
  "interval_seconds": null,
  "parameters": {
    "intervals": ["1h"],
    "exchanges": ["BNC", "OKX", "GIO"]
  },
  "timeout_seconds": 300,
  "max_instances": 1,
  "enabled": true,
  "last_run_at": "2026-01-15T08:00:00Z",
  "next_run_at": "2026-01-15T09:00:00Z",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-15T08:00:00Z"
}
```

### 错误响应

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Job not found: invalid_job_name"
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_get_job",
  "parameters": {
    "job_id": "sync_klines_1h"
  }
}
```

---

## 获取所有执行记录

获取所有任务的执行历史记录。

**端点**: `GET /api/v1/jobs/executions`

**权限**: `read:jobs`

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `search` | string | 否 | - | 搜索任务名称或状态 |
| `limit` | int | 否 | 50 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `started_at` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限 |
| `after` | datetime | 否 | - | 时间下限 |

### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | string | 执行记录 ID |
| `job_id` | string | 关联任务 ID |
| `job_name` | string | 任务名称快照 |
| `status` | string | 执行状态：`PENDING`, `RUNNING`, `SUCCESS`, `FAILURE`, `TIMEOUT` |
| `started_at` | datetime | 开始时间 |
| `completed_at` | datetime | 完成时间 |
| `duration_ms` | int | 执行耗时（毫秒） |
| `result` | object | 执行结果 |
| `error` | string | 错误信息（如有） |
| `trace_id` | string | 分布式追踪 ID |
| `worker_id` | string | 执行 Worker 标识 |
| `parameters_snapshot` | object | 执行时的参数快照 |
| `created_at` | datetime | 记录创建时间 |

### 执行状态说明

| 状态 | 描述 |
|------|------|
| `PENDING` | 等待执行 |
| `RUNNING` | 执行中 |
| `SUCCESS` | 执行成功 |
| `FAILURE` | 执行失败 |
| `TIMEOUT` | 执行超时 |

### 请求示例

```bash
# 获取最新执行记录
curl -X GET "https://api.datahub.example.com/api/v1/jobs/executions?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索失败的执行
curl -X GET "https://api.datahub.example.com/api/v1/jobs/executions?search=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定时间范围的执行记录
curl -X GET "https://api.datahub.example.com/api/v1/jobs/executions?after=2026-01-01T00:00:00Z&before=2026-01-15T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "data": [
    {
      "id": "12345",
      "job_id": "1",
      "job_name": "sync_klines_1h",
      "status": "SUCCESS",
      "started_at": "2026-01-15T08:00:00Z",
      "completed_at": "2026-01-15T08:02:30Z",
      "duration_ms": 150000,
      "result": {
        "processed": 500,
        "inserted": 450,
        "updated": 50
      },
      "error": null,
      "trace_id": "abc123def456",
      "worker_id": "worker-01",
      "parameters_snapshot": {
        "intervals": ["1h"],
        "exchanges": ["BNC", "OKX", "GIO"]
      },
      "created_at": "2026-01-15T08:00:00Z"
    },
    {
      "id": "12344",
      "job_id": "2",
      "job_name": "sync_symbols_all",
      "status": "FAILURE",
      "started_at": "2026-01-15T00:00:00Z",
      "completed_at": "2026-01-15T00:01:00Z",
      "duration_ms": 60000,
      "result": {
        "error_message": "Connection timeout"
      },
      "error": "Connection timeout",
      "trace_id": "xyz789abc012",
      "worker_id": "worker-02",
      "parameters_snapshot": {
        "exchanges": ["BNC", "OKX", "GIO"]
      },
      "created_at": "2026-01-15T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 1500,
    "total_pages": 30,
    "has_next": true,
    "has_prev": false
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_list_job_executions",
  "parameters": {
    "search": "failed",
    "limit": 20,
    "after": "2026-01-01T00:00:00Z"
  }
}
```

---

## 获取任务执行记录

获取指定任务的执行历史记录。

**端点**: `GET /api/v1/jobs/{job_id}/executions`

**权限**: `read:jobs`

### 路径参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | string | 是 | 任务 ID 或任务名称 |

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `search` | string | 否 | - | 搜索状态 |
| `limit` | int | 否 | 50 | 返回记录数，范围 1-1000 |
| `offset` | int | 否 | 0 | 跳过记录数 |
| `order_by` | string | 否 | `started_at` | 排序字段 |
| `order_desc` | bool | 否 | `true` | 是否降序 |
| `before` | datetime | 否 | - | 时间上限 |
| `after` | datetime | 否 | - | 时间下限 |

### 请求示例

```bash
# 获取指定任务的执行记录
curl -X GET "https://api.datahub.example.com/api/v1/jobs/sync_klines_1h/executions" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取失败的执行记录
curl -X GET "https://api.datahub.example.com/api/v1/jobs/sync_klines_1h/executions?search=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取指定时间范围的执行记录
curl -X GET "https://api.datahub.example.com/api/v1/jobs/sync_klines_1h/executions?after=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应示例

```json
{
  "data": [
    {
      "id": "12345",
      "job_id": "1",
      "job_name": "sync_klines_1h",
      "status": "SUCCESS",
      "started_at": "2026-01-15T08:00:00Z",
      "completed_at": "2026-01-15T08:02:30Z",
      "duration_ms": 150000,
      "result": {
        "processed": 500,
        "inserted": 450,
        "updated": 50
      },
      "error": null,
      "trace_id": "abc123def456",
      "worker_id": "worker-01",
      "parameters_snapshot": {
        "intervals": ["1h"],
        "exchanges": ["BNC", "OKX", "GIO"]
      },
      "created_at": "2026-01-15T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 720,
    "total_pages": 15,
    "has_next": true,
    "has_prev": false
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_get_job_executions",
  "parameters": {
    "job_id": "sync_klines_1h",
    "limit": 10,
    "order_desc": true
  }
}
```

---

## 使用场景

### 场景 1：监控任务执行状态

```python
# 获取最近失败的任务执行
failed_executions = datahub.list_job_executions(
    search="failed",
    limit=10,
    order_desc=True
)

for exec in failed_executions["data"]:
    print(f"任务 {exec['job_name']} 失败: {exec['error']}")
    print(f"  Trace ID: {exec['trace_id']}")
    print(f"  时间: {exec['started_at']}")
```

### 场景 2：分析任务执行效率

```python
# 获取指定任务的执行历史
executions = datahub.get_job_executions(
    job_id="sync_klines_1h",
    limit=100,
    after="2026-01-01T00:00:00Z"
)

# 计算平均执行时间
durations = [e["duration_ms"] for e in executions["data"] if e["duration_ms"]]
avg_duration = sum(durations) / len(durations) if durations else 0
print(f"平均执行时间: {avg_duration / 1000:.2f} 秒")

# 计算成功率
success_count = sum(1 for e in executions["data"] if e["status"] == "SUCCESS")
success_rate = success_count / len(executions["data"]) * 100
print(f"成功率: {success_rate:.1f}%")
```

### 场景 3：查看任务配置

```python
# 获取所有同步类任务
jobs = datahub.list_jobs(search="sync")

for job in jobs["data"]:
    if job["enabled"]:
        print(f"任务: {job['name']}")
        print(f"  类型: {job['job_type']}")
        print(f"  调度: {job['schedule']}")
        print(f"  下次执行: {job['next_run_at']}")
```

---

## 注意事项

1. **只读接口**: 任务管理 API 仅提供查询功能，任务配置由调度器管理
2. **ID 与名称**: `job_id` 参数同时支持数字 ID 和任务名称
3. **执行记录保留**: 执行记录会定期清理，建议及时导出需要保留的数据
4. **Trace ID**: 可用于关联日志系统中的详细执行日志
5. **时间范围**: 建议使用 `before` 和 `after` 参数限制查询范围

