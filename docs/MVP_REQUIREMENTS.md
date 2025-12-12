# 量化交易系统 MVP 需求规格说明书 (PRD)

**版本**: 0.1.0 (Draft)
**日期**: 2025-12-08
**作者**: Senior Quant Architect (AI)

## 1. 项目概述 (Overview)
本项目旨在构建一个高可用、模块化、前后端分离的量化交易系统。MVP (Minimum Viable Product) 版本将聚焦于核心交易链路的打通，支持多交易所账户管理、手动交易、基础策略自动化运行以及实时监控。

### 1.1 核心目标
1.  **策略自动化**: 支持简单的趋势跟踪或网格策略，能够跨交易所执行。
2.  **手动干预**: 交易员可通过 Web 界面手动下单，接管或辅助策略。
3.  **统一视图**: 聚合多交易所资产、持仓和订单状态。

## 2. 系统架构 (Architecture)

采用 **前后端分离** 架构，通过 RESTful API 和 WebSocket 进行通信。

### 2.1 技术栈选型 (建议)
*   **前端 (Frontend)**:
    *   框架: React 18 + TypeScript
    *   UI 组件库: Ant Design (适合中后台/金融仪表盘)
    *   状态管理: Zustand or Redux Toolkit
    *   数据流: Axios (REST), Socket.io-client (WS)
    *   构建工具: Vite
*   **后端 (Backend)**:
    *   语言: Python 3.10+ (量化生态首选)
    *   Web 框架: FastAPI (高性能，原生异步支持)
    *   交易库: CCXT (支持全球主流交易所 API)
    *   数据处理: Pandas, NumPy
*   **数据库 & 缓存 (Data)**:
    *   关系型数据库: PostgreSQL (存储用户、账户配置、历史订单、策略配置)
    *   缓存/消息队列: Redis (用于实时行情分发、Pub/Sub 内部通信)

### 2.2 模块划分
1.  **Web Dashboard**: 用户交互界面。
2.  **API Gateway (Server)**: 处理 HTTP 请求，鉴权，路由。
3.  **Trade Engine (Core)**: 订单路由、风险控制、状态维护。
4.  **Strategy Executor**: 运行量化策略逻辑的独立进程/线程。
5.  **Market Data Service**: 负责从交易所获取行情并推送到 Redis/Frontend。

## 3. 功能需求 (Functional Requirements)

### 3.1 账户管理 (Account Management)
*   **API Key 管理**: 支持用户加密录入交易所 API Key/Secret。
*   **多账户支持**: 系统需支持同时配置 Binance, OKX, Bybit 等多个交易所的多个账户。
*   **资产同步**: 定时或实时同步各账户的 USDT 余额、持仓数量、未结盈亏 (UPNL)。

### 3.2 交易功能 (Trading)
*   **手动下单 (Manual Order)**:
    *   参数: 标的 (Symbol), 方向 (Buy/Sell), 动作 (Open/Close for Futures), 类型 (Limit/Market), 价格, 数量/金额。
    *   支持现货 (Spot) 和 合约 (Futures/Swap)。
*   **策略下单 (Algo Order)**:
    *   策略引擎需具备标准的 `on_tick` 或 `on_bar` 事件驱动能力。
    *   支持做多 (Long) 和 做空 (Short) 双向操作。
*   **订单管理**:
    *   查询当前挂单 (Open Orders)。
    *   撤单 (Cancel Order)。
    *   查看历史成交 (Trade History)。

### 3.3 策略系统 (Strategy System)
*   **策略配置**: 前端可配置策略参数 (如：MA周期, 网格间距, 止损比例)。
*   **启停控制**: 可一键启动或停止某个策略实例。
*   **日志记录**: 记录策略的触发信号和执行逻辑。

### 3.4 仪表盘 (Dashboard)
*   **行情监控**: 重点关注标的的最新价格 (Ticker) 和 K线图 (可选，MVP可简化)。
*   **权益曲线**: 展示账户总资产的变化趋势。
*   **实时持仓**: 表格展示各交易所的当前持仓、均价、浮动盈亏。

## 4. 非功能需求 (Non-Functional Requirements)
*   **安全性**: API Key 必须加密存储 (如 AES-256)，不在前端明文展示。
*   **响应速度**: 下单接口内部处理延迟 < 50ms (不含网络IO)。
*   **稳定性**: 单个交易所连接断开不应影响整个系统崩溃 (Error Handling & Reconnect)。
*   **扩展性**: 代码结构需预留接入更多交易所和复杂策略的接口。

## 5. 开发计划 (Roadmap)
1.  **Phase 1: 基础架构搭建**: 项目初始化，数据库设计，交易所连接器封装 (CCXT Wrapper)。
2.  **Phase 2: 后端核心逻辑**: 实现手动下单接口，账户余额同步，简单的策略引擎。
3.  **Phase 3: 前端页面开发**: 仪表盘布局，API Key 配置页，下单组件。
4.  **Phase 4: 联调与策略实装**: 编写一个简单的 Demo 策略 (如双均线)，全链路测试。
