# CryptoQuant Menu Structure

> **Version**: v1.6.0
> **Updated**: 2026-01-31
> **Status**: Planning

---

## Overview

This document defines the menu structure for the CryptoQuant trading platform. The design prioritizes:
- Clear business logic separation
- Professional trading platform experience
- Scalability for future features

---

## Level 1 Menus (7 Core Modules)

| Level 1 | Icon | Business Focus |
|---------|------|----------------|
| **Dashboard** | 🏠 | Asset overview, quick access |
| **Trading** | 📈 | Trade desk with TradingView, order book, order form |
| **Market** | 📊 | Market overview, news |
| **Orders** | 📋 | Order management, trade history |
| **Portfolio & Analytics** | 💰 | Accounts, positions, P&L, analysis |
| **Strategy** | 🤖 | Strategy management, backtesting |
| **Tools** | 🛠️ | Alerts, watchlist, AI, logs |
| **Settings** | ⚙️ | Profile, risk control, preferences |

---

## Menu Structure

**Note:** Indented items represent page-level navigation (tabs or side-nav), not sidebar sub-menus.

```
Dashboard

Trading             ← Single page: Trade Desk with TradingView, Order Book, Order Form

Market
├── Overview       ← Market overview, hot pairs, price trends
└── News           ← Market news and updates

Orders
├── Orders          ← Tab: ALL (default 7 days) / Open / Closed
├── Trade History
└── Reconciliation

Portfolio & Analytics
├── Accounts        ← Tab: Balances / Positions
├── P&L             ← Tab: Overview / Daily / Monthly / Breakdown
└── Portfolio       ← Tab: Analytics / Stats / Risk

Strategy
├── My Strategies (Coming Soon)
├── Backtesting (Coming Soon)
└── Strategy Logs (Coming Soon)

Tools
├── Alerts         ← Multiple alert types: Price, Order, Position, P&L, System (with notification settings)
├── Watchlist
├── AI Assistant   ← Full chat interface (also available via floating button)
└── Trading Journal

Settings
├── Profile & Security
├── Trading
├── Risk Control
├── API Keys
└── System          ← Admin only (page with tabs)
    ├── Health Check
    ├── DataHub      ← Tab with sub-navigation: Jobs, Backfill, OnChain
    └── System Logs
```

---

## System Status Card

**Location**: Bottom-left of sidebar (below menu items)

### Design

```
┌─────────────────────┐
│  System Status       │
│  ● All Systems Go    │  ← Status indicator: Green/Yellow/Red
│  ─────────────────   │
│  OMS    ✓ Online     │
│  DataHub ✓ Online    │
│  API    ✓ Online     │
│  Latency 45ms        │
└─────────────────────┘
```

### Behavior

- **Display**: Always visible in sidebar
- **Click**: Opens detailed Health Check modal
- **Status Colors**:
  - 🟢 Green: All services healthy
  - 🟡 Yellow: Degraded performance
  - 🔴 Red: Service down

### Health Check Services

| Service | Description |
|---------|-------------|
| OMS | Order Management System |
| DataHub | Market Data Service |
| API | Application Gateway |
| Latency | Average response time |

---

## Menu Feature Mapping

### Phase 1 (MVP)

| Menu | Features |
|------|----------|
| Dashboard | Overview (single page, no sub-menus) |
| Trading | Spot (Trade Desk with TradingView, Order Book, Order Form) |
| Market | Overview (basic market data, hot pairs) |
| Orders | Orders (ALL/Open/Closed tabs), Trade History, Reconciliation |
| Portfolio & Analytics | Accounts (Balances/Positions tabs) |
| Strategy | *Placeholder* (coming in Phase 4) |
| Tools | Alerts (Price Alerts) |
| Settings | Profile, Risk Control |

### Phase 2 (Feature Enhancement)

