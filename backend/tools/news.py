

import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


NEWS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_financial_news",
        "description": (
            "Get the latest financial or business news. "
            "Use this whenever the user asks for finance news, "
            "stock market news, crypto news, economy updates, "
            "or business headlines."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Topic to search, e.g. finance, bitcoin, stock market, economy"
                }
            },
            "required": ["query"]
        }
    }
}


def get_financial_news(query):

    if not NEWS_API_KEY:
        return {"error": "News API key not configured"}

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "pageSize": 5,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            # Surface the real reason (bad key, rate limit, plan
            # restriction, etc.) instead of failing silently.
            return {
                "error": data.get("message", "Unknown NewsAPI error"),
                "code": data.get("code")
            }

        news = []

        for article in data.get("articles", []):
            news.append({
                "title": article.get("title"),
                "source": (article.get("source") or {}).get("name"),
                "url": article.get("url")
            })

        return {"news": news}

    except Exception as e:
        return {"error": str(e)}