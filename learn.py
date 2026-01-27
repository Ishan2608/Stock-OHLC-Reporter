import json
import yfinance as yf
from learn_utility import print_separation, display_news_article

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
ticker_NSE = yf.Ticker('TCS.NS')
ticker_BSE = yf.Ticker('TCS.BO')

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

"""
2. UPCOMING FINANCIAL EVENTS FOR THE TICKER
- The .calendar property provides a dictionary of upcoming corporate events.
- Such as earnings announcement dates and ex-dividend dates.
"""

cal = ticker_NSE.calendar
print_separation("Upcoming Financial Events")
for k,v in cal.items():
    print(f"{k}: {v}")

"""
3. READ NEWS ARTICLES ASSOCIATED WITH THE TICKER
- The .news property returns a list of dictionaries, where each dictionary represents a recent article.
- Properties: 'title', 'publisher', 'link', and 'provider_publish_time'.
- The time is provided in Unix epoch format.
"""

print_separation('News Articles')
news = ticker_NSE.news
article1 = news[0]

print_separation("View a Single Article Dictionary")
formatted_json = json.dumps(article1, indent=4)
print(formatted_json)

print_separation("View a Single Formatted Article")
display_news_article(article1)

# for article in news:
#     display_news_article(article)
