# `jugaad-data` Library Documentation

`jugaad-data` is a powerful Python library and command-line interface (CLI) tool designed for downloading historical stock market data and fetching live market data from the National Stock Exchange of India (NSE). 

Below is the comprehensive documentation detailing how to use the Python API and the CLI.

---

## Table of Contents

1. [Historical Data (Python API)](#1-historical-data-python-api)
    * [Download Bhavcopies](#download-bhavcopies)
    * [Download Historical Stock Data](#download-historical-stock-data)
    * [Download Historical Index Data](#download-historical-index-data)
    * [Download Historical Derivatives Data](#download-historical-derivatives-data)
2. [Live Market Data (Python API)](#2-live-market-data-python-api)
    * [Market and Index Data](#market-and-index-data)
    * [Live Stock and F&O Data](#live-stock-and-fo-data)
    * [Corporate Announcements](#corporate-announcements)
3. [Command Line Interface (CLI)](#3-command-line-interface-cli)
    * [Bhavcopies](#bhavcopies-cli)
    * [Historical Stock Data](#historical-stock-data-cli)
    * [Historical Index Data](#historical-index-data-cli)
    * [Futures & Options Data](#futures--options-data-cli)

---

## 1. Historical Data (Python API)

The historical data module provides methods to download past bhavcopies, stock data, index data, and derivatives (Futures & Options) data. Outputs can be loaded directly into a Pandas DataFrame or saved as CSV files.

### Download Bhavcopies
You can download bhavcopies for stocks, indices, and futures & options (F&O) for a specific date and save them to a target directory.

```python
from datetime import date
from jugaad_data.nse import bhavcopy_save, full_bhavcopy_save, bhavcopy_fo_save, bhavcopy_index_save

# Download different bhavcopies for 1st Jan 2020
bhavcopy_save(date(2020, 1, 1), "/path/to/directory")
full_bhavcopy_save(date(2020, 1, 1), "/path/to/directory")
bhavcopy_fo_save(date(2020, 1, 1), "/path/to/directory")
bhavcopy_index_save(date(2020, 1, 1), "/path/to/directory")
```
> **Note:** The difference between `bhavcopy_save` and `full_bhavcopy_save` is that the full bhavcopy includes the percentage of volume that was delivered.

### Download Historical Stock Data
Download historical data for individual equities.

```python
from datetime import date
from jugaad_data.nse import stock_csv, stock_df

# Download as a pandas dataframe
df = stock_df(symbol="SBIN", from_date=date(2020,1,1), to_date=date(2020,1,30), series="EQ")
print(df.head())

# Download data and save directly to a CSV file
stock_csv(symbol="SBIN", from_date=date(2020,1,1), to_date=date(2020,1,30), series="EQ", output="/path/to/file.csv")
```

### Download Historical Index Data
Download historical data for market indices (e.g., NIFTY 50).

```python
from datetime import date
from jugaad_data.nse import index_csv, index_df

# Download as a pandas dataframe
df = index_df(symbol="NIFTY 50", from_date=date(2020,1,1), to_date=date(2020,1,30))
print(df.head())

# Download as a CSV file
index_csv(symbol="NIFTY 50", from_date=date(2020,1,1), to_date=date(2020,1,30), output="/path/to/file.csv")
```

### Download Historical Derivatives Data

#### 1. Get Expiry Dates
For a given trading day, you can fetch the expiry dates of all active contracts.

```python
from datetime import date
from jugaad_data.nse import expiry_dates

# All active expiry dates
expiries = expiry_dates(date(2020,1,1))
print(expiries)

# Filter by contract type (e.g., FUTSTK)
expiries_futstk = expiry_dates(date(2020,1,1), "FUTSTK")
print(expiries_futstk)
```

#### 2. Master Functions for F&O Data
The library provides master functions to download derivative data as DataFrames or CSVs:
*   `derivatives_df(symbol, from_date, to_date, expiry_date, instrument_type, option_type, strike_price)`
*   `derivatives_csv(symbol, from_date, to_date, expiry_date, instrument_type, option_type, strike_price, output)`

**Arguments:**
*   `symbol`: Stock symbol (e.g., "SBIN") or Index symbol (e.g., "NIFTY")
*   `from_date`: Start date (`datetime.date`)
*   `to_date`: End date (`datetime.date`)
*   `expiry_date`: Expiry date (`datetime.date`)
*   `instrument_type`: Accepts `"FUTSTK"`, `"FUTIDX"`, `"OPTSTK"`, or `"OPTIDX"`
*   `option_type`: `"CE"` for call option and `"PE"` for put option (Required for `OPTSTK` and `OPTIDX`)
*   `strike_price`: Strike price as a float (Required for `OPTSTK` and `OPTIDX`)
*   `output`: Name/path of the output CSV file (Only for `derivatives_csv`)

#### Examples

**Stock Futures**
```python
from jugaad_data.nse import derivatives_df
df = derivatives_df(symbol="SBIN", from_date=date(2020,1,1), to_date=date(2020,1,30),
                    expiry_date=date(2020,1,30), instrument_type="FUTSTK")
```

**Stock Options**
```python
df = derivatives_df(symbol="SBIN", from_date=date(2020,1,1), to_date=date(2020,1,30),
                    expiry_date=date(2020,1,30), instrument_type="OPTSTK", 
                    option_type="CE", strike_price=300.0)
```

**Index Futures**
```python
df = derivatives_df(symbol="NIFTY", from_date=date(2020,1,1), to_date=date(2020,1,30),
                    expiry_date=date(2020,1,30), instrument_type="FUTIDX")
```

**Index Options**
```python
df = derivatives_df(symbol="NIFTY", from_date=date(2020,1,1), to_date=date(2020,1,30),
                    expiry_date=date(2020,1,30), instrument_type="OPTIDX", 
                    option_type="CE", strike_price=12000.0)
```

---

## 2. Live Market Data (Python API)

The `NSELive` class holds all methods required to fetch live market data from the NSE. *Note: If you are a beginner, proficiency with Python dictionaries and lists is recommended, as the NSE returns rich, nested JSON data.*

First, initialize the class:
```python
from jugaad_data.nse import NSELive
n = NSELive()
```

### Market and Index Data

**Market Status**
Returns the status of different markets (Capital, Currency, Commodity, etc.).
```python
status = n.market_status()
print(status['marketState']) 
```

**All Indices**
Fetches the current values, advances/declines, and historical changes of all broader market indices.
```python
all_indices = n.all_indices()

# Print advances and declines
print(all_indices['advances'], all_indices['declines'])

# Print values for all available indices
for idx in all_indices['data']:
    print("{} - {}".format(idx['index'], idx['last']))
```

**Individual Index Data**
Get detailed metadata and price info for a specific index.
```python
nifty = n.live_index("NIFTY 50")
print(nifty['marketStatus'])
print(nifty['data'][0]) # Main price & volume information
print(nifty['advance']) # Declines/advances/unchanged data
```

**Market Turnover**
Get turnover data across different segments (Equities, Futures, Options, Currency, etc.).
```python
turnover = n.market_turnover()
for t in turnover['data']:
    print("{} - {}".format(t['name'], t['today']))
```

### Live Stock and F&O Data

**Live Stock Data**
Fetch detailed information for a specific stock, including current price, company info, security info, and pre-open data.
```python
q = n.stock_quote("HDFC")

print(q['priceInfo'])     # Last price, VWAP, high/low, upper/lower circuits
print(q['info'])          # General company info, active series
print(q['metadata'])      # ISIN, industry, PE
print(q['securityInfo'])  # Trading segment, face value, issued capital
print(q['preOpenMarket']) # Pre-open market order quantities and final price
```

**Live Tick Data**
Fetch intraday tick-level graph data.
```python
tick_data = n.tick_data("HDFC")
print(tick_data['grapthData'][0:10]) # Returns list of [timestamp, price] pairs
```

**Stock Trade Information**
Fetch bulk/block deals, market depth (order book), value at risk, and delivery position data.
```python
trade_info = n.trade_info("HDFC")
print(trade_info['marketDeptOrderBook'])
```

**Live Option Chains**
Fetch full option chains for Indices, Equities, and Currencies.
```python
option_chain = n.index_option_chain("NIFTY") 
eq_option_chain = n.equities_option_chain("RELIANCE") 
curr_option_chain = n.currency_option_chain("USDINR") 

# Fetch expiry dates from an option chain
print(option_chain['records']['expiryDates'])

# Iterate through strike prices, mapping CE (Call) and PE (Put) prices
for option in option_chain['filtered']['data'][80:100]:
    print("{}\t{}\t{}".format(option['CE']['lastPrice'], option['strikePrice'], option['PE']['lastPrice']))
```

**Equity Derivative Turnover**
View highest turnover contracts in derivatives.
```python
turnover = n.eq_derivative_turnover()
for t in turnover['value']:
    print("{} \t {}".format(t['identifier'], t['totalTurnover']))
```

**Stock Futures and Options Live Quote**
Fetch last traded prices and detailed metadata for all F&O contracts of a specific stock.
```python
quotes = n.stock_quote_fno("HDFC")

# Print all available contracts and their last traded price
for quote in quotes['stocks']:
    print("{}\t{}".format(quote['metadata']['identifier'], quote['metadata']['lastPrice']))

# Inspect detailed info for the first contract (order book, OI, volatility, etc.)
print(quotes['stocks'][0])
```

### Corporate Announcements

Fetch company announcements. You can pass a date range and a specific symbol to filter results, or call it without arguments to get the latest announcements market-wide.

```python
from datetime import date
import pprint

# With filters
an = n.corporate_announcements(from_date=date(2025,6,9), to_date=date(2025,6,10), symbol="NH")
pprint.pprint(an)

# By symbol only
an_symbol = n.corporate_announcements(symbol="NH")

# Without any filters (latest market-wide announcements)
an_all = n.corporate_announcements()
```

---

## 3. Command Line Interface (CLI)

`jugaad-data` provides a robust CLI tool named `jdata` to download data directly from your terminal to CSV files. 

Access the main help menu using:
```bash
$ jdata --help
```

### Bhavcopies (CLI)
Download daily bhavcopies.
```bash
# View options
$ jdata bhavcopy --help

# Download today's bhavcopy (works after market hours)
$ jdata bhavcopy -d /path/to/dir

# Download bhavcopy for a specific date
$ jdata bhavcopy -d /path/to/dir -f 2020-01-01

# Download bhavcopies for a date range
$ jdata bhavcopy -d /path/to/dir -f 2020-01-01 -t 2020-01-30

# Download full bhavcopies (includes delivery trade quantity)
$ jdata bhavcopy -d /path/to/dir -f 2020-01-01 -t 2020-01-30 --full

# Download index bhavcopies
$ jdata bhavcopy -d /path/to/dir -f 2020-01-01 -t 2020-01-30 --idx

# Download derivatives (F&O) bhavcopies
$ jdata bhavcopy -d /path/to/dir -f 2020-01-01 -t 2020-01-30 --fo
```

### Historical Stock Data (CLI)
Download historical prices for specific stock symbols.
```bash
# View options
$ jdata stock --help

# Download historical stock data
$ jdata stock -s SBIN -f 2020-01-01 -t 2020-01-31 -o SBIN-Jan.csv
```

### Historical Index Data (CLI)
Download historical prices for indices.
```bash
# View options
$ jdata index --help

# Download historical index data
$ jdata index -s "NIFTY 50" -f 2020-01-01 -t 2020-01-31 -o NIFTY-Jan.csv
```

### Futures & Options Data (CLI)
Download specific derivative contracts.
```bash
# View options
$ jdata derivatives --help

# Download Stock Futures
$ jdata derivatives -s SBIN -f 2020-01-01 -t 2020-01-30 -e 2020-01-30 -i FUTSTK -o file_name.csv

# Download Index Futures
$ jdata derivatives -s NIFTY -f 2020-01-01 -t 2020-01-30 -e 2020-01-30 -i FUTIDX -o file_name.csv

# Download Stock Call Options (CE)
$ jdata derivatives -s SBIN -f 2020-01-01 -t 2020-01-30 -e 2020-01-30 -i OPTSTK -p 330 --ce -o file_name.csv

# Download Index Put Options (PE)
$ jdata derivatives -s NIFTY -f 2020-01-01 -t 2020-01-23 -e 2020-01-23 -i OPTIDX -p 11000 --pe -o file_name.csv
```