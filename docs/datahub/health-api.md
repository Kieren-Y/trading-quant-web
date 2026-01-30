# 健康检查 API

提供系统健康状态检查接口，用于监控各组件运行状态。

## 获取健康状态

获取系统整体健康状态及各组件详情。

**端点**: `GET /api/v1/health`

**权限**: 无需认证（白名单接口）

### 响应字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | 整体状态：`healthy`, `degraded`, `unhealthy` |
| `timestamp` | datetime | 检查时间 |
| `components` | object | 各组件状态详情 |

### 组件状态

#### database

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | 数据库状态 |
| `latency_ms` | int | 连接延迟（毫秒） |
| `message` | string | 状态描述 |

#### batch

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | 批处理任务状态 |
| `running_jobs` | int | 正在运行的任务数 |
| `message` | string | 状态描述 |

#### websocket

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | WebSocket 连接状态 |
| `active_streamers` | int | 活跃流处理器数量 |
| `streamers` | object | 各流处理器详情 |
| `message` | string | 状态描述 |

#### exchanges

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | 交易所连接状态 |
| `active_exchanges` | int | 活跃交易所数量 |
| `exchanges` | object | 各交易所详情 |
| `message` | string | 状态描述 |

#### api

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | API 服务状态 |
| `message` | string | 状态描述 |

### 状态说明

| 状态 | 描述 |
|------|------|
| `healthy` | 正常运行 |
| `degraded` | 部分功能受限 |
| `warning` | 存在潜在问题 |
| `unhealthy` | 服务不可用 |
| `inactive` | 组件未启用 |

### 请求示例

```bash
curl -X GET "https://api.datahub.example.com/api/v1/health"
```

### 响应示例

```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T08:30:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "latency_ms": 5,
      "message": "Connected (5ms)"
    },
    "batch": {
      "status": "healthy",
      "running_jobs": 2,
      "message": "Running: 2, Last: 2026-01-15T08:25:00Z"
    },
    "websocket": {
      "status": "healthy",
      "active_streamers": 6,
      "streamers": {
        "kline:BNC": {"type": "kline", "exchange": "BNC", "status": "running"},
        "kline:OKX": {"type": "kline", "exchange": "OKX", "status": "running"},
        "ticker:BNC": {"type": "ticker", "exchange": "BNC", "status": "running"},
        "ticker:OKX": {"type": "ticker", "exchange": "OKX", "status": "running"},
        "orderbook:BNC": {"type": "orderbook", "exchange": "BNC", "status": "running"},
        "orderbook:OKX": {"type": "orderbook", "exchange": "OKX", "status": "running"}
      },
      "message": "6 active streamer(s)"
    },
    "exchanges": {
      "status": "healthy",
      "active_exchanges": 3,
      "exchanges": {
        "BNC": {"running": 3},
        "OKX": {"running": 3},
        "GIO": {"running": 2}
      },
      "message": "3 exchange(s) connected"
    },
    "api": {
      "status": "healthy",
      "message": "API is running"
    }
  }
}
```

### 降级状态示例

```json
{
  "status": "degraded",
  "timestamp": "2026-01-15T08:30:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "latency_ms": 10,
      "message": "Connected (10ms)"
    },
    "batch": {
      "status": "warning",
      "message": "No recent executions (10min)"
    },
    "websocket": {
      "status": "degraded",
      "active_streamers": 2,
      "message": "2 active streamer(s)"
    },
    "exchanges": {
      "status": "warning",
      "message": "Check failed: Redis unavailable"
    },
    "api": {
      "status": "healthy",
      "message": "API is running"
    }
  }
}
```

### AI Tool 调用示例

```json
{
  "tool": "datahub_health_check",
  "parameters": {}
}
```

---

## 简易健康检查

快速检查 API 服务是否可用。

**端点**: `GET /health`

**权限**: 无需认证

### 响应示例

```json
{
  "status": "healthy",
  "message": "Use /api/v1/health for detailed health information"
}
```

---

## 使用场景

### 场景 1：监控系统状态

```python
# 定期检查系统健康状态
health = datahub.health_check()

if health["status"] != "healthy":
    print(f"系统状态异常: {health['status']}")
    
    for name, component in health["components"].items():
        if component["status"] not in ("healthy", "inactive"):
            print(f"  {name}: {component['status']} - {component['message']}")
```

### 场景 2：检查特定组件

```python
health = datahub.health_check()

# 检查数据库连接
db = health["components"]["database"]
if db["status"] != "healthy":
    print(f"数据库异常: {db['message']}")
elif db.get("latency_ms", 0) > 100:
    print(f"数据库延迟较高: {db['latency_ms']}ms")

# 检查 WebSocket 流处理器
ws = health["components"]["websocket"]
if ws["status"] != "healthy":
    print(f"WebSocket 异常: {ws['message']}")
else:
    print(f"活跃流处理器: {ws['active_streamers']}")
```

### 场景 3：集成监控告警

```python
import time

def monitor_health():
    while True:
        try:
            health = datahub.health_check()
            
            if health["status"] == "unhealthy":
                send_alert("DataHub 服务不可用", health)
            elif health["status"] == "degraded":
                send_warning("DataHub 服务降级", health)
                
        except Exception as e:
            send_alert("DataHub 健康检查失败", str(e))
            
        time.sleep(60)  # 每分钟检查一次
```

---

## 注意事项

1. **无需认证**: 健康检查接口在白名单中，无需提供 Token
2. **整体状态判定**: 
   - 任一组件 `unhealthy` → 整体 `unhealthy`
   - 任一组件 `degraded`/`warning`/`inactive` → 整体 `degraded`
   - 全部组件 `healthy` → 整体 `healthy`
3. **Redis 依赖**: WebSocket 和 Exchanges 状态检查依赖 Redis，Redis 不可用时返回 `warning`
4. **批处理检查**: 10 分钟内无执行记录会返回 `warning`
5. **建议用途**: 用于负载均衡健康检查、监控告警、运维面板展示

