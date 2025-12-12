Here is the **Product Requirement Document (PRD) and Technical Architecture Design** for your **DataHub**.

This document outlines the implementation plan to acquire, normalize, and distribute data from Binance, OKX, and Gate.io without using `ccxt`, utilizing official SDKs and raw WebSocket protocols.

---

# DataHub Component Design Document (v1.0)

## 1. Executive Summary
**DataHub** is the central nervous system of the trading platform. Its primary responsibility is to ingest raw data from external exchanges, normalize it into a unified internal format, and distribute it to the Strategy Engine (real-time) and Database (persistence).

**Core Design Principles:**
*   **Low Latency:** Prioritize WebSocket for market data and order updates.
*   **High Availability:** Implement automatic reconnection, heartbeat monitoring, and data gap filling (REST fallback).
*   **Standardization:** Decouple strategy logic from exchange-specific data formats (Adapter Pattern).

---

## 2. Data Acquisition Scope & Strategy

We will classify data into **Market Data (Public)** and **Account Data (Private)**.

### 2.1 Supported Exchanges
*   **Binance** (Spot & Futures) - *Ref: official SDK & API docs*
*   **OKX** (Unified V5) - *Ref: V5 SDK & API docs*
*   **Gate.io** (V4) - *Ref: V4 SDK & API docs*

### 2.2 Data Requirements Matrix

| ID | Data Type | Source Type | Acquisition Channel | Strategy Description |
|:---|:---|:---|:---|:---|
| **1** | **Balance** | Private | **WS + REST** | **WS**: Listen for real-time asset changes.<br>**REST**: Periodic snapshots (e.g., every 1 min) for reconciliation. |
| **2** | **Funding/Transfer** | Private | **REST** | **REST**: Low-frequency polling (e.g., every 1 hour) for ledger history, funding fee deductions, and deposits/withdrawals. |
| **3** | **Symbols** | Public | **REST** | **REST**: Fetch on system startup to load trading rules (tick size, lot size, contract multiplier). |
| **4** | **Kline (Candles)** | Public | **WS + REST** | **WS**: Stream real-time updates for 1m/5m/15m/1h/1d.<br>**REST**: Fetch historical data on startup or after WS disconnection to fill gaps. |
| **5** | **Orders** | Private | **WS + REST** | **WS**: Critical path. Listen for order updates (Filled, Canceled, New).<br>**REST**: Fetch open orders on startup; poll if WS heartbeat fails. |
| **6** | **Trades** | Private | **WS** | **WS**: Real-time stream of your own executions (fills) for PnL calculation. |

---

## 3. System Architecture

The system follows an **Adapter Pattern** to handle exchange differences.

```mermaid
graph TD
    subgraph "External Exchanges"
        BIN[Binance]
        OKX[OKX]
        GATE[Gate.io]
    end

    subgraph "DataHub Layer"
        subgraph "Connectors (Adapters)"
            B_Conn[Binance Adapter]
            O_Conn[OKX Adapter]
            G_Conn[Gate Adapter]
        end

        NORM[Data Normalizer]

        subgraph "Managers"
            WM[WebSocket Manager]
            RM[REST Poller Scheduler]
        end
    end

    subgraph "Downstream"
        MSG[Message Bus (Redis/Kafka)]
        DB[(Time-Series DB / SQL)]
    end

    BIN & OKX & GATE -->|WS Stream| B_Conn & O_Conn & G_Conn
    BIN & OKX & GATE -->|REST API| B_Conn & O_Conn & G_Conn

    B_Conn & O_Conn & G_Conn --> NORM
    NORM --> MSG
    NORM --> DB

    WM -->|Manage Connections| B_Conn & O_Conn & G_Conn
    RM -->|Schedule Tasks| B_Conn & O_Conn & G_Conn
```

### 3.1 Component Definitions

1.  **Exchange Adapter (Base Class):**
    *   Abstract base class defining methods like `get_balance()`, `subscribe_kline()`.
    *   Concrete implementations (`BinanceAdapter`, `OKXAdapter`) wrap the official SDKs.
2.  **WebSocket Manager:**
    *   Handles connection lifecycle: Connect -> Auth -> Subscribe -> Heartbeat (Ping/Pong) -> Reconnect.
    *   **Binance Specifics:** Requires generating a `ListenKey` via REST every 60 minutes to keep the User Data Stream alive.
3.  **Normalizer:**
    *   Converts exchange-specific JSON into **Unified Data Models** (see Section 5).
4.  **REST Poller:**
    *   Handles Rate Limiting (Weight management) to prevent IP bans.

---

## 4. Implementation Details by Exchange

