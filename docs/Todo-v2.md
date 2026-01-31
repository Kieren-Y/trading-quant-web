# Crypto量化交易平台完整功能需求分析 (v2.0)

**文档版本**: 2.0
**创建日期**: 2025-12-31
**作者**: Senior Quant Architect (AI)
**视角**: 专业金融交易员 + 产品经理

---

## 📊 执行摘要

本文档从专业金融交易员和产品经理的双重视角，全面分析一个合格的Crypto量化交易平台需要具备的功能模块。

**当前系统完成度**: 约 25%

**核心缺失模块**（按优先级排序）:
1. ⭐⭐⭐⭐⭐ **持仓管理系统 (PMS)** - 致命缺陷，立即补充
2. ⭐⭐⭐⭐⭐ **风险控制引擎 (RMS)** - 没有风控=定时炸弹
3. ⭐⭐⭐⭐⭐ **实时市场数据服务** - 策略决策基础
4. ⭐⭐⭐⭐ **订单状态同步** - 交易员必须实时掌握订单状态
5. ⭐⭐⭐⭐ **回测系统** - 策略验证必需

---

## 🔍 第一部分：现有系统评估

### ✅ 已实现功能

#### 1. OMS (订单管理系统) - 部分完成 (40%)

**位置**: `api-gateway/app/services/order_service.py:17`

**已实现**:
- ✅ 基础订单创建 (市价单/限价单)
- ✅ 订单历史查询
- ✅ 订单撤销
- ✅ 多交易所CCXT统一接口

**API端点** (`api-gateway/app/api/v1/order.py`):
```python
POST   /api/v1/orders/        # 创建订单
GET    /api/v1/orders/        # 查询订单列表
POST   /api/v1/orders/{id}/cancel  # 撤销订单
```

#### 2. 交易所管理 - 完成 (80%)

**位置**: `api-gateway/app/services/exchange_service.py:10`

**已实现**:
- ✅ 多交易所API Key配置
- ✅ API Key加密存储
- ✅ 账户激活/停用管理
- ✅ CCXT统一封装

**数据模型**:
```python
class ExchangeConfig(Base):
    exchange_name = Column(String)  # binance/okx/bybit
    api_key = Column(String)  # 加密存储
    secret_key = Column(String)  # 加密存储
    account_name = Column(String)  # 用户自定义名称
    is_active = Column(Boolean)
```

#### 3. 策略框架 - 基础完成 (30%)

**位置**: `api-gateway/app/strategies/base.py:5`

**已实现**:
- ✅ 策略生命周期管理 (start/stop)
- ✅ 策略配置存储 (JSON参数)
- ✅ 简单网格策略示例 (仅Mock)

**严重不足**:
- ❌ 无真实市场数据接入
- ❌ 无回测系统
- ❌ 无绩效分析
- ❌ 无参数优化

**API端点** (`api-gateway/app/api/v1/strategy.py`):
```python
GET    /api/v1/strategies/        # 查询策略列表
POST   /api/v1/strategies/        # 创建策略配置
PUT    /api/v1/strategies/{id}    # 更新策略参数
DELETE /api/v1/strategies/{id}    # 删除策略
POST   /api/v1/strategies/{id}/start  # 启动策略
POST   /api/v1/strategies/{id}/stop   # 停止策略
```

#### 4. 资产视图 - 基础完成 (20%)

**位置**: `api-gateway/app/api/v1/asset.py:16`

**已实现**:
- ✅ 投资组合汇总 (PortfolioSummary)

**缺失**:
- ❌ 持仓明细
- ❌ 实时盈亏计算
- ❌ 多账户聚合视图

#### 5. 基础设施 - 完成 (90%)

**技术栈**:
- ✅ FastAPI (高性能异步框架)
- ✅ PostgreSQL (关系型数据库)
- ✅ Redis (缓存/消息队列)
- ✅ SQLAlchemy (异步ORM)
- ✅ CCXT (交易所统一接口)
- ✅ Docker Compose (基础设施编排)

**依赖管理** (`pyproject.toml`):
```toml
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.109.0"
ccxt = "^4.2.0"
pandas = "^2.2.0"
sqlalchemy = "^2.0.0"
redis = "^5.0.0"
```

---

### ❌ 关键缺失模块

| 模块 | 影响程度 | 优先级 | 预计工作量 |
|------|---------|--------|-----------|
| **持仓管理系统 (PMS)** | 🔴 致命 | P0 | 2周 |
| **风险控制引擎 (RMS)** | 🔴 致命 | P0 | 2-3周 |
| **实时市场数据服务** | 🔴 严重 | P0 | 1-2周 |
| **订单状态实时同步** | 🟠 严重 | P0 | 1周 |
| **回测系统** | 🟠 严重 | P1 | 3-4周 |
| **高级订单类型** | 🟡 重要 | P1 | 2周 |
| **监控告警系统** | 🟡 重要 | P1 | 2周 |
| **算法订单 (TWAP/VWAP)** | 🟢 可选 | P2 | 4周 |

---

## 🎯 第二部分：完整功能架构详解

### 系统一：OMS (Order Management System) 订单管理

**当前状态**: 基础完成度 40%

#### 1.1 订单生命周期管理 (P0 - 立即实现)

**完整订单状态机**:
```
[创建] → [待提交] → [已提交] → [部分成交] → [完全成交]
                  ↓
              [已撤销] ← [撤销中]
                  ↓
              [拒绝] ← [事前风控未通过]
                  ↓
              [失败] ← [交易所错误]
```

**缺失功能**:

**1) 订单状态实时同步** ⭐⭐⭐⭐⭐

```python
# 需新增: api-gateway/app/services/order_sync_service.py

class OrderSyncService:
    """订单状态实时同步服务"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6380)
        self.sync_interval = 2  # 每2秒同步一次

    async def start_sync_loop(self, user_id: int):
        """
        后台循环：每2秒从交易所同步订单状态
        """
        while True:
            try:
                await self.sync_open_orders(user_id)
                await self.sync_closed_orders(user_id)
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"订单同步失败: {e}")
                await asyncio.sleep(5)

    async def sync_open_orders(self, user_id: int):
        """
        同步未完成订单
        """
        # 1. 从数据库获取所有未完成订单
        open_orders = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.status.in_(['open', 'partially_filled'])
            )
        )

        # 2. 按交易所分组
        orders_by_exchange = self._group_by_exchange(open_orders)

        # 3. 批量查询交易所
        for exchange_id, orders in orders_by_exchange.items():
            exchange = await self.get_exchange(exchange_id)

            for order in orders:
                try:
                    # 从交易所获取最新状态
                    ccxt_order = await exchange.fetch_order(order.exchange_order_id, order.symbol)

                    # 如果状态有变化，更新数据库
                    if ccxt_order['status'] != order.status:
                        await self._update_order_status(order, ccxt_order)

                        # 通过WebSocket推送到前端
                        await self._push_order_update(order)

                except Exception as e:
                    logger.error(f"同步订单{order.id}失败: {e}")

    async def _update_order_status(self, order: Order, ccxt_order: dict):
        """更新订单状态"""
        order.status = ccxt_order['status']
        order.filled = ccxt_order.get('filled', 0)
        order.cost = ccxt_order.get('cost', 0)

        # 计算平均成交价
        if order.filled > 0:
            order.avg_price = order.cost / order.filled

        await self.db.commit()
```

**WebSocket推送**:
```python
# 需新增: api-gateway/app/api/v1/websocket.py

@router.websocket("/ws/orders")
async def order_updates(websocket: WebSocket, user_id: int):
    await websocket.accept()

    try:
        while True:
            # 从Redis订阅订单更新
            message = await redis_sub.get_message()
            if message and message['type'] == 'message':
                await websocket.send_json(message['data'])
    except WebSocketDisconnect:
        logger.info(f"用户{user_id}断开WebSocket连接")
```

**2) 订单修改功能** ⭐⭐⭐⭐

```python
# 扩展: api-gateway/app/services/order_service.py

async def modify_order(
    self,
    user_id: int,
    order_id: int,
    new_price: Optional[float] = None,
    new_amount: Optional[float] = None
) -> Order:
    """
    修改订单（无需撤销重建）

    实现方式：
    1. 如果交易所支持edit_order，直接调用
    2. 否则：撤销旧订单 → 创建新订单（原子操作）
    """
    order = await self.get_by_id(order_id, user_id)
    if not order:
        raise ValueError("订单不存在")

    if order.status not in ['open', 'partially_filled']:
        raise ValueError("只能修改未完成的订单")

    exchange = await CCXTService.get_exchange(order.exchange_config)

    # 尝试直接修改（部分交易所支持）
    if hasattr(exchange, 'edit_order'):
        try:
            ccxt_order = await exchange.edit_order(
                order.exchange_order_id,
                order.symbol,
                amount=new_amount or order.amount,
                price=new_price or order.price
            )

            # 更新数据库
            order.price = new_price or order.price
            order.amount = new_amount or order.amount
            await self.db.commit()

            return order

        except Exception as e:
            logger.warning(f"直接修改失败，尝试撤销重建: {e}")

    # 降级方案：撤销后重建
    async with self.db.begin():  # 事务保证原子性
        # 1. 撤销旧订单
        await self.cancel_order(user_id, order_id)

        # 2. 创建新订单
        new_order = await self.create_order(user_id, OrderCreate(
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            price=new_price or order.price,
            amount=new_amount or order.amount,
            exchange_config_id=order.exchange_config_id
        ))

        return new_order
```

**API端点**:
```python
@router.put("/orders/{order_id}")
async def modify_order(
    order_id: int,
    price: Optional[float] = None,
    amount: Optional[float] = None
):
    """修改订单价格或数量"""
    return await order_service.modify_order(user_id, order_id, price, amount)
```

#### 1.2 条件单系统 (P0 - 立即实现)

**条件单类型**:

| 类型 | 说明 | 优先级 |
|------|------|--------|
| **止损单 (Stop Loss)** | 价格跌破X USD时卖出 | ⭐⭐⭐⭐⭐ |
| **止盈单 (Take Profit)** | 价格突破X USD时卖出 | ⭐⭐⭐⭐⭐ |
| **跟踪止损 (Trailing Stop)** | 距离最高点回落3%时卖出 | ⭐⭐⭐⭐ |
| **条件单 (Conditional)** | BTC突破100K则买入ETH | ⭐⭐⭐ |

