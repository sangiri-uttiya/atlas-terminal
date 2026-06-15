# AtlasTerminal — Product Requirements Document
**Version:** 1.0  
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
14. [Module 09 — NSE F&O Analytics](#14-module-09--nse-fo-analytics)
15. [Module 10 — Macro & Economic Dashboard](#15-module-10--macro--economic-dashboard)
16. [Module 11 — Portfolio & Manual Trade Manager](#16-module-11--portfolio--manual-trade-manager)
17. [Module 12 — Risk Analytics](#17-module-12--risk-analytics)
18. [Module 13 — Catalyst & Event Calendar](#18-module-13--catalyst--event-calendar)
19. [Module 14 — Atlas Engine (Embedded Algorithm)](#19-module-14--atlas-engine-embedded-algorithm)
20. [Module 15 — Backtester](#20-module-15--backtester)
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

AtlasTerminal is a professional-grade desktop application for Indian equity retail swing traders, built entirely in Python and compiled to a standalone Windows executable via Nuitka. It combines the Project Atlas momentum algorithm (currently operated via CLI scripts on NSE Nifty 500 data) with a Bloomberg-style multi-panel workspace, eliminating the need to context-switch between the CLI signal scripts, browser tabs for news and charts, and a separate spreadsheet for portfolio tracking.

The core problem: the current workflow requires running `live_signal.py` from a terminal, checking NSE announcements in a browser, tracking positions in a CSV, and drawing charts in TradingView or Kite — all as disconnected tools. AtlasTerminal unifies all of this into a single compiled executable that has no Python runtime dependency for end users.

### 1.2 Non-Negotiable Design Constraints

These constraints come from the user's existing system and must be honored everywhere in the design:

- **Pure Python only.** No JavaScript, no Electron, no web stack. The entire application — UI, charting, data processing, persistence — must be implementable in Python. The compiled `.exe` produced by Nuitka must run on a fresh Windows 10/11 machine without any Python installation.
- **No broker API integration.** AtlasTerminal does not place, stage, or route orders. It generates trade signals and worksheets. The user executes trades manually in their broker (Groww, Zerodha, or otherwise). The GTT stop feature is described as a recommended price level to manually enter in the broker — it is not programmatic.
- **jugaad-data is the primary data source.** NSE Bhavcopy downloads via jugaad-data are the canonical OHLCV source. yfinance is the fallback for symbols jugaad-data fails to deliver. The application must clearly distinguish which source was used for each symbol and flag mismatches.
- **Offline-capable.** The core Atlas signal, backtester, charting, and portfolio tracking must work entirely from locally downloaded price data. Internet is only required for incremental data downloads and live quote checks. An airplane-mode user can still run their full weekly workflow.

### 1.3 Design Philosophy

- **Every function is reachable from the keyboard.** A command bar at the top handles ticker lookup and module navigation.
- **Panels are the atomic unit.** Every view is a dockable, resizable panel. The user composes their workspace.
- **The Atlas engine is first class.** The signal generation workflow is not buried in settings — it occupies its own prominent module and is the centerpiece of the Friday workflow.
- **Indian-native formatting.** All currency values are in INR, displayed in lakh/crore notation (₹2.3 cr, not $2.3M). Dates are DD-Mon-YYYY. Market hours are IST. Settlement is T+1.
- **Opinionated defaults, full configurability.** The default workspace mirrors the Friday signal generation workflow. Everything is overridable.

### 1.4 What This Product Is Not

- A trading bot or order management system.
- A web or mobile application.
- A real-time Level 2 order book terminal (NSE data for Level 2 is not publicly accessible without an exchange-licensed feed; this product works from daily/end-of-day data supplemented by delayed intraday quotes where available).
- A product for US or international equity markets (though the architecture allows for future extension).

---

## 2. Target User Persona

### 2.1 Primary Persona — The Project Atlas Operator

- Runs a systematic momentum strategy (Project Atlas) on NSE Nifty 500 equities
- Weekly rebalancing cadence: generates signal on Thursday/Friday before close, executes manually in broker
- Monitors 6–10 open positions simultaneously (equal-slot sizing with sector caps)
- Uses GTT stop-loss orders in Groww or Zerodha for catastrophic downside protection
- Tracks portfolio in a CSV file (`current_portfolio.csv`) and updates it after each trade
- Runs data downloads and signal generation from a Windows machine
- Does not want to maintain a Python environment on every machine they use
- Wants a `.exe` they can double-click and have their entire workflow available

### 2.2 What the User Currently Does (Workflow to Absorb)

This is the existing manual workflow that AtlasTerminal must automate and unify. Every step below must have a direct UI equivalent in the terminal:

1. Friday ~3:00 PM IST: Open a terminal in the project folder.
2. Run `py download_data.py --start 2017-01-01 --end <today> --output-dir bhavcopy_data` to refresh NSE Bhavcopy data.
3. OR run `py download_yahoo_data.py` as fallback for failed symbols.
4. Run `py live_signal.py --data-dir bhavcopy_data` to generate the rebalance signal.
5. Read the printed output: breadth, regime, sells, buys, holds, GTT stop levels.
6. Open Groww/Zerodha in browser.
7. Execute sells first, then buys, manually for each action.
8. Place GTT stop orders 12% below entry for each buy.
9. Update `data/current_portfolio.csv` to reflect new state.
10. Optionally run `py backtest_vectorbt.py` to check if strategy parameters have degraded.

### 2.3 Secondary Persona — The Discretionary Swing Trader

A user who does not run Atlas systematically but uses AtlasTerminal for:
- Chart analysis with technical indicators
- Sector heatmap and breadth monitoring
- Screener for momentum candidates
- Trade journal and portfolio tracking
- Macro calendar for India-specific events (RBI policy, earnings season)

---

## 3. Technology Stack

### 3.1 UI Framework

**PyQt6** is the mandatory UI framework. It is the most capable Python GUI toolkit for financial terminal-style applications, supports native OS rendering (including high-DPI on Windows), and has well-documented Nuitka compilation paths. PySide6 is an acceptable substitute if the developer prefers its LGPL license, but the codebase must pick one and be consistent.

Do NOT use Tkinter (inadequate for financial data density), wxPython (poor Nuitka support), or Dear PyGui (no proper docking/layout system).

### 3.2 Charting

**PyQtGraph** is the mandatory charting library. It is the only Python charting library capable of 60fps interactive rendering of 5,000+ candlestick bars with multiple overlaid indicator lines. It renders natively to Qt's graphics pipeline, making Nuitka compilation straightforward.

Do NOT use Matplotlib (too slow for live financial charts, poor interactivity), Plotly (requires a web browser), or any JS-based charting library.

PyQtGraph's `CandlestickItem` must be subclassed to build a proper OHLC candlestick renderer, as the built-in one is minimal. The developer must write a custom `OHLCCandlestickItem` that renders colored candle bodies (green/red) with thin wicks. This is a known requirement and approximately 150–200 lines of PyQtGraph subclassing.

### 3.3 Data Layer

- **Primary OHLCV source:** jugaad-data (NSE Bhavcopy, stock history via `NSEHistory`)
- **Fallback/supplement:** yfinance (`SYMBOL.NS` tickers)
- **Data format:** Local CSV files, one per symbol (existing `nse_data/` directory structure — unchanged from the current project)
- **In-memory price matrices:** pandas DataFrames (existing `PriceData` dataclass — unchanged)
- **Persistence:** SQLite via Python's built-in `sqlite3` module (watchlists, portfolio snapshots, journal, alert definitions, workspace layouts)
- **Background tasks:** Python `threading` module with `QTimer` for periodic UI refresh. Do NOT use `asyncio` in the Qt thread — use `QRunnable` / `QThreadPool` for background work that needs to update the UI, emitting results via Qt signals.

### 3.4 Key Python Libraries

All libraries below must be verified to compile cleanly under Nuitka 2.x on Windows before project start. The developer must create a Nuitka compilation test fixture early.

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
apscheduler>=3.10
sqlalchemy>=2.0
```

Optional (for Kronos overlay — same as current requirements-kronos.txt):
```
torch>=2.0.0
einops==0.8.1
huggingface_hub>=0.33.1
safetensors>=0.6.2
```

### 3.5 Nuitka Compilation Notes

These requirements apply to all code written for AtlasTerminal:

- All resource files (icons, default config JSON, example universe CSV, stylesheet QSS) must be embedded using Nuitka's `--include-data-files` or the `importlib.resources` API. No `open("relative/path")` calls for resources.
- All dynamic imports must be guarded with try/except or listed in `--include-module`. The Kronos import chain in `kronos_engine.py` (which inserts a path and imports dynamically) must be handled with a Nuitka `--include-plugin-directory` directive.
- PyQtGraph imports `pyqtgraph.graphicsItems` submodules dynamically. The Nuitka compilation command must include `--include-package=pyqtgraph`.
- jugaad-data uses `appdirs` for cache directory resolution — this must work correctly in the compiled executable context. Test this early.
- The compiled executable should be a single-file exe via `--onefile` or a single-directory distribution via `--standalone`. The developer must test both and choose based on startup performance.
- No `__file__` assumptions for data path resolution. Use `sys.executable` and a companion `data/` directory next to the exe.

---

## 4. Architecture Overview

### 4.1 Process Model

AtlasTerminal is a single-process application. There is no separate backend server. All data processing runs in the same process as the UI. Heavy operations (bhavcopy downloads, full backtest, Atlas signal computation, Kronos inference) run on `QRunnable` worker threads and communicate results to the main Qt thread via Qt signals/slots.

The main thread owns:
- All Qt widget operations
- SQLite reads (via connection pool on main thread)
- Panel state management
- Keyboard/mouse event handling

Worker threads own:
- NSE Bhavcopy or jugaad-data downloads
- yfinance batch downloads
- Atlas signal computation (`compute_alpha`, `build_ranked_snapshot`)
- Backtest execution
- Kronos inference
- Periodic live quote refreshes (polling a quote API every N seconds)

### 4.2 Data Flow

```
NSE Bhavcopy (jugaad-data)  ──►  Local CSV files  ──►  PriceData (in-memory)
yfinance (fallback)          ──►  Local CSV files  ──►  AlphaData  ──►  RankedSnapshot
                                                    ──►  BacktestResult
                                                    ──►  UI Panels (via Qt signals)
```

The `PriceData` object is loaded once at application startup (for the configured data directory and universe) and kept in memory. Panels read from it. When new data is downloaded, the `PriceData` object is reloaded and all panels refresh.

### 4.3 Persistence Layer

SQLite database at `{app_data}/atlas_terminal.db`. Tables:

- `workspaces` — JSON-serialized panel layout trees, keyed by workspace name
- `watchlists` — Ticker lists with user metadata
- `portfolio` — Current positions (replaces current_portfolio.csv, but can export to CSV for backward compatibility)
- `journal_trades` — Full trade journal with all metadata
- `journal_playbook` — Named setups and criteria
- `alerts` — Alert definitions
- `app_settings` — Key-value config store

The CSV files for portfolio (`current_portfolio.csv`) remain supported as import/export format for backward compatibility with the existing live_signal.py workflow.

### 4.4 Configuration

All configurable parameters use `AtlasConfig` (existing dataclass) extended with UI-specific fields. The full config is serialized to `{app_data}/atlas_config.json` and loaded on startup. The UI provides a settings panel to edit all parameters. Changes to AtlasConfig parameters trigger a re-computation of alpha on the loaded PriceData.

### 4.5 File System Layout (Runtime)

```
AtlasTerminal.exe              ← compiled Nuitka executable
data/
  universe_nifty500.csv        ← Nifty 500 universe with sector mappings
  current_portfolio.csv        ← current holdings (writable by UI)
  corporate_actions.csv        ← split/bonus adjustments
nse_data/                      ← one CSV per symbol (jugaad/bhavcopy)
reports/
  equity_curve.csv             ← backtest output
  trades.csv                   ← backtest trade log
  summary.json                 ← backtest summary
  kronos_predictions.csv       ← optional Kronos forecasts
atlas_terminal.db              ← SQLite persistence
logs/
  atlas_terminal.log           ← rotating log file
```

---

## 5. Module Index

| # | Module | Priority |
|---|--------|----------|
| 01 | Application Shell & Panel System | P0 — Core |
| 02 | Command Bar | P0 — Core |
| 03 | Market Data & Quote Display | P0 — Core |
| 04 | Charting Engine | P0 — Core |
| 05 | Watchlists | P0 — Core |
| 06 | Screener & Discovery | P0 — Core |
| 07 | News, Filings & Announcements | P1 — High |
| 08 | Fundamentals & Financial Analysis | P1 — High |
| 09 | NSE F&O Analytics | P2 — Medium |
| 10 | Macro & Economic Dashboard | P1 — High |
| 11 | Portfolio & Manual Trade Manager | P0 — Core |
| 12 | Risk Analytics | P1 — High |
| 13 | Catalyst & Event Calendar | P1 — High |
| 14 | Atlas Engine (Embedded Algorithm) | P0 — Core |
| 15 | Backtester | P0 — Core |
| 16 | Market Breadth & Internals | P1 — High |
| 17 | FII/DII Flow Tracker | P2 — Medium |
| 18 | Block Deals & Bulk Deals | P2 — Medium |
| 19 | Delivery & Institutional Data | P2 — Medium |
| 20 | Promoter & Insider Holdings | P2 — Medium |
| 21 | Trade Journal & Playbook | P1 — High |
| 22 | Sector Heatmap & Rotation | P1 — High |
| 23 | Relative Strength & Correlation | P1 — High |
| 24 | Data Download Manager | P0 — Core |
| 25 | Settings & Configuration | P0 — Core |

---

## 6. Module 01 — Application Shell & Panel System

### 6.1 Main Window Structure

The application main window (`QMainWindow`) has the following regions, from top to bottom:

- **Menu bar** (QMenuBar): File | Data | Atlas | View | Tools | Help
- **Command bar** (custom QWidget, full width, 32px tall): Always visible below the menu bar
- **Panel workspace** (central widget): The resizable multi-panel area
- **Status bar** (QStatusBar): Market session status, last data date, feed health, time

### 6.2 Panel Model

Every piece of content lives in a `AtlasPanel` — a `QDockWidget` subclass. The developer must subclass `QDockWidget` and override:

- The title bar to be a custom widget (not the default Qt title bar) showing: panel type icon (16px), ticker label (if applicable), link group color button, a minimize/detach/close button cluster
- The floating behavior (already supported by `QDockWidget`)
- Dock area restrictions (panels can dock to any edge or be floating)

The central `QMainWindow` uses `QDockWidget` docking system: panels dock into the main window and split/tabify via Qt's native docking engine. This is the correct approach for Nuitka-compiled PyQt6 — do NOT attempt a custom tiling window manager from scratch.

**Panel types correspond to modules:**
- `QuotePanel` — live quote display for one ticker
- `ChartPanel` — price chart
- `WatchlistPanel` — ticker watchlist
- `ScreenerPanel` — stock screener
- `AtlasSignalPanel` — Atlas rebalance signal view
- `AtlasBacktestPanel` — backtest runner and result view
- `PortfolioPanel` — current holdings
- `JournalPanel` — trade journal
- `NewsPanel` — news and announcements feed
- `FundamentalsPanel` — company financials
- `MacroPanel` — Indian macro dashboard
- `HeatmapPanel` — sector heatmap
- `BreadthPanel` — market breadth indicators
- `FIIDIIPanel` — FII/DII flow data
- `BlockDealPanel` — block/bulk deals
- `CalendarPanel` — event calendar
- `DownloadPanel` — data download manager

### 6.3 Link Groups

Panels are assigned link group colors (6 colors: red, blue, green, yellow, orange, purple). When a ticker changes in any panel in group X (user clicks a row in the screener, or types in the panel title bar), all panels in group X update to that ticker simultaneously.

Link group assignment: clicking the colored circle in the custom panel title bar cycles through colors (and an "unlinked" / gray state). This is a single click per cycle; right-click shows a color picker popup.

The link group state is stored as an integer in `AtlasPanel` and managed by a singleton `LinkGroupManager` that maintains a `dict[int, set[AtlasPanel]]`. When a ticker changes in one panel, `LinkGroupManager.broadcast(group_id, ticker)` is called, which emits a signal received by all panels in the group.

### 6.4 Saved Workspaces

Workspaces are serialized to the `workspaces` SQLite table. Each workspace stores:
- A JSON tree of `QMainWindow.saveState()` output for panel dock positions
- A parallel JSON structure of panel configurations (type, ticker, link group, panel-specific settings)
- A workspace name

Workspaces appear as tabs in a `QTabBar` below the command bar. The `QTabBar` shows up to 10 workspace tabs. Switching tabs triggers `QMainWindow.restoreState()` followed by per-panel config restoration.

**Default workspaces to ship:**

1. **Atlas Friday Signal** — AtlasSignalPanel (full left 60%) | PortfolioPanel (top-right 40%) | NewsPanel (bottom-right)
2. **Charting** — ChartPanel (large, 70%) | WatchlistPanel (top-right) | QuotePanel (bottom-right)
3. **Screener** — ScreenerPanel (left 65%) | ChartPanel (top-right) | NewsPanel (bottom-right)
4. **Market Overview** — HeatmapPanel (top-left 50%) | BreadthPanel (top-right 50%) | FIIDIIPanel (bottom-left) | MacroPanel (bottom-right)
5. **Backtester** — AtlasBacktestPanel (full width, with results below)

### 6.5 Panel Quick-Open

`Ctrl+Shift+N` opens a `QDialog` (not a native modal — use a frameless `QFrame` overlay that doesn't block the workspace) showing all panel types as a grid of icon buttons with labels. Clicking one creates a floating instance of that panel. The dialog closes on Escape or on click-outside.

### 6.6 Density Modes

Two density modes, toggled from the View menu or `Ctrl+D`:
- **Compact** (default): 10px data font, 24px row height, reduced padding. Bloomberg-like density.
- **Comfortable**: 12px data font, 28px row height. For single-monitor setups.

A global QSS stylesheet variable `--row-height` and `--font-size-data` is set at startup. All panel widgets reference these variables. Switching density modes re-applies the stylesheet.

---

## 7. Module 02 — Command Bar

### 7.1 Command Bar Widget

A full-width `QLineEdit` subclass styled as a dark terminal prompt, placed directly below the menu bar. Height: 32px. Placeholder text: `Enter ticker or command... (F1 for help)`.

The command bar is always focused when no other input is active. Pressing any letter key when a non-input widget has focus activates the command bar (global event filter on the main window).

### 7.2 Ticker Autocomplete

As the user types, a `QListWidget` dropdown (styled as a popup, parented to the main window, floating above the workspace) shows matching NSE symbols from the universe file. Each result row shows:

- Ticker symbol (bold, monospace)
- Company name (smaller, regular)
- Sector badge
- Last close price (from in-memory PriceData)
- Day % change if available from live quote cache

Matching is prefix-first (RELI → RELIANCE first) then fuzzy (REL → RELINFRA, RELIASSET, etc.). Results limited to 10. Pressing Enter or clicking a result pushes the ticker to all panels in the active link group.

The universe for autocomplete is the loaded `universe_nifty500.csv`. Symbols not in the universe (e.g., indices like NIFTY, NIFTYBANK) can also be typed directly.

### 7.3 Command Table

The developer must implement all commands in the following table. Commands are case-insensitive. A command can be combined with a ticker (`CHART RELIANCE` or `RELIANCE CHART`).

| Command | Panel Opened | Notes |
|---------|-------------|-------|
| `CHART` or `C` | ChartPanel | |
| `QUOTE` or `Q` | QuotePanel | |
| `WATCH` or `W` | WatchlistPanel | |
| `SCRE` or `SCR` | ScreenerPanel | |
| `NEWS` or `N` | NewsPanel | |
| `FA` or `FUND` | FundamentalsPanel | |
| `OPT` or `FO` | NSE F&O Panel | |
| `PORT` or `P` | PortfolioPanel | |
| `ATLAS` or `SIGNAL` | AtlasSignalPanel | |
| `BACK` or `BT` | AtlasBacktestPanel | |
| `MACRO` or `INDIA` | MacroPanel | |
| `CAL` or `ECO` | CalendarPanel | |
| `HEAT` | HeatmapPanel | |
| `BREADTH` or `BR` | BreadthPanel | |
| `FII` | FIIDIIPanel | |
| `BLOCK` | BlockDealPanel | |
| `JOURNAL` or `J` | JournalPanel | |
| `RS` | Relative Strength Panel | |
| `CORR` | Correlation Matrix Panel | |
| `DOWNLOAD` or `DL` | DownloadPanel | |
| `SETTINGS` or `SET` | Settings Dialog | |
| `HELP` or `?` | Command reference overlay | |

### 7.4 Command History and Help

- Command history: last 50 entries, navigated with up/down arrow keys
- `HELP` opens a `QDialog` with a searchable `QTableWidget` of all commands and their descriptions
- Tab key completes the topmost autocomplete suggestion

---

## 8. Module 03 — Market Data & Quote Display

### 8.1 Data Sources for Quotes

AtlasTerminal works primarily from locally downloaded daily OHLCV data. It does not connect to a real-time market feed by default. "Live" quotes are fetched on demand from yfinance (`yf.Ticker("SYMBOL.NS").fast_info`) as a polling mechanism, with results cached for 5 minutes. The developer must implement a `QuoteCache` singleton that stores the last fetched quote per symbol with a TTL.

For end-of-day data (after 3:30 PM IST), the last bhavcopy row is the authoritative price. For intraday, the yfinance fast_info endpoint provides a "best effort" delayed quote (15 minutes delayed for most NSE stocks on Yahoo).

The application must be usable entirely from local EOD data (no internet required for core workflow). All "live quote" fields degrade gracefully to last EOD values with a "EOD" badge when no internet is available.

### 8.2 Security Header

Every panel that shows a single-ticker view has a security header at the top. All values from local EOD data unless a live quote has been fetched within the TTL.

**Left section:**
- NSE Symbol (large, bold, monospace, white)
- Company full name (smaller, below, secondary color)
- Series badge (EQ / BE / BZ / N2 etc.)
- Exchange badge: NSE | BSE
- Index membership badges: NIFTY50 | NIFTYBANK | NIFTY500 | NIFTYMIDCAP150 (show only relevant)

**Center section — prices in INR:**
- Last trade price (large, primary color)
- Day change ₹ (e.g., "+₹18.50", colored green/red)
- Day change % (e.g., "+1.23%", colored green/red)
- Previous close
- Open price
- Day High / Day Low (formatted as "H: ₹X / L: ₹Y")
- 52-week High / 52-week Low

**Right section — session data:**
- Volume (formatted as "X.X cr shares" or "X.X lakh shares" — threshold at 10 lakh)
- Traded Value (formatted as "₹X.X cr" — crore always, with one decimal)
- 30-day Average Daily Value (ADV30) in crore
- ADV Ratio (today / ADV30, colored green if > 1.5)
- Delivery % (today's delivery as % of total volume — NSE publishes this)
- VWAP (Volume Weighted Average Price)
- Market Cap (₹ cr or ₹ lakh cr depending on size)
- Free Float Market Cap
- Beta (52-week, vs Nifty 50)

**Status badges:**
- "CIRCUIT" badge (red, blinking) when price is at upper or lower circuit limit. Show "UC" for upper circuit, "LC" for lower circuit.
- "SUSPENDED" badge when the stock is suspended from trading
- "EOD" badge (amber) when displaying last end-of-day data, no live quote
- "DELAYED" badge (gray) when displaying a 15-minute delayed yfinance quote
- "T2T" badge when the stock is in Trade-to-Trade (T2T/BE series) — square-off on same day is not possible
- "SLB" badge when stock is available for Securities Lending & Borrowing

### 8.3 Standalone Quote Panel (QUOTE command)

A dedicated panel for the full quote view of one symbol. All fields from 8.2, plus:

**52-Week Range Gauge:** A horizontal bar showing today's price relative to the 52-week high-low range. Include the percentile position (e.g., "72nd percentile of 52W range"). This is computed from local OHLCV data.

**Key Statistics Grid (computed from local OHLCV and fundamentals data):**
- P/E (TTM) — from fundamentals DB or yfinance
- P/B — from fundamentals DB
- EV/EBITDA — from fundamentals DB
- Price/Sales — from fundamentals DB
- Dividend Yield — from fundamentals DB
- Dividend Ex-Date — last known
- EPS (TTM) — from fundamentals
- Face Value — from NSE (₹1, ₹2, ₹5, ₹10)
- Next Earnings Date — from calendar DB
- 30-Day Historical Volatility (computed from local close prices)
- RSI 14 (computed from local close prices)
- ATR 14 in ₹ and % (computed from local OHLCV)
- Relative Volume (today / ADV30)
- 60D Return %, 120D Return %, 200D Return % (from AlphaData — same inputs as Atlas score)
- Atlas Score (if atlas data is loaded for this symbol — from the most recent RankedSnapshot)
- Atlas Rank (out of universe — e.g., "Rank 12 / 487")

**Analyst Consensus (from fundamental data source):**
- Consensus: Strong Buy / Buy / Hold / Sell / Strong Sell
- Count of analysts at each level
- Median price target in ₹
- % upside/downside from current price
- Most recent rating change with date

### 8.4 Multi-Quote Board

A panel showing a configurable table of multiple tickers simultaneously. Default columns: Symbol, Last ₹, Chg ₹, Chg%, Volume (cr shs), Val (₹ cr), ADV30 (₹ cr), ADV Ratio, 52W High, 52W Low, RSI14, Atlas Score, Atlas Rank, Sector.

All values from local EOD data. Manual refresh button (since no real-time feed). Auto-refresh every 5 minutes via QTimer when market is open (9:15–15:30 IST) — fetches yfinance fast_info for all visible symbols in a background QRunnable.

### 8.5 India VIX Display

India VIX (ticker: `^INDIAVIX` on yfinance) is shown in the status bar as a persistent data point. Include:
- Current India VIX level
- Day change (value and %)
- A color indicator: green (VIX < 15), amber (15–20), orange (20–25), red (> 25)

India VIX refreshes on the same yfinance polling schedule as other quotes.

### 8.6 Market Status Bar (Bottom of Window)

A 22px-tall persistent strip at the bottom of the `QMainWindow`, using the `QStatusBar`. Left to right:

- Session status indicator: "PRE-OPEN 9:00–9:15" | "OPEN 9:15–15:30" | "POST-CLOSE" | "CLOSED" (colored label)
- IST current time (live, updated every second via QTimer)
- Time to next session event (e.g., "Opens in 1h 22m" or "Closes in 43m")
- NIFTY50 last price and day % (from yfinance or EOD cache)
- NIFTYBANK last price and day %
- NIFTYMIDCAP150 last price and day %
- India VIX last value and day %
- USD/INR exchange rate (₹/$ — from yfinance `USDINR=X`)
- Data freshness indicator: date of the last loaded Bhavcopy file (e.g., "Data: 13-Jun-2026")
- Feed health: green dot (all OK), amber (yfinance slow/errors), red (no internet or data error)

---

## 9. Module 04 — Charting Engine

### 9.1 Architecture

All charts use PyQtGraph. The main chart widget is a `PlotWidget` (or `GraphicsLayoutWidget` for multi-pane charts) embedded in a `ChartPanel`. The developer must implement a `ATLASChart` class that manages:

- The main price pane (top, 60% of vertical space)
- Up to 3 sub-indicator panes below (each ~13% vertical, adjustable by dragging the divider)
- A thin volume sub-pane directly below the price pane (always visible)
- An x-axis shared across all panes (date labels, synchronized crosshair)

The chart data source is the local `PriceData` object. When the ticker changes, the chart slices the relevant columns from the in-memory matrices and re-renders. No network call is made for chart data.

### 9.2 Chart Types

- Candlestick (default): Custom `OHLCCandlestickItem` (PyQtGraph `GraphicsObject` subclass). Green body + thin wick for bullish candle; red body + thin wick for bearish. Filled body style is default.
- Heikin-Ashi: Pre-compute HA OHLC from regular OHLC before passing to the same `OHLCCandlestickItem`.
- OHLC Bar: Standard bar chart using PyQtGraph's `BarGraphItem` or a custom painter.
- Line (Close): Simple `PlotDataItem` with the close series.
- Area (Close): `PlotDataItem` with `fillLevel=0` and semi-transparent fill.

### 9.3 Timeframes

Since data is daily EOD, all intraday timeframes < 1D require a live data source (yfinance intraday). The chart must support both:

**EOD timeframes (default — from local data):**
Daily, Weekly (resampled weekly OHLCV from daily), Monthly (resampled monthly OHLCV from daily)

**Intraday timeframes (via yfinance, market hours only):**
1-minute, 5-minute, 15-minute, 30-minute, 1-hour

For intraday charts, data is fetched via `yf.download(ticker, period="1d", interval="Xm")` in a background worker. The intraday data is NOT cached to disk (too large for 500 symbols). It is held in memory per-panel and refreshed on user request.

The timeframe selector is a `QComboBox` in the chart toolbar showing: 1m, 5m, 15m, 30m, 1h | D, W, M. A separator divides intraday (requires internet) from EOD (from local data).

When an intraday timeframe is selected and internet is unavailable, show an in-chart error overlay: "Intraday data requires internet. Switch to Daily/Weekly/Monthly or connect to the internet."

Extended hours: NSE pre-open is 9:00–9:15 IST. Post-close session is 15:40–16:00 IST. yfinance does not cleanly expose these; mark pre-open and post-close bars (if returned) with a distinct candle color (lighter shade).

### 9.4 Chart Toolbar

A horizontal `QToolBar` above the chart containing:

- Ticker `QLineEdit` (changes the chart ticker; also responds to link group broadcasts)
- Timeframe `QComboBox`
- Chart type `QComboBox` (Candlestick / Heikin-Ashi / OHLC / Line / Area)
- "Add Indicator" button → opens `IndicatorPicker` dialog
- "Draw" button → activates drawing mode and shows drawing toolbar
- "Compare" button → opens a small overlay to add a comparison ticker (overlay as % normalized line)
- "Events" button → toggles event marker overlay (earnings, corporate actions, dividends)
- "Atlas Levels" button → overlays Atlas-computed levels (52W high, 50-day SMA, stop levels)
- "Snapshot" button → saves the chart to a PNG in the `reports/` folder
- "Replay" button → enters bar-by-bar replay mode (see 9.11)

### 9.5 Technical Indicators

All indicator computations happen in Python/NumPy/pandas. PyQtGraph renders the results. The developer must implement each indicator as a function taking a `PriceData` slice and returning one or more arrays. Indicators are applied per-chart-instance and stored in the chart's state dict.

**Overlay Indicators (rendered on price pane):**

- Simple Moving Average (SMA): `ta.sma(close, period)`. Default series: SMA 50 (yellow), SMA 200 (orange). Period, color, line width, line style (solid/dashed/dotted) all configurable.
- Exponential Moving Average (EMA): `ta.ema(close, period)`. Default: EMA 20 (cyan).
- Weighted Moving Average (WMA)
- Hull Moving Average (HMA)
- Volume Weighted Moving Average (VWMA): `sum(close * volume, N) / sum(volume, N)`
- VWAP (daily session VWAP): Computed from intraday data only; for daily charts, show a DVWAP line representing the VWAP of each completed session as a constant-per-session step line.
- Anchored VWAP: User clicks a candle to anchor; VWAP computed from that point forward. Unlimited simultaneous anchors. Removes when the user right-clicks the anchored VWAP line.
- Bollinger Bands (period, sigma): Upper/lower bands as line series; optional fill between bands.
- Keltner Channels (EMA base, ATR multiplier)
- Donchian Channels (N-period highest high / lowest low)
- Ichimoku Cloud (Tenkan 9, Kijun 26, Senkou A/B, Chikou 26 shift). Cloud fill between Senkou A and B (green when A > B, red when B > A).
- Parabolic SAR: Dots plotted above/below candles.
- Supertrend (ATR factor, period): Line that flips sides and changes color on trend change.
- Linear Regression Line (N-period)
- Pivot Points: Standard daily/weekly/monthly pivots (P, R1, R2, R3, S1, S2, S3) shown as horizontal lines with labels. Selectable period.
- Camarilla Pivots: Alternative pivot formula, shown the same way.

**Sub-Pane Indicators:**

- RSI (period configurable, default 14): Line chart in sub-pane. Horizontal reference lines at 70 and 30. Fill between RSI and 70 line (red) and between RSI and 30 line (green) when in overbought/oversold zones. RSI Moving Average overlay (optional signal line).
- Stochastic RSI (K and D configurable)
- MACD (fast/slow/signal configurable, default 12/26/9): Histogram (bars colored green above zero, red below) plus MACD line and Signal line overlaid.
- CCI (Commodity Channel Index, default 20)
- Williams %R (default 14)
- Stochastic Oscillator (%K and %D, default 14/3)
- On-Balance Volume (OBV): Cumulative volume indicator
- Chaikin Money Flow (CMF, default 20)
- Average True Range (ATR, default 14): In crore or points
- Historical Volatility (annualized, default 20-day)
- Volume (always-present sub-pane, not add/remove): Bar chart with bars colored same as the corresponding candle. Volume MA (20-period, white line) always overlaid. Volume displayed in absolute shares (in lakh or crore notation).
- Relative Volume (today's volume bar / 20-day avg): Displayed as a ratio line (1.0 = average, > 1 = above average). Only meaningful on daily charts.
- Money Flow Index (MFI, default 14)
- Aroon Indicator (Up and Down lines, default 25)
- ADX / DMI (ADX, +DI, -DI, default 14)

**India-Specific Indicators:**

- Delivery Percentage: An additional sub-pane bar chart showing delivery % per day (NSE publishes this in bhavcopy data when available). High delivery % on an up day = strong conviction buying. The developer must parse the delivery column from the bhavcopy when it exists. Display as a bar chart, coloring bars above 50% green and below 50% orange.
- FII/DII Net Flow overlay: An optional cumulative line overlay on the price chart showing rolling 20-day FII+DII net equity flow (from the FII/DII module's stored data). Helps visualize institutional pressure alongside price.

### 9.6 Drawing Tools

All drawings are stored per-ticker in the SQLite `chart_drawings` table. They persist across sessions and restore when the ticker is reopened. Drawings are implemented as PyQtGraph `ROI` or `InfiniteLine` or custom `GraphicsObject` subclasses.

**Line Tools:**
- Horizontal Line (extends across entire chart; most commonly used for support/resistance)
- Horizontal Ray (extends right only from the anchor point)
- Vertical Line (marks a specific date)
- Trend Line (two-point, finite; extends to both edges optionally)
- Extended Line (two-point, infinite both ways)
- Arrow (with optional label)

**Fibonacci Tools:**
- Fibonacci Retracement: User drags from swing low to swing high (or reverse). Lines drawn at 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%. Labels show level % and the price at that level in ₹. Price levels are the most important — show them prominently (e.g., "38.2% | ₹2,847").
- Fibonacci Extension: Three-point (swing low, swing high, retracement) drawing. Extension levels: 127.2%, 161.8%, 200%, 261.8%.
- Fibonacci Fan

**Channel Tools:**
- Parallel Channel (two parallel lines, fill between)
- Pitchfork (Andrews Pitchfork, three handles)

**Text and Annotation:**
- Text label (pinned to price level or free-floating date+price anchor)
- Note (sticky-note style annotation for trade thoughts)
- Price label (auto-shows the INR price at the anchor level)

**Drawing Properties:**
Each drawing supports: color, line width (1–4px), line style (solid/dashed/dotted), fill color and opacity (for channel tools), text (for labels), lock toggle (prevent accidental drag), show/hide toggle, and "delete" (right-click context menu). All drawing objects serialize to JSON in the SQLite drawings table.

**Drawing Toolbar:**
Appears as a vertical toolbar on the left edge of the chart panel when "Draw" mode is active. Shows icons for each tool type. Clicking a tool icon activates that drawing mode; the cursor changes to a crosshair. Drawing mode is deactivated by pressing Escape or clicking the active tool icon again.

### 9.7 Event Markers on Chart

Togglable event overlays, each shown as small labeled markers on the candles. Implemented as PyQtGraph `TextItem` or small `PlotDataItem` scatter points with distinct shapes.

- **Earnings dates** ("E" marker, dark blue triangle): Date of the quarterly results announcement. Source: loaded from the calendar database. Hovering shows a tooltip with EPS actual vs estimate and revenue vs estimate if available.
- **Dividend ex-dates** ("D" marker, amber triangle): NSE ex-dividend date. Hovering shows dividend amount in ₹/share.
- **Bonus / Split dates** ("B" or "S" marker, purple triangle): Corporate action effective date. Hovering shows ratio (e.g., 1:1 bonus or 2:1 split).
- **NSE Announcements** ("A" marker, white square): Material announcements from NSE (board meetings, merger discussions, etc.) loaded from the local announcements database.
- **User trade entries** (triangles with ₹ annotation): Entry and exit dates from the user's journal for this ticker. Entry = green upward triangle; exit = red downward triangle. Hovering shows P&L in ₹ and %.
- **Atlas buy/sell dates** (from the user's portfolio history — the dates on which Atlas signaled a buy or sell for this stock): Small circle markers.

All marker types are individually togglable from the "Events" button in the chart toolbar, which opens a `QMenu` with checkboxes.

### 9.8 Atlas Price Level Overlays

When "Atlas Levels" is toggled on, the chart overlays the following horizontal lines with labels (computed from local data):

- **50-day SMA** (yellow dashed line): The primary trend filter used in Atlas's `use_sma_filter`. Label: "SMA50 ₹X,XXX"
- **200-day SMA** (orange dashed line): Long-term trend context. Label: "SMA200 ₹X,XXX"
- **52-Week High** (bright green dotted line): Resistance/breakout level. Label: "52W High ₹X,XXX"
- **52-Week Low** (bright red dotted line): Support/crash level. Label: "52W Low ₹X,XXX"
- **User's entry price** (white dashed line, if this ticker is in the portfolio): Label: "Entry ₹X,XXX"
- **GTT Stop level** (red solid thin line, 12% below entry): Label: "GTT Stop ₹X,XXX (12%)"
- **ADV30 line**: Not a price line — shown as a horizontal reference on the volume sub-pane showing the 30-day average daily value in crore.

### 9.9 Chart Crosshair

A synchronized crosshair: vertical line snapping to the nearest candle date, horizontal line following the cursor price. The crosshair values are shown in a compact data bar at the top of the chart (floating text boxes over the price pane, not a separate row):

- Date (DD-Mon-YYYY)
- O: ₹X,XXX.XX  H: ₹X,XXX.XX  L: ₹X,XXX.XX  C: ₹X,XXX.XX  V: X.X cr sh  Val: ₹X.X cr

Values for all active indicators at that date are also shown in the data bar (e.g., "RSI: 58.3  MACD: +2.1  SMA50: ₹2,847").

### 9.10 Comparison Overlay

The user can add one or more comparison tickers. Each is plotted as a percentage-normalized line (anchored to 0% at the left edge of the visible range) in a distinct color, overlaid on the price pane. The primary ticker is also shown as a % line when comparison mode is active (optional toggle). Up to 4 comparison tickers.

Useful patterns: RELIANCE vs NIFTY50 vs NIFTYENERGY; a stock vs its sector ETF (e.g., HDFCBANK vs NIFTYBANK index).

### 9.11 Replay Mode

A bar-by-bar study mode for practice and historical analysis. Activated from the toolbar "Replay" button.

On activation: user selects a start date from a `QDateEdit`. The chart truncates at that date (all subsequent bars hidden). An amber frame border appears around the entire chart panel to indicate replay mode.

Controls appear in a mini toolbar: Play/Pause (auto-advance), Step Forward (one bar), Step Back (one bar), Speed (1×, 2×, 5×, 10×). All indicators recalculate correctly on each step. The user can draw on the chart in replay mode. Exiting replay mode (Escape or the X button in the replay toolbar) restores live data.

### 9.12 Chart Templates

Named chart configurations (indicator set + display settings) saved to SQLite. Applied with one click from a "Templates" dropdown in the chart toolbar.

**Bundled templates to ship:**
- "Atlas Base" — SMA 20/50/200, Volume, RSI 14
- "Momentum Swing" — EMA 8/21/50, VWAP, RSI 14, MACD
- "Delivery Analysis" — Volume, Delivery %, RSI 14
- "Weekly Trend" — Ichimoku Cloud, Volume (on Weekly timeframe)
- "Clean Price" — No indicators, just price candles

---

## 10. Module 05 — Watchlists

### 10.1 Watchlist Management

Multiple named watchlists stored in SQLite. A "Universe" watchlist is always present and is populated from `universe_nifty500.csv` (read-only, auto-synced). A "Nifty 50" watchlist is also always present (the 50 largest caps in the universe — can be manually maintained or auto-populated from a filter).

User-created watchlists: create, rename, duplicate, delete. Maximum 20 user watchlists. Tickers can appear in multiple watchlists.

### 10.2 Watchlist Panel UI

A `QDockWidget` containing a `QTableWidget` or `QTreeWidget` styled as a dense data table.

Columns (configurable via right-click on column header → "Customize Columns"):
- Symbol (monospace, bold)
- Company Name (truncated)
- Last ₹ (live if available, else EOD)
- Chg ₹
- Chg %
- Volume (in lakh shares)
- Val (₹ cr traded today)
- ADV30 (₹ cr, 30-day average daily value)
- ADV Ratio (today/ADV30)
- 52W High / Low (as a range bar in the cell — a tiny horizontal bar)
- RSI 14
- Atlas Score (if computed)
- Atlas Rank (out of universe)
- Sector
- Alerts (bell icon, filled if any alert active for this ticker)
- Notes (free text, user-editable inline)

Clicking a row selects the ticker and pushes it to all panels in the active link group. Right-click context menu: Open Chart | Open Quote | Open News | Open Fundamentals | Add to Atlas Signal | Create Alert | Remove from Watchlist | Copy Symbol.

### 10.3 Watchlist Filtering and Sorting

Sort by any column (click column header). A filter bar (QLineEdit above the table) filters rows by symbol or company name substring. A sector filter dropdown (QComboBox) shows only stocks in a selected sector.

### 10.4 Import/Export

Import: paste a comma or newline separated list of NSE symbols in a `QInputDialog`; each is looked up in the universe and added. Or import from a CSV file (column named "symbol" is required).

Export: right-click → "Export Watchlist" → saves the watchlist with all displayed column values to CSV in the `reports/` folder.

### 10.5 Alert Badges

Each row in the watchlist shows an alert bell icon in the Alerts column. If any active alert exists for that ticker (see Module 14), the icon is filled/colored. Clicking it opens the alert creation dialog pre-filled with that ticker.

---

## 11. Module 06 — Screener & Discovery

### 11.1 Overview

The screener queries the loaded `PriceData` and `AlphaData` in-memory (no external API calls) and returns a filtered, ranked list of stocks from the universe. This is essentially the Atlas screener plus additional filters exposed in a GUI. Since all data is local, screener results appear in < 1 second for most filter combinations.

Fundamental and valuation data (P/E, EPS, etc.) requires a separately loaded fundamentals database (see Module 08). If the fundamentals database is not loaded, those filter rows are greyed out with a tooltip "Fundamentals DB not loaded — see Settings."

### 11.2 Universe Selector

At the top of the screener panel:
- **Nifty 500** (default — all enabled symbols from universe CSV)
- **Nifty 50** (top 50 by market cap — requires market cap data in the fundamentals DB)
- **Nifty Next 50**
- **Nifty Midcap 150**
- **Nifty Smallcap 250**
- **My Watchlist** (screens only tickers in a selected watchlist)
- **Custom** (user pastes or imports a ticker list)

### 11.3 Filter Categories and Fields

All filter fields have a min/max range with a `QDoubleSpinBox` pair, or a specific dropdown for categorical filters. Each filter has an enable/disable `QCheckBox`.

**Price & Liquidity Filters:**
- Last Price (₹ min/max)
- Market Cap (₹ cr min/max)
- ADV30 — 30-day average daily traded value (₹ cr min/max; default shown: ≥ 15 cr, which is the Atlas liquidity threshold)
- Volume today (in lakh shares, min/max)
- ADV Ratio (today / ADV30, min/max; e.g., > 2.0 for unusual volume)
- Face Value (dropdown: ₹1 / ₹2 / ₹5 / ₹10 / Any)
- Series filter (EQ only / All)

**Technical Momentum Filters (computed from local OHLCV):**
- Day change % (min/max)
- Week return % (5-day, min/max)
- Month return % (21-day, min/max)
- 60-day return % (Atlas momentum window, min/max)
- 120-day return % (Atlas momentum window, min/max)
- 200-day return % (Atlas momentum window, min/max)
- YTD return %
- 52W High proximity (price within N% of 52W high; e.g., within 5%)
- 52W Low proximity (price within N% of 52W low)
- Price vs SMA 50 (above/below dropdown; distance % min/max)
- Price vs SMA 200 (above/below dropdown; distance % min/max)
- Price vs EMA 20
- SMA 50 vs SMA 200 (golden cross: SMA50 above SMA200; or death cross: below)
- RSI 14 (min/max)
- Stochastic %K (min/max)
- MACD histogram sign (positive/negative toggle)
- ATR % — ATR14 as % of price (min/max; useful for volatility screening)
- Historical Volatility 20D annualized % (min/max)
- Beta vs Nifty 50 (min/max)

**Atlas-Specific Filters:**
- Atlas Score (min/max — the raw momentum composite score)
- Atlas Rank (1 through N — e.g., rank ≤ 20 for top 20)
- Above 50-day SMA (yes/no toggle — matches `use_sma_filter` in AtlasConfig)
- ADV30 threshold filter (show only stocks passing the Atlas liquidity threshold)

**Sector / Classification Filters:**
- Sector (multi-select `QListWidget` — select one or more sectors from the GICS/NSE sector list in the universe file)
- Index membership (checkboxes: Nifty 50 | Nifty Next 50 | Nifty Midcap 150 | Nifty Bank)

**Delivery Data Filters (from bhavcopy, where available):**
- Delivery % today (min/max)
- Delivery % vs 20-day average delivery % (delivery ratio, min/max; > 1.5 = unusually high delivery)

**Valuation Filters (from Fundamentals DB):**
- P/E TTM (min/max; exclude negative P/E option)
- P/B (min/max)
- EV/EBITDA (min/max)
- Price/Sales TTM (min/max)
- Dividend Yield % (min/max)

**Fundamental Quality Filters (from Fundamentals DB):**
- Revenue growth YoY % (last quarter or TTM)
- EPS growth YoY %
- Net Profit Margin %
- Return on Equity % (ROE)
- Debt-to-Equity ratio (min/max)
- Promoter Holding % (min/max)
- FII Holding % (min/max)
- Pledge % of promoter shares (max — high pledge = risk; e.g., < 10%)

**Event Filters:**
- Earnings within N days (upcoming)
- Earnings in last N days (recently reported)
- Ex-dividend within N days
- Bonus/split announced (yes/no)

### 11.4 Filter Summary Line

A `QLabel` above the results table showing all active filters in plain text (e.g., "RSI between 40–65 AND ADV30 ≥ ₹15 cr AND Above SMA50 AND Sector: Financials, IT"). This helps the user verify their intent.

### 11.5 Screener Results Table

A virtualized `QTableWidget` (or a `QAbstractItemModel` backed custom view for better performance) showing up to 1,000 rows. Columns match those configurable in the watchlist (see Module 05, 10.2), plus any filter fields that are active (automatically added as columns when a filter is enabled).

Results count in header (e.g., "198 stocks match").

Row interaction: click → push to link group. Right-click: context menu identical to watchlist right-click. Multi-select (Shift+Click / Ctrl+Click) → right-click → "Add selected to watchlist."

Sort by any column header (click to sort ascending; click again to sort descending).

### 11.6 Built-In Screener Presets

A `QComboBox` at the top of the screener panel loads named presets. The following are built-in (not user-editable, but the user can save their own presets on top):

- **"Atlas BUY Candidates"** — ADV30 ≥ 15 cr, Above SMA50, RSI 50–75, 60D return > 5%, Score ranked top 30
- **"Atlas WATCH (Below Rank 120)"** — ADV30 ≥ 15 cr, Atlas Rank > 120 (approaching exit threshold)
- **"Volume Spikes"** — ADV Ratio > 2.5, Price > 50-SMA, Volume today > 5 lakh shares
- **"Momentum Breakouts"** — Price within 2% of 52W high, ADV Ratio > 1.5, RSI 55–75
- **"Oversold Bounces"** — RSI < 30, Price > ₹50, ADV30 ≥ 15 cr
- **"High Delivery Today"** — Delivery % > 60%, ADV Ratio > 1.5
- **"Sector Leaders"** — Top 2 by Atlas Score per sector (sector cap logic from Atlas)
- **"Low Pledge Quality"** — Pledge % < 5%, ROE > 12%, P/E < 25 (requires Fundamentals DB)
- **"Earnings Watch"** — Earnings within 7 days, IV Rank > 50 if F&O data available
- **"Strong Promoter Holdings"** — Promoter Holding > 50%, FII Holding > 10%, Debt/Equity < 0.5

User-saved presets are stored in SQLite with the filter JSON. The preset dropdown shows built-in presets first, then a separator, then user presets.

### 11.7 Real-Time Scan (Friday Mode)

A "Scan" button that re-runs the active filters against the latest `PriceData` state. Since data is local EOD, this is instantaneous. After a daily data download, the user clicks Scan to see fresh results. There is no "auto-refresh" for the screener since there is no real-time feed. On the Friday workflow, the user downloads data at 3:15 PM, then scans.

---

## 12. Module 07 — News, Filings & Announcements

### 12.1 Data Sources for Indian Market News

AtlasTerminal sources news and announcements from the following, in priority order:

1. **NSE Corporate Announcements** — NSE publishes XML/JSON feeds of corporate announcements (board meetings, results, dividends, buybacks, mergers). Fetched from `https://www.nseindia.com/api/corp-info?symbol=SYMBOL&corpType=announcements`. Requires a proper session/cookie (NSE rate-limits headless requests). The developer must implement a NSE session manager with a cookie refresh mechanism (see data architecture section).

2. **BSE Announcements** — BSE's corporate announcement feed at `https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?`. Similar structure to NSE.

3. **MoneyControl / Economic Times / Business Standard** — Financial news sources that can be RSS-scraped (no paywalled content). RSS feeds exist for: ET Markets (`economictimes.indiatimes.com/markets/rss`), Business Standard (`business-standard.com/rss`).

4. **Screener.in / Ticker Tape** — Do not scrape without API keys. Mention in settings as "bring your own RSS URL" for additional sources.

5. **SEBI Announcements** — SEBI's enforcement actions, new regulations, and circulars from `https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFbo=yes` (or RSS equivalents).

All fetched news is stored in the SQLite `news_items` table (ticker, headline, source, published_at, url, sentiment_score, category). The news panel reads from this table. Background fetching via `QRunnable`.

### 12.2 NSE Announcements Feed

This is the highest-priority news source. Implementation details:

The NSE website requires browser-like headers and a valid `nsit` session cookie obtained from `https://www.nseindia.com`. The `data_fetcher.py` `BHAVCOPY_HEADERS` approach (browser User-Agent) is used. A `NSESession` class manages the session with automatic cookie refresh every 15 minutes.

The NSE announcements API returns structured JSON with fields: `symbol`, `desc` (announcement description), `attchmntFile` (PDF URL), `exchdisstime` (exchange dissemination time). Parse these and insert into the local news DB.

The fetch strategy: on app startup, fetch announcements for all watchlist tickers from the past 7 days. During market hours, refresh every 10 minutes for all watchlist tickers. After market close, refresh once.

### 12.3 News Panel UI

A `QDockWidget` containing a `QListWidget` (custom delegate for rich rows) showing news items.

Each news item row in the list shows (custom `QListWidgetItem` delegate):
- Source logo (16px icon: NSE, BSE, ET, BS badge)
- Headline (truncated to 2 lines, with ellipsis)
- Relative timestamp (e.g., "23 min ago") with absolute timestamp on hover
- Sentiment badge: UP (green arrow) / DOWN (red arrow) / NEUTRAL (gray dash) — from a keyword-based classifier (not a full NLP model — use a weighted keyword list approach that runs synchronously and is Nuitka-compatible)
- Category badge: Results | Dividend | Board Meeting | Bonus/Split | Merger | Regulatory | Macro

**Category keyword classifier for sentiment (implemented as a simple Python dict lookup):**
- Positive keywords: "profit", "dividend", "buyback", "order win", "expansion", "rating upgrade", "board approves", "revised upward", "beat estimates"
- Negative keywords: "loss", "default", "SEBI notice", "probe", "penalty", "rating downgrade", "revised downward", "missed estimates", "delist"
- This runs in < 1ms per headline and is fully Nuitka-compatible.

Clicking a news item opens the full text in a side panel (`QTextBrowser` widget) showing the announcement text. If the announcement has a PDF attachment (NSE corporate actions often do), a "Open PDF" button opens it in the default system PDF viewer via `os.startfile()`.

### 12.4 News Filtering

A compact filter row above the news list:
- Ticker filter: "All" (market-wide) or current linked ticker
- Source filter: NSE | BSE | ET | BS | All
- Category filter: multi-select
- Time filter: Last 1 hour / 6 hours / 24 hours / 7 days / 30 days
- Keyword search (QLineEdit, filters headlines in real time)

### 12.5 NSE Quarterly Results

NSE publishes quarterly financial results announcements as structured data. When a results announcement is fetched, the system attempts to extract key financial fields from the announcement text using a regex-based extractor:

- Net Revenue (₹ cr)
- Net Profit (₹ cr)
- EPS (₹)
- vs Previous Quarter (QoQ %)
- vs Same Quarter Last Year (YoY %)

These extracted values are stored in the `earnings_history` SQLite table and used by the Fundamentals panel and Catalyst Calendar. This is best-effort extraction — the developer must handle failure gracefully (store raw text when structured extraction fails).

### 12.6 SEBI Action Monitor

A separate tab within the news panel (or a sub-filter option) showing recent SEBI enforcement actions, insider trading cases, and new circular publications. Source: SEBI RSS or periodic HTML fetch. This is a P2 feature. Store in the same `news_items` table with `source='SEBI'` and `ticker=NULL`.

---

## 13. Module 08 — Fundamentals & Financial Analysis

### 13.1 Fundamentals Data Source

Fundamentals data for Indian equities is harder to get programmatically than for US equities. The following approach is used:

**Primary source: Screener.in export** — Screener.in allows CSV export of financial statements for individual companies. The user can manually download these CSVs for their watchlist stocks and import them into AtlasTerminal via the Data Download Manager (Module 24). The import parser handles Screener.in's specific CSV format.

**Secondary source: yfinance** — `yf.Ticker("SYMBOL.NS").info` returns a dict of fundamental fields including market cap, P/E, EPS, dividend yield, etc. This is fetched on-demand when the Fundamentals panel is opened for a ticker and no locally cached data exists. Results cached in SQLite for 24 hours.

**Tertiary source: NSE / BSE API** — Key fields like face value, lot size (for F&O), and promoter holding can be fetched from NSE's company info API.

The fundamentals data architecture: a `FundamentalsDB` class manages the `fundamentals` SQLite table and provides `get_fundamentals(ticker)` returning a unified dict regardless of which source provided the data.

### 13.2 Company Overview Panel (DES analog)

Header block: same as security header (section 8.2), plus:
- Registered office address
- Incorporation date
- CIN (Corporate Identity Number)
- Promoter group name (e.g., "Tata Sons", "HDFC Ltd")
- NSE listing date
- ISIN code
- NSE/BSE scrip code

Business description: 3–5 paragraphs from yfinance's `longBusinessSummary` field (or a manually imported text file). Truncated with "Show more" toggle.

Key executives table: Name, Title, from NSE's company page data. Where available. Source: `yf.Ticker().info["companyOfficers"]` or manually entered.

Capital structure:
- Authorized share capital (from BSE filing)
- Issued/Subscribed share capital
- Face Value
- Total shares outstanding
- Free float shares
- Free float market cap

Index memberships: Which Nifty indices this stock is a constituent of.

### 13.3 Financial Statements

Three tabs: Income Statement | Balance Sheet | Cash Flow

**Display options:**
- Annual (last 5 years) or Quarterly (last 8 quarters)
- Values in ₹ crore (always — no lakh notation in financial statements)
- Show as absolute values or as % of Revenue (common-size)

**Income Statement fields (all values ₹ cr):**
All standard income statement items, adapted to Indian GAAP / Ind AS terminology:
- Revenue from Operations (Net)
- Other Income
- Total Income
- Cost of Materials Consumed
- Purchases of Stock-in-Trade
- Changes in Inventories
- Employee Benefits Expense
- Finance Costs
- Depreciation and Amortization
- Other Expenses
- Total Expenses
- Profit Before Exceptional Items and Tax (PBIT)
- Exceptional Items (if any)
- Profit Before Tax (PBT)
- Tax Expense (Current Tax + Deferred Tax)
- Profit After Tax (PAT) / Net Profit
- Earnings Per Share — Basic ₹
- Earnings Per Share — Diluted ₹
- EBITDA (calculated: PAT + tax + finance costs + D&A)
- EBITDA Margin %

**Balance Sheet fields (₹ cr):**
Assets side: Fixed Assets (Tangible, Intangible), Capital WIP, Non-current Investments, Long-term Loans and Advances, Other Non-current Assets, Current Assets (Inventories, Trade Receivables, Cash and Bank, Short-term Investments, Other Current Assets)

Liabilities side: Share Capital, Reserves and Surplus, Long-term Borrowings, Deferred Tax Liability, Other Long-term Liabilities, Short-term Borrowings, Trade Payables, Other Current Liabilities, Short-term Provisions

**Cash Flow Statement fields (₹ cr):**
Operating, Investing, Financing activities — Indian companies report these under Ind AS with slightly different labeling vs IFRS. Use the actual line item names from the imported data without remapping.

**Inline sparkline:** Clicking a row (e.g., "Revenue from Operations") shows a tiny bar chart inline in the row or as a tooltip showing that metric's trend across the displayed periods.

### 13.4 Valuation History

For each valuation multiple (P/E, P/B, EV/EBITDA, Price/Sales), a PyQtGraph line chart shows the trailing value over the past 5 years. The current value is marked; the 5-year average and ±1 standard deviation bands are shown as horizontal dashed lines. This requires historical price data (available locally) and historical EPS/book value (requires fundamentals import or yfinance historical earnings).

### 13.5 Peer Comparison

A table comparing the current stock against its GICS/NSE industry peers. The peer list defaults to the sector peers in the universe file. The user can add/remove peers.

Columns: Symbol, Mkt Cap (₹ cr), P/E, P/B, EV/EBITDA, Gross Margin %, PAT Margin %, ROE %, Revenue Growth YoY %, EPS Growth YoY %, Debt/Equity, Dividend Yield %, Promoter Holding %.

Current ticker row highlighted. Cells color-coded relative to peer median.

### 13.6 Promoter Holding Trend

A bar chart showing the promoter holding % over the last 8 quarters (from quarterly shareholding pattern data — available from BSE/NSE). Decreasing promoter holding is a risk signal. Increasing = bullish sign. Overlay the pledge % as a line on the same chart.

---

## 14. Module 09 — NSE F&O Analytics

### 14.1 Overview and Data Source

NSE publishes daily F&O Bhavcopy files (equity derivatives data: futures and options OHLC, OI, volume). These are available from `https://archives.nseindia.com/content/historical/DERIVATIVES/`. The `data_fetcher.py` must be extended with a `download_fo_bhavcopy()` function analogous to `download_bhavcopy_history()` for equity.

F&O data is end-of-day only. No real-time options chain without an exchange feed or a paid API (Upstox / Zerodha Kite Connect data API). The developer should note this limitation clearly in the UI: "F&O data is end-of-day from NSE. Last updated: [date]."

For near-real-time options data (P2 feature), the developer can integrate with the Upstox historical data API or a similar SEBI-registered data provider's API if the user provides their own API key.

### 14.2 NSE F&O Eligible Universe

Not all stocks are available in the F&O segment. NSE publishes a list of F&O-eligible stocks (currently ~200 stocks). The universe file should include a `fo_enabled` column (true/false). The screener's F&O filters only apply to stocks with `fo_enabled=true`.

### 14.3 Options Chain Display

For F&O-eligible stocks, an "Options Chain" tab or panel showing the end-of-day options chain for the current ticker and selected expiry.

**Expiry selector:** NSE has weekly expiries (Thursday for indices; monthly for stocks). A dropdown shows available expiries sorted by date. Label format: "25-Jul-26 (10 DTE)".

**Chain layout:** Standard two-column (calls left, puts right) with strike in center. Columns per side:
- OI (Open Interest, in number of contracts)
- OI Change (vs previous day)
- Volume (contracts today)
- LTP (Last Trade Price, ₹)
- Change ₹
- Bid / Ask (last known, EOD)
- IV (Implied Volatility %) — computed using Black-Scholes with the last OI-weighted mid price
- Delta (computed)
- Gamma (computed)
- Theta (computed per day, in ₹)
- Vega (computed)

**ATM strike highlighted** (current spot price is between two strikes — highlight the one closest to spot). ITM strikes for calls (strike < spot) and ITM strikes for puts (strike > spot) shown with a distinct background.

**Max Pain:** Computed strike price at which total open interest value at expiry is minimized. Shown as a labeled line on the OI chart (see 14.5) and as a number at the top of the chain.

**PCR (Put-Call Ratio):** Displayed at the top: total put OI / total call OI. High PCR > 1.2 = bearish sentiment; PCR < 0.8 = bullish sentiment (contrarian indicator).

### 14.4 F&O Snapshot for a Stock

For any F&O-enabled stock, a compact F&O summary card (can be shown in the security header or as a separate tab):

- Lot size (e.g., 500 shares per lot for RELIANCE)
- Market lot value (₹) = lot size × spot price
- Near-month futures price, basis (futures - spot), annualized cost of carry %
- Total futures OI across all expiries (in contracts)
- Futures OI change (vs previous day, % and absolute)
- Futures volume today (contracts)
- Near-month ATM IV (implied volatility of ATM call or put)
- IV Rank — current IV vs 52-week IV range (0–100 scale)
- IV Percentile — % of days in past 52 weeks where IV was lower than today

### 14.5 OI Chart (Open Interest Visualization)

A PyQtGraph bar chart showing call OI vs put OI at each strike for the selected expiry:
- X-axis: strike prices, centered on ATM
- Y-axis: open interest in contracts
- Calls as green bars (left side of each strike pair or separate color)
- Puts as red bars

Large OI concentrations at specific strikes = "options walls" (resistance for calls, support for puts). This is one of the most useful F&O tools for swing traders.

An "OI Change" view toggle: instead of absolute OI, shows the day's change in OI (new longs/shorts vs liquidation).

### 14.6 F&O Activity Screener

A standalone screener tab within the F&O panel showing all F&O-eligible stocks ranked by:
- Highest OI buildup (OI increase % today)
- Highest PCR
- Highest futures basis (cost of carry)
- Highest IV Rank (approaching earnings or event)
- Long buildup (OI increase + price increase)
- Short buildup (OI increase + price decrease)
- Long unwinding (OI decrease + price decrease)
- Short covering (OI decrease + price increase)

This requires the full F&O Bhavcopy loaded for all eligible stocks — a heavier data load. This is a P2 feature.

---

## 15. Module 10 — Macro & Economic Dashboard

### 15.1 Indian Macro Calendar

A calendar view of key Indian economic data releases and RBI events. The developer maintains a static reference table of recurring release dates (e.g., CPI is released on the 12th-14th of each month; IIP is released on the 12th of each month with a 6-week lag). Store these as recurring entries in the SQLite calendar table; user can manually add or correct dates.

**Key Indian economic events covered:**

- RBI Monetary Policy Committee (MPC) meetings and decisions (6 per year): repo rate decision, CRR, SLR, monetary stance (accommodative/neutral/withdrawal of accommodation/hawkish)
- CPI Inflation (All India — Combined, month-over-month and year-over-year)
- WPI Inflation (Wholesale Price Index)
- IIP (Index of Industrial Production — manufacturing, mining, electricity)
- GDP Growth Rate (quarterly, advance and final estimates)
- Fiscal Deficit data (monthly from CGA)
- India PMI Manufacturing (HSBC/S&P, monthly)
- India PMI Services (HSBC/S&P, monthly)
- India PMI Composite
- Trade Balance and Current Account data (quarterly)
- Foreign Exchange Reserves (weekly, from RBI)
- Bank Credit Growth (fortnightly, from RBI)
- GST Collection (monthly revenue data from Finance Ministry)

**Data sources for actual values:**
- MOSPI (Ministry of Statistics) website for CPI, IIP, GDP
- RBI website for FX reserves, bank credit, MPC decisions
- These are scraped on a weekly basis and stored in SQLite. The user may also manually update actual values after release.

**Event calendar display:** Same layout as Module 13 (Catalyst Calendar) — each event shows: Date | Time (IST) | Event Name | Importance (High/Medium/Low) | Previous Value | Consensus Estimate (if available) | Actual (post-release).

### 15.2 RBI Dashboard

A dedicated view for RBI-related data:

- Current Repo Rate (with history chart — last 5 years, showing each rate change event as a step)
- Reverse Repo Rate
- CRR (Cash Reserve Ratio)
- SLR (Statutory Liquidity Ratio)
- Standing Deposit Facility (SDF) Rate
- Marginal Standing Facility (MSF) Rate
- The "liquidity corridor" visualization (a horizontal band showing SDF floor and MSF ceiling, with the effective overnight rate plotted within it)
- Next MPC meeting date (with countdown in days)
- Last MPC decision: "HOLD / CUT / HIKE by 25 bps — unanimous/split vote" with the vote breakdown

Source: RBI's policy announcements are published on `rbi.org.in`. Fetch post-meeting statement and extract decision programmatically. Store in SQLite.

### 15.3 India Macro Indicator Charts

A "Macro Charts" view — a scrollable grid of PyQtGraph line charts showing historical time series for key Indian indicators. Each chart can be opened full-screen by double-clicking.

Charts available:
- CPI Inflation (YoY %) — with RBI's target band (2–6%) shown as a horizontal shaded region
- Core CPI (excluding food and fuel)
- WPI Inflation (YoY %)
- GDP Growth Rate (quarterly, YoY %)
- IIP Growth (MoM % and YoY %)
- Repo Rate history
- India VIX (30-day chart from yfinance)
- USD/INR exchange rate (from yfinance)
- Nifty 50 price with CPI overlay (dual-axis)
- FII equity flow (cumulative YTD — from Module 17 data)
- GST monthly collections (₹ lakh cr)
- India's Forex reserves ($ billion)
- India PMI Manufacturing (50 = expansion threshold shown as horizontal line)

### 15.4 Global Macro Sidebar

A compact panel showing global macro indicators relevant to Indian markets:

- US Fed Funds Rate (current target range)
- US 10-Year Treasury Yield
- DXY (US Dollar Index) — critical for FII flow: strong USD → FII outflows from India
- WTI / Brent Crude Oil (India is oil-import-dependent; oil price directly affects CAD and margins)
- Gold price (MCX, ₹/10g)
- US S&P 500 (day %)
- MSCI Emerging Markets Index (day %)
- Hang Seng Index (day %) — proxy for Asia sentiment
- SGX Nifty (Singapore-listed Nifty futures — leading indicator for India's open)

Source: yfinance for all. Refreshed every 5 minutes via QTimer during market hours (9:00–15:30 IST). Cached in-memory with timestamp.

---

## 16. Module 11 — Portfolio & Manual Trade Manager

### 16.1 Core Design Principle

AtlasTerminal does NOT connect to brokers. It manages a local portfolio record that the user keeps synchronized with their actual Groww/Zerodha account. The user is responsible for updating the portfolio after every trade. The application helps by making the update process friction-free and by validating the changes against the Atlas signal.

### 16.2 Portfolio Data Model

The portfolio is stored in the SQLite `portfolio` table (replaces `current_portfolio.csv`) with the following columns:

```
symbol TEXT
quantity INTEGER
avg_price REAL
entry_date TEXT (ISO date)
gtt_stop REAL (₹ price level for GTT stop order)
target_price REAL (optional — user's planned exit target)
strategy_tag TEXT (e.g., "Atlas Monthly", "Discretionary")
notes TEXT
```

The existing `current_portfolio.csv` is automatically imported on first launch and kept as an export target (CSV export always available from the portfolio panel).

### 16.3 Portfolio Panel UI

A `QDockWidget` containing a `QTableWidget` with one row per open position.

Columns:
- Symbol
- Company Name
- Qty (shares)
- Avg Cost (₹)
- Last Price (₹) — from EOD data or live quote cache
- Market Value (₹ cr) = Qty × Last Price
- Unrealized P&L (₹) = Qty × (Last - Avg Cost)
- Unrealized P&L % = (Last - Avg Cost) / Avg Cost × 100
- % of Portfolio = Market Value / Total Portfolio Value × 100
- Entry Date
- Holding Days = today − Entry Date
- GTT Stop (₹) — user-set level
- Distance from GTT Stop % = (Last − GTT Stop) / Last × 100. Shown in red if < 5% (approaching stop)
- Target Price (₹, optional)
- Upside to Target % = (Target − Last) / Last × 100
- Atlas Rank (current rank in Atlas ranked universe)
- Sector
- 30D Return %
- 60D Return %

**Portfolio Summary Header** (above the table, compact horizontal strip):
- Total Portfolio Value: ₹X.XX lakh / ₹X.XX cr
- Unrealized P&L: ₹X.XX lakh (X.X%)
- Realized P&L (MTD): ₹X.XX lakh
- Realized P&L (YTD): ₹X.XX lakh
- Number of positions: X
- Cash (user-entered estimated available cash): ₹X.XX lakh
- Total portfolio peak value (user-entered, for DD calculation): ₹X.XX lakh
- Current drawdown from peak: X.X% (color-coded: amber > 10%, red > 20%)

### 16.4 Manual Trade Entry

Adding a new position or recording a trade is done via a `QDialog` with the following fields:

- Ticker (QLineEdit with autocomplete from universe)
- Side: BUY / SELL (QRadioButton)
- Quantity (QSpinBox)
- Executed Price ₹ (QDoubleSpinBox)
- Trade Date (QDateEdit, defaults to today)
- Strategy Tag (QComboBox: Atlas Monthly | Discretionary | Earnings Play | Custom)
- Notes (QTextEdit, optional)
- GTT Stop Level ₹ (QDoubleSpinBox, pre-filled with 12%-below-entry calculation when side = BUY and strategy = Atlas)
- Brokerage & Charges ₹ (QDoubleSpinBox, pre-filled with STT + brokerage estimate)

When a SELL is entered for an existing position, the dialog auto-fills the quantity (from current holdings) and computes: Realized P&L, Holding period (days), STCG or LTCG classification (STCG if < 12 months; LTCG if ≥ 12 months), estimated tax liability, and net P&L after tax. These are shown in a summary box below the form before the user confirms.

### 16.5 Trade Costs Estimator

Every trade entry auto-computes estimated costs using the following standard NSE/SEBI charges (configurable in Settings):

- **STT (Securities Transaction Tax):** 0.1% on turnover (buy + sell)
- **Exchange Transaction Charges (NSE):** 0.00322% on turnover (equity delivery)
- **SEBI Turnover Fee:** 0.0001% on turnover
- **Stamp Duty:** 0.015% on buy-side only (delivery)
- **GST:** 18% on brokerage + exchange charges
- **Brokerage:** Zerodha/Groww = ₹0 for delivery equity (zero brokerage). User can configure their broker's rate if different.
- **Total friction estimate** = sum of above, shown in ₹ and as % of trade value

These match the 0.46% round-trip rate used in AtlasConfig's `trade_cost_rate`.

### 16.6 GTT Stop Tracker

A dedicated sub-view within the Portfolio panel (accessible as a tab or below the main table) showing all active GTT stop orders:

For each position:
- Symbol
- Entry Price ₹
- GTT Stop ₹ (12% below entry by default)
- Current Price ₹
- Distance to Stop ₹ and %
- GTT Stop Status: SAFE (> 10% above stop), WATCH (5–10% above stop, amber), ALERT (< 5% above stop, red)

Sorting the table by "Distance to Stop %" ascending shows the most at-risk positions first.

The GTT stop levels are informational — the user must manually enter or update them in Groww/Zerodha. This panel serves as a reference and an alert trigger (see Module 14).

### 16.7 Trade History

A separate tab in the Portfolio panel showing all closed trades (from journal entries with EXIT records):

Columns: Date Closed | Symbol | Side (originally) | Qty | Avg Buy ₹ | Sell ₹ | Gross P&L ₹ | Gross P&L % | Holding Days | Tax (STCG/LTCG) | Net P&L ₹ | Strategy Tag | Reason (Atlas exit reason if applicable)

Filter by: Date range | Symbol | Strategy Tag | Outcome (profit/loss)

Export to CSV button.

### 16.8 P&L Analytics

A "Performance" tab showing:

**Equity curve:** PyQtGraph `PlotWidget` line chart of cumulative portfolio value over time. X-axis: date; Y-axis: ₹ total value. Requires the user to have maintained portfolio history entries (each time the portfolio is updated, a snapshot is saved to SQLite). The first portfolio snapshot is taken on first launch.

**Monthly P&L bar chart:** Bars show realized P&L per month (₹). Current month is updated as positions close.

**Key stats computed from closed trade history:**
- Total trades (round trips)
- Win rate (% profitable)
- Average profit on winning trades (₹ and %)
- Average loss on losing trades (₹ and %)
- Profit Factor = Gross Profit / Gross Loss
- Maximum consecutive wins / losses
- Largest single win (₹)
- Largest single loss (₹)
- Average holding period (days) for winners vs. losers
- Estimated STCG paid YTD
- Estimated LTCG paid YTD
- Net return after tax YTD %

---

## 17. Module 12 — Risk Analytics

### 17.1 Portfolio Risk Dashboard

A panel showing aggregate portfolio risk metrics computed from the local `PriceData` and the current portfolio holdings.

**Market Exposure:**
- Net Beta (weighted average beta of all positions vs Nifty 50, computed from 52-week daily returns in PriceData)
- Nifty 50 Beta-adjusted Exposure: "You have the equivalent of ₹X.X lakh in Nifty 50 beta exposure" (net portfolio value × weighted beta)
- Sector concentration: horizontal bar chart showing % of portfolio by sector. Warning flag (amber) if any sector > 40% of portfolio.
- Number of positions / Target slots ratio (e.g., "7/10 slots filled")

**Correlation Matrix:**
- A PyQtGraph heatmap showing pairwise 60-day rolling return correlations between all held positions.
- Cells colored from green (-1.0, negative correlation) through white (0.0) to red (+1.0, positive correlation).
- Value displayed in each cell.
- High correlations within a "diversified" portfolio mean it is effectively less diversified than it appears. Flag any pair with correlation > 0.8.

**Atlas Regime Validation:**
- Current market breadth (% Nifty 500 stocks above 50-day SMA, computed from PriceData)
- Current regime: FULL_RISK / DEFENSIVE / LIQUIDATE
- Target slots for current regime
- Mismatch warning: if the user holds 10 positions but breadth says DEFENSIVE (target = 5), show a red warning: "REGIME MISMATCH: Hold 10 positions, but DEFENSIVE regime targets 5. Run Atlas Signal to generate sell recommendations."

**Portfolio Drawdown:**
- Current drawdown from user-entered peak value: ₹ and %
- Atlas DD circuit breaker level: 30% (from AtlasConfig.portfolio_dd_stop)
- Remaining buffer before circuit breaker triggers: ₹ and %
- If drawdown > 20%: amber warning. If drawdown > 30%: red warning with "LIQUIDATE ALL HOLDINGS" recommendation text.

**Individual Position Risk:**
- Table of all positions showing: unrealized P&L %, distance to 12% catastrophe stop, estimated stop-loss value (₹).
- Row colored red if stop is within 3% of current price.
- "If all stops are hit today" scenario: total estimated loss in ₹.

### 17.2 Position Sizing Calculator

A utility widget (accessible from the Portfolio panel or as a floating `QDialog` via `Ctrl+Shift+S`):

**Inputs:**
- Account Value ₹ (pre-filled from portfolio summary or user-entered)
- Risk per trade % (default: equal slot sizing = 100% / target_slots; e.g., 10% for 10 slots)
- Entry Price ₹
- Stop Loss Price ₹ (or stop %)

**Outputs (auto-computed, live as inputs change):**
- Risk ₹ per trade = Account Value × Risk %
- Stop distance ₹ = Entry − Stop Loss
- Stop distance % = Stop distance / Entry × 100
- Position size (shares) = Risk ₹ / Stop distance ₹
- Position value ₹ = Shares × Entry Price
- % of account in this position
- Lot size check (if F&O): nearest lot boundary

Also shows the Atlas-standard calculation: "Equal slot sizing: ₹X.X lakh per slot (₹X.X lakh portfolio / N slots)."

### 17.3 Tax Estimation

A "Tax Preview" panel showing estimated tax liability on open and closed positions:

**For open positions (unrealized gains — for planning, not actual liability):**
- If sold today: STCG or LTCG classification (based on holding period)
- STCG rate: 15% (for equity held < 12 months, post-July 2024 budget change from 15% to 20% for > ₹1.25 lakh — confirm current rate in spec review, as tax rates change)
- LTCG rate: 10% on gains > ₹1.25 lakh (post-July 2024; earlier ₹1 lakh threshold)
- Estimated tax ₹ on unrealized gain

**For closed positions YTD:**
- Total STCG realized: ₹
- Total LTCG realized: ₹
- Estimated STCG tax: ₹
- Estimated LTCG tax: ₹
- Net post-tax gain: ₹

**Disclaimer (mandatory in the UI):** "Tax estimates are indicative only. Consult a chartered accountant for actual tax filing. Rates reflect post-July 2024 Finance Act provisions."

---

## 18. Module 13 — Catalyst & Event Calendar

### 18.1 Calendar Views

A `QCalendarWidget` extended with event markers, plus a detailed list view for the selected date or date range.

**Views:**
- Monthly calendar (default): Dates with events have color-coded dots (blue = earnings, green = dividend/bonus, red = regulatory, amber = macro)
- Weekly agenda: Five-column view showing all events for Monday–Friday
- Daily list: All events for the selected day, sorted by time

### 18.2 Event Types

**Earnings / Quarterly Results:**
- Company: Company name and NSE symbol
- Type: Q1/Q2/Q3/Q4 results
- Expected date: from NSE's results calendar (fetched from NSE API or manually maintained)
- If watchlist ticker: highlighted in bold
- Consensus EPS estimate (from yfinance or manual entry)
- Previous quarter EPS (from stored history)
- Atlas-computed "expected move": ATR14 as a proxy for expected volatility (not an options-derived move, since real-time options IV is not always available)

**Dividends:**
- Ex-dividend date (NSE announcement)
- Record date
- Payment date
- Dividend amount ₹/share and yield %
- Type: Interim / Final / Special

**Corporate Actions:**
- Bonus issue (e.g., 1:2 ratio — 1 share for every 2 held)
- Stock split (e.g., face value ₹10 → ₹5, i.e., 2:1 split)
- Rights issue (ratio, issue price, open and close dates)
- Buyback (price, number of shares)
- Merger/demerger (ex-date, record date)

**RBI and Macro Events** (from Module 10):
- MPC meetings
- Key macro data releases

**Exchange Events:**
- F&O expiry dates (last Thursday of each month for monthly contracts; every Thursday for weekly index contracts)
- Circuit limit changes
- Stock suspension/reinstatement

### 18.3 Upcoming Earnings Widget

A compact list (also usable as a standalone panel) showing the next 10 upcoming earnings announcements for watchlist tickers:

Columns: Days Until | Symbol | Quarter | Consensus EPS Estimate | Previous Quarter EPS | Atlas Score | Atlas Rank

Sorted by nearest date. This is visible in the Atlas Friday Signal view as a reminder: "These watchlist stocks report results in the next 30 days — consider whether you want to hold through earnings."

### 18.4 F&O Expiry Calendar

NSE monthly F&O contracts expire on the last Thursday of each month. Weekly Nifty and BankNifty options expire every Thursday. A permanent visual indicator on the date axis of charts marks expiry Thursdays.

The calendar highlights every expiry Thursday with a special label ("NSE Monthly F&O Expiry" or "NSE Weekly Expiry"). This is particularly important because expiry weeks often have elevated F&O settlement-related volatility.

---

## 19. Module 14 — Atlas Engine (Embedded Algorithm)

### 19.1 Overview

The Atlas Engine is the heart of AtlasTerminal — the embedded version of the CLI scripts (`live_signal.py`, `alpha_engine.py`, `portfolio_manager.py`, `kronos_engine.py`) presented through a dedicated, polished UI panel. The existing Python modules are reused without modification. The Atlas Engine module is a UI wrapper around them.

### 19.2 Atlas Signal Panel (Main View)

This is the default panel in the "Atlas Friday Signal" workspace. It presents the output of `live_signal.py` as a structured, interactive UI rather than terminal text.

**Panel Layout (top to bottom):**

**Header bar (compact, 40px):**
- "RUN ATLAS SIGNAL" button (prominent, accent colored)
- "Data as of:" date label (from loaded PriceData)
- "Signal date:" date picker (QDateEdit, defaults to latest available date; user can override for historical signals)
- Optional Kronos overlay toggle (QCheckBox — matches the `--kronos` flag)

**Regime Card (120px tall, full width):**
A visually prominent card showing:
- Breadth gauge: a horizontal gauge from 0% to 100%, with shaded regions (red 0–25% = LIQUIDATE, amber 25–50% = DEFENSIVE, green 50–100% = FULL_RISK). Current breadth shown as a marker on the gauge.
- Breadth value: "Breadth: 62.4% (374 of 499 stocks above 50-day SMA)"
- Regime label: "FULL_RISK" / "DEFENSIVE" / "LIQUIDATE" (large text, color-coded)
- Target slots: "Target: 10 positions"
- Data source: "Universe: Nifty 500 | 499 symbols loaded | Data: 13-Jun-2026"

**Actions Block (expandable, highlighted):**
Three sub-sections: SELL | BUY | HOLD. Each rendered as a colored card (sells = red-tinted, buys = green-tinted, holds = gray-tinted).

For each action, show:
- BUY: Symbol | Company | Rank | Score | Close ₹ | Sector | Suggested Qty (based on account value / target slots / last close) | GTT Stop ₹ (12% below close) | Atlas reason
- SELL: Symbol | Company | Current Rank | Your Entry ₹ | Current ₹ | P&L ₹ and % | Sell reason (rank exit / regime sizing / liquidation)
- HOLD: Symbol | Company | Current Rank | Your Entry ₹ | Current ₹ | P&L ₹ and % | GTT Stop ₹

**Top Candidates Table:**
Below the actions block, a sortable table of the top 20 Atlas-ranked stocks (sector-capped), showing: Rank | Symbol | Sector | Score | Close ₹ | 60D Return % | 120D Return % | 200D Return % | ADV30 (₹ cr) | Above SMA50 | Kronos Return % (if Kronos enabled) | Kronos Rank.

Clicking any row in the table pushes the ticker to linked panels (for charting, news, fundamentals review).

**Export / Actions:**
- "Export Signal to CSV" button: saves the complete ranked table and action list to `reports/atlas_signal_YYYY-MM-DD.csv`
- "Update Portfolio" button: opens a dialog to confirm and record any trades suggested by the signal directly into the portfolio (see 11.4)
- "Print Signal" button: generates a `reports/atlas_signal_YYYY-MM-DD.txt` identical to the existing CLI output format (backward compatible with current workflow)

### 19.3 Signal Computation Pipeline

When "RUN ATLAS SIGNAL" is clicked:

1. A `QRunnable` worker is dispatched on `QThreadPool`.
2. Worker calls: `load_local_price_data(data_dir, universe_symbols)` → `build_ranked_snapshot(prices, universe, config)` → `apply_kronos_overlay(...)` (if enabled) → `select_with_sector_cap(ranked, ...)` → `load_current_portfolio()` → `build_rebalance_plan(...)`.
3. Worker emits a `signal_ready(RebalancePlan, ranked_df)` Qt signal.
4. Main thread receives the signal and renders the Atlas Signal Panel with the new data.

A progress indicator (QProgressBar or a throbber spinner) is shown in the panel while computation runs. Computation typically takes 0.5–3 seconds depending on universe size and hardware.

### 19.4 Atlas Configuration UI

A "Configure Atlas" button opens a `QDialog` (not a settings page — kept close to the signal panel for convenience) showing all `AtlasConfig` parameters as editable fields:

**Organized into sections:**

*Universe & Data:*
- Account Value (₹): QDoubleSpinBox
- Data directory: QLineEdit + Browse button
- Universe file: QLineEdit + Browse button
- Corporate actions file: QLineEdit + Browse button

*Regime & Slots:*
- Full risk slots (default 10)
- Defensive slots (default 5)
- Full risk breadth threshold % (default 50%)
- Liquidate breadth threshold % (default 25%)

*Portfolio Rules:*
- Max stocks per sector (default 2)
- Exit rank threshold (default 120)
- Min holding days (default 30)
- Portfolio drawdown circuit breaker % (default 30%)

*Momentum Parameters:*
- Momentum windows: 3 QSpinBox fields (default 60, 120, 200 days)
- Momentum weights: 3 QDoubleSpinBox fields (default 0.2, 0.4, 0.4)
- Volatility window (default 120 days)
- SMA window (default 50 days)
- Score mode: Raw / Risk-Adjusted (QComboBox)
- Use SMA filter: QCheckBox (default enabled)

*Liquidity:*
- Min ADV30 (₹ cr): QDoubleSpinBox (default 15 cr = 150,000,000 ₹)
- Liquidity window (default 30 days)

*Trade Costs:*
- Trade cost rate % (default 0.46%)
- STCG tax rate % (default 15% — note: verify current budget rates)
- LTCG tax rate % (default 10% on gains above ₹1.25 lakh)
- LTCG exemption limit ₹ (default ₹1,25,000)

*Kronos Overlay (collapsible section, only visible if enabled):*
- Kronos enabled: QCheckBox
- Kronos path: QLineEdit + Browse
- Model: NeoQuasar/Kronos-small (dropdown or text)
- Tokenizer: NeoQuasar/Kronos-Tokenizer-base
- Top N candidates to overlay: QSpinBox (default 50)
- Lookback days: QSpinBox (default 256)
- Pred length (trading days): QSpinBox (default 20)
- Weight (blend with Atlas score): QDoubleSpinBox (default 0.25)
- Batch size: QSpinBox (default 8)
- Device: auto / cpu / cuda (QComboBox)

Changes to AtlasConfig via this dialog are saved to `atlas_config.json` and applied to the next signal run.

### 19.5 Kronos-Only Signal Mode

A secondary button "Run Kronos Standalone" in the Atlas Signal Panel (only visible when Kronos is enabled) that runs `kronos_signal.py` logic and shows a Kronos-only ranked table and action plan, distinct from the combined Atlas+Kronos signal. This maps to the `kronos_signal.py` CLI workflow.

### 19.6 Historical Signal Explorer

A "Signal History" tab within the Atlas Signal Panel showing previously generated signals stored in SQLite. The user can browse any past signal date, see the original recommendations, and compare to what actually happened (using the PriceData — the system can look up what the price was 30/60/90 days after the signal date for each recommended stock and compute the hypothetical return).

This is a P2 feature.

---

## 20. Module 15 — Backtester

### 20.1 Overview

The Backtester is an interactive UI wrapper around the existing `backtest_vectorbt.py` logic. No changes are made to the backtesting algorithm itself. The UI provides:

- Parameter configuration
- Visual progress during the run
- Interactive result visualization

### 20.2 Backtester Panel UI

**Configuration Form (left pane, 40% width):**

All parameters from the `main()` function of `backtest_vectorbt.py` are exposed as form fields:
- Data directory (QLineEdit + Browse)
- Universe file
- Corporate actions file
- Start date (QDateEdit, default 2018-01-01)
- End date (QDateEdit, default today)
- Starting capital ₹ (QDoubleSpinBox, default 50,000)
- All AtlasConfig parameters (same as the Atlas Configure dialog — reuse the same config widget)
- Kronos toggle + Kronos parameters (collapsible, same as Atlas configure)

A "Run Backtest" button (large, prominent). Greyed out while a backtest is running.

**Progress indicator:** During a run, a `QProgressBar` shows approximate progress (the backtest iterates over dates — the total date count is known, so progress is deterministic). A "Cancel" button stops the backtest gracefully (the backtest loop must check a `threading.Event` cancellation token on each date).

**Results Panel (right pane, 60% width, visible after run completes):**

Top row: key summary statistics in large text:
- CAGR (after tax): large, bold, green/red
- Max Drawdown: large, bold, red
- Sharpe Ratio (0-RF): large, medium
- Total trades
- Total costs ₹
- Estimated STCG tax ₹

Tabs below the summary:

**Equity Curve tab:** PyQtGraph line chart of portfolio value over time. X-axis: date; Y-axis: ₹ value. Drawdown periods shaded red. A horizontal line at starting capital. The chart should also overlay the Nifty 50 index (normalized to the same starting value) for benchmark comparison — this requires the Nifty 50 OHLCV to be available in PriceData (the `NIFTY` symbol from the bhavcopy universe, if loaded).

**Trade Log tab:** A `QTableWidget` with all trades from `trades.csv`: Date | Symbol | Side | Qty | Price ₹ | Value ₹ | Cost ₹ | Reason. Sortable and filterable. "Export to CSV" button.

**Annual Returns tab:** A bar chart (PyQtGraph) showing the return for each calendar year of the backtest, vs Nifty 50 return for the same year.

**Monthly Heatmap tab:** A table (12 columns × N years rows) showing monthly returns as a color heatmap (green = positive, red = negative). Each cell shows the month's P&L %. Standard "returns calendar" format.

**Drawdown Analysis tab:** A separate PyQtGraph chart of the rolling drawdown curve (percentage below the running high-water mark). Table below showing the top 5 deepest drawdowns with start date, trough date, recovery date, and max depth.

**Parameter Sensitivity tab (P2):** Run the backtest multiple times with varied parameters (e.g., sweep exit_rank from 50 to 150) and display the results as a heatmap of CAGR vs. the varied parameter. This helps identify robust parameter regions.

### 20.3 Saving Results

After a backtest completes, results are:
1. Saved to `reports/equity_curve.csv`, `reports/trades.csv`, `reports/summary.json` (matching the existing CLI behavior — backward compatible)
2. Also saved to SQLite `backtest_runs` table with a run ID, timestamp, config hash, and summary JSON
3. A "Compare Runs" button opens a side-by-side table of all saved runs sorted by CAGR, with all summary metrics as columns

---

## 21. Module 16 — Market Breadth & Internals

### 21.1 Data Source

All breadth computations use the locally loaded `PriceData` object, not an external API. The developer computes breadth from the price matrices directly.

### 21.2 Breadth Dashboard

A `QDockWidget` containing a dashboard of market breadth indicators for the Nifty 500 universe.

**Primary Breadth Indicators (computed from PriceData):**

- **% Above 50-day SMA** (the Atlas breadth metric): Computed as `(close > close.rolling(50).mean()).mean(axis=1)` across all universe symbols. Shows as a time-series chart and as a current gauge. This is the most important breadth indicator for Atlas traders.
- **% Above 200-day SMA**: Same but for 200-day SMA. Slower-moving, more indicative of the long-term trend.
- **% Above 20-day SMA**: Fast-moving, short-term overbought/oversold indicator.
- **Advance/Decline Line (cumulative)**: Each day, count advancing symbols − declining symbols. The cumulative sum is the A/D Line. Plot as a line chart. Divergence from Nifty 50 price (index making new highs but A/D Line lagging) = distribution warning.
- **New 52-Week Highs minus New 52-Week Lows**: Daily count from PriceData. Plot as a bar chart. When more stocks make new highs than lows, the broad trend is healthy.
- **McClellan Oscillator** (computed from advancing-declining daily difference via 19-day and 39-day exponential averages): A short-term breadth oscillator. Zero-line crossings are signals.
- **Breadth by Sector**: For each of the sectors in the universe CSV, compute the % of that sector's stocks above their 50-day SMA. Displayed as a horizontal bar chart sorted by value. This immediately shows which sectors are strong vs. weak.

**Display:** All indicators as PyQtGraph charts in a scrollable layout within the panel. Each chart has a date-range slider or uses the same date range as the main chart panel if linked.

### 21.3 India VIX Dashboard

A dedicated sub-section (or tab) for India VIX analysis:
- Current India VIX value and day change
- 1-year India VIX chart (from yfinance `^INDIAVIX`)
- VIX historical average and ±1 standard deviation bands
- "VIX Spike" detection: flags dates in the past year where VIX rose by > 3 points in a single day (panic entries) and where VIX fell by > 3 points (panic exits) — annotated on the chart
- Rolling correlation of India VIX with Nifty 50 returns (typically strong negative correlation)

### 21.4 Nifty Advance/Decline Data

On NSE, the daily advancing/declining data is published in the Bhavcopy as the count of EQ-series stocks with a positive/negative/flat close. Parse this from the bhavcopy data and store in SQLite. Display as a chart and as today's values in the breadth dashboard.

---

## 22. Module 17 — FII/DII Flow Tracker

### 22.1 Data Source

NSE publishes daily FII (Foreign Institutional Investor) and DII (Domestic Institutional Investor) net equity cash market activity. URL: `https://www.nseindia.com/api/fiidiiTradeReact`. Fetched daily (once, after market close) via NSESession and stored in SQLite.

Fields per day: FII Gross Buy ₹ cr, FII Gross Sell ₹ cr, FII Net ₹ cr; DII Gross Buy ₹ cr, DII Gross Sell ₹ cr, DII Net ₹ cr.

### 22.2 FII/DII Panel

A `QDockWidget` showing a comprehensive view of institutional flows.

**Daily Flow Bar Chart:** PyQtGraph bar chart with two bar groups per day (FII net and DII net). Bars colored green for net buying, red for net selling. Last 30 or 90 trading days visible (slider to choose range).

**Cumulative Flow Chart:** Line chart of cumulative FII net flow (sum of daily net) and DII net flow over the past year. Divergence between the two lines (FII selling while DII buying, or vice versa) shows the "war between foreign and domestic institutions."

**Rolling Sum Table:** A compact table showing:
- FII Net: Last 1 day / 5 days / 10 days / 30 days / YTD (₹ cr)
- DII Net: Same windows
- Combined Net: Same windows

**FII + DII Combined Overlay on Nifty:** A dual-axis PyQtGraph chart showing Nifty 50 price (line) and the rolling 20-day FII+DII combined net flow (bar chart) on the same x-axis. Periods of heavy net selling by both FII and DII often correlate with market drawdowns.

**Interpretation Guide (static, in-panel):** A compact legend below the chart explaining the conventional interpretation: "FII net buyer for 10+ days = bullish signal; FII net seller for 10+ days with DII buying = domestic conviction but foreign caution; Both selling = high risk-off regime."

### 22.3 FII in F&O (Futures)

NSE also publishes FII positions in index futures and options (the "Participant-wise OI" report). This data shows whether FIIs are net long or short Nifty futures — a critical sentiment indicator.

Source: NSE's `https://www.nseindia.com/api/participants?date=DDMMYYYY` endpoint.

Fields: FII index futures long contracts / short contracts / net; DII index futures; Client category; Proprietary category.

Display as a table for today plus a 20-day trend chart showing FII net position in Nifty futures (in contracts).

---

## 23. Module 18 — Block Deals & Bulk Deals

### 23.1 Data Source

NSE publishes block deals (large trades in the special block deal window, 8:45–9:00 AM IST, minimum 5 lakh shares or ₹5 cr) and bulk deals (single client trades > 0.5% of company's equity). Source: `https://www.nseindia.com/api/block-deal` and `https://www.nseindia.com/api/bulk-deal`. Fetch daily after market close.

### 23.2 Block/Bulk Deal Panel

A `QDockWidget` with a tabbed view:

**Block Deals tab:**
- Table showing today's block deals: Time | Symbol | Buyer/Seller | Quantity | Price ₹ | Value ₹ cr
- Who is buying/selling is particularly important — if a known institution or promoter entity is a buyer, it's a significant signal.
- Historical block deal search: filter by symbol, date range, buyer/seller name

**Bulk Deals tab:**
- Same structure as block deals tab
- Bulk deals are filed at end of day and reflect large trades by a single entity

**Company Bulk Deal History:** Clicking any row pushes the symbol to linked panels; also shows a table of all past bulk and block deals for that symbol over the past 6 months. This gives context: "Axis MF has been buying this stock in block deals for the past 3 months."

**Alert integration:** User can set an alert "Notify me when any block/bulk deal occurs for [symbol]" — stored in the alerts DB.

---

## 24. Module 19 — Delivery & Institutional Data

### 24.1 Delivery Percentage

NSE publishes delivery data (shares delivered vs. total traded) in the security-wise deliverable position data report. URL: NSE bhavcopy derivatives and delivery files. Delivery data is included in the broader bhavcopy download.

For each symbol and each day, `delivery_pct = delivery_qty / total_traded_qty × 100`.

High delivery % on an up day = strong conviction buying (investors taking delivery, not just intraday trading). Low delivery % on a high-volume up day = suspicious pump (mostly intraday activity, no real conviction).

### 24.2 Delivery Panel

A panel showing delivery analysis for the current linked ticker:

**Delivery Trend Chart:** PyQtGraph dual-axis chart. Primary axis (left): price candlestick or line. Secondary axis (right): delivery % bar chart. Both on the same x-axis (date). Color-code delivery bars: > 60% = green, 40–60% = amber, < 40% = red.

**Rolling Average:** A 20-day rolling average delivery % line overlaid on the delivery bars. Current delivery vs average delivery ratio (high ratio = unusual conviction).

**Delivery Table:** The last 20 trading days in a table: Date | Close ₹ | Volume (lakh sh) | Delivery Qty (lakh sh) | Delivery % | Delivery vs 20D avg %

---

## 25. Module 20 — Promoter & Insider Holdings

### 25.1 Data Source

NSE and BSE require listed companies to publish quarterly shareholding patterns (Regulation 31 of SEBI LODR). These are available as structured CSV/XLS files on NSE and BSE websites.

Fetch quarterly: NSE's shareholding API at `https://www.nseindia.com/api/corporate-share-hldg-info?symbol=SYMBOL&quarterly=q1q` (unofficial; may require session). BSE's equivalent at `https://api.bseindia.com/BseIndiaAPI/api/Share_Holding_Pat_New/w?scripcode=BSESCRIP`.

Store in SQLite `shareholding_pattern` table: symbol, quarter_end_date, promoter_pct, fii_pct, dii_pct, public_pct, other_pct, promoter_pledged_pct.

### 25.2 Shareholding Pattern Panel

A panel for the current linked ticker:

**Current Quarter Summary:**
- Promoter Holding %
- Pledged Shares (as % of promoter holding) — high pledge = financial distress risk
- FII Holding %
- DII Holding %
- Public Holding %

**Trend Chart:** A stacked area chart showing how each category's % has changed over the last 8 quarters. The most important trend to watch: declining promoter holding (selling out) or increasing FII holding (institutional accumulation).

**QoQ Change table:** Each category's holding %, change from last quarter (+ or - percentage points), and change from a year ago.

**Pledge Change Alerts:** If promoter pledge % increases by > 5 percentage points in a single quarter, flag it prominently in red with the label "PLEDGE INCREASE ALERT." High and rising pledge is one of the most dangerous signals in Indian equities.

### 25.3 Insider Trading (SEBI SAST/PIT Compliance)

NSE publishes insider trading filings made under SEBI's Prohibition of Insider Trading (PIT) regulations. Listed promoters and key managerial personnel must file details of trades within 2 trading days.

Source: NSE API or SEBI's SCORES/disclosure portal. Fetch for watchlist tickers.

Display as a table: Date | Insider Name | Designation | Transaction Type (Buy/Sell) | Shares | Price ₹ | Post-transaction Holding %

Insider buying at market price (open-market purchase, not ESOP exercise) by promoters or senior management is one of the strongest bullish signals in Indian markets.

---

## 26. Module 21 — Trade Journal & Playbook

### 26.1 Trade Journal

A structured log of all trades the user has made. Replaces and extends the `current_portfolio.csv` history.

**Journal Entry Fields:**

*Entry record (when opening a position):*
- Ticker
- Direction: Long / Short (NSE does not allow retail short-selling in cash market; "Short" is relevant for F&O)
- Entry date
- Entry price ₹
- Quantity
- Total entry value ₹
- Brokerage and charges ₹
- Strategy tag: Atlas Monthly / Earnings Play / Discretionary / Sector Rotation / Custom
- Setup description (which Atlas signal date recommended this, or the discretionary thesis)
- Entry chart snapshot (user attaches a PNG — saved to `data/journal_images/`)
- GTT stop level ₹
- Target price ₹ (optional)
- Confidence: 1–5 stars
- Market context: Bull Trend / Bear Trend / Range-bound / High Volatility / Sector Theme

*Exit record (when closing a position):*
- Exit date
- Exit price ₹
- Exit reason: Atlas exit rank / Regime liquidation / Manual target hit / GTT stop triggered / Discretionary exit / Partial exit
- Exit chart snapshot
- Post-trade notes: "What I did well" | "What I would do differently" | "Would I take this setup again?"
- Final realized P&L ₹ and % (auto-computed)
- Holding days (auto-computed)
- STCG/LTCG classification (auto-computed from holding period)
- Estimated tax ₹

**Journal List View:** A `QTableWidget` showing all journal entries (open and closed). Columns: Date | Ticker | Side | Strategy Tag | Entry ₹ | Exit ₹ | P&L ₹ | P&L % | Holding Days | Confidence | Outcome (green WIN / red LOSS / blue OPEN). Sortable and filterable.

**Journal Detail View:** Clicking a row opens a `QDialog` or side panel with all fields, entry/exit chart snapshots, and full notes.

### 26.2 Journal Analytics

A "Performance Analytics" tab within the Journal panel:

- Win rate by strategy tag (table + bar chart)
- Average P&L % by strategy tag
- Expectancy = (Win rate × Avg Win %) - (Loss rate × Avg Loss %)
- Best performing strategy
- P&L by holding period bucket (0–7 days, 8–30 days, 31–90 days, > 90 days) — helps identify if the Atlas 30+ day hold discipline is working
- P&L by entry confidence rating (do 5-star setups outperform 3-star setups?)
- Monthly P&L bar chart (realized P&L per month)
- Biggest winners and biggest losers (top 5 each, by ₹ and by %)

### 26.3 Playbook

A library of named setups that the user documents for future reference and for linking to journal entries.

Each playbook entry contains:
- Setup name (e.g., "Atlas Monthly Momentum Buy", "Pre-Earnings Call Buy", "F&O Expiry Squeeze")
- Setup description (free text — the thesis and rationale)
- Entry criteria (checklist format — the user writes conditions; each condition is a checkbox that can be checked in the journal entry form when using this setup)
- Exit rules
- Stop loss rule
- Position sizing rule
- Ideal market conditions
- Historical performance: auto-populated by linking journal trades tagged with this setup
- Example trade screenshots

When creating a new journal entry, the user selects a playbook setup. The entry criteria checklist is shown, and the user checks off which conditions were met at entry. This meta-data feeds into the analytics: "Atlas trades where I missed the 'Above SMA50' criterion had a 60% lower win rate — the filter matters."

---

## 27. Module 22 — Sector Heatmap & Rotation

### 27.1 Market Heatmap

A treemap-style visualization using a custom PyQtGraph widget (or a `QGraphicsScene` with `QGraphicsRectItem` children).

**Layout:** Rectangles represent stocks. Rectangle area ∝ market cap (or configurable: ADV30, free float). Rectangle color = performance metric (day %, week %, month %, 60D %, Atlas Score — user selects from a dropdown). Rectangles grouped and bordered by sector.

**Color scale:** Red (strong negative) → light red → gray (0%) → light green → dark green (strong positive). The color range min/max adapts to the actual data range for the selected metric.

**Interaction:** Hovering a rectangle shows a tooltip with: Ticker, Company, Close ₹, the selected metric value, ADV30, Atlas Rank. Clicking pushes the ticker to linked panels.

**Controls:**
- Color metric: Day % | Week % | Month % | 60D % | 120D % | 200D % | Atlas Score | RSI 14 | Delivery %
- Size metric: Market Cap | ADV30 | Free Float
- Grouping: By Sector | By Industry | Flat (no grouping)

### 27.2 Sector Performance Table

Below the heatmap (or as a separate tab), a table showing each sector with its NSE sector index performance:

Columns: Sector | Sector Index Name | Index Level | Day % | Week % | Month % | QTD % | YTD % | # Stocks in Universe | # Stocks Above SMA50 (sector breadth %)

The sector indices available on NSE: NIFTY AUTO, NIFTY BANK, NIFTY ENERGY, NIFTY FMCG, NIFTY HEALTHCARE, NIFTY IT, NIFTY MEDIA, NIFTY METAL, NIFTY PHARMA, NIFTY PSU BANK, NIFTY REALTY, NIFTY FINANCIAL SERVICES, NIFTY CONSUMER DURABLES, NIFTY OIL AND GAS, NIFTY MIDSMALL HEALTHCARE.

Fetch index performance from yfinance (^NIFTYAUTO.NS, ^NIFTYBANK.NS, etc.). Cache for 15 minutes.

### 27.3 Sector Rotation Cycle Visualization

A static visualization (not algorithmic) showing the typical sector rotation cycle across economic phases. A circle diagram (PyQtGraph or SVG overlay) with sectors positioned at their typical outperformance phases (Recovery → Expansion → Slowdown → Contraction). The user overlays the current macro context and where they believe India is in the cycle. This is an educational/reference tool. Not algorithmic.

---

## 28. Module 23 — Relative Strength & Correlation

### 28.1 Relative Strength Line

For the current ticker, a relative strength (RS) line showing performance vs. a benchmark. Computed from PriceData: `RS = stock_close / benchmark_close`, normalized to 100 at the left edge of the visible date range.

Benchmark defaults to Nifty 50. User can change to Nifty 500, a sector index, or any other symbol in the universe.

The RS line is shown as a sub-pane below the main price chart in the ChartPanel (when the "RS" overlay is toggled on in the chart toolbar).

### 28.2 RS Rank

Atlas's core alpha metric is effectively a cross-sectional momentum score. The "Atlas Rank" already captures relative strength. This module extends it with a standard RS Rank calculation:

RS Rank = percentile of the stock's trailing 63-day return vs. all universe stocks. A stock with RS Rank 95 has outperformed 95% of the universe in the past quarter. Computed daily from PriceData and stored in the `alpha_data` in-memory cache.

A standalone RS Rank screener (accessible from the command bar with `RS`) shows all universe stocks sorted by RS Rank, with sector grouping.

### 28.3 Correlation Matrix

For a user-defined set of tickers (up to 20, drawn from the current watchlist or typed in), a PyQtGraph heatmap showing the pairwise 60-day rolling return correlation.

Implementation: `returns_df.corr()` on the selected subset of PriceData.close columns for the trailing 60 days. The matrix is symmetric. Color: dark green = -1.0, white = 0.0, dark red = +1.0.

**Primary use case:** Portfolio risk assessment. The user adds their current holdings to the matrix and discovers that all their "diversified" positions are actually highly correlated with Nifty IT (all move together). This is the same insight as the risk analytics module's correlation section (17.1), but presented here as a freeform analysis tool with user-selected tickers.

**Configurable lookback:** 30 / 60 / 90 / 252 days (QComboBox).

---

## 29. Module 24 — Data Download Manager

### 29.1 Overview

The Data Download Manager is the replacement for the CLI commands `download_data.py` and `download_yahoo_data.py`, presented as a GUI panel. It exposes all download options from both scripts as form fields and shows progress in a real-time log window.

### 29.2 Download Manager Panel UI

**Source Selection (tab strip at top):**
- NSE Bhavcopy (jugaad-data primary)
- Yahoo Finance (fallback / supplemental)

**NSE Bhavcopy Tab:**

Form fields:
- Universe file: QLineEdit + Browse (defaults to configured universe path)
- Output directory: QLineEdit + Browse (defaults to configured data dir, e.g., `bhavcopy_data/`)
- Start date: QDateEdit (default 2017-01-01 — needed for 120D lookback + extra buffer)
- End date: QDateEdit (default today)
- Request timeout (seconds): QSpinBox (default 45)
- Retries per date: QSpinBox (default 5)
- Retry delay (seconds): QDoubleSpinBox (default 12)
- Day delay (seconds): QDoubleSpinBox (default 0.75)
- Rate limit cooldown (seconds): QSpinBox (default 1800)
- Rate limit retries: QSpinBox (default 1)
- Retry previously failed "no data" dates: QCheckBox
- Overwrite existing files: QCheckBox (use with caution)
- Build-only mode (no downloads, just rebuild symbol CSVs from existing bhavcopies): QCheckBox

Buttons:
- "Start Download" (large, accent colored)
- "Stop" (cancel in-progress download; the `QRunnable` worker checks a cancellation event on each date iteration)
- "Build Symbol CSVs Only" (shortcut for `--build-only` mode)

**Yahoo Finance Tab:**

Form fields:
- Universe file: same as above
- Output directory: QLineEdit + Browse (default `nse_data/`)
- Start date: QDateEdit (default 2017-01-01)
- End date: QDateEdit (default today)
- Batch size: QSpinBox (default 40)
- Retries: QSpinBox (default 4)
- Retry backoff (seconds): QDoubleSpinBox (default 8)
- Batch delay (seconds): QDoubleSpinBox (default 2)
- Max age hours (skip fresh files): QDoubleSpinBox (default 36)
- Min rows (reject thin data): QSpinBox (default 100)
- Force re-download: QCheckBox (equivalent to `--force`)

Buttons:
- "Start Yahoo Download"
- "Stop"

### 29.3 Progress Log

Below the form, a `QTextBrowser` (read-only, auto-scrolling) shows real-time download progress output. Each downloaded file, failure, and status message appears here, styled with color coding:
- Green text: "SAVED bhavcopy_20260613.csv"
- Red text: "FAILED RELIANCE: connection timeout"
- Amber text: "SKIP TCS: already exists (fresh)"
- Gray text: "[126/250] DOWNLOADING BHAVCOPY 2026-06-13"

The log is also written to `logs/downloads.log` for post-run review.

### 29.4 Download Status Summary

After a download completes (or is stopped), a summary bar shows: Downloaded: N | Skipped: N | Failed: N | Total: N. A "View Failures" button opens the `_download_failures.csv` in a `QTableWidget` dialog.

### 29.5 Post-Download Auto-Reload

When a download completes successfully, a dialog asks: "New data downloaded. Reload price data and recompute Atlas signal?" Clicking Yes re-runs `load_local_price_data()` and `compute_alpha()` in a background worker, refreshing all open panels.

### 29.6 Fundamentals Import (Screener.in CSV)

A separate "Import Fundamentals" section within the Data Manager:
- User selects a folder of Screener.in CSV exports (one file per company)
- The importer parses each CSV, extracts: P/E, P/B, EPS, revenue growth, ROE, debt/equity, promoter holding, and quarterly results history
- Stores in SQLite `fundamentals` table
- Reports: "Imported N companies, N failed"

This is the mechanism for populating the fundamentals data that enables valuation filters in the screener and fundamentals analysis in the panel.

---

## 30. Module 25 — Settings, Configuration & Nuitka Notes

### 30.1 Settings Dialog

A `QDialog` opened from Menu Bar → Tools → Settings, or from the command bar with `SETTINGS`. Uses a `QListWidget` on the left for navigation between sections, and a `QStackedWidget` on the right for the content of each section.

**Section: General**
- Application data directory (where `atlas_terminal.db` and other persistent data live)
- Default data directory (where symbol CSVs are stored; pre-fills download manager)
- Default universe file path
- Default portfolio file path
- Default corporate actions file path
- Theme: Dark (default) / Light (QSS stylesheet swap)
- Density mode: Compact / Comfortable
- Color scheme for up/down: Standard (Green/Red) | Colorblind-friendly (Teal/Red) | Colorblind-friendly (White/Red)
- Startup workspace (dropdown of saved workspace names)
- Number of undo steps for drawings (default 20)
- Log level: DEBUG / INFO / WARNING (for `logs/atlas_terminal.log`)

**Section: Market & Session**
- Primary market: NSE (fixed for v1.0)
- IST timezone (fixed; application always uses Asia/Kolkata for session boundaries)
- Market open: 09:15 (fixed)
- Market close: 15:30 (fixed)
- Pre-open: 09:00–09:15 (fixed)
- Post-close: 15:40–16:00 (fixed)
- F&O expiry day: Thursday (fixed)

**Section: Quote & Data Refresh**
- Live quote poll interval (during market hours): 1 / 3 / 5 / 10 minutes (QComboBox)
- Live quote poll interval (extended hours): 5 / 15 minutes
- yfinance fallback: enabled by default; can be disabled for offline-only use
- NSE session refresh interval: 15 minutes (configurable 5–60 min)
- News fetch interval: 10 / 30 / 60 minutes

**Section: Atlas Configuration**
- All AtlasConfig parameters (same as Module 14's Atlas Configure dialog — this section is the same form embedded here for completeness; both locations write to the same `atlas_config.json`)

**Section: Trade Costs**
- STT rate %
- NSE exchange transaction charges %
- SEBI turnover fee %
- Stamp duty %
- GST rate %
- Brokerage ₹ per trade (or 0 for zero-brokerage)
- STCG tax rate %
- LTCG tax rate %
- LTCG exemption limit ₹

**Section: Alerts**
- Desktop notifications: enabled/disabled
- Notification sound: enabled/disabled; sound file picker
- Alert polling interval: 30 / 60 / 120 seconds
- Email alerts: SMTP server, port, from address, to address, app password (stored encrypted in SQLite)
- Maximum alerts per hour (anti-spam limiter)

**Section: Data Sources**
- jugaad-data path override (if user has a local jugaad-data install they want to use instead of the pip-installed version)
- NSE session cookie refresh URL
- News RSS URLs (user can add custom RSS feeds)
- Fundamentals data directory (where Screener.in CSVs are imported from)

**Section: Appearance**
- Font size (global override)
- Chart background color (dark black default)
- Chart candle colors: bullish / bearish
- Chart grid: on/off
- PyQtGraph antialiasing: on/off (disable for performance on older machines)
- Default chart timeframe
- Default chart type

**Section: Keyboard Shortcuts**
- A table showing all commands and their keyboard shortcuts. Click a row to reassign the shortcut (QKeySequenceEdit). "Reset to Defaults" button.

**Section: About**
- Version, build date, Python version, PyQt6 version, PyQtGraph version
- License note (internal tool — no distribution license required)
- Nuitka compilation info: if compiled, show compilation date and Python version used

### 30.2 Alert System

Alerts stored in SQLite `alerts` table. A background `QTimer` fires every 30–120 seconds (configurable) and evaluates all active alerts against the current cached data.

**Alert types implemented in v1.0:**

- Price crosses above ₹[value]
- Price crosses below ₹[value]
- Day change % exceeds +[value]%
- Day change % exceeds -[value]%
- New 52-week high
- New 52-week low
- Atlas rank rises above [N] (moving into exit zone)
- Atlas rank improves below [N] (entering buy zone)
- Breadth crosses below [threshold]% (regime change warning)
- India VIX crosses above [value]
- GTT stop within [N]% of current price
- Portfolio drawdown exceeds [N]%
- Block deal occurs for [ticker]
- New NSE announcement for [ticker]

**Alert delivery:**
- In-app toast notification (a `QFrame` that slides in from the bottom-right corner and auto-dismisses after 10 seconds; clicking it opens the relevant panel for that ticker)
- Desktop system notification (via `plyer` library or `win10toast-reborn` on Windows — verify Nuitka compatibility)
- Optional sound (`.wav` file played via Python's `winsound` module on Windows)
- Optional email (via `smtplib` using configured SMTP settings)

**Alert Manager Panel:** A `QDockWidget` with a `QTableWidget` of all alerts (active, triggered, paused). Columns: Status | Ticker | Alert Type | Condition Value | Created | Last Triggered. Right-click: Edit | Pause | Delete | Duplicate. Triggered alerts show a timestamp and the value at trigger.

---

## 31. UI/UX Design Requirements

### 31.1 Color Palette

The application ships with a dark theme as default. All colors defined as constants in a `palette.py` file and referenced throughout the codebase. Never hardcode colors inline.

```python
# palette.py — dark theme
BACKGROUND       = "#0A0C10"   # near-black workspace background
SURFACE          = "#12151C"   # panel background
SURFACE_ELEVATED = "#1A1E28"   # cards within panels
SURFACE_BORDER   = "#2A2F3D"   # panel borders, grid lines
ACCENT           = "#00C4FF"   # active states, links, focused elements
BULLISH          = "#00D97E"   # positive values, buy signals, up candles
BEARISH          = "#FF4560"   # negative values, sell signals, down candles
WARNING          = "#FFAB00"   # amber — circuit limits, GTT near-miss
TEXT_PRIMARY     = "#E8ECF2"   # primary labels, prices
TEXT_SECONDARY   = "#8B95A8"   # metadata, secondary fields
TEXT_MUTED       = "#505A6B"   # placeholder text, disabled fields
CHART_GRID       = "#1E2330"   # chart background grid lines
```

The QSS stylesheet is generated from these palette constants at runtime. The entire application is re-themed by changing the palette values and calling `QApplication.setStyleSheet(generate_qss(palette))`.

**Light theme:** A second palette dict that the user can activate from Settings. Light themes for financial terminals are unusual; ship it but consider it a P2 polish task.

**Colorblind theme:** Replace BULLISH/BEARISH with TEAL (#009688) / MAGENTA (#C2185B) in the palette.

### 31.2 Typography

All fonts are bundled with the application (embedded in the Nuitka build). Do not rely on system-installed fonts.

- **UI font (panels, tables, labels):** IBM Plex Sans (variable font, weights 300–700). Available under SIL OFL, freely embeddable.
- **Monospace (prices, tickers, numbers):** IBM Plex Mono. Same family, monospace variant for numerical data in tables.
- **All numeric data cells must use tabular figures** (CSS `font-variant-numeric: tabular-nums` equivalent in PyQt6: use a fixed-width font or ensure the monospace font is used for price columns). This prevents width jitter when prices update.

Font sizes:
- Data table cells: 10px (Compact) / 12px (Comfortable)
- Section headers: 12px / 14px
- Command bar: 14px
- Security header ticker symbol: 20px / 22px
- Panel title bar: 11px / 12px

### 31.3 Number Formatting

All Indian-format number formatting is encapsulated in a `format_inr()` utility function. Never format currency inline. Rules:

```
< ₹1 lakh      → ₹XX,XXX.XX
₹1 lakh – ₹1 cr  → ₹XX.XX lakh
₹1 cr – ₹1 lakh cr → ₹XX.XX cr
> ₹1 lakh cr   → ₹XX.XX lakh cr
```

Volume formatting:
```
< 1 lakh shares → X,XXX shares  
1 lakh – 1 cr   → XX.X lakh sh
> 1 cr shares   → X.X cr sh
```

These formatters must be correct in all cases. Test with: ₹0, ₹999, ₹50,000, ₹1,50,000, ₹10 lakh, ₹100 cr, ₹10,000 cr, ₹1 lakh cr.

### 31.4 Price Update Animation

When a price value updates in a table or quote panel, the cell flashes briefly:
- Positive update (price increased): cell background transitions from BULLISH (#00D97E at 60% opacity) to SURFACE over 200ms
- Negative update (price decreased): cell background transitions from BEARISH (#FF4560 at 60% opacity) to SURFACE over 200ms
- Neutral (price unchanged but refreshed): no animation

This is implemented using `QPropertyAnimation` on a custom cell background color property, or by manually painting the cell with a fading overlay via `QTimer`.

### 31.5 Loading and Error States

Loading (data being fetched in background):
- Panel shows a `QProgressBar` with `setRange(0, 0)` (indeterminate / pulsing) in the panel header or overlaid centrally on the panel content area.
- Never leave a panel blank. Show skeleton placeholder content (gray rounded rectangles matching the expected data layout) while data loads.

Error states:
- When data load fails, show an in-panel error card (not a modal dialog): icon + error message + "Retry" button.
- Messages are user-friendly: "Could not load price data for RELIANCE. The file `nse_data/RELIANCE.csv` may be missing or corrupted. Try re-downloading data." Never show Python tracebacks in the UI.
- Log the full traceback to `logs/atlas_terminal.log` at ERROR level.

Empty states:
- When a screener returns no results: show centered text "No stocks match your current filters. Try relaxing one or more conditions."
- When watchlist is empty: show centered text + "Add stocks" CTA button.

### 31.6 Context Menus

Right-clicking any ticker (in any view — watchlist row, screener result, chart, quote panel header) shows a consistent `QMenu`:

- Open Chart
- Open Quote
- Open News Feed
- Open Fundamentals
- Open F&O Chain (only if fo_enabled for this symbol)
- Add to Watchlist → submenu of watchlist names
- Remove from Watchlist (if in a watchlist panel)
- Create Alert
- Add to Journal
- Copy NSE Symbol (copies plain text like "RELIANCE")
- Copy Yahoo Symbol (copies "RELIANCE.NS" for use in external tools)
- Open on NSE Website (opens `nseindia.com/get-quotes/equity?symbol=RELIANCE` in system browser)
- Open on Screener.in (opens `screener.in/company/RELIANCE/` in system browser)
- Open on TradingView (opens `tradingview.com/chart/?symbol=NSE:RELIANCE` in system browser)

The last three use `QDesktopServices.openUrl()` which works correctly in Nuitka-compiled executables.

---

## 32. Data Architecture & Feed Requirements

### 32.1 Local Data First

The application's philosophy is "local data first, network second." The `PriceData` object is loaded at startup from the local CSV directory. All core computations (Alpha engine, Screener, Backtester, Charts with daily data) work from this local data. Network is only used for:
- Incremental data download (Module 24)
- Live quote refresh (yfinance fast_info poll)
- News and announcements fetch (NSE session)
- Fundamentals fetch (yfinance info, on-demand)
- FII/DII fetch (NSE API)

### 32.2 PriceData Loading

At startup, the application loads `PriceData` from the configured data directory using the existing `load_local_price_data()` function. This runs in a `QRunnable` worker (it can take 2–10 seconds for 500 symbols). While loading, the UI shows a startup splash screen with a progress bar.

Once loaded, `PriceData` is stored as a singleton in a `DataStore` class and accessed by all panels via the `DataStore.instance()` pattern.

### 32.3 NSE Session Manager

NSE's API requires browser-like headers and a session cookie. The `NSESession` class:
- Initializes by visiting `https://www.nseindia.com` with browser headers (from existing `BHAVCOPY_HEADERS` in data_fetcher.py, extended with `Referer` and `Cookie` fields)
- Stores the session cookies in a `requests.Session` object
- Refreshes the session automatically every 15 minutes (the NSE cookies typically expire in 15–30 minutes)
- Exposes `get(url)` and `get_json(url)` methods used by all NSE-facing fetchers
- Handles HTTP 403 (rate limit) with a configurable cooldown

The NSESession singleton is initialized on first network request and reused throughout the application lifetime.

### 32.4 jugaad-data vs yfinance Decision Logic

When downloading or refreshing data for a symbol, the following decision logic applies:

```
1. Attempt jugaad-data (NSE Bhavcopy path):
   - Download via download_bhavcopy_history() (daily bhavcopy files → per-symbol CSVs)
   - If symbol has < 100 rows in result: FAILED
   
2. On failure: attempt yfinance fallback:
   - Download via download_yahoo_data.py logic (yf.download SYMBOL.NS)
   - If symbol has < 100 rows: FAILED (log to _yahoo_download_failures.csv)
   
3. On both failures: symbol is excluded from universe for the next run.
   - User sees "N symbols failed download" warning in the Download Manager panel.
   - Suggested actions: check if symbol is newly listed, delisted, or has a name change.
```

The source used for each symbol is recorded in SQLite `data_sources` table: symbol, source (jugaad/yfinance/both), last_updated_date, row_count. This is displayed in the Download Manager panel as a status table.

### 32.5 Data Validation

After loading `PriceData`, the application runs validation checks:
- Flag symbols with < 120 rows of data (insufficient for 120-day momentum window — these are excluded from the Atlas score computation)
- Flag symbols with a gap of > 5 trading days in the recent history (stale data — recent bhavcopy may have been missed)
- Flag symbols where the latest date is more than 3 business days behind the expected latest date (indicates the data directory has not been refreshed)
- These flags are shown in the status bar (a small warning icon with a count) and in a "Data Quality" tab in the Download Manager panel

### 32.6 SQLite Database Schema

All SQLite table definitions must be created via a `migrations.py` module using `CREATE TABLE IF NOT EXISTS`. No ORM — raw `sqlite3` cursor calls only (Nuitka compiles `sqlite3` cleanly; SQLAlchemy is heavy and has Nuitka complications).

Tables:
```sql
workspaces(id, name, layout_json, panel_configs_json, created_at, updated_at)
watchlists(id, name, created_at)
watchlist_items(watchlist_id, symbol, sort_order, notes)
portfolio(id, symbol, quantity, avg_price, entry_date, gtt_stop, target_price, strategy_tag, notes)
portfolio_history(id, snapshot_date, total_value, cash, holdings_json)
journal_trades(id, ticker, direction, entry_date, entry_price, quantity, entry_value, brokerage, strategy_tag, setup_notes, entry_image_path, gtt_stop, target_price, confidence, market_context, exit_date, exit_price, exit_value, exit_reason, exit_notes, exit_image_path, realized_pnl, holding_days, tax_type, tax_estimate)
playbook_setups(id, name, description, entry_criteria_json, exit_rules, stop_rules, sizing_rules, market_conditions, notes)
alerts(id, ticker, alert_type, condition_value, created_at, last_triggered, is_active, notification_channels)
news_items(id, ticker, headline, source, published_at, url, sentiment_score, category, full_text, is_read)
fundamentals(id, symbol, source, last_updated, pe_ttm, pb, ev_ebitda, ps_ttm, dividend_yield, eps_ttm, revenue_growth_yoy, net_margin, roe, debt_equity, promoter_holding, fii_holding, face_value, market_cap_cr, raw_json)
earnings_history(id, symbol, quarter, result_date, eps_actual, eps_estimate, revenue_actual, revenue_estimate, pat_cr, source)
shareholding_pattern(id, symbol, quarter_end_date, promoter_pct, fii_pct, dii_pct, public_pct, promoter_pledged_pct, source)
fii_dii_flow(id, flow_date, fii_buy_cr, fii_sell_cr, fii_net_cr, dii_buy_cr, dii_sell_cr, dii_net_cr)
block_deals(id, deal_date, deal_time, symbol, client_name, deal_type, quantity, price, value_cr)
corporate_events(id, symbol, event_type, ex_date, record_date, payment_date, amount, ratio, description)
backtest_runs(id, run_timestamp, start_date, end_date, config_json, cagr_after_tax, max_drawdown, sharpe, trade_count, summary_json)
chart_drawings(id, symbol, timeframe, drawing_type, data_json, created_at, updated_at)
data_sources(symbol, source, last_updated, row_count, validation_status)
app_settings(key TEXT PRIMARY KEY, value TEXT)
```

---

## 33. Non-Functional Requirements

### 33.1 Performance

- **Startup to interactive:** Cold start from `.exe` double-click to fully interactive workspace in < 10 seconds for a 500-symbol universe on a mid-range Windows machine (Intel i5, 16GB RAM, SSD). PriceData loading is the dominant cost.
- **Chart render:** A daily candlestick chart with 1,800 candles (7 years of daily data) and 5 overlaid indicators must render in < 200ms on first draw. Pan/zoom must achieve 60fps.
- **Atlas signal:** Full Atlas signal computation for 500 symbols must complete in < 5 seconds.
- **Screener:** Screener results for any single-criterion filter must appear in < 500ms. Multi-criterion filters with fundamentals data: < 2 seconds.
- **Memory:** At steady state (PriceData loaded for 500 symbols × 7 years daily data × 6 price fields) ≈ 500 × 1800 × 6 × 8 bytes ≈ 43MB of raw price data. With pandas overhead: expect 200–400MB total application RSS. Must stay below 1.5GB to be safe on 8GB machines.
- **Data loading:** Loading 500 CSV files at startup must use multiprocessing or a fast sequential read. Use `pandas.read_csv` with `dtype` hints to minimize parsing overhead. Profiling target: < 6 seconds for 500 × 1,800 rows.

### 33.2 Reliability

- All background workers must catch all exceptions and emit a failure signal to the UI. No unhandled exceptions in worker threads (these crash the application silently on Windows).
- The application must not lose journal entries, portfolio state, or alert configurations on crash. Use SQLite transactions: every write to portfolio/journal is wrapped in `BEGIN IMMEDIATE ... COMMIT`. If the app crashes between writes, the DB is left in the state of the last committed transaction.
- Auto-save workspace layout on every panel move/resize (debounced: save no more than once per 5 seconds of inactivity after a change).
- Rotating log file: `logs/atlas_terminal.log` with a 5MB max size and 3 backup rotations.

### 33.3 Nuitka Compilation Requirements

- **No `__file__` for resource access.** Use `importlib.resources` or a `get_resource_path()` utility that returns the correct path both in development (relative to source root) and in the Nuitka exe (relative to `sys.executable`).
- **No dynamic module imports** outside of try/except guarded Kronos loading. All `import` statements at module level.
- **Include directives for Nuitka build:** `--include-package=pyqtgraph`, `--include-package=pandas`, `--include-package=jugaad_data`, `--include-data-dir=data=data`, `--include-data-dir=assets=assets`.
- **Qt plugins:** Nuitka's Qt plugin (`--enable-plugin=pyqt6`) handles most PyQt6 compilation. Verify that `QDockWidget`, `QWebEngineView` (avoid this — use `QTextBrowser` instead), `QAbstractItemModel`, and `QGraphicsScene` all compile correctly in a pre-build test fixture.
- **No `ctypes` or platform-specific hacks** that aren't wrapped in try/except with graceful fallback.
- **Test the `.exe` on a machine with no Python installation** before each milestone release.

### 33.4 Data Privacy

- All user data (portfolio, journal, alerts) is stored locally. Nothing is transmitted to any cloud service.
- Email alert credentials (SMTP password) are stored in SQLite with AES-256 encryption using a machine-derived key (same pattern as the existing `HEL·SAMAST` Bridge — `Windows MachineGuid + CPU ID` hash as the key derivation input).
- No analytics, crash reporting, or telemetry of any kind.

### 33.5 Accessibility

- All buttons and interactive elements have `setToolTip()` calls with descriptive text.
- Keyboard navigation: Tab order is logical within each panel (top-to-bottom, left-to-right).
- The status bar and alert toasts are not the only mechanism for important information (alerts also appear in the Alert Manager panel).
- Colorblind mode (Section 31.1) ensures up/down is not communicated by color alone.

---

## 34. Phased Delivery Roadmap

### Phase 1 — Core Terminal (Months 1–3)

Goal: A working NSE terminal that replaces the current CLI workflow. The user can run the full Friday signal workflow from the GUI.

Modules:
- Module 01 — Application Shell & Panel System (QDockWidget-based, 5 default workspaces, link groups)
- Module 02 — Command Bar (ticker lookup, core commands)
- Module 03 — Market Data & Quote Display (EOD from local data; basic yfinance quote refresh)
- Module 04 — Charting Engine (candlestick/line/area, 15 indicators, 8 drawing tools, daily/weekly/monthly from local data)
- Module 05 — Watchlists (3 watchlists, basic columns)
- Module 11 — Portfolio & Manual Trade Manager (manual entry, GTT tracker, basic P&L)
- Module 14 — Atlas Engine (full signal computation, Configure dialog, signal panel with actions/holds/candidates)
- Module 15 — Backtester (full backtest UI wrapping existing backtest_vectorbt.py)
- Module 24 — Data Download Manager (jugaad bhavcopy + yfinance tabs, progress log)
- Module 25 — Settings (all settings sections, Nuitka packaging)

Phase 1 exit criteria: The user can double-click AtlasTerminal.exe, see their portfolio, run data downloads, generate the Atlas Friday signal, and view charts — all without touching a terminal.

### Phase 2 — Intelligence Layer (Months 4–6)

Modules:
- Module 06 — Screener (full filter set, built-in presets)
- Module 07 — News & Announcements (NSE announcements, basic news, sentiment tagging)
- Module 08 — Fundamentals (yfinance fundamentals, Screener.in import)
- Module 13 — Catalyst & Event Calendar (earnings dates, dividends, F&O expiry, RBI meetings)
- Module 16 — Market Breadth (% above SMA50, A/D line, New Highs/Lows, sector breadth)
- Module 21 — Trade Journal & Playbook (full journal, analytics, playbook)
- Module 22 — Sector Heatmap (treemap, sector performance table)
- Module 25 — Alert System (price, RSI, Atlas rank, GTT proximity alerts; in-app toast + desktop notification)

Phase 2 exit criteria: The user can research stocks, track their journal, monitor market breadth, and receive alerts — entirely within AtlasTerminal.

### Phase 3 — Depth Layer (Months 7–10)

Modules:
- Module 09 — NSE F&O Analytics (options chain EOD, OI chart, PCR, max pain)
- Module 10 — Macro & Economic Dashboard (RBI dashboard, India macro charts, global sidebar)
- Module 12 — Risk Analytics (correlation matrix, beta exposure, tax estimation)
- Module 17 — FII/DII Flow Tracker
- Module 18 — Block Deals & Bulk Deals
- Module 19 — Delivery & Institutional Data
- Module 20 — Promoter & Insider Holdings
- Module 23 — Relative Strength & Correlation (RS rank screener, correlation matrix)

Phase 3 exit criteria: Professional-grade institutional and alternative data coverage for NSE equities. The terminal is a complete research and monitoring environment.

### Phase 4 — Polish & Power (Months 11–12)

- Kronos standalone signal panel (UI wrapper for kronos_signal.py and kronos_predict.py)
- Chart replay mode
- Custom indicator scripting (simplified Python-based indicator definition)
- Module 19 Signal History Explorer (Atlas Module 14 extension)
- Performance optimization pass (startup time, chart render, screener latency)
- Parameter sensitivity analysis in Backtester (Module 15 extension)
- Complete Nuitka packaging, installer creation (Inno Setup or NSIS), auto-update stub
- Full E2E test suite for the signal workflow

---

## 35. Indian Market Reference Data

The developer must implement the following as hard-coded reference data (not fetched from a database), used throughout the application. Store in a `market_constants.py` module.

### 35.1 NSE Indices and Symbols

```python
NSE_INDICES = {
    "NIFTY50":        {"yf_ticker": "^NSEI",         "display": "Nifty 50"},
    "NIFTYBANK":      {"yf_ticker": "^NSEBANK",       "display": "Nifty Bank"},
    "NIFTYMIDCAP150": {"yf_ticker": "NIFTYMIDCAP150.NS", "display": "Nifty Midcap 150"},
    "NIFTYSMALLCAP":  {"yf_ticker": "NIFTYSMALLCAP250.NS", "display": "Nifty Smallcap 250"},
    "NIFTYAUTO":      {"yf_ticker": "^CNXAUTO",       "display": "Nifty Auto"},
    "NIFTYFMCG":      {"yf_ticker": "^CNXFMCG",       "display": "Nifty FMCG"},
    "NIFTYIT":        {"yf_ticker": "^CNXIT",          "display": "Nifty IT"},
    "NIFTYMETAL":     {"yf_ticker": "^CNXMETAL",       "display": "Nifty Metal"},
    "NIFTYPHARMA":    {"yf_ticker": "^CNXPHARMA",      "display": "Nifty Pharma"},
    "NIFTYENERGY":    {"yf_ticker": "^CNXENERGY",      "display": "Nifty Energy"},
    "INDIAVIX":       {"yf_ticker": "^INDIAVIX",       "display": "India VIX"},
}
```

### 35.2 Market Hours (IST = UTC+5:30)

```python
MARKET_HOURS = {
    "pre_open_start":   time(9, 0),
    "pre_open_end":     time(9, 15),
    "regular_open":     time(9, 15),
    "regular_close":    time(15, 30),
    "post_close_start": time(15, 40),
    "post_close_end":   time(16, 0),
    "timezone":         "Asia/Kolkata",
}
```

### 35.3 Transaction Cost Schedule (as of FY2025-26)

```python
TRANSACTION_COSTS = {
    "stt_delivery_pct":           0.001,    # 0.1% on buy+sell
    "nse_txn_charges_pct":        0.0000322, # ₹3.22 per lakh
    "sebi_turnover_fee_pct":      0.000001,  # ₹1 per cr
    "stamp_duty_pct":             0.00015,   # 0.015% on buy only
    "gst_on_charges_pct":         0.18,      # 18% on brokerage + exchange charges
    "stcg_rate":                  0.20,      # 20% (post July 23, 2024 budget)
    "ltcg_rate":                  0.125,     # 12.5% (post July 23, 2024 budget)
    "ltcg_exemption_inr":         125_000,   # ₹1.25 lakh per year
    "surcharge_applicable":       False,     # apply if applicable for high-income users
}
```

Note: Tax rates changed in the Union Budget July 23, 2024 (STCG: 15%→20%; LTCG: 10%→12.5%; LTCG exemption: ₹1 lakh → ₹1.25 lakh). The developer must verify these rates against the most current Finance Act before coding the tax estimator. Add a settings override so users can adjust if rates change again.

### 35.4 GICS/NSE Sector Mapping

The universe CSV uses sector names. Map these to standardized display names and associated NSE sector index symbols. The default sectors from NSE's classification:

Energy | Financial Services | Fast Moving Consumer Goods | Healthcare | Information Technology | Metals | Oil Gas & Consumable Fuels | Realty | Automobile and Auto Components | Capital Goods | Construction | Chemicals | Consumer Durables | Diversified | Forest Materials | Media Entertainment & Publication | Power | Services | Telecommunication | Textiles | Transportation

The `max_per_sector` Atlas constraint uses these sector labels as provided in the universe CSV.

---

## 36. Glossary

**ADV30** — 30-day average daily value (traded turnover in ₹ crore). The Atlas liquidity filter uses ADV30 ≥ ₹15 crore.

**ATM** — At the Money. An options contract with a strike price equal to or very close to the current spot price.

**Beta** — The sensitivity of a stock's returns to the benchmark (Nifty 50 for NSE stocks). Beta of 1.5 means the stock tends to move 1.5% for every 1% move in Nifty 50.

**Bhavcopy** — NSE's daily market-wide data file. Contains OHLCV for all traded securities. Source for all price data in Atlas when using the bhavcopy download path.

**BMS** — In the context of market sessions: "Before Market Session" (pre-open). Not to be confused with Battery Management System.

**CIN** — Corporate Identity Number. Unique identifier for registered Indian companies, assigned by the Ministry of Corporate Affairs.

**Circuit breaker / Circuit limit** — Upper and lower price bands (typically ±5%, ±10%, or ±20% from the previous close) within which NSE allows a stock to trade in a session. When the price hits the limit, trading may be halted or only one side (buyer/seller) exists.

**CRR** — Cash Reserve Ratio. The fraction of a bank's total deposits that must be held in reserve with the RBI. RBI uses CRR as a monetary policy tool.

**DII** — Domestic Institutional Investor. Indian institutions such as mutual funds, insurance companies, and pension funds. Counterpart to FII.

**DTAA** — Double Taxation Avoidance Agreement. Relevant for FII taxation.

**EQ series** — The standard equity trading series on NSE (normal delivery-based equity trades). Contrast with BE (trade-to-trade), BZ (permitted-to-trade companies), N2 (Nifty 50), etc.

**F&O** — Futures and Options. NSE's equity derivatives segment. Not all stocks are F&O-eligible (currently ~200 stocks + indices).

**FII** — Foreign Institutional Investor. Foreign entities registered with SEBI to invest in Indian equity and debt markets. FII flow data is a key institutional sentiment indicator.

**GTT** — Good Till Triggered. A conditional order type offered by Indian brokers (Groww, Zerodha) where an order is placed only when a trigger price condition is met. AtlasTerminal uses GTT for the 12%-below-entry catastrophe stop.

**IIP** — Index of Industrial Production. India's monthly manufacturing output indicator, published by MOSPI.

**Ind AS** — Indian Accounting Standards. India's equivalent of IFRS (International Financial Reporting Standards), adopted by listed companies.

**ISIN** — International Securities Identification Number. A 12-character alphanumeric code uniquely identifying a security globally. INE prefix for Indian equities.

**LODR** — Listing Obligations and Disclosure Requirements. SEBI's regulatory framework governing what listed companies must disclose and when.

**LTCG** — Long-Term Capital Gains. In India, equity held for > 12 months. Tax: 12.5% on gains above ₹1.25 lakh (post July 23, 2024 budget).

**Max Pain** — The options strike price at which the maximum number of outstanding contracts (calls + puts combined) would expire worthless. Price tends to gravitate toward max pain near expiry due to dealer hedging activity.

**MPC** — Monetary Policy Committee. The RBI's rate-setting committee, comprising 6 members (3 RBI officials + 3 external). Meets 6 times per year to set the repo rate.

**MSCI EM** — MSCI Emerging Markets Index. Important because Indian equities have a ~18–20% weight in this index. When MSCI rebalances, FII flows into/out of India change substantially.

**NSE** — National Stock Exchange of India. Primary exchange where Project Atlas trades. Bhavcopy is NSE's daily data file.

**OHLCV** — Open, High, Low, Close, Volume. The five standard fields in a price bar.

**PCR** — Put-Call Ratio. Total put OI / total call OI. A reading above 1 indicates more bearish positioning (more puts than calls outstanding); below 1 indicates bullish positioning.

**PIT** — Prohibition of Insider Trading. SEBI's regulatory framework governing insider trading disclosures. Promoters and KMPs must file Form C within 2 trading days of any trade.

**Pledging** — Promoters pledge their shares as collateral to raise loans. High and increasing promoter pledge % is a significant risk flag — if the stock falls, the lender may sell pledged shares, causing further price decline (a "pledge cascade").

**PDUFA** — Not applicable to Indian markets. India's equivalent for pharma companies: CDSCO (Central Drugs Standard Control Organisation) approval dates.

**Repo Rate** — The rate at which the RBI lends money to commercial banks. The primary interest rate tool. Higher repo = tighter monetary policy = bearish for equities (higher cost of capital, lower valuations).

**RoE** — Return on Equity. Net Profit / Shareholders' Equity. A key measure of capital efficiency.

**SAST** — Substantial Acquisition of Shares and Takeovers. SEBI's takeover code requiring disclosure when an entity acquires > 5% of a company's equity.

**SEBI** — Securities and Exchange Board of India. The market regulator for securities markets in India. Equivalent to the US SEC.

**SGX Nifty** — Nifty 50 futures listed on the Singapore Exchange (SGX). Trades outside Indian market hours and serves as a leading indicator for where the Indian market will open.

**SLB** — Securities Lending and Borrowing. The NSE mechanism for short selling (borrow shares, sell them short, return later). Retail participation is low but FIIs use this.

**SLR** — Statutory Liquidity Ratio. The minimum percentage of a bank's total deposits that must be maintained in liquid assets (gold, government securities). Complementary to CRR.

**STCG** — Short-Term Capital Gains. In India, equity held for ≤ 12 months. Tax: 20% on gains (post July 23, 2024 budget).

**STT** — Securities Transaction Tax. Applied on every buy and sell of listed equities in India. Currently 0.1% on delivery equity trades.

**T+1** — Trade plus 1 day settlement. India moved to T+1 settlement for all equity trades in January 2023. Shares are delivered to the buyer's demat account by the next trading day.

**T2T / BE series** — Trade-to-Trade or Book Entry series. Stocks where intraday square-off is not permitted. Each buy must result in delivery; each sell must be delivery-based. Used by NSE for illiquid or under-surveillance stocks.

**VWAP** — Volume Weighted Average Price. The average price at which a security traded throughout the session, weighted by volume. Key institutional benchmark for execution quality.

**WPI** — Wholesale Price Index. India's producer price inflation measure, complementary to CPI.

---

*End of Document — AtlasTerminal PRD v1.0*

*This document is the complete specification for AtlasTerminal. The developer should treat every described feature as a build requirement unless explicitly marked P2 or P3 (medium or future priority). All existing Python modules (`alpha_engine.py`, `backtest_vectorbt.py`, `data_fetcher.py`, `kronos_engine.py`, `kronos_predict.py`, `kronos_signal.py`, `kronos_strategy.py`, `portfolio_manager.py`, `alert_system.py`, `config.py`, `download_data.py`, `download_yahoo_data.py`) are reused without modification. AtlasTerminal wraps them in a professional PyQt6 GUI. The codebase should be structured so that the CLI scripts remain runnable independently for backward compatibility.*
