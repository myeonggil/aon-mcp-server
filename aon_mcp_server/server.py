import re
import yfinance
import pandas as pd
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP(name="AON")

###### example ######
# # Add an addition tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b


# # Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"

# @mcp.tool(
#     name="stock_data",
#     description="Fetch metrics for stocks by ticker symbols or names."
# )
# def stock_data(input_str: str = None, **kwargs):
#     input_str = kwargs.get('input', input_str)
#     if not input_str:
#         return {
#             "error": "No input provided."
#         }

#     # Extract tickers
#     if ',' in input_str:
#         tickers = [t.strip().upper() for t in input_str.split(',')]
#     else:
#         tickers = [w.upper() for w in re.findall(r"\b[A-Za-z]{1,5}\b", input_str)]
#     # Fallback common names
#     common = {
#         "apple": "APPL",
#         "nvidia": "NVDA"
#     }
#     if not tickers:
#         for name, t in common.items():
#             if name in input_str.lower(): tickers.append(t)
#     results = {}
#     for t in tickers:
#         tk = yfinance.Ticker(t)
#         hist = tk.history(period="1mo")
#         if hist.empty:
#             results[t] = {"error": "No data."}
#             continue
#         first, last = hist.iloc[0], hist.iloc[-1]
#         change = float(last["Close"] - first["Close"])
#         pct = change / float(first["Close"]) * 100
#         info = tk.info
#         summary = {
#             "latest_price": float(last['Close']),
#             "price_change": change,
#             "%_change": pct,
#             "52_week_high": info.get('fiftyTwoWeekHigh'),
#             "52_week_low": info.get('fiftyTwoWeekLow'),
#             "market_cap": info.get('marketCap'),
#             "pe_ratio": info.get('trailingPE')
#         }
#         results[t] = summary
#     return results


# @mcp.tool(
#     name="web_scraper",
#     description="Scrape latest headlines and company snapshot from Finviz."
# )
# def web_scraper(input_str: str = None, **kwargs):
#     ticker = (kwargs.get('input') or input_str or '').upper()
#     url = f"https://finviz.com/quote.ashx?t={ticker.lower()}"
#     headers = {'User-Agent': 'Mozila/5.0'}
#     resp = requests.get(url, headers=headers)
#     soup = BeautifulSoup(resp.text, 'html.parser')
#     news = []
#     for row in soup.select('#news-table tr')[:5]:
#         date, title = row.find_all('td')
#         link = title.a['href']
#         if not link.startswith('http'):
#             link = urljoin(url, link)
#         news.append(
#             {
#                 "data": date.text,
#                 "title": title.text.strip(),
#                 "link": link
#             }
#         )
#         details = {}
#         snap = soup.find('table', {'class': 'snapshot-table2'})
#         for r in snap.find_all('tr'):
#             cells = r.find_all('td')
#             for i in range(0, len(cells), 2):
#                 details[cells[i].text] = cells[i + 1].text
#         return {
#             "news_items": news,
#             "snapshot": details
#         }

###### AON ######
@mcp.resource(
    uri="config://version",
    description="Server configuration"
)
def get_config() -> dict[str, str]:
    return {
        "version": "1.0.0"
    }


@mcp.prompt(description="AON Support")
def aon_prompt() -> str:
    return """
        example
    """


# if __name__ == '__main__':
#     mcp.run()
