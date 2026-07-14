

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")


MARKET_DATA_TOOL = {
    "type": "function",
    "function": {
        "name": "get_market_data",
        "description": (
            "Get the latest real-time or recent price for a stock, "
            "cryptocurrency, or foreign exchange (currency) pair. Use "
            "this whenever the user asks for a current price, rate, "
            "or quote — never guess a price from memory."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "asset_type": {
                    "type": "string",
                    "enum": ["stock", "crypto", "forex"],
                    "description": "Type of asset being asked about"
                },
                "symbol": {
                    "type": "string",
                    "description": (
                        "Ticker or code. Stock e.g. 'AAPL'. Crypto e.g. "
                        "'BTC'. Forex base currency e.g. 'USD'."
                    )
                },
                "target_currency": {
                    "type": "string",
                    "description": (
                        "Only for forex/crypto: the currency to quote "
                        "against, e.g. 'PKR' or 'USD'. Defaults to USD."
                    )
                }
            },
            "required": ["asset_type", "symbol"]
        }
    }
}


def get_market_data(asset_type, symbol, target_currency="USD"):

    if not ALPHA_VANTAGE_KEY:
        return {"error": "Market data API key not configured"}

    base_url = "https://www.alphavantage.co/query"

    if asset_type == "stock":
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_KEY
        }

    elif asset_type in ("crypto", "forex"):
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol,
            "to_currency": target_currency or "USD",
            "apikey": ALPHA_VANTAGE_KEY
        }

    else:
        return {"error": "Unsupported asset_type"}

    try:
        response = requests.get(base_url, params=params, timeout=10)
        return response.json()

    except Exception as e:
        return {"error": str(e)}