**数据模型**:
```python
# 需新增: api-gateway/app/models/conditional_order.py

class ConditionalOrder(Base, TimeStampMixin):
    """条件单表"""
    __tablename__ = "conditional_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exchange_config_id = Column(Integer, ForeignKey("exchange_configs.id"))

    # 条件参数
    condition_type = Column(String)  # stop_loss/take_profit/trailing_stop/conditional
    symbol = Column(String)
    trigger_price = Column(Float)  # 触发价格
    trail_percent = Column(Float)  # 跟踪止损百分比

    # 触发后的订单参数
    order_side = Column(String)  # buy/sell
    order_type = Column(String)  # market/limit
    order_price = Column(Float)  # 限价单价格
    order_amount = Column(Float)

    # 状态
    status = Column(String, default="pending")  # pending/triggered/executed/canceled
    triggered_at = Column(DateTime)

    # 关联
    parent_order_id = Column(Integer, ForeignKey("orders.id"))  # 如果是从某个订单衍生的
```

**条件单监控引擎**:
```python
# 需新增: api-gateway/app/services/conditional_order_service.py

class ConditionalOrderMonitor:
    """条件单监控引擎"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6380)
        self.check_interval = 0.5  # 每0.5秒检查一次

    async def start_monitor(self):
        """启动监控循环"""
        while True:
            try:
                await self.check_and_trigger_orders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"条件单监控失败: {e}")
                await asyncio.sleep(5)

    async def check_and_trigger_orders(self):
        """
        检查所有待触发的条件单
        """
        # 1. 从数据库获取所有pending状态的条件单
        pending_orders = await self.db.execute(
            select(ConditionalOrder).where(
                ConditionalOrder.status == 'pending'
            )
        )

        # 2. 获取实时价格
        symbols = set([order.symbol for order in pending_orders])
        prices = await self._get_latest_prices(symbols)

        # 3. 检查触发条件
        for order in pending_orders:
            current_price = prices.get(order.symbol)

            if self._should_trigger(order, current_price):
                await self._execute_conditional_order(order, current_price)

    def _should_trigger(self, order: ConditionalOrder, current_price: float) -> bool:
        """判断是否应该触发"""
        if order.condition_type == 'stop_loss':
            # 止损：当前价 <= 触发价
            return current_price <= order.trigger_price

        elif order.condition_type == 'take_profit':
            # 止盈：当前价 >= 触发价
            return current_price >= order.trigger_price

        elif order.condition_type == 'trailing_stop':
            # 跟踪止损：从最高点回落超过trail_percent
            highest_price = self._get_highest_price(order.symbol, period='1h')
            drawdown = (highest_price - current_price) / highest_price
            return drawdown >= order.trail_percent

        return False

    async def _execute_conditional_order(
        self,
        order: ConditionalOrder,
        trigger_price: float
    ):
        """执行条件单"""
        # 1. 更新状态为triggered
        order.status = 'triggered'
        order.triggered_at = datetime.now()
        await self.db.commit()

        # 2. 提交实际订单到交易所
        order_service = OrderService(self.db)
        try:
            executed_order = await order_service.create_order(
                user_id=order.user_id,
                order_in=OrderCreate(
                    symbol=order.symbol,
                    side=order.order_side,
                    type=order.order_type,
                    price=order.order_price,
                    amount=order.order_amount,
                    exchange_config_id=order.exchange_config_id
                )
            )

            # 3. 更新状态为executed
            order.status = 'executed'
            await self.db.commit()

            # 4. 发送通知
            await self._send_notification(
                user_id=order.user_id,
                message=f"✅ 条件单已触发: {order.symbol} @ {trigger_price}",
                order_id=executed_order.id
            )

        except Exception as e:
            logger.error(f"条件单执行失败: {e}")
            order.status = 'failed'
            await self.db.commit()
```

#### 1.3 OCO订单 (One-Cancels-Other) (P1 - 2周内)

**使用场景**: 同时设置止损和止盈，任意一个触发则另一个自动撤销

```python
class OCOOrderService:
    """OCO订单服务"""

    async def create_oco_order(
        self,
        user_id: int,
        symbol: str,
        side: str,
        amount: float,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float
    ):
        """
        创建OCO订单对

        示例：
        买入BTC @ $95,000
        - 止损: $93,000 (亏损$2,000)
        - 止盈: $98,000 (盈利$3,000)

        任意一个成交，另一个自动撤销
        """
        async with self.db.begin():
            # 1. 创建父订单记录OCO关系
            parent_order = Order(
                user_id=user_id,
                symbol=symbol,
                side=side,
                type='oco',
                amount=amount,
                status='oco_parent'
            )
            self.db.add(parent_order)
            await self.db.flush()  # 获取parent_order.id

            # 2. 创建止损单
            stop_loss_order = await order_service.create_order(user_id, OrderCreate(
                symbol=symbol,
                side='sell' if side == 'buy' else 'buy',
                type='stop_loss',
                price=stop_loss_price,
                amount=amount,
                parent_order_id=parent_order.id
            ))

            # 3. 创建止盈单
            take_profit_order = await order_service.create_order(user_id, OrderCreate(
                symbol=symbol,
                side='sell' if side == 'buy' else 'buy',
                type='limit',
                price=take_profit_price,
                amount=amount,
                parent_order_id=parent_order.id
            ))

            # 4. 记录OCO关系
            oco_relation = OCOOrder(
                parent_order_id=parent_order.id,
                stop_loss_order_id=stop_loss_order.id,
                take_profit_order_id=take_profit_order.id
            )
            self.db.add(oco_relation)

            await self.db.commit()

            return parent_order

    async def on_order_filled(self, filled_order_id: int):
        """
        当OCO订单中任意一个成交时，自动撤销另一个

        这个方法应该在订单状态同步时被调用
        """
        # 1. 查找OCO关系
        oco_relation = await self.db.execute(
            select(OCOOrder).where(
                or_(
                    OCOOrder.stop_loss_order_id == filled_order_id,
                    OCOOrder.take_profit_order_id == filled_order_id
                )
            )
        )
        oco = oco_relation.scalar_one_or_none()

        if not oco:
            return  # 不是OCO订单

        # 2. 确定需要撤销的订单
        if filled_order_id == oco.stop_loss_order_id:
            to_cancel_id = oco.take_profit_order_id
        else:
            to_cancel_id = oco.stop_loss_order_id

        # 3. 撤销另一个订单
        await order_service.cancel_order(
            user_id=oco.parent_order.user_id,
            order_id=to_cancel_id
        )

        logger.info(f"OCO订单触发: 订单{filled_order_id}成交，自动撤销订单{to_cancel_id}")
```

#### 1.4 批量订单操作 (P1 - 2周内)

**使用场景**: 一键平仓所有持仓、批量调整止损价

```python
class BulkOrderService:
    """批量订单服务"""

    async def close_all_positions(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        exchange_id: Optional[int] = None
    ):
        """
        一键平仓

        参数:
        - symbol: 指定币种（可选），None则平所有
        - exchange_id: 指定交易所（可选），None则所有交易所
        """
        # 1. 获取所有持仓
        positions = await position_service.get_positions(user_id, symbol, exchange_id)

        # 2. 按交易所分组
        positions_by_exchange = self._group_by_exchange(positions)

        # 3. 批量提交平仓单
        results = []
        for exchange_id, pos_list in positions_by_exchange.items():
            for pos in pos_list:
                try:
                    # 多头持仓 → 卖出平仓
                    # 空头持仓 → 买入平仓
                    close_side = 'sell' if pos.size > 0 else 'buy'

                    order = await order_service.create_order(user_id, OrderCreate(
                        symbol=pos.symbol,
                        side=close_side,
                        type='market',  # 市价单快速平仓
                        amount=abs(pos.size),
                        exchange_config_id=exchange_id
                    ))

                    results.append({
                        'position': pos,
                        'order': order,
                        'status': 'success'
                    })

                except Exception as e:
                    results.append({
                        'position': pos,
                        'error': str(e),
                        'status': 'failed'
                    })

        return results

    async def batch_modify_stop_loss(
        self,
        user_id: int,
        symbol: str,
        new_stop_loss_price: float
    ):
        """批量调整止损价"""
        # 1. 查找所有该币种的开仓订单和条件单
        orders = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.symbol == symbol,
                Order.status.in_(['open', 'partially_filled'])
            )
        )

        # 2. 批量修改
        for order in orders:
            await order_service.modify_order(
                user_id=user_id,
                order_id=order.id,
                new_price=new_stop_loss_price
            )

        # 3. 查找并修改条件止损单
        conditional_orders = await self.db.execute(
            select(ConditionalOrder).where(
                ConditionalOrder.user_id == user_id,
                ConditionalOrder.symbol == symbol,
                ConditionalOrder.condition_type == 'stop_loss',
                ConditionalOrder.status == 'pending'
            )
        )

        for co in conditional_orders:
            co.trigger_price = new_stop_loss_price

        await self.db.commit()
```

---

### 系统二：PMS (Portfolio Management System) 投资组合管理

**当前状态**: 完全缺失 ❌

**这是你系统最大、最致命的缺陷！**

没有持仓管理，交易员就像"盲人骑瞎马"，无法回答以下问题：
- 我现在持有多少BTC？
- 我的总资产是多少？
- 我今天赚了还是亏了？
- 我的杠杆倍数是否过高？
- 哪个币种风险敞口最大？

#### 2.1 持仓管理核心数据模型 (P0 - 立即实现)

```python
# 需新增: api-gateway/app/models/position.py

class Position(Base, TimeStampMixin):
    """持仓表"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    exchange_config_id = Column(Integer, ForeignKey("exchange_configs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ========== 标的与方向 ==========
    symbol = Column(String, nullable=False, index=True)  # BTC/USDT
    position_side = Column(String, nullable=False)  # long/short

    # ========== 数量与价格 ==========
    size = Column(Float, default=0, nullable=False)  # 持仓数量
    # 正数 = 多头持仓，负数 = 空头持仓
    # 例如：size=0.5 表示持有0.5 BTC多头
    #      size=-5.0 表示持有5 ETH空头

    entry_price = Column(Float)  # 开仓均价（加权平均）
    mark_price = Column(Float)  # 标记价格（交易所实时提供）
    liquidation_price = Column(Float)  # 强平价格
    bankruptcy_price = Column(Float)  # 破产价格

    leverage = Column(Integer, default=1)  # 杠杆倍数
    margin_type = Column(String)  # cross/isolated（全仓/逐仓）

    # ========== 盈亏计算 ==========
    unrealized_pnl = Column(Float, default=0)  # 浮动盈亏
    realized_pnl = Column(Float, default=0)  # 已实现盈亏
    commission = Column(Float, default=0)  # 已付手续费

    # ========== 保证金 ==========
    margin_used = Column(Float, default=0)  # 占用保证金
    margin_ratio = Column(Float)  # 保证金率 = 当前权益 / 占用保证金

    # ========== 时间戳 ==========
    opened_at = Column(DateTime)  # 开仓时间
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ========== 状态 ==========
    status = Column(String, default="open")  # open/closed/closing
    # open: 正常持仓
    # closing: 正在平仓中
    # closed: 已平仓

    # ========== 索引优化 ==========
    __table_args__ = (
        Index('idx_user_symbol', 'user_id', 'symbol'),
        Index('idx_exchange_symbol', 'exchange_config_id', 'symbol'),
    )


class PositionHistory(Base, TimeStampMixin):
    """持仓历史表（用于分析历史交易）"""
    __tablename__ = "position_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))

    symbol = Column(String)
    position_side = Column(String)

    size = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float)  # 平仓价格
    hold_duration = Column(Float)  # 持仓时长（秒）

    realized_pnl = Column(Float)  # 已实现盈亏
    commission = Column(Float)  # 手续费
    net_pnl = Column(Float)  # 净盈亏（扣除手续费后）

    opened_at = Column(DateTime)
    closed_at = Column(DateTime)
```

