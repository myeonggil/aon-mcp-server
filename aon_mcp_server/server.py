import os
import asyncio

from typing import AsyncGenerator, Any

from configs import config
from mongodb_cluster import MongoDBCluster
from aon_models import AONModel

from groq.types.chat import ChatCompletionChunk
from fastmcp import FastMCP, Context
from pydantic import BaseModel
from nomic import embed, login
os.environ["TOKENIZERS_PARALLELISM"] = "true"
login(token=config["NOMIC_API_TOKEN"])

# Create an MCP server
mcp = FastMCP(name="aon_mcp_server")
mongodb_cluster = MongoDBCluster()
aon_model = AONModel()


class MessageRole(BaseModel):
    role: str
    content: str


class LLMParameter(BaseModel):
    model_name: str # llama-3.3-70b-versatile
    messages: list[MessageRole]
    stream: bool
    timeout: int
    temperature: float # more lower focus on consistency, more higher focus on newer answer
    max_tokens: int # response maximum token length(different by language) Between 512 and 1024
    top_p: int # random response match temperature 
    frequency_penalty: int # more lower use unique word
    presence_penalty: int # more lower use similar and repeat word

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
    uri="config://aon",
    description="Server configuration"
)
def get_config() -> dict[str, str]:
    return {
        "version": "1.0.0",
        "model": ""
    }


@mcp.prompt(description="AON Support")
def get_prompt(context_string: str, query: str) -> str:
    prompt = f"""
        You are helpful assistant.

        Remember that you answer a question, you must check to see 
        if it complies with your mission above. If not, you must respond, 
        "I am not able to answer this question". But, you must translate to Korean

        Use the following pieces of context to answer the question at the end.
        {context_string}
        Question: {query}
    """
    return prompt


class Test(BaseModel):
    res: list[float]

@mcp.tool(description="Embed input query")
async def process_embedding(query: str) -> AsyncGenerator:
    yield '12'


# @mcp.tool(description="Embed input query")
# async def process_embedding(query: str) -> list[float]:
#     embedded_query = embed.text([query])
#     return embedded_query['embeddings'][0]


@mcp.tool(description="Search vector DB")
async def search_vector(embedded_query: list[float]) -> list[str]:
    result = await mongodb_cluster.get_context_string_from_docs(embedded_query)
    return result


@mcp.tool(description="GROQ API call streamable")
async def get_stream(prompt: str) -> AsyncGenerator:
    response = await aon_model.get_chat_completion(prompt, True)
    chunk: ChatCompletionChunk
    async for chunk in response:
        message = chunk.choices[0].delta.content
        if message is not None:
            yield message
        await asyncio.sleep(0.01)


@mcp.tool(description="GROQ API call response")
async def get_string(prompt: str) -> str | None:
    response = await aon_model.get_chat_completion(prompt, False)
    if response.choices:
        return response.choices[0].message.content
    else:
        return None
