# DataHub Implementation Plan

Based on `requirement_v1.md` and `tech_v1.md`, this document outlines the step-by-step implementation plan for the DataHub component.

## Phase 1: Core Infrastructure & Data Models

**Goal**: Establish the project skeleton, define unified data models, and set up the base connector architecture.

### 1.1 Project Structure & Environment
- [x] Initialize `datahub` directory and `pyproject.toml` (Already done).
- [ ] Create detailed directory structure:
    - `src/datahub/core` (Engine, Config, EventBus)
    - `src/datahub/models` (Base, Market, Account)
    - `src/datahub/connectors` (Base, Exchanges)
    - `src/datahub/storage` (DB, Redis)
    - `src/datahub/utils` (Logger, Time)

### 1.2 Unified Data Models (Pydantic)
- [ ] Implement `src/datahub/models/base.py`:
    - `ExchangeType` Enum (BINANCE, OKX, GATE)
    - `EventType` Enum (KLINE, ORDER, BALANCE, TRADE)
    - `BaseDataModel` with `raw_payload` field.
- [ ] Implement `src/datahub/models/market.py`:
    - `SymbolInfo` (Trading rules)
    - `KlineData` (OHLCV)
- [ ] Implement `src/datahub/models/account.py`:
    - `BalanceData`
    - `OrderData`
    - `TradeData` (Fills)

### 1.3 Base Connector Interface
- [ ] Implement `src/datahub/connectors/base.py`:
    - Define abstract class `BaseConnector`.
    - Define abstract methods: `fetch_symbols`, `fetch_kline_history`, `connect`, `subscribe_market_data`, etc.

### 1.4 Configuration & Logging
- [ ] Implement `src/datahub/core/config.py` using `pydantic-settings`.
- [ ] Setup `loguru` in `src/datahub/utils/logger.py`.

---

## Phase 2: Market Data (REST Polling)

**Goal**: Implement symbol synchronization and historical data fetching using REST APIs.

### 2.1 Binance REST Implementation
- [ ] Create `src/datahub/connectors/exchanges/binance/rest.py`.
- [ ] Implement `fetch_symbols`: Map Binance exchange info to `SymbolInfo`.
- [ ] Implement `fetch_kline_history`: Fetch OHLCV data.

### 2.2 Storage Layer (PostgreSQL)
- [ ] Design Database Schema (SQLAlchemy Models) in `src/datahub/storage/models.py`.
    - `market_symbols` table.
    - `market_klines` table (Prepare for TimescaleDB or partitioning).
- [ ] Implement `src/datahub/storage/database.py` for AsyncPG connection.

### 2.3 Symbol Sync Service
- [ ] Implement `MarketMetadataManager` in `src/datahub/core/engine.py`.
- [ ] Create a script to run symbol sync on startup.

### 2.4 OKX & Gate.io REST (Iterative)
- [ ] Implement `src/datahub/connectors/exchanges/okx/rest.py`.
- [ ] Implement `src/datahub/connectors/exchanges/gate/rest.py`.

---

## Phase 3: Real-time Market Data (WebSocket)

**Goal**: Stream real-time Klines and Trades using WebSockets without `ccxt`.

### 3.1 WebSocket Infrastructure
- [ ] Implement `WebSocketManager` in `src/datahub/core/websocket.py`.
    - Handle connection, auto-reconnect, and heartbeat (Ping/Pong).
    - Support subscription management.

### 3.2 Binance WebSocket
- [ ] Implement `src/datahub/connectors/exchanges/binance/ws.py`.
- [ ] Implement `subscribe_kline`: Handle Combined Streams.
- [ ] Implement Normalizer: Convert raw WS payload to `KlineData`.

### 3.3 Event Bus & Redis Distribution
- [ ] Implement `src/datahub/core/event_bus.py`.
- [ ] Setup Redis publisher in `src/datahub/storage/cache.py`.
- [ ] Verify data flow: Exchange WS -> Normalizer -> EventBus -> Redis.

### 3.4 OKX & Gate.io WebSocket (Iterative)
- [ ] Implement OKX WS (Unified V5).
- [ ] Implement Gate.io WS (V4).

---

## Phase 4: Private Data (Account & Trading)

**Goal**: Securely stream private account data (Balances, Orders).

### 4.1 Authentication Module
- [ ] Implement signature generation utils for Binance (HMAC-SHA256), OKX, and Gate.io.
- [ ] Securely load API Keys from `.env`.

### 4.2 Binance Private Stream
- [ ] Implement `ListenKey` management (Keep-alive every 60m).
- [ ] Implement `subscribe_account_data`: Handle `outboundAccountPosition` and `executionReport`.

### 4.3 OKX & Gate.io Private Stream
- [ ] Implement Login frames for OKX/Gate WS.
- [ ] Handle private channel subscriptions.

### 4.4 Account Data Persistence
- [ ] Define DB tables for `orders`, `trades`, `balances`.
- [ ] Implement persistence logic for private events.

---

## Phase 5: Reliability & Optimization

**Goal**: Ensure system stability and data integrity.

### 5.1 Gap Filler (Kline Repair)
- [ ] Implement a background task to check for missing candle timestamps in DB.
- [ ] Trigger REST fetch to fill gaps.

### 5.2 Funding Rates & Transfers
- [ ] Implement polling for Funding Rates (Futures).
- [ ] Implement polling for Deposit/Withdrawal history.

### 5.3 Monitoring & Alerting
- [ ] Add Prometheus metrics (WS latency, message rate).
- [ ] Add health check endpoints.