#### 2.2 持仓同步引擎 (P0 - 核心功能)

**目标**: 从各交易所实时同步持仓到本地数据库

```python
# 需新增: api-gateway/app/services/position_sync_service.py

class PositionSyncService:
    """持仓实时同步引擎"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sync_interval = 5  # 每5秒同步一次
        self.redis_client = redis.Redis(host='localhost', port=6380, decode_responses=True)

    async def start_sync_loop(self, user_id: int):
        """
        后台循环：每5秒同步用户的所有持仓
        """
        while True:
            try:
                await self.sync_user_positions(user_id)
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"持仓同步失败 (user_id={user_id}): {e}")
                await asyncio.sleep(10)

    async def sync_user_positions(self, user_id: int):
        """
        同步用户的所有持仓
        """
        # 1. 获取用户的所有交易所账户
        exchanges = await self.db.execute(
            select(ExchangeConfig).where(
                ExchangeConfig.user_id == user_id,
                ExchangeConfig.is_active == True
            )
        )

        for exchange_config in exchanges:
            await self.sync_exchange_positions(exchange_config)

    async def sync_exchange_positions(self, exchange_config: ExchangeConfig):
        """
        同步单个交易所的持仓
        """
        # 1. 获取CCXT交易所实例
        exchange = await CCXTService.get_exchange(exchange_config)

        # 2. 调用交易所API获取持仓
        try:
            ccxt_positions = await exchange.fetch_positions([])

            # 3. 对比本地数据库，进行增删改
            for ccxt_pos in ccxt_positions:
                # CCXT返回的数据格式：
                # {
                #     'symbol': 'BTC/USDT:USDT',
                #     'contracts': 0.5,  # 持仓数量（正数=多头，负数=空头）
                #     'notional': 49061.5,  # 持仓价值
                #     'unrealizedPnl': 1234.56,  # 浮动盈亏
                #     'leverage': 10,
                #     'liquidationPrice': 86520.5,
                #     'entryPrice': 98123.0,
                #     'markPrice': 98145.5,
                #     ...
                # }

                if abs(ccxt_pos['contracts']) > 0.0001:  # 有持仓（避免浮点误差）
                    await self.upsert_position(exchange_config, ccxt_pos)
                else:
                    # 持仓数量为0，标记为已平仓
                    await self.close_position(exchange_config, ccxt_pos['symbol'])

        except Exception as e:
            logger.error(f"从{exchange_config.exchange_name}同步持仓失败: {e}")

    async def upsert_position(
        self,
        exchange_config: ExchangeConfig,
        ccxt_pos: dict
    ):
        """
        更新或插入持仓
        """
        # 1. 查询是否已存在该持仓
        position = await self.db.execute(
            select(Position).where(
                Position.exchange_config_id == exchange_config.id,
                Position.symbol == ccxt_pos['symbol'],
                Position.status == 'open'
            )
        )
        pos = position.scalar_one_or_none()

        if pos:
            # 2. 更新现有持仓
            pos.size = ccxt_pos['contracts']
            pos.entry_price = ccxt_pos['entryPrice']
            pos.mark_price = ccxt_pos['markPrice']
            pos.liquidation_price = ccxt_pos.get('liquidationPrice')
            pos.leverage = ccxt_pos.get('leverage', 1)
            pos.unrealized_pnl = ccxt_pos.get('unrealizedPnl', 0)
            pos.last_updated = datetime.now()

        else:
            # 3. 创建新持仓
            pos = Position(
                exchange_config_id=exchange_config.id,
                user_id=exchange_config.user_id,
                symbol=ccxt_pos['symbol'],
                position_side='long' if ccxt_pos['contracts'] > 0 else 'short',
                size=ccxt_pos['contracts'],
                entry_price=ccxt_pos['entryPrice'],
                mark_price=ccxt_pos['markPrice'],
                liquidation_price=ccxt_pos.get('liquidationPrice'),
                leverage=ccxt_pos.get('leverage', 1),
                unrealized_pnl=ccxt_pos.get('unrealizedPnl', 0),
                status='open',
                opened_at=datetime.now()
            )
            self.db.add(pos)

        await self.db.commit()

        # 4. 通过WebSocket推送到前端
        await self._push_position_update(pos)

    async def close_position(
        self,
        exchange_config: ExchangeConfig,
        symbol: str
    ):
        """
        平仓（标记持仓为关闭）
        """
        position = await self.db.execute(
            select(Position).where(
                Position.exchange_config_id == exchange_config.id,
                Position.symbol == symbol,
                Position.status == 'open'
            )
        )
        pos = position.scalar_one_or_none()

        if pos:
            # 1. 更新状态
            pos.status = 'closed'
            pos.closed_at = datetime.now()

            # 2. 计算已实现盈亏
            pos.realized_pnl = pos.unrealized_pnl  # 浮动盈亏转为已实现

            await self.db.commit()

            # 3. 保存到历史表
            await self._save_to_history(pos)

            # 4. 推送到前端
            await self._push_position_update(pos)

    async def _save_to_history(self, position: Position):
        """保存持仓到历史表"""
        history = PositionHistory(
            user_id=position.user_id,
            position_id=position.id,
            symbol=position.symbol,
            position_side=position.position_side,
            size=position.size,
            entry_price=position.entry_price,
            exit_price=position.mark_price,  # 平仓价格
            realized_pnl=position.realized_pnl,
            commission=position.commission,
            net_pnl=position.realized_pnl - position.commission,
            opened_at=position.opened_at,
            closed_at=position.closed_at
        )
        self.db.add(history)
        await self.db.commit()

    async def _push_position_update(self, position: Position):
        """通过WebSocket推送持仓更新"""
        message = {
            'type': 'position_update',
            'data': {
                'id': position.id,
                'symbol': position.symbol,
                'side': position.position_side,
                'size': position.size,
                'entry_price': position.entry_price,
                'mark_price': position.mark_price,
                'unrealized_pnl': position.unrealized_pnl,
                'status': position.status
            }
        }

        # 发布到Redis
        await self.redis_client.publish(
            f'positions:{position.user_id}',
            json.dumps(message)
        )
```

#### 2.3 风险敞口分析 (P0 - 核心功能)

**Dashboard实时展示的关键指标**:

