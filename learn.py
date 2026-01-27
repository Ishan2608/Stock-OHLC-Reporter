# %%
import json

import pandas as pd
import yfinance as yf

from learn_utility import display_news_article, print_separation

# %%
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)

# %%
"""
1. CREATE A TICKER OBJECT
- The Ticker class is the primary entry point for accessing data related to a specific financial instrument.
- It acts as an object-oriented wrapper around the Yahoo Finance API for a given symbol.
- You instantiate it by passing the ticker string (e.g., "AAPL" for Apple Inc. or "BTC-USD" for Bitcoin).

Syntax:
    import yfinance as yf
    ticker_object = yf.Ticker("SYMBOL")
For Indian Stock Market, append the suffic .NS and .BO for NSE and BSE data respectively.
Example:
    ticker_NSE = yf.Ticker('TCS.NS')
    ticker_BSE = yf.Ticker('TCS.BO')

Use `.info` propertyfor getting information about the stock. This returns a dictionary.
"""
ticker_NSE = yf.Ticker("TCS.NS")
ticker_BSE = yf.Ticker("TCS.BO")


# View all available key in info dictionary
def get_all_info_keys(ticker):
    print_separation("Available Keys in Info Dictionary")
    for key in ticker.info:
        print(f"{key}: {ticker.info[key]}")


# get_all_info_keys(ticker_NSE)

# print(f"===============================================================================")
# print(f"Current price: {ticker_NSE.info['currentPrice']}")
# print(f"Lowest price in last one year: {ticker_NSE.info['fiftyTwoWeekLow']}")
# print(f"Highest price in last one year: {ticker_NSE.info['fiftyTwoWeekHigh']}")
# print(f"===============================================================================")

# %%
"""
NOTE:
    - Accessing ticker.info multiple times (as in your loops and print statements) is inefficnet.
    - It triggers a fresh network request each time, which can lead to rate limiting.
    - It is more efficient to store the dictionary in a variable first.
"""

tcs_info = ticker_NSE.info
print_separation("Accessing Info Keys")
print(f"Complete Company Name: {tcs_info.get('longName')}")
print(f"Type: {tcs_info.get('typeDisp')}")
print(f"Currency: {tcs_info.get('financialCurrency')}")
print(f"Current price: {tcs_info.get('currentPrice')}")
print(f"52-Week Low: {tcs_info.get('fiftyTwoWeekLow')}")
print(f"52-Week High: {tcs_info.get('fiftyTwoWeekHigh')}")
print(f"52-Week Change %: {tcs_info.get('fiftyTwoWeekChangePercent')}")
# print(f"52-Week High: {tcs_info.get('')}")

# %%
"""
2. UPCOMING FINANCIAL EVENTS FOR THE TICKER
- The .calendar property provides a dictionary of upcoming corporate events.
- Such as earnings announcement dates and ex-dividend dates.
"""

cal = ticker_NSE.calendar
print_separation("Upcoming Financial Events")
for k, v in cal.items():
    print(f"{k}: {v}")

# %%
"""
3. READ NEWS ARTICLES ASSOCIATED WITH THE TICKER
- The .news property returns a list of dictionaries, where each dictionary represents a recent article.
- Properties: 'title', 'publisher', 'link', and 'provider_publish_time'.
- The time is provided in Unix epoch format.
"""

print_separation("News Articles")
news = ticker_NSE.news
article1 = news[0]

print_separation("View a Single Article Dictionary")
formatted_json = json.dumps(article1, indent=4)
print(formatted_json)

print_separation("View a Single Formatted Article")
display_news_article(article1)

# for article in news:
#     display_news_article(article)

# %%
"""
5. HISTORICAL DATA
- Use the .history() method to retrieve OHLCV data.
- Returns a pandas DataFrame with Date as the index.
- Automatically adjusts for stock splits and dividends by default (auto_adjust=True).

Examples:
- Today's price: Uses period='1d' with small intervals like '1m'.
- 30-day price: Uses period='1mo' with '1d' intervals.
- 1-year price: Uses period='1y' with '1d' intervals.
"""
# Initialize Ticker for Wipro
wipro = yf.Ticker("WIPRO.NS")

print_separation(f"Fetch Historical Data for {wipro.info['longName']}")

# Fetching today's price data (Intraday)
# Note: 1m interval data is only available for the last 7 days.
today_df = wipro.history(period="1d", interval="1m")
current_price = today_df["Close"].iloc[-1] if not today_df.empty else "N/A"
print(f"Current Wipro Price (NSE): {current_price}")

# Fetching previous 30 days data
monthly_df = wipro.history(period="1mo", interval="1d")
print("\nLast 30 Days High/Low:")
print(monthly_df[["High", "Low"]].tail())

# Fetching 1 year data
yearly_df = wipro.history(period="1y", interval="1d")
print("\nYearly Data Summary (First 5 rows):")
print(yearly_df.head())

# %%
"""
6. FUNDAMENTAL ANALYSES
Three core financial statements:
    - The Income Statement: <ticker_obj>.financials, and <ticker_obj>.quaterly_financials
    - Balance Sheet: <ticker_obj>.balance_sheet, and <ticker_obj>.quarterly_balance_sheet
    - Cash Flow Statement. <ticker_obj>.cashflow and <ticker_obj>.quarterly_cashflow
"""

tata_steel = yf.Ticker("TATASTEEL.NS")

# %%
"""
- financials: Returns annual data for the last 4 years.
- quarterly_financials: Returns data for the last 4 quarters.
- Rows represent metrics (Revenue, EBITDA, Net Income), columns represent dates.
"""

# Fetch and display the annual Income Statement
income_stmt = tata_steel.financials

print_separation("Annual Income Statement (Latest 2 Years):")
# Use .iloc to slice the first two columns (most recent years)

print(income_stmt.iloc[:, :2])
# Access a specific metric like 'Total Revenue'
if "Total Revenue" in income_stmt.index:
    latest_revenue = income_stmt.loc["Total Revenue"].iloc[0]
    print(f"\nLatest Annual Revenue: {latest_revenue}")

# %%
"""
- balance_sheet: Annual snapshot of Assets, Liabilities, and Equity.
- quarterly_balance_sheet: Snapshot for the last 4 reporting quarters.
"""

# Fetch quarterly Balance Sheet for Tata Steel
quarterly_bs = tata_steel.quarterly_balance_sheet

print_separation("Quarterly Balance Sheet (Most Recent Quarter):")
# Display only the most recent quarter (first column)
print(quarterly_bs.iloc[:, 0])

# %%
"""
- cashflow: Tracks annual cash movements.
- quarterly_cashflow: Tracks quarterly cash movements.
"""
# Fetch annual Cash Flow
cash_flow = tata_steel.cashflow

print_separation("Annual Cash Flow (Top 5 Rows):")
print(cash_flow.head(5))