### 4.1 Binance Implementation
*   **SDK:** `binance-connector-python` (Official).
*   **Auth:** HMAC SHA256 signature.
*   **WebSocket:**
    *   **Market Data:** Use `Combined Streams` to reduce connection count (e.g., `/stream?streams=btcusdt@kline_1m/ethusdt@kline_1m`).
    *   **Private Data:** Must call `POST /api/v3/userDataStream` to get a `listenKey`, then connect to `wss://stream.binance.com:9443/ws/<listenKey>`.
*   **Data Quirk:** Watch for the `x` (Is Closed) boolean in K-line data to determine if a candle is finalized.

### 4.2 OKX Implementation
*   **SDK:** `okx-sdk-python` (V5).
*   **Auth:** Custom header generation (Timestamp + Method + Path + Body signed).
*   **WebSocket:**
    *   Unified V5 API. One connection supports both Public and Private channels.
    *   Requires a "Login" frame sent immediately after connection established for private data.
*   **Data Quirk:** Instruments are named `BTC-USDT` (Spot) vs `BTC-USDT-SWAP` (Perp). Needs mapping.

### 4.3 Gate.io Implementation
*   **SDK:** `gate-api` (Official Python SDK).
*   **Auth:** V4 API signature.
*   **WebSocket:**
    *   Uses a request-response style for subscription (JSON-RPC like).
    *   Must sign the subscription payload for private channels (Spot Orders, Futures Orders).

---

## 5. Unified Data Models (Standardization)

To make the strategy engine generic, DataHub must output strictly typed objects.

### 5.1 Unified Symbol Format
*   **Internal:** `BTC_USDT` (Spot), `BTC_USDT_PERP` (Perpetual).
*   **Mapping:** The Adapter maintains a `dict` mapping internal symbols to exchange symbols.

### 5.2 Unified Kline (Candle) Structure
```json
{
  "event_type": "kline",
  "exchange": "BINANCE",
  "symbol": "BTC_USDT",
  "timestamp_open": 1672531200000,
  "open": "16500.50",
  "high": "16510.00",
  "low": "16490.00",
  "close": "16505.00",
  "volume": "25.4",
  "is_closed": true,  // True if the minute/hour has finished
  "period": "1m"
}
```

### 5.3 Unified Order Update
```json
{
  "event_type": "order_update",
  "exchange": "OKX",
  "symbol": "ETH_USDT_PERP",
  "client_order_id": "my_sys_id_123",
  "exchange_order_id": "okx_id_999",
  "side": "BUY",
  "type": "LIMIT",
  "price": "1200.50",
  "quantity": "10.0",
  "filled_quantity": "5.0",
  "status": "PARTIALLY_FILLED", // Standardized Enum: NEW, PARTIAL, FILLED, CANCELED
  "update_time": 1672531205000
}
```

---

## 6. Development Roadmap

### Phase 1: Infrastructure & Market Data
1.  **Skeleton**: Create `BaseExchange` class and DataHub service runner.
2.  **Binance Public**: Implement `get_symbols` and `subscribe_kline` (1m).
3.  **Storage**: Set up TimescaleDB/ClickHouse schemas for Klines.

### Phase 2: Account Connectivity
1.  **Auth Module**: Implement secure API Key/Secret management (Load from Env/Vault).
2.  **Binance Private**: Implement `subscribe_user_data` (ListenKey management) and Balance parsing.
3.  **Order Management**: Implement `get_open_orders` (REST) and Order Update Stream (WS).

### Phase 3: Multi-Exchange Expansion
1.  **OKX Integration**: Replicate functionality using OKX V5 SDK. Handle the "Login" frame logic in WS.
2.  **Gate.io Integration**: Implement V4 API logic.
3.  **Symbol Mapping**: Build a robust mapping utility to translate `BTC-USDT-SWAP` -> `BTC_USDT_PERP`.

### Phase 4: Reliability & Data Integrity
1.  **Heartbeat Logic**: If no WS message received in 10s -> Reconnect.
2.  **Gap Filler**: Logic to detect missing Klines in DB and fetch via REST API automatically.
3.  **Funding/Transfer Poller**: Implement the background job for strictly REST-based data (Funding fees, Deposits).

---

## 7. Technology Stack Recommendations

*   **Language:** Python 3.10+ (Asyncio is mandatory for high-performance WS).
*   **Libraries:** `aiohttp` (for Async REST/WS), `pydantic` (for Data Validation/Normalization).
*   **Message Bus:** Redis (Pub/Sub) for real-time data distribution.
*   **Database:**
    *   **PostgreSQL**: For Configuration, Orders, Balances, Transfers.
    *   **TimescaleDB** (Extension of Postgres): For Klines/Tickers.(暂不使用)

This document serves as the implementation guide. By avoiding `ccxt`, you gain full control over the `websocket` heartbeat and reconnection logic, which is critical for a stable production trading system.