```python
# 需新增: api-gateway/app/services/portfolio_analysis_service.py

class PortfolioAnalysisService:
    """投资组合分析服务"""

    async def get_portfolio_summary(self, user_id: int) -> dict:
        """
        获取投资组合汇总（Dashboard展示）

        返回示例:
        {
            'total_equity': 125430.50,  # 总权益
            'available_balance': 87230.20,  # 可用余额
            'total_margin_used': 38100.30,  # 占用保证金
            'total_unrealized_pnl': 2340.50,  # 浮动盈亏
            'daily_pnl': 1450.20,  # 今日盈亏
            'daily_return': 0.012,  # 今日收益率 1.2%
            'total_exposure': 380000.00,  # 总敞口
            'net_exposure': 150000.00,  # 净敞口（多空对冲后）
            'leverage': 3.03,  # 实际杠杆倍数 = 总敞口 / 总权益
            'max_drawdown': -0.08,  # 最大回撤 -8%
            'positions_count': 12,  # 持仓数量
            'long_exposure': 265000.00,  # 多头敞口
            'short_exposure': 115000.00,  # 空头敞口
            'long_short_ratio': 2.30,  # 多空比
        }
        """

        # 1. 获取所有持仓
        positions = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            )
        )

        # 2. 获取所有交易所余额
        balances = await self._get_all_balances(user_id)

        # 3. 计算各项指标
        total_balance = sum([b['total'] for b in balances])
        available_balance = sum([b['free'] for b in balances])

        total_unrealized_pnl = sum([p.unrealized_pnl for p in positions])
        total_margin_used = sum([p.margin_used for p in positions])

        long_positions = [p for p in positions if p.position_side == 'long']
        short_positions = [p for p in positions if p.position_side == 'short']

        long_exposure = sum([abs(p.size) * p.mark_price for p in long_positions])
        short_exposure = sum([abs(p.size) * p.mark_price for p in short_positions])

        total_exposure = long_exposure + short_exposure
        net_exposure = long_exposure - short_exposure

        total_equity = total_balance + total_unrealized_pnl
        leverage = total_exposure / total_equity if total_equity > 0 else 0

        long_short_ratio = long_exposure / short_exposure if short_exposure > 0 else float('inf')

        # 4. 今日盈亏
        today_pnl = await self._get_today_pnl(user_id)

        return {
            'total_equity': round(total_equity, 2),
            'available_balance': round(available_balance, 2),
            'total_margin_used': round(total_margin_used, 2),
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'daily_pnl': round(today_pnl, 2),
            'daily_return': round(today_pnl / (total_equity - total_unrealized_pnl), 4) if total_equity > 0 else 0,
            'total_exposure': round(total_exposure, 2),
            'net_exposure': round(net_exposure, 2),
            'leverage': round(leverage, 2),
            'long_exposure': round(long_exposure, 2),
            'short_exposure': round(short_exposure, 2),
            'long_short_ratio': round(long_short_ratio, 2),
            'positions_count': len(positions),
        }

    async def get_position_detail(self, user_id: int) -> list:
        """
        获取持仓明细（用于Dashboard表格展示）

        返回示例:
        [
            {
                'symbol': 'BTC/USDT',
                'position_side': 'long',
                'size': 0.5,
                'entry_price': 95123.50,
                'mark_price': 98120.00,
                'liquidation_price': 86520.50,
                'leverage': 10,
                'unrealized_pnl': 1448.25,
                'unrealized_pnl_percent': 3.05,  # 收益率%
                'margin_used': 9512.35,
                'margin_ratio': 1.15,  # 保证金率
                'opened_at': '2025-12-31 10:30:00',
                'hold_duration': '5h 23m',  # 持仓时长
            },
            ...
        ]
        """
        positions = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            ).order_by(Position.unrealized_pnl.desc())
        )

        result = []
        for pos in positions:
            pnl_percent = (pos.unrealized_pnl / (pos.entry_price * abs(pos.size))) * 100 if pos.size != 0 else 0
            hold_duration = datetime.now() - pos.opened_at

            result.append({
                'id': pos.id,
                'symbol': pos.symbol,
                'position_side': pos.position_side,
                'size': abs(pos.size),
                'entry_price': round(pos.entry_price, 2),
                'mark_price': round(pos.mark_price, 2),
                'liquidation_price': round(pos.liquidation_price, 2) if pos.liquidation_price else None,
                'leverage': pos.leverage,
                'unrealized_pnl': round(pos.unrealized_pnl, 2),
                'unrealized_pnl_percent': round(pnl_percent, 2),
                'margin_used': round(pos.margin_used, 2),
                'margin_ratio': round(pos.margin_ratio, 2) if pos.margin_ratio else None,
                'opened_at': pos.opened_at.strftime('%Y-%m-%d %H:%M:%S'),
                'hold_duration': self._format_duration(hold_duration),
                'distance_to_liquidation': self._calc_distance_to_liquidation(pos),
            })

        return result

    def _format_duration(self, timedelta: timedelta) -> str:
        """格式化时长"""
        hours = timedelta.total_seconds() / 3600
        if hours < 1:
            return f"{int(timedelta.total_seconds() / 60)}m"
        elif hours < 24:
            return f"{int(hours)}h {int((hours % 1) * 60)}m"
        else:
            days = int(hours / 24)
            return f"{days}d {int(hours % 24)}h"

    def _calc_distance_to_liquidation(self, position: Position) -> dict:
        """
        计算距离强平的距离

        返回:
        {
            'price_distance': 11599.5,  # 价格距离强平还有$11599.5
            'percent_distance': 11.82,  # 百分比距离11.82%
        }
        """
        if not position.liquidation_price:
            return None

        if position.position_side == 'long':
            # 多头：强平价 < 当前价
            price_distance = position.mark_price - position.liquidation_price
            percent_distance = (price_distance / position.mark_price) * 100
        else:
            # 空头：强平价 > 当前价
            price_distance = position.liquidation_price - position.mark_price
            percent_distance = (price_distance / position.mark_price) * 100

        return {
            'price_distance': round(price_distance, 2),
            'percent_distance': round(percent_distance, 2),
        }

    async def get_risk_exposure_analysis(self, user_id: int) -> dict:
        """
        风险敞口分析

        按币种、按交易所分析风险集中度
        """
        positions = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            )
        )

        # 按币种分组
        by_symbol = {}
        for pos in positions:
            exposure = abs(pos.size) * pos.mark_price
            symbol = pos.symbol.split('/')[0]  # BTC/USDT → BTC

            if symbol not in by_symbol:
                by_symbol[symbol] = {
                    'symbol': symbol,
                    'exposure': 0,
                    'unrealized_pnl': 0,
                    'count': 0
                }

            by_symbol[symbol]['exposure'] += exposure
            by_symbol[symbol]['unrealized_pnl'] += pos.unrealized_pnl
            by_symbol[symbol]['count'] += 1

        # 按交易所分组
        by_exchange = {}
        for pos in positions:
            exchange_id = pos.exchange_config_id
            exposure = abs(pos.size) * pos.mark_price

            if exchange_id not in by_exchange:
                by_exchange[exchange_id] = {
                    'exchange_id': exchange_id,
                    'exposure': 0,
                    'count': 0
                }

            by_exchange[exchange_id]['exposure'] += exposure
            by_exchange[exchange_id]['count'] += 1

        total_equity = await self._get_total_equity(user_id)

        return {
            'by_symbol': sorted(by_symbol.values(), key=lambda x: x['exposure'], reverse=True),
            'by_exchange': sorted(by_exchange.values(), key=lambda x: x['exposure'], reverse=True),
            'max_single_symbol_exposure_ratio': max([v['exposure'] for v in by_symbol.values()]) / total_equity if total_equity > 0 else 0,
        }
```

**API端点**:
```python
# api-gateway/app/api/v1/portfolio.py

@router.get("/summary")
async def get_portfolio_summary(user_id: int = Depends(get_current_user_id)):
    """获取投资组合汇总"""
    service = PortfolioAnalysisService(db)
    return await service.get_portfolio_summary(user_id)

@router.get("/positions")
async def get_positions(user_id: int = Depends(get_current_user_id)):
    """获取持仓明细"""
    service = PortfolioAnalysisService(db)
    return await service.get_position_detail(user_id)

@router.get("/risk-analysis")
async def get_risk_analysis(user_id: int = Depends(get_current_user_id)):
    """获取风险敞口分析"""
    service = PortfolioAnalysisService(db)
    return await service.get_risk_exposure_analysis(user_id)
```

---

### 系统三：RMS (Risk Management System) 风险管理

**当前状态**: 完全缺失 ❌

**这是专业交易系统和个人玩具的分水岭！**

没有风控系统，任何策略都可能因为一次意外而爆仓归零。

#### 3.1 事前风控 (P0 - 立即实现)

**在每一笔订单提交到交易所之前，必须通过以下检查**:

```python
# 需新增: api-gateway/app/services/risk_service.py

class PreTradeRiskCheck:
    """事前风控检查清单"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client = redis.Redis(host='localhost', port=6380)

    async def check_order(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        风控检查流程

        任何一项不通过则拒绝订单，返回具体原因
        """
        checks = [
            {
                'name': '余额检查',
                'func': self.check_account_balance,
                'priority': 'critical'
            },
            {
                'name': '仓位限制',
                'func': self.check_position_limit,
                'priority': 'critical'
            },
            {
                'name': '日亏损限制',
                'func': self.check_daily_loss_limit,
                'priority': 'critical'
            },
            {
                'name': '杠杆限制',
                'func': self.check_leverage_limit,
                'priority': 'high'
            },
            {
                'name': '流动性检查',
                'func': self.check_liquidity,
                'priority': 'high'
            },
            {
                'name': 'API限流',
                'func': self.check_exchange_rate_limit,
                'priority': 'medium'
            },
        ]

        failed_checks = []

        for check in checks:
            result = await check['func'](order, user_id)

            if not result.passed:
                failed_checks.append({
                    'name': check['name'],
                    'reason': result.reason,
                    'priority': check['priority'],
                    'suggestion': result.suggestion
                })

                # 如果是关键检查失败，立即返回
                if check['priority'] == 'critical':
                    return RiskCheckResult(
                        passed=False,
                        reason=f"风控检查失败: {check['name']}",
                        failed_checks=failed_checks
                    )

        if failed_checks:
            return RiskCheckResult(
                passed=False,
                reason=f"风控检查未通过: {len(failed_checks)}项检查失败",
                failed_checks=failed_checks
            )

        return RiskCheckResult(passed=True)

    async def check_account_balance(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        检查1: 账户余额充足

        规则：可用余额 > 订单所需保证金 + 手续费
        """
        # 1. 获取账户余额
        exchange_config = await self.db.get(ExchangeConfig, order.exchange_config_id)
        exchange = await CCXTService.get_exchange(exchange_config)
        balance = await exchange.fetch_balance()

        # 2. 计算订单所需资金
        order_value = order.amount * (order.price or await self._get_market_price(order.symbol))
        required_margin = order_value / order.leverage if order.leverage else order_value
        estimated_fee = order_value * 0.001  # 假设手续费0.1%

        # 3. 检查余额
        available_balance = balance['USDT']['free']

        if available_balance < required_margin + estimated_fee:
            return RiskCheckResult(
                passed=False,
                reason=f"余额不足: 需要${required_margin + estimated_fee:.2f}，可用${available_balance:.2f}",
                suggestion="请充值或减少订单数量",
                current_value=available_balance,
                required_value=required_margin + estimated_fee
            )

        return RiskCheckResult(passed=True)

    async def check_position_limit(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        检查2: 单币种仓位限制

        规则：单个币种持仓不得超过总权益的20%
        """
        # 1. 获取当前持仓
        current_position = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.symbol == order.symbol,
                Position.status == 'open'
            )
        )
        pos = current_position.scalar_one_or_none()

        # 2. 计算新持仓价值
        current_size = pos.size if pos else 0
        new_size = current_size + (order.amount if order.side == 'buy' else -order.amount)
        new_position_value = abs(new_size) * (order.price or await self._get_market_price(order.symbol))

        # 3. 获取总权益
        total_equity = await self._get_total_equity(user_id)

        # 4. 计算仓位比例
        position_ratio = new_position_value / total_equity

        if position_ratio > 0.20:  # 20%阈值
            return RiskCheckResult(
                passed=False,
                reason=f"单币种仓位超限: {position_ratio*100:.1f}% > 20%",
                suggestion=f"该币种最大仓位为${total_equity * 0.20:.2f}",
                current_value=new_position_value,
                limit_value=total_equity * 0.20
            )

        return RiskCheckResult(passed=True)

    async def check_daily_loss_limit(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        检查3: 日亏损限制

        规则：当日亏损超过5%，禁止开新仓（只允许平仓）
        """
        # 1. 计算今日盈亏
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        realized_pnl = await self.db.execute(
            select(func.sum(PositionHistory.realized_pnl)).where(
                PositionHistory.user_id == user_id,
                PositionHistory.closed_at >= today_start
            )
        )
        today_realized_pnl = realized_pnl.scalar() or 0

        # 2. 获取昨日权益
        yesterday_equity = await self._get_yesterday_equity(user_id)

        # 3. 计算亏损比例
        loss_ratio = today_realized_pnl / yesterday_equity if yesterday_equity > 0 else 0

        if loss_ratio < -0.05:  # 亏损超过5%
            # 检查是否是平仓订单（允许）
            current_position = await self._get_current_position(user_id, order.symbol)

            if (order.side == 'sell' and current_position and current_position.size > 0) or \
               (order.side == 'buy' and current_position and current_position.size < 0):
                # 是平仓订单，允许
                return RiskCheckResult(passed=True)

            # 是开仓订单，拒绝
            return RiskCheckResult(
                passed=False,
                reason=f"触发日亏损限制: 今日亏损{loss_ratio*100:.1f}% < -5%",
                suggestion="今日只能平仓，禁止开新仓",
                action="stop_trading",
                current_value=loss_ratio,
                limit_value=-0.05
            )

        return RiskCheckResult(passed=True)

    async def check_leverage_limit(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        检查4: 杠杆限制

        规则：实际杠杆不得超过5倍（总敞口 / 总权益）
        """
        # 1. 获取所有持仓
        positions = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            )
        )

        # 2. 计算总敞口
        total_exposure = sum([abs(p.size) * p.mark_price for p in positions])

        # 3. 计算新订单后的敞口
        order_value = order.amount * (order.price or await self._get_market_price(order.symbol))
        new_total_exposure = total_exposure + order_value

        # 4. 获取总权益
        total_equity = await self._get_total_equity(user_id)

        # 5. 计算杠杆倍数
        new_leverage = new_total_exposure / total_equity if total_equity > 0 else 0

        if new_leverage > 5:
            return RiskCheckResult(
                passed=False,
                reason=f"杠杆超限: {new_leverage:.1f}x > 5x",
                suggestion="请降低订单数量或先平仓部分持仓",
                current_value=new_leverage,
                limit_value=5
            )

        return RiskCheckResult(passed=True)

    async def check_liquidity(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        检查5: 流动性检查

        避免：在低流动性币种大额交易导致滑点过大
        """
        # 1. 获取订单簿深度
        exchange_config = await self.db.get(ExchangeConfig, order.exchange_config_id)
        exchange = await CCXTService.get_exchange(exchange_config)
        order_book = await exchange.fetch_order_book(order.symbol, limit=20)

        # 2. 计算盘口深度
        if order.side == 'buy':
            # 买单：检查卖单深度
            ask_depth = sum([level[1] for level in order_book['asks'][:10]])
            threshold = ask_depth * 0.10  # 不超过前10档卖盘的10%
        else:
            # 卖单：检查买单深度
            bid_depth = sum([level[1] for level in order_book['bids'][:10]])
            threshold = bid_depth * 0.10

        # 3. 检查订单量
        if order.amount > threshold:
            return RiskCheckResult(
                passed=False,
                reason=f"流动性不足: 订单量{order.amount:.4f} > 盘口深度{threshold:.4f}",
                suggestion=f"建议单次订单不超过{threshold:.4f}",
                current_value=order.amount,
                limit_value=threshold
            )

        return RiskCheckResult(passed=True)

    async def check_exchange_rate_limit(
        self,
        order: OrderCreate,
        user_id: int
    ) -> RiskCheckResult:
        """
        检查6: API限流检查

        避免：超过交易所API请求频率限制
        """
        # 从Redis获取最近请求计数
        key = f"api_rate_limit:{order.exchange_config_id}"
        recent_requests = await self.redis_client.get(key)

        if recent_requests and int(recent_requests) > 100:  # 假设每分钟限制100次
            return RiskCheckResult(
                passed=False,
                reason="交易所API请求频率过高",
                suggestion="请稍后再试"
            )

        return RiskCheckResult(passed=True)
```

