Here is the completely revised **AtlasTerminal Product Requirements Document (PRD) v1.1**. It retains the immense depth, structure, and technical rigor of the original, but the data architecture has been overhauled to fully leverage `jugaad-data`'s native capabilities (specifically the `NSELive` class) for live quotes, corporate announcements, real-time option chains, and bulk deals, eliminating the need for brittle custom web scrapers.

---

# AtlasTerminal — Product Requirements Document
**Version:** 1.1  
**Status:** Draft for Development  
**Audience:** Lead Developer / Engineering Team  
**Last Updated:** June 2026  
**Market Target:** NSE/BSE Indian Equities — Nifty 500 Universe  
**Runtime:** Python 3.11+ Desktop Application, compiled to .exe via Nuitka

---

## Table of Contents

1. [Vision & Product Philosophy](#1-vision--product-philosophy)
2. [Target User Persona](#2-target-user-persona)
3. [Technology Stack](#3-technology-stack)
4. [Architecture Overview](#4-architecture-overview)
5. [Module Index](#5-module-index)
6. [Module 01 — Application Shell & Panel System](#6-module-01--application-shell--panel-system)
7. [Module 02 — Command Bar](#7-module-02--command-bar)
8. [Module 03 — Market Data & Quote Display](#8-module-03--market-data--quote-display)
9. [Module 04 — Charting Engine](#9-module-04--charting-engine)
10. [Module 05 — Watchlists](#10-module-05--watchlists)
11. [Module 06 — Screener & Discovery](#11-module-06--screener--discovery)
12. [Module 07 — News, Filings & Announcements](#12-module-07--news-filings--announcements)
13. [Module 08 — Fundamentals & Financial Analysis](#13-module-08--fundamentals--financial-analysis)
14. [Module 09 — NSE F&O Analytics (Live)](#14-module-09--nse-fo-analytics-live)
15. [Module 10 — Macro & Economic Dashboard](#15-module-10--macro--economic-dashboard)
16. [Module 11 — Portfolio & Manual Trade Manager](#16-module-11--portfolio--manual-trade-manager)
17. [Module 12 — Risk Analytics](#17-module-12--risk-analytics)
18. [Module 13 — Catalyst & Event Calendar](#18-module-13--catalyst--event-calendar)
19. [Module 14 — Atlas Engine (Embedded Algorithm)](#19-module-14--atlas-engine-embedded-algorithm)
20. [Module 20 — Backtester](#20-module-15--backtester)
21. [Module 16 — Market Breadth & Internals](#21-module-16--market-breadth--internals)
22. [Module 17 — FII/DII Flow Tracker](#22-module-17--fiidii-flow-tracker)
23. [Module 18 — Block Deals & Bulk Deals](#23-module-18--block-deals--bulk-deals)
24. [Module 19 — Delivery & Institutional Data](#24-module-19--delivery--institutional-data)
25. [Module 20 — Promoter & Insider Holdings](#25-module-20--promoter--insider-holdings)
26. [Module 21 — Trade Journal & Playbook](#26-module-21--trade-journal--playbook)
27. [Module 22 — Sector Heatmap & Rotation](#27-module-22--sector-heatmap--rotation)
28. [Module 23 — Relative Strength & Correlation](#28-module-23--relative-strength--correlation)
29. [Module 24 — Data Download Manager](#29-module-24--data-download-manager)
30. [Module 25 — Settings, Configuration & Nuitka Notes](#30-module-25--settings-configuration--nuitka-notes)
31. [UI/UX Design Requirements](#31-uiux-design-requirements)
32. [Data Architecture & Feed Requirements](#32-data-architecture--feed-requirements)
33. [Non-Functional Requirements](#33-non-functional-requirements)
34. [Phased Delivery Roadmap](#34-phased-delivery-roadmap)
35. [Indian Market Reference Data](#35-indian-market-reference-data)
36. [Glossary](#36-glossary)

---

## 1. Vision & Product Philosophy

### 1.1 What This Product Is

AtlasTerminal is a professional-grade desktop application for Indian equity retail swing traders, built entirely in Python and compiled to a standalone Windows executable via Nuitka. It combines the Project Atlas momentum algorithm with a Bloomberg-style multi-panel workspace, eliminating the need to context-switch between CLI signal scripts, browser tabs for news and charts, and a separate spreadsheet for portfolio tracking.

### 1.2 Non-Negotiable Design Constraints

- **Pure Python only.** No JavaScript, no Electron, no web stack.
- **No broker API integration.** AtlasTerminal generates trade signals and worksheets. The user executes trades manually in their broker.
- **`jugaad-data` is the powerhouse.** NSE Bhavcopy downloads via `jugaad-data` are the canonical EOD OHLCV source. Furthermore, `jugaad-data`'s `NSELive` class is the primary engine for live quotes, corporate announcements, and live option chains. `yfinance` is relegated to a fallback and macro/global data source.
- **Offline-capable.** The core Atlas signal, backtester, charting, and portfolio tracking must work entirely from locally downloaded EOD price data. 

### 1.3 Design Philosophy
- **Every function is reachable from the keyboard.** Command bar navigation.
- **Panels are the atomic unit.** Every view is a dockable, resizable panel.
- **Indian-native formatting.** All currency values are in INR (lakh/crore notation).
- **Opinionated defaults, full configurability.** 

---

## 2. Target User Persona
*(Unchanged from v1.0)*
Primary Persona: The Project Atlas Operator who runs systematic momentum strategies weekly. Secondary Persona: Discretionary swing trader needing robust, free Indian market data and charting.

---

## 3. Technology Stack

### 3.1 UI Framework
**PyQt6** is the mandatory UI framework. 

### 3.2 Charting
**PyQtGraph** is the mandatory charting library. The developer must write a custom `OHLCCandlestickItem` that renders colored candle bodies (green/red) with thin wicks. Use `QPicture` caching for high-performance rendering of 5,000+ candles.

### 3.3 Data Layer
- **Primary Live Feed & EOD Source:** `jugaad-data` (NSE Bhavcopy for EOD, `NSELive` for real-time polling).
- **Fallback / Intraday OHLC / Global Macro:** `yfinance`
- **Data format:** Local CSV files for EOD history.
- **Persistence:** SQLite using **WAL mode** (`PRAGMA journal_mode=WAL;`) for thread-safe concurrency.
- **Background tasks:** Python `threading` with `QRunnable` / `QThreadPool`.

### 3.4 Key Python Libraries
```
pyqt6>=6.6
pyqtgraph>=0.13
pandas>=2.2
numpy>=1.26,<2
jugaad-data>=0.26
yfinance>=0.2
requests>=2.31
tqdm>=4.66
vectorbt>=0.26
```

---

## 4. Architecture Overview

### 4.1 Process Model
Single-process application. Heavy operations (bhavcopy downloads, backtests, Atlas signals) run on `QRunnable` worker threads.

### 4.2 Data Flow
```
NSE Bhavcopy (jugaad-data)  ──►  Local CSV files  ──►  PriceData (EOD in-memory cache)
NSELive (jugaad-data)       ──►  Live Quotes & Options Chains ──►  UI Panels (Polled)
yfinance (fallback/macro)   ──►  Intraday Charts / Global Data
```

### 4.3 Persistence Layer
SQLite database at `{app_data}/atlas_terminal.db`. Initialized in WAL mode to prevent locking when background threads write data while the UI reads.

---

## 5. Module Index
*(Same as v1.0)*

---

## 6. Module 01 — Application Shell & Panel System
*(Unchanged from v1.0 — QDockWidget-based panel system, Link Groups, Saved Workspaces).*

---

## 7. Module 02 — Command Bar
*(Unchanged from v1.0 — Ticker autocomplete, Command table).*

---

## 8. Module 03 — Market Data & Quote Display

### 8.1 Data Sources for Quotes

AtlasTerminal works primarily from locally downloaded daily EOD OHLCV data. However, for "Live" quotes during market hours, the terminal uses `jugaad-data`'s `NSELive().stock_quote(symbol)` method as a polling mechanism, caching results for 1–5 minutes. 

`NSELive` is vastly superior to Yahoo Finance for Indian equities, natively providing Upper/Lower circuits, VWAP, Pre-Open data, and precise NSE sector classifications. `yfinance` is only used if `NSELive` times out or for global indices.

### 8.2 Security Header
Every panel showing a single-ticker view has a security header at the top.

**Left section:** NSE Symbol, Company name, Series badge, Index membership.
**Center section — prices:** Last trade price, Day change ₹/%, Previous close, Open, High, Low.
**Right section — session data:** Volume, Traded Value (crores), Delivery %, **VWAP** (from `NSELive`), Market Cap.

**Status badges:**
- **CIRCUIT:** Extracted directly from `NSELive`'s `priceInfo['lowerCP']` and `upperCP`. Blinks red when LTP equals circuit limit.
- **PRE-OPEN:** Deduced from `NSELive`'s `preOpenMarket` payload before 9:15 AM.
- **EOD:** Amber badge when displaying local EOD data (offline mode).

### 8.3 Multi-Quote Board
A configurable table of multiple tickers simultaneously. Auto-refreshes every N minutes via QTimer using `NSELive` batch polling (or sequential polling with delays to respect rate limits).

### 8.4 India VIX Display
India VIX is shown in the status bar. Sourced from `jugaad-data`'s `NSELive().live_index("INDIA VIX")`.

---

## 9. Module 04 — Charting Engine

### 9.1 Architecture
All charts use PyQtGraph with a custom `OHLCCandlestickItem`.

### 9.2 Timeframes & Data Sources
**EOD timeframes (default — from local `PriceData` CSVs):**
Daily, Weekly, Monthly.

**Intraday timeframes (via `yfinance`):**
1-minute, 5-minute, 15-minute, 1-hour. 
*Note:* `jugaad-data` provides today's live tick data (`tick_data()`), but does not provide historical minute-level OHLC bars. Therefore, historical intraday charting relies on `yf.download(ticker, interval="Xm")` fetched on-demand.

### 9.3 Technical Indicators
All standard indicators computed via Python/NumPy (SMA, EMA, VWAP, RSI, MACD, Bollinger Bands, etc.). 

### 9.4 Event Markers on Chart
- **Earnings/Dividends/Bonuses:** Sourced from `NSELive().corporate_announcements()`.
- **Atlas Levels:** 50-day SMA, 200-day SMA, GTT Stops overlaid on price.

---

## 10. Module 05 — Watchlists
*(Unchanged from v1.0)*

---

## 11. Module 06 — Screener & Discovery
*(Unchanged from v1.0. Screener queries the local EOD `PriceData` for instant results).*

---

## 12. Module 07 — News, Filings & Announcements

### 12.1 Data Sources for Announcements
Unlike generic scrapers, AtlasTerminal leverages `jugaad-data`'s built-in `NSELive().corporate_announcements()` to fetch structured, real-time corporate filings directly from the exchange. No custom cookie managers or headless browser emulation are required.

### 12.2 Announcement Fetching Strategy
- **Market-wide:** On startup, call `corporate_announcements()` without filters to get the latest market-wide announcements.
- **Ticker-specific:** When a user clicks a ticker, fetch `corporate_announcements(symbol=ticker)`.
- Data is cached in the SQLite `news_items` table.

### 12.3 News Panel UI
Rows show: Source logo, Headline, Relative timestamp, Sentiment Badge (up/down/neutral based on quick keyword classification), and Category badge.
Clicking an announcement opens the full text. If a PDF attachment exists (common in NSE filings), provide an "Open PDF" button.

### 12.4 External News Fallback
For general business news (non-regulatory), RSS feeds from Economic Times / MoneyControl are scraped in the background.

---

## 13. Module 08 — Fundamentals & Financial Analysis
*(Unchanged from v1.0. `jugaad-data` does not provide full P&L statements, so the Screener.in CSV import methodology remains the primary way to populate deep fundamental data, supplemented by `yfinance.info` for quick P/E and EPS data).*

---

## 14. Module 09 — NSE F&O Analytics (Live)

### 14.1 Overview and Data Source
AtlasTerminal provides **Real-Time F&O Option Chains** using `jugaad-data`. This elevates the terminal from a purely EOD tool to a live derivatives monitoring station.

Data is fetched via `NSELive().index_option_chain(symbol)` and `NSELive().equities_option_chain(symbol)`. Historical F&O data and OI visualizations use the EOD F&O bhavcopy downloads.

### 14.2 Options Chain Display
For F&O-eligible stocks, an "Options Chain" tab shows live data.
- **Expiry selector:** Populated from the `expiryDates` array in the `NSELive` payload.
- **Chain layout:** Standard two-column (Calls left, Puts right).
- **Columns:** OI, OI Change, Volume, LTP, Bid/Ask. All fields are directly mapped from the `CE` and `PE` dicts returned by `jugaad-data`.
- **Max Pain & PCR:** Computed locally from the fetched chain data.

### 14.3 Live F&O Quote
For quick insights, the terminal uses `NSELive().stock_quote_fno(symbol)` to fetch the last traded prices and order book depth for all available derivatives contracts of a stock in a single call.

### 14.4 OI Chart (Open Interest Visualization)
A PyQtGraph bar chart showing Call OI (red) vs Put OI (green) at each strike for the selected expiry, generated instantly from the live option chain payload.

---

## 15. Module 10 — Macro & Economic Dashboard
*(Unchanged from v1.0. Includes RBI dashboard, Indian macro calendar, and Global Macro sidebar powered by `yfinance` for US indices, crude oil, and USD/INR).*

---

## 16. Module 11 — Portfolio & Manual Trade Manager
*(Unchanged from v1.0. Tracks portfolio, auto-calculates STCG/LTCG taxes based on July 2024 budget, tracks GTT stops 12% below entry).*

---

## 17. Module 12 — Risk Analytics
*(Unchanged from v1.0. Portfolio beta, correlation matrices, and drawdown circuit breakers).*

---

## 18. Module 13 — Catalyst & Event Calendar
*(Unchanged from v1.0. Combines corporate announcements fetched via `NSELive` with static macro dates).*

---

## 19. Module 14 — Atlas Engine (Embedded Algorithm)
*(Unchanged from v1.0. The UI wrapper around `live_signal.py`. Generates BUY/SELL/HOLD instructions based on the Nifty 500 EOD Bhavcopy).*

---

## 20. Module 15 — Backtester
*(Unchanged from v1.0. UI wrapper around `backtest_vectorbt.py` with PyQtGraph equity curves and monthly heatmaps).*

---

## 21. Module 16 — Market Breadth & Internals
*(Unchanged from v1.0. Breadth computed locally from `PriceData`. India VIX tracked via `NSELive`).*

---

## 22. Module 17 — FII/DII Flow Tracker
*(Unchanged from v1.0. As `jugaad-data` lacks an FII/DII endpoint, the terminal fetches the daily net flows directly from NSE's `fiidiiTradeReact` endpoint, displaying cumulative charts).*

---

## 23. Module 18 — Block Deals & Bulk Deals

### 23.1 Data Source
**Live/Ticker-Specific Deals:** Uses `jugaad-data`'s `NSELive().trade_info(symbol)` method, which natively returns recent block and bulk deal data for a specific stock, alongside market depth.
**Market-wide Deals:** EOD fetch from NSE's block-deal API to populate the market-wide dashboard.

### 23.2 Deal Panel
A tabbed view showing today's block deals (Time, Symbol, Buyer/Seller, Qty, Price) and a historical table. Clicking a row pushes the symbol to linked panels.

---

## 24. Module 19 — Delivery & Institutional Data
*(Unchanged from v1.0. Computes delivery percentage from the full bhavcopy download).*

---

## 25. Module 20 — Promoter & Insider Holdings
*(Unchanged from v1.0. Requires CSV downloads of Regulation 31 and SAST filings).*

---

## 26. Module 21 — Trade Journal & Playbook
*(Unchanged from v1.0. Replaces `current_portfolio.csv` history with a rich SQL-backed trade log).*

---

## 27. Module 22 — Sector Heatmap & Rotation
*(Unchanged from v1.0. Visualizes sector momentum using a custom PyQtGraph treemap).*

---

## 28. Module 23 — Relative Strength & Correlation
*(Unchanged from v1.0. Cross-sectional momentum analysis and rolling correlation heatmaps).*

---

## 29. Module 24 — Data Download Manager

### 29.1 Overview
GUI wrapper for `download_data.py`. Manages the EOD data cache.

### 29.2 Bhavcopy & Data Fetching
Uses `jugaad-data`'s `bhavcopy_save()` and `full_bhavcopy_save()`. Configurable rate limiting, retry logic, and concurrent processing. Shows real-time color-coded terminal logs in a `QTextBrowser`.

### 29.3 Fundamentals Import
A dedicated tab for importing Screener.in CSV exports to populate the local fundamentals database.

---

## 30. Module 25 — Settings, Configuration & Nuitka Notes

### 30.1 Settings Dialog
Sections for Data Paths, UI density, Atlas parameters, Tax rates, and **Live Data Polling** (configuring how often `NSELive` fetches background updates for watchlists, ensuring rate limits are respected).

### 30.2 Alert System
Background `QTimer` evaluates local EOD data and polled `NSELive` data against user conditions (e.g., "Alert me if LTP approaches Upper Circuit"). Triggers in-app toasts or Windows desktop notifications.

---

## 31. UI/UX Design Requirements
*(Unchanged from v1.0. Dark theme palette, tabular-nums typography, colorblind modes, property animations for price flashes).*

---

## 32. Data Architecture & Feed Requirements

### 32.1 Local EOD First, `NSELive` Second
The architecture isolates historical EOD data from live polling.
- **`PriceData` Store:** Loaded entirely from local CSVs at startup. Used by charts, backtester, and screener.
- **`LiveStore` Manager:** A singleton managing `NSELive` instances. Uses a thread pool to dispatch live quote and option chain requests. Caches responses with short TTLs (1–5 mins) to avoid spamming the NSE servers.

### 32.2 `jugaad-data` Integration Advantages
By relying on `NSELive`, the application eliminates the need to maintain manual browser headers, session cookies, and regex HTML scraping. The architecture defers to `jugaad-data` to handle NSE's routing and payload decoding.

### 32.3 Fallback Logic
If `NSELive` requests fail repeatedly (e.g., NSE IP ban), the `LiveStore` manager degrades gracefully to `yfinance` for basic price polling, disabling advanced features (Option chains, Market depth) until connectivity is restored.

### 32.4 SQLite Database (WAL Mode)
To support background downloads and live quote updates without freezing the UI, SQLite is strictly initialized using `PRAGMA journal_mode=WAL;`. This allows concurrent readers (UI) and writers (background threads).

---

## 33. Non-Functional Requirements

### 33.1 Performance
- **Startup:** < 10 seconds.
- **Chart render:** 60fps via `QPicture` caching for candlesticks.
- **Memory:** ~300MB steady state.

### 33.2 Reliability
- Unhandled exceptions in background threads must be caught and routed to the UI via Qt Signals to prevent silent Windows crashes.

### 33.3 Nuitka Compilation Requirements
- Use **`--standalone`** instead of `--onefile` to ensure instant application launch times. Distribute via Inno Setup.
- Include directives: `--include-package=pyqtgraph`, `--include-package=pandas`, `--include-package=jugaad_data`.

---

## 34. Phased Delivery Roadmap

### Phase 1 — Core Terminal (Months 1–3)
- Module 01, 02, 03 (Live quotes via `NSELive`), 04 (Charts), 05, 11 (Portfolio), 14 (Atlas Engine), 24 (Data Downloader).
*Exit:* Double-click `.exe`, view portfolio, fetch Bhavcopy, run Atlas signal.

### Phase 2 — Intelligence Layer (Months 4–6)
- Module 06 (Screener), 07 (Announcements via `NSELive`), 08, 13, 16, 21, 22, 25 (Alerts).
*Exit:* Terminal replaces browser for news and tracking.

### Phase 3 — Depth Layer & Live F&O (Months 7–10)
- **Module 09 (Live F&O Chains via `NSELive`)**, 10, 12, 17, 18 (`NSELive` bulk deals), 19, 20, 23.
*Exit:* Terminal serves as a live monitoring station for derivatives.

### Phase 4 — Polish & Power (Months 11–12)
- Replay mode, advanced backtester stats, final Nuitka optimization.

---

## 35. Indian Market Reference Data
*(Unchanged from v1.0. Contains standard NSE Indices, Market hours, and current July 2024 STT/Tax transaction costs).*

---

## 36. Glossary
*(Unchanged from v1.0)*

---

*End of Document — AtlasTerminal PRD v1.1*