| Menu | Features |
|------|----------|
| Trading | Spot: Add Bracket Order (OCO) support |
| Market | News |
| Portfolio & Analytics | P&L (Overview/Daily/Monthly tabs) |
| Tools | Watchlist |

### Phase 3 (Smart Enhancement)

| Menu | Features |
|------|----------|
| Portfolio & Analytics | Portfolio (Analytics/Stats/Risk tabs) |
| Tools | AI Assistant (with floating button), Trading Journal |

### Phase 4 (Strategy Module)

| Menu | Features |
|------|----------|
| Strategy | My Strategies, Backtesting, Strategy Logs |

---

## Design Rationale

### 1. Dashboard
- **Purpose**: Landing page showing asset status at first glance
- **Content**: Asset overview, P&L summary, quick access to key features

### 2. Trading
- **Purpose**: Trade desk with TradingView, order book, and order form
- **High-frequency use**: Core trading functionality
- **Order Types**: Limit, Market, Bracket OCO (Phase 2)

### 3. Market
- **Purpose**: Market overview, hot pairs, price trends, news
- **Overview**: Market indices, top gainers/losers, volume leaders
- **News**: Market news and updates (can be filtered by token)

### 4. Orders
- **Purpose**: Separate order management from trading to avoid cluttered interface
- **Orders**: Single page with tab filters (ALL/Open/Closed), default shows last 7 days
- **Trade History**: Filled trade records from OMS /trades endpoint
- **Reconciliation**: Compare OMS orders vs Exchange orders, show discrepancies

### 5. Portfolio & Analytics
- **Purpose**: Combine "viewing" functions (accounts, positions) with analytics
- **Rationale**: Analytics is a core differentiator for quantitative platforms
- **Accounts**: Balances and Positions tabs
- **P&L**: Overview, Daily, Monthly, Breakdown tabs
- **Portfolio**: Asset allocation, exchange distribution, net worth curve, analytics/stats/risk tabs

### 6. Strategy
- **Purpose**: Dedicated module for quantitative strategies
- **Phase 4 placeholder**: All sub-menus marked as "Coming Soon"
- **Rationale**: Establishes platform as a professional quantitative trading system

### 7. Tools
- **Purpose**: Collection of auxiliary trading utilities
- **Alerts**: Multiple types - Price, Order, Position, P&L, System alerts (with notification settings integrated)
- **Watchlist**: Save and monitor favorite trading pairs
- **AI Assistant**: Full chat interface, also accessible via floating button (bottom-right)
- **Trading Journal**: Record trade notes and analysis
- **System Logs**: Moved to Settings → System (admin only)

### 8. Settings
- **Purpose**: All configuration options at the bottom
- **Profile & Security**: Avatar, username, email, timezone, password, 2FA, active sessions, login history
- **Trading**: Default exchange, order type, confirmation settings
- **Risk Control**: Position limits, daily loss limit
- **API Keys**: API key management with permissions
- **System** (Admin only): Page with tabs for Health Check, DataHub (with Jobs/Backfill/OnChain sub-tabs), System Logs

---

## Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-31 | Initial version |
| 1.1.0 | 2026-01-31 | Simplified Trading sub-menus (Spot/Swap), removed Dashboard sub-menu |
| 1.2.0 | 2026-01-31 | Redesigned Orders: ALL/Open/Closed tabs, added Reconciliation |
| 1.3.0 | 2026-01-31 | Simplified Portfolio & Analytics: Accounts/P&L/Portfolio with tabs |
| 1.4.0 | 2026-01-31 | Added Market menu, renamed Price Alerts → Alerts, added AI floating button |
| 1.5.0 | 2026-01-31 | Redesigned Settings: Profile+Security merged, added Trading/API Keys/System (DataHub/OnChain), moved System Logs. Note: 3rd level = page tabs, not sidebar menus |
| 1.6.0 | 2026-01-31 | Simplified Trading: removed Spot/Swap sub-menus, now single page |

---

*Document End*