**集成到订单服务**:
```python
# 修改: api-gateway/app/services/order_service.py

async def create_order(self, user_id: int, order_in: OrderCreate) -> Order:
    # 1. 事前风控检查
    risk_check = PreTradeRiskCheck(self.db)
    risk_result = await risk_check.check_order(order_in, user_id)

    if not risk_result.passed:
        # 风控未通过，拒绝订单
        raise ValueError(f"风控检查失败: {risk_result.reason}")

    # 2. 风控通过，继续原有逻辑
    config = await self.exchange_service.get_by_id(order_in.exchange_config_id, user_id)
    exchange = await CCXTService.get_exchange(config)
    # ... 其余代码不变
```

#### 3.2 事中风控 (P0 - 实时监控)

```python
# 需新增: api-gateway/app/services/intraday_risk_monitor.py

class IntradayRiskMonitor:
    """盘中实时风险监控"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client = redis.Redis(host='localhost', port=6380)
        self.notification_service = NotificationService()

    async def start_monitor(self, user_id: int):
        """
        启动实时监控循环
        每秒检查一次持仓风险
        """
        while True:
            try:
                await self.monitor_positions(user_id)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"盘中监控失败: {e}")
                await asyncio.sleep(5)

    async def monitor_positions(self, user_id: int):
        """
        检查所有持仓的风险指标
        """
        # 1. 获取所有持仓
        positions = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            )
        )

        for pos in positions:
            # 检查1: 接近强平
            await self._check_liquidation_risk(pos)

            # 检查2: 单笔持仓亏损
            await self._check_position_loss(pos)

            # 检查3: 总回撤
            await self._check_total_drawdown(user_id)

    async def _check_liquidation_risk(self, position: Position):
        """
        检查是否接近强平价

        阈值：距离强平价 < 10%
        """
        if not position.liquidation_price:
            return

        # 计算距离强平的百分比
        if position.position_side == 'long':
            distance = (position.mark_price - position.liquidation_price) / position.mark_price
        else:
            distance = (position.liquidation_price - position.mark_price) / position.mark_price

        if distance < 0.10:  # 距离强平 < 10%
            level = AlertLevel.CRITICAL if distance < 0.05 else AlertLevel.WARNING

            await self.notification_service.send_alert(
                user_id=position.user_id,
                message=f"{'🚨' if level == AlertLevel.CRITICAL else '⚠️'} "
                       f"{position.symbol} 接近强平！\n"
                       f"当前价: ${position.mark_price:.2f}\n"
                       f"强平价: ${position.liquidation_price:.2f}\n"
                       f"距离: {distance*100:.1f}%",
                level=level
            )

            # 如果非常接近强平（< 3%），自动发送紧急通知
            if distance < 0.03:
                await self.notification_service.send_alert(
                    user_id=position.user_id,
                    message=f"🚨🚨🚨 紧急：{position.symbol} 即将强平！",
                    level=AlertLevel.EMERGENCY,
                    channels=['telegram', 'email', 'sms']  # 全渠道推送
                )

    async def _check_position_loss(self, position: Position):
        """
        检查单笔持仓亏损

        阈值：浮动亏损 > 10%
        """
        if position.unrealized_pnl < 0:
            entry_value = abs(position.size) * position.entry_price
            loss_percent = position.unrealized_pnl / entry_value

            if loss_percent < -0.10:  # 亏损超过10%
                await self.notification_service.send_alert(
                    user_id=position.user_id,
                    message=f"⚠️ {position.symbol} 浮亏较大\n"
                           f"亏损: {position.unrealized_pnl:.2f} ({loss_percent*100:.1f}%)\n"
                           f"建议：考虑止损",
                    level=AlertLevel.WARNING
                )

            if loss_percent < -0.20:  # 亏损超过20%
                await self.notification_service.send_alert(
                    user_id=position.user_id,
                    message=f"🚨 {position.symbol} 浮亏严重\n"
                           f"亏损: {position.unrealized_pnl:.2f} ({loss_percent*100:.1f}%)\n"
                           f"建议：立即止损！",
                    level=AlertLevel.CRITICAL
                )

    async def _check_total_drawdown(self, user_id: int):
        """
        检查总回撤

        阈值：从最高点回撤 > 15%
        """
        # 1. 获取历史最高权益
        peak_equity = await self._get_peak_equity(user_id)
        current_equity = await self._get_total_equity(user_id)

        # 2. 计算回撤
        drawdown = (current_equity - peak_equity) / peak_equity

        if drawdown < -0.15:  # 回撤超过15%
            await self.notification_service.send_alert(
                user_id=user_id,
                message=f"🚨 总回撤{drawdown*100:.1f}%，建议立即降低仓位",
                level=AlertLevel.CRITICAL
            )

            # 自动选项：强制停止所有策略
            if drawdown < -0.20:  # 回撤超过20%
                await self._emergency_stop_all_strategies(user_id)
                await self.notification_service.send_alert(
                    user_id=user_id,
                    message=f"🚨🚨🚨 紧急：回撤超限，所有策略已自动停止",
                    level=AlertLevel.EMERGENCY
                )

    async def _emergency_stop_all_strategies(self, user_id: int):
        """紧急停止所有策略"""
        strategies = await self.db.execute(
            select(StrategyConfig).where(
                StrategyConfig.user_id == user_id,
                StrategyConfig.status == 'running'
            )
        )

        for strategy in strategies:
            await strategy_service.stop_strategy(strategy.id, user_id)

        logger.warning(f"紧急停止用户{user_id}的所有策略")
```

#### 3.3 事后风控 (P1 - 每日复盘)

```python
# 需新增: api-gateway/app/services/post_trade_analysis.py

class PostTradeAnalysis:
    """交易后分析"""

    async def daily_risk_report(self, user_id: int, date: date) -> dict:
        """
        每日风控报告

        包含：
        - 总权益变化
        - 日盈亏
        - 最大回撤
        - 胜率
        - 最大单笔亏损
        - 风险违规次数
        """
        # 1. 总权益
        start_equity = await self._get_equity_at_date(user_id, date)
        end_equity = await self._get_equity_at_date(user_id, date + timedelta(days=1))
        daily_pnl = end_equity - start_equity
        daily_return = daily_pnl / start_equity if start_equity > 0 else 0

        # 2. 最大回撤
        max_drawdown = await self._calculate_max_drawdown(user_id, date)

        # 3. 交易统计
        closed_positions = await self.db.execute(
            select(PositionHistory).where(
                PositionHistory.user_id == user_id,
                func.date(PositionHistory.closed_at) == date
            )
        )

        total_trades = len(closed_positions)
        winning_trades = [p for p in closed_positions if p.net_pnl > 0]
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

        # 4. 最大单笔盈亏
        largest_win = max([p.net_pnl for p in closed_positions]) if closed_positions else 0
        largest_loss = min([p.net_pnl for p in closed_positions]) if closed_positions else 0

        # 5. 风险违规
        violations = await self.db.execute(
            select(RiskViolation).where(
                RiskViolation.user_id == user_id,
                func.date(RiskViolation.created_at) == date
            )
        )

        return {
            'date': date.isoformat(),
            'start_equity': round(start_equity, 2),
            'end_equity': round(end_equity, 2),
            'daily_pnl': round(daily_pnl, 2),
            'daily_return': round(daily_return, 4),
            'max_drawdown': round(max_drawdown, 4),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 4),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'risk_violations': len(violations),
        }

    async def weekly_performance_report(self, user_id: int, week_start: date) -> dict:
        """周度绩效报告"""
        # 类似日度报告，但按周聚合
        pass

    async def monthly_performance_report(self, user_id: int, month: int) -> dict:
        """月度绩效报告"""
        pass
```

---

### 系统四：Market Data / Datahub 数据管理

**当前状态**: 你提到已实现，但代码中未见完整实现

#### 4.1 实时行情服务 (P0 - 立即完善)

```python
# 需新增: data-service/market_data_service.py

class MarketDataService:
    """统一市场数据服务"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6380, decode_responses=True)
        self.ws_connections = {}  # 维持与各交易所的WebSocket连接
        self.subscribers = defaultdict(set)  # symbol -> set of websocket connections

    async def subscribe_ticker(self, symbol: str, exchange: str, websocket: WebSocket):
        """
        订阅实时Ticker

        数据结构:
        {
            "symbol": "BTC/USDT",
            "exchange": "binance",
            "bid": 98123.45,
            "ask": 98124.50,
            "bid_volume": 1.5,
            "ask_volume": 2.0,
            "last": 98124.00,
            "volume": 12345.67,
            "timestamp": 1704067200000
        }
        """
        # 1. 添加到订阅列表
        self.subscribers[f"{exchange}:{symbol}"].add(websocket)

        # 2. 如果还没有与该交易所的WebSocket连接，则创建
        if exchange not in self.ws_connections:
            await self._create_exchange_ws_connection(exchange)

        # 3. 从Redis获取最新数据（如果有的话）
        latest_data = await self.redis_client.get(f"ticker:{exchange}:{symbol}")
        if latest_data:
            await websocket.send_json(json.loads(latest_data))

    async def _create_exchange_ws_connection(self, exchange: str):
        """
        创建与交易所的WebSocket连接
        """
        # 使用CCXT的WebSocket支持
        exchange_class = getattr(ccxt, exchange)
        exchange_ws = exchange_class({
            'options': {
                'defaultType': 'spot',  # 或 'future'
            }
        })

        await exchange_ws.load_markets()

        # 订阅所有需要的symbol
        symbols_to_subscribe = [
            s.split(':')[1] for s in self.subscribers.keys()
            if s.startswith(f"{exchange}:")
        ]

        @exchange_ws.on('ticker')
        async def on_ticker(ticker):
            """接收到Ticker数据"""
            symbol = ticker['symbol']
            exchange_name = ticker.get('exchange', exchange)

            # 1. 存储到Redis（设置1秒过期）
            await self.redis_client.setex(
                f"ticker:{exchange_name}:{symbol}",
                1,
                json.dumps(ticker)
            )

            # 2. 推送到所有订阅者
            key = f"{exchange_name}:{symbol}"
            if key in self.subscribers:
                for websocket in self.subscribers[key]:
                    try:
                        await websocket.send_json(ticker)
                    except:
                        # 连接已断开，移除
                        self.subscribers[key].remove(websocket)

        # 启动WebSocket
        await exchange_ws.watch_tickers(symbols_to_subscribe)
        self.ws_connections[exchange] = exchange_ws

    async def subscribe_orderbook(self, symbol: str, exchange: str, websocket: WebSocket):
        """
        订阅深度数据

        返回前20档买卖盘
        """
        # 实现类似subscribe_ticker
        pass

    async def subscribe_trades(self, symbol: str, exchange: str, websocket: WebSocket):
        """
        订阅成交数据
        """
        pass

    async def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
        exchange: str = 'binance'
    ) -> list:
        """
        获取K线数据

        参数:
        - symbol: BTC/USDT
        - timeframe: 1m/5m/15m/1h/4h/1d
        - limit: 数量（最多1000）
        - exchange: 交易所

        返回:
        [
            [timestamp, open, high, low, close, volume],
            ...
        ]
        """
        # 1. 先尝试从Redis缓存读取
        cache_key = f"klines:{exchange}:{symbol}:{timeframe}"
        cached_data = await self.redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        # 2. 缓存未命中，从交易所获取
        exchange_class = getattr(ccxt, exchange)
        exchange_instance = exchange_class()

        ohlcv = await exchange_instance.fetch_ohlcv(
            symbol,
            timeframe,
            limit=limit
        )

        # 3. 存储到Redis（根据timeframe设置不同的过期时间）
        ttl_map = {
            '1m': 60,  # 1分钟
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400,
        }
        ttl = ttl_map.get(timeframe, 60)

        await self.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(ohlcv)
        )

        return ohlcv

    async def backfill_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: date,
        end_date: date,
        exchange: str = 'binance'
    ):
        """
        补充历史数据

        用于回测
        """
        exchange_class = getattr(ccxt, exchange)
        exchange_instance = exchange_class()

        since = int(datetime(start_date.year, start_date.month, start_date.day).timestamp() * 1000)

        all_data = []
        while True:
            ohlcv = await exchange_instance.fetch_ohlcv(
                symbol,
                timeframe,
                since=since,
                limit=1000
            )

            if not ohlcv:
                break

            all_data.extend(ohlcv)

            # 检查是否已经到达结束日期
            last_timestamp = ohlcv[-1][0]
            if last_timestamp >= int(datetime(end_date.year, end_date.month, end_date.day).timestamp() * 1000):
                break

            since = last_timestamp + 1

            # 避免请求过快
            await asyncio.sleep(0.1)

        # 存储到数据库或文件
        await self._save_klines_to_db(symbol, timeframe, all_data)

        logger.info(f"补充历史数据完成: {symbol} {timeframe} {start_date}~{end_date}, 共{len(all_data)}条")
```

#### 4.2 数据存储架构

**建议**:
- **Redis**: 实时数据缓存（Ticker、最新K线）
- **PostgreSQL**: 历史K线存储
- **InfluxDB/TimescaleDB** (可选): 高频数据、tick级数据

```sql
-- K线数据表
CREATE TABLE klines (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- 1m/5m/15m/1h/4h/1d
    timestamp BIGINT NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,

    UNIQUE(exchange, symbol, timeframe, timestamp)
);

-- 索引优化
CREATE INDEX idx_klines_symbol_time ON klines(symbol, timeframe, timestamp DESC);
CREATE INDEX idx_klines_timestamp ON klines(timestamp DESC);
```

#### 4.3 技术指标计算

```python
# 需新增: data-service/indicators.py

import talib
import pandas as pd

class TechnicalIndicators:
    """技术指标计算"""

    @staticmethod
    def sma(df: pd.DataFrame, period: int) -> pd.Series:
        """简单移动平均"""
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def ema(df: pd.DataFrame, period: int) -> pd.Series:
        """指数移动平均"""
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> dict:
        """MACD指标"""
        macd_line, signal_line, histogram = talib.MACD(
            df['close'],
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSI指标"""
        return talib.RSI(df['close'], timeperiod=period)

    @staticmethod
    def bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> dict:
        """布林带"""
        upper, middle, lower = talib.BBANDS(
            df['close'],
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev
        )

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """平均真实波幅"""
        return talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
```

---

### 系统五：Strategy 策略系统

**当前状态**: 基础完成 30%

**主要缺陷**:
- ❌ 无真实市场数据接入
- ❌ 无回测系统
- ❌ 无绩效分析
- ❌ 无参数优化

#### 5.1 策略引擎增强 (P0 - 立即实现)

```python
# 增强: api-gateway/app/strategies/base.py

class BaseStrategy(ABC):
    """策略基类（增强版）"""

    def __init__(self, config: dict):
        self.config = config
        self.is_running = False
        self.db = None  # 数据库连接
        self.exchange = None  # CCXT交易所实例
        self.position = None  # 当前持仓
        self.indicators = None  # 技术指标

    async def initialize(self):
        """
        初始化策略
        """
        # 1. 加载配置
        self.strategy_id = self.config['id']
        self.user_id = self.config['user_id']
        self.parameters = self.config['parameters']

        # 2. 获取交易所实例
        exchange_config_id = self.config.get('exchange_config_id')
        if exchange_config_id:
            self.exchange = await CCXTService.get_exchange_by_id(exchange_config_id)

        # 3. 初始化数据库连接
        self.db = async_session_maker()

    @abstractmethod
    async def on_tick(self, tick: dict):
        """
        逐笔行情事件

        参数:
        - tick: {
            'symbol': 'BTC/USDT',
            'price': 98123.45,
            'volume': 1.5,
            'timestamp': 1704067200000
        }
        """
        pass

    @abstractmethod
    async def on_bar(self, bar: dict):
        """
        K线闭合事件

        参数:
        - bar: {
            'symbol': 'BTC/USDT',
            'timeframe': '1h',
            'timestamp': 1704067200000,
            'open': 98000,
            'high': 98200,
            'low': 97900,
            'close': 98123,
            'volume': 123.45
        }
        """
        pass

    async def on_order_filled(self, order: Order):
        """
        订单成交事件

        可以在这里更新持仓、计算盈亏、记录日志
        """
        logger.info(f"订单成交: {order.symbol} {order.side} {order.amount} @ {order.price}")

        # 更新持仓
        await self._update_position(order)

    async def on_position_changed(self, position: Position):
        """
        持仓变化事件
        """
        self.position = position
        logger.info(f"持仓更新: {position.symbol} {position.size} @ {position.mark_price}")

    async def start(self):
        """启动策略"""
        await self.initialize()
        self.is_running = True
        logger.info(f"策略 {self.__class__.__name__} 启动")

        # 启动主循环
        asyncio.create_task(self._main_loop())

    async def stop(self):
        """停止策略"""
        self.is_running = False
        logger.info(f"策略 {self.__class__.__name__} 停止")

    async def _main_loop(self):
        """
        主循环（事件驱动）
        """
        while self.is_running:
            try:
                # 1. 获取最新K线
                symbol = self.parameters['symbol']
                timeframe = self.parameters.get('timeframe', '1h')

                klines = await MarketDataService().get_klines(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=100
                )

                latest_bar = self._convert_kline_to_dict(klines[-1])

                # 2. 检查K线是否更新
                last_bar_timestamp = self._get_last_bar_timestamp()

                if latest_bar['timestamp'] > last_bar_timestamp:
                    # 新K线闭合，触发on_bar事件
                    await self.on_bar(latest_bar)
                    self._set_last_bar_timestamp(latest_bar['timestamp'])

                # 3. 获取最新Ticker
                ticker = await MarketDataService().get_latest_ticker(symbol)
                await self.on_tick(ticker)

                # 4. 等待下一个周期
                await asyncio.sleep(10)  # 每10秒检查一次

            except Exception as e:
                logger.error(f"策略主循环错误: {e}")
                await asyncio.sleep(10)

    async def buy(self, symbol: str, amount: float, price: float = None):
        """买入"""
        order_type = 'limit' if price else 'market'
        return await self._create_order(symbol, 'buy', amount, price, order_type)

    async def sell(self, symbol: str, amount: float, price: float = None):
        """卖出"""
        order_type = 'limit' if price else 'market'
        return await self._create_order(symbol, 'sell', amount, price, order_type)

    async def _create_order(self, symbol: str, side: str, amount: float, price: float, order_type: str):
        """创建订单（带风控检查）"""
        order_service = OrderService(self.db)

        order_in = OrderCreate(
            symbol=symbol,
            side=side,
            type=order_type,
            amount=amount,
            price=price,
            exchange_config_id=self.config.get('exchange_config_id')
        )

        return await order_service.create_order(self.user_id, order_in)

    def _convert_kline_to_dict(self, kline: list) -> dict:
        """转换K线数据格式"""
        return {
            'timestamp': kline[0],
            'open': kline[1],
            'high': kline[2],
            'low': kline[3],
            'close': kline[4],
            'volume': kline[5],
        }


# 示例：双均线策略
class DualMovingAverageStrategy(BaseStrategy):
    """
    双均线交叉策略

    参数:
    - fast_period: 快线周期（默认5）
    - slow_period: 慢线周期（默认20）
    - symbol: 交易标的
    - amount: 交易数量
    """

    async def on_bar(self, bar: dict):
        # 1. 获取历史K线
        klines = await MarketDataService().get_klines(
            symbol=self.parameters['symbol'],
            timeframe=self.parameters.get('timeframe', '1h'),
            limit=100
        )

        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 2. 计算均线
        fast_ma = TechnicalIndicators.ema(df, self.parameters['fast_period'])
        slow_ma = TechnicalIndicators.ema(df, self.parameters['slow_period'])

        # 3. 判断交叉
        if fast_ma.iloc[-2] <= slow_ma.iloc[-2] and fast_ma.iloc[-1] > slow_ma.iloc[-1]:
            # 金叉：买入
            logger.info(f"金叉买入 @ {bar['close']}")
            await self.buy(
                symbol=self.parameters['symbol'],
                amount=self.parameters['amount']
            )

        elif fast_ma.iloc[-2] >= slow_ma.iloc[-2] and fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            # 死叉：卖出
            logger.info(f"死叉卖出 @ {bar['close']}")
            await self.sell(
                symbol=self.parameters['symbol'],
                amount=self.parameters['amount']
            )

    async def on_tick(self, tick: dict):
        # 不需要处理逐笔行情
        pass
```

#### 5.2 回测系统 (P1 - 3-4周)

```python
# 需新增: api-gateway/app/services/backtest_service.py

class BacktestService:
    """回测服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_backtest(
        self,
        strategy_class: type,
        strategy_params: dict,
        symbol: str,
        start_date: date,
        end_date: date,
        initial_capital: float = 10000
    ) -> dict:
        """
        运行回测

        返回:
        {
            'total_return': 0.25,  # 总收益率 25%
            'annual_return': 0.30,  # 年化收益率
            'sharpe_ratio': 1.5,  # 夏普比率
            'max_drawdown': -0.12,  # 最大回撤 -12%
            'win_rate': 0.60,  # 胜率 60%
            'total_trades': 120,  # 总交易次数
            'equity_curve': [...],  # 权益曲线
            'trades': [...],  # 交易记录
        }
        """
        # 1. 获取历史数据
        klines = await self._get_historical_klines(symbol, start_date, end_date)

        # 2. 初始化策略
        strategy = strategy_class(strategy_params)

        # 3. 模拟交易
        capital = initial_capital
        position = 0  # 持仓数量
        trades = []
        equity_curve = []

        for i in range(len(klines)):
            bar = klines[i]

            # 更新当前权益
            if position != 0:
                unrealized_pnl = position * (bar['close'] - self.entry_price)
                current_equity = capital + unrealized_pnl
            else:
                current_equity = capital

            equity_curve.append({
                'timestamp': bar['timestamp'],
                'equity': current_equity
            })

            # 触发策略
            signal = await strategy.on_bar(bar)

            # 执行交易
            if signal == 'buy' and position == 0:
                position = capital / bar['close']
                self.entry_price = bar['close']
                capital = 0

                trades.append({
                    'type': 'buy',
                    'price': bar['close'],
                    'amount': position,
                    'timestamp': bar['timestamp']
                })

            elif signal == 'sell' and position > 0:
                capital = position * bar['close']
                realized_pnl = capital - initial_capital

                trades.append({
                    'type': 'sell',
                    'price': bar['close'],
                    'amount': position,
                    'pnl': realized_pnl,
                    'timestamp': bar['timestamp']
                })

                position = 0

        # 4. 计算绩效指标
        total_return = (current_equity - initial_capital) / initial_capital
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)

        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0

        return {
            'total_return': round(total_return, 4),
            'max_drawdown': round(max_drawdown, 4),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'win_rate': round(win_rate, 4),
            'total_trades': len(trades),
            'equity_curve': equity_curve,
            'trades': trades,
        }

    def _calculate_max_drawdown(self, equity_curve: list) -> float:
        """计算最大回撤"""
        peak = equity_curve[0]['equity']
        max_drawdown = 0

        for point in equity_curve:
            if point['equity'] > peak:
                peak = point['equity']

            drawdown = (point['equity'] - peak) / peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

    def _calculate_sharpe_ratio(self, equity_curve: list, risk_free_rate=0.03) -> float:
        """计算夏普比率"""
        # 计算日收益率
        returns = []
        for i in range(1, len(equity_curve)):
            daily_return = (equity_curve[i]['equity'] - equity_curve[i-1]['equity']) / equity_curve[i-1]['equity']
            returns.append(daily_return)

        if not returns:
            return 0

        # 年化夏普比率
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0

        sharpe = (avg_return * 365 - risk_free_rate) / (std_return * np.sqrt(365))
        return sharpe
```

#### 5.3 参数优化 (P2 - 1个月后)

```python
class ParameterOptimizationService:
    """参数优化服务"""

    async def grid_search(
        self,
        strategy_class: type,
        param_grid: dict,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> list:
        """
        网格搜索参数优化

        示例:
        param_grid = {
            'fast_period': [5, 10, 15],
            'slow_period': [20, 30, 40],
        }

        会测试 3×3 = 9 种参数组合
        """
        results = []

        # 生成所有参数组合
        param_combinations = self._generate_param_combinations(param_grid)

        for params in param_combinations:
            # 运行回测
            backtest_result = await BacktestService(self.db).run_backtest(
                strategy_class=strategy_class,
                strategy_params=params,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )

            results.append({
                'params': params,
                'metrics': backtest_result
            })

            logger.info(f"参数组合 {params} 完成: 总收益{backtest_result['total_return']*100:.1f}%")

        # 按夏普比率排序
        results.sort(key=lambda x: x['metrics']['sharpe_ratio'], reverse=True)

        return results

    def _generate_param_combinations(self, param_grid: dict) -> list:
        """生成所有参数组合"""
        keys = param_grid.keys()
        values = param_grid.values()

        return [dict(zip(keys, combination)) for combination in itertools.product(*values)]
```

---

### 系统六：Monitoring 监控告警

**当前状态**: 完全缺失

#### 6.1 实时监控Dashboard (P1 - 2周内)

**前端展示内容**:

```
┌─────────────────────────────────────────────────────────────┐
│  Trading Quant Dashboard                      用户: Admin   │
├─────────────────────────────────────────────────────────────┤
│  总资产: $125,430  (+1.2%)  可用: $87,230  占用: $38,200   │
│  今日盈亏: +$1,450  本月盈亏: +$12,340                       │
├─────────────────────────────────────────────────────────────┤
│  持仓明细                                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 币种    方向   数量    入仓价    当前价   浮盈    杠杆  │ │
│  │ BTC    Long   0.5     $95,230   $98,120  +$1,445  10x  │ │
│  │ ETH    Short  5.0     $3,520    $3,480   +$200    5x   │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  策略状态                                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 双均线策略    运行中   收益 +8.5%   今日交易 3次       │ │
│  │ 网格策略      运行中   收益 +2.3%   今日交易 12次      │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  风险指标                                                   │
│  总敞口: $380,000 (3.0x杠杆)   最大回撤: -8%              │
│  多空比: 2.3   单币种最大敞口: BTC 25%                     │
└─────────────────────────────────────────────────────────────┘
```

#### 6.2 告警系统 (P1 - 2周内)

```python
# 需新增: api-gateway/app/services/notification_service.py

class NotificationService:
    """通知服务"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6380)

    async def send_alert(
        self,
        user_id: int,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        channels: list = None
    ):
        """
        发送告警

        参数:
        - user_id: 用户ID
        - message: 消息内容
        - level: 告警级别 (INFO/WARNING/CRITICAL/EMERGENCY)
        - channels: 通知渠道 ['telegram', 'email', 'web']
        """
        if channels is None:
            channels = ['web']  # 默认仅Web通知

        # 1. 保存到数据库
        alert = Alert(
            user_id=user_id,
            message=message,
            level=level.value,
            channels=','.join(channels)
        )
        self.db.add(alert)
        await self.db.commit()

        # 2. 推送到Redis (WebSocket)
        await self.redis_client.publish(
            f"alerts:{user_id}",
            json.dumps({
                'message': message,
                'level': level.value,
                'timestamp': datetime.now().isoformat()
            })
        )

        # 3. 发送到外部渠道
        if 'telegram' in channels:
            await self._send_telegram(user_id, message, level)

        if 'email' in channels:
            await self._send_email(user_id, message, level)

    async def _send_telegram(self, user_id: int, message: str, level: AlertLevel):
        """发送Telegram通知"""
        # 1. 获取用户Telegram Chat ID
        user = await self.db.get(User, user_id)
        telegram_chat_id = user.telegram_chat_id

        if not telegram_chat_id:
            logger.warning(f"用户{user_id}未配置Telegram")
            return

        # 2. 发送消息
        emoji_map = {
            AlertLevel.INFO: 'ℹ️',
            AlertLevel.WARNING: '⚠️',
            AlertLevel.CRITICAL: '🚨',
            AlertLevel.EMERGENCY: '🚨🚨🚨'
        }

        formatted_message = f"{emoji_map[level]} *量化交易平台*\n\n{message}"

        # 调用Telegram Bot API
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                'chat_id': telegram_chat_id,
                'text': formatted_message,
                'parse_mode': 'Markdown'
            })

    async def _send_email(self, user_id: int, message: str, level: AlertLevel):
        """发送邮件通知"""
        # 使用SendGrid/AWS SES等邮件服务
        pass


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
```

---

## 🗺️ 第三部分：开发优先级路线图

### Phase 1: 核心交易功能 (3-4周)

**目标**: 补齐致命缺陷，达到可用状态

| 优先级 | 功能模块 | 工作量 | 负责人 |
|-------|---------|--------|--------|
| **P0** | 持仓管理系统 (PMS) | 2周 | 后端 |
| **P0** | 事前风控系统 (RMS) | 1.5周 | 后端 |
| **P0** | 订单状态实时同步 | 1周 | 后端 |
| **P0** | 市场数据服务 (Datahub) | 1.5周 | 后端 |
| **P0** | 条件单 (止损止盈) | 1周 | 后端 |
| **P0** | Dashboard持仓展示 | 1周 | 前端 |

**验收标准**:
- ✅ 实时查看所有交易所持仓
- ✅ 浮动盈亏实时计算
- ✅ 下单前强制风控检查
- ✅ 支持止损止盈单

### Phase 2: 策略增强 (3-4周)

**目标**: 完善策略系统，支持回测

| 优先级 | 功能模块 | 工作量 | 负责人 |
|-------|---------|--------|--------|
| **P1** | 事件驱动策略引擎 | 1.5周 | 后端 |
| **P1** | 回测系统 | 2周 | 后端 |
| **P1** | 技术指标库 (TA-Lib) | 1周 | 后端 |
| **P1** | 事中风控实时监控 | 1.5周 | 后端 |
| **P1** | 策略绩效分析 | 1周 | 后端 |
| **P1** | Dashboard策略管理页面 | 1周 | 前端 |

**验收标准**:
- ✅ 支持K线事件驱动
- ✅ 历史数据回测
- ✅ 策略绩效指标计算

### Phase 3: 高级功能 (4-6周)

**目标**: 增强交易能力，提升用户体验

| 优先级 | 功能模块 | 工作量 | 负责人 |
|-------|---------|--------|--------|
| **P1** | OCO订单 | 1周 | 后端 |
| **P1** | 批量订单操作 | 1周 | 后端 |
| **P1** | 监控告警系统 | 2周 | 后端 |
| **P1** | Telegram通知集成 | 0.5周 | 后端 |
| **P1** | 参数优化 | 2周 | 后端 |
| **P1** | 实时图表 (K线图) | 2周 | 前端 |

**验收标准**:
- ✅ 支持OCO订单
- ✅ 监控告警推送
- ✅ 参数网格搜索

### Phase 4: 生产级优化 (6-8周)

**目标**: 性能优化、稳定性提升

| 优先级 | 功能模块 | 工作量 |
|-------|---------|--------|
| **P2** | 算法订单 (TWAP/VWAP) | 3周 |
| **P2** | 数据库读写分离 | 1周 |
| **P2** | Redis集群 | 1周 |
| **P2** | API限流与熔断 | 1周 |
| **P2** | 单元测试覆盖率 > 80% | 2周 |
| **P2** | 压力测试 (1000 QPS) | 1周 |
| **P2** | 日志系统 (ELK) | 1周 |

---

## 📊 第四部分：核心数据模型

### 数据库Schema

```sql
-- 持仓表
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    exchange_config_id INTEGER NOT NULL REFERENCES exchange_configs(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    symbol VARCHAR(50) NOT NULL,
    position_side VARCHAR(10) NOT NULL,  -- long/short
    size DECIMAL(20, 8) NOT NULL DEFAULT 0,
    entry_price DECIMAL(20, 8),
    mark_price DECIMAL(20, 8),
    liquidation_price DECIMAL(20, 8),
    leverage INTEGER NOT NULL DEFAULT 1,
    margin_type VARCHAR(20),  -- cross/isolated
    unrealized_pnl DECIMAL(20, 8) DEFAULT 0,
    realized_pnl DECIMAL(20, 8) DEFAULT 0,
    commission DECIMAL(20, 8) DEFAULT 0,
    margin_used DECIMAL(20, 8) DEFAULT 0,
    margin_ratio DECIMAL(10, 4),
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'open',  -- open/closed/closing
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_positions_user_symbol ON positions(user_id, symbol);
CREATE INDEX idx_positions_exchange_symbol ON positions(exchange_config_id, symbol);

-- 持仓历史表
CREATE TABLE position_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    position_id INTEGER REFERENCES positions(id),
    symbol VARCHAR(50) NOT NULL,
    position_side VARCHAR(10) NOT NULL,
    size DECIMAL(20, 8) NOT NULL,
    entry_price DECIMAL(20, 8),
    exit_price DECIMAL(20, 8),
    hold_duration FLOAT,  -- 持仓时长（秒）
    realized_pnl DECIMAL(20, 8),
    commission DECIMAL(20, 8),
    net_pnl DECIMAL(20, 8),
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 条件单表
CREATE TABLE conditional_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    exchange_config_id INTEGER NOT NULL REFERENCES exchange_configs(id),
    condition_type VARCHAR(50) NOT NULL,  -- stop_loss/take_profit/trailing_stop/conditional
    symbol VARCHAR(50) NOT NULL,
    trigger_price DECIMAL(20, 8),
    trail_percent DECIMAL(10, 4),
    order_side VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    order_price DECIMAL(20, 8),
    order_amount DECIMAL(20, 8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending/triggered/executed/canceled
    triggered_at TIMESTAMP,
    parent_order_id INTEGER REFERENCES orders(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- OCO订单表
CREATE TABLE oco_orders (
    id SERIAL PRIMARY KEY,
    parent_order_id INTEGER NOT NULL REFERENCES orders(id),
    stop_loss_order_id INTEGER REFERENCES orders(id),
    take_profit_order_id INTEGER REFERENCES orders(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 告警表
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    level VARCHAR(20) NOT NULL,  -- info/warning/critical/emergency
    channels VARCHAR(100),  -- telegram/email/web
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 风险违规记录表
CREATE TABLE risk_violations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    violation_type VARCHAR(50) NOT NULL,  -- position_limit/daily_loss/leverage_limit
    description TEXT,
    order_id INTEGER REFERENCES orders(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- K线数据表
CREATE TABLE klines (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- 1m/5m/15m/1h/4h/1d
    timestamp BIGINT NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    UNIQUE(exchange, symbol, timeframe, timestamp)
);

CREATE INDEX idx_klines_symbol_time ON klines(symbol, timeframe, timestamp DESC);
CREATE INDEX idx_klines_timestamp ON klines(timestamp DESC);

-- 回测结果表
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    strategy_name VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20, 8) NOT NULL,
    final_capital DECIMAL(20, 8) NOT NULL,
    total_return DECIMAL(10, 4),
    annual_return DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 2),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(10, 4),
    total_trades INTEGER,
    equity_curve JSONB,
    trades JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 第五部分：技术栈建议

### 后端技术栈

| 组件 | 当前 | 建议 | 优先级 |
|------|------|------|--------|
| Web框架 | FastAPI ✅ | 保持 | - |
| 交易库 | CCXT ✅ | 保持 | - |
| 数据库 | PostgreSQL ✅ | 保持 | - |
| 缓存 | Redis ✅ | 保持 | - |
| 数据分析 | Pandas ✅ | 保持 | - |
| 技术指标 | - | TA-Lib | P1 |
| 时序数据库 | - | InfluxDB (可选) | P2 |
| 消息队列 | - | RabbitMQ/Redis | P1 |
| WebSocket | - | Socket.io | P0 |
| 任务队列 | - | Celery | P1 |
| 监控 | - | Prometheus + Grafana | P2 |

### 前端技术栈

| 组件 | 当前 | 建议 | 优先级 |
|------|------|------|--------|
| 框架 | React ✅ | 保持 | - |
| UI库 | Ant Design ✅ | 保持 | - |
| 状态管理 | Zustand ✅ | 保持 | - |
| 图表库 | - | TradingView Charting Library | P1 |
| WebSocket | - | Socket.io-client | P0 |
| 数据可视化 | - | ECharts/D3.js | P1 |

---

## 📝 第六部分：总结与建议

### 当前系统评分

| 模块 | 完成度 | 评分 | 说明 |
|------|--------|------|------|
| OMS订单管理 | 40% | C+ | 基础功能完成，缺高级订单 |
| PMS持仓管理 | 0% | F | 致命缺陷，立即补充 |
| RMS风险管理 | 0% | F | 致命缺陷，立即补充 |
| Market Data | 20% | D | 基础存在，需完善 |
| Strategy策略 | 30% | C | 框架存在，缺回测 |
| Monitoring监控 | 0% | F | 完全缺失 |
| **总体** | **25%** | **D** | **不可用于实盘** |

### 立即行动清单（Top 5）

1. **创建Position模型和同步引擎** (2周)
   - 没有持仓管理 = 瞎子交易
   - 这是优先级最高的任务

2. **实现事前风控系统** (1.5周)
   - 没有风控 = 定时炸弹
   - 在每笔订单提交前强制检查

3. **订单状态实时同步** (1周)
   - 交易员必须实时掌握订单状态
   - 使用WebSocket推送

4. **完善市场数据服务** (1.5周)
   - 策略需要高质量数据
   - K线数据 + 实时Ticker

5. **实现条件单** (1周)
   - 止损止盈是基本需求
   - 保护资金安全

### 预计时间线

- **1个月后**: 达到可用状态（60%完成度）
- **2个月后**: 达到专业级别（80%完成度）
- **3个月后**: 生产级系统（90%完成度）

### 风险提示

1. **数据质量**: 垃圾进垃圾出，确保市场数据准确
2. **API限制**: 交易所API有频率限制，需要做限流保护
3. **网络延迟**: Crypto市场波动大，延迟可能导致滑点
4. **测试覆盖**: 必须有充分的单元测试和集成测试
5. **安全性**: API Key必须加密存储，操作需要审计日志

---

## 📚 参考资源

### 优秀开源项目参考

1. **VeighNa** - 专业量化交易平台
   - 网址: https://www.vnpy.com/
   - GitHub: https://github.com/veighna/vnpy
   - 参考其策略引擎、回测系统设计

2. **Freqtrade** - 加密货币交易机器人
   - GitHub: https://github.com/freqtrade/freqtrade
   - 参考其技术指标计算、参数优化

3. **Jesse** - 现代化回测框架
   - GitHub: https://github.com/jesse-ai/jesse
   - 参考其回测引擎设计

### 技术文档

1. **CCXT文档**: https://docs.ccxt.com/
2. **FastAPI文档**: https://fastapi.tiangolo.com/
3. **PostgreSQL性能优化**: https://wiki.postgresql.org/wiki/Performance_Optimization

---

**文档结束**

祝开发顺利！如有任何疑问，随时沟通。
