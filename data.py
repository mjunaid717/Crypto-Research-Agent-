import requests

# 🔹 Base URL
BASE_URL = "https://api.coingecko.com/api/v3"


# =========================================
# 🪙 1. Get price of ANY coin
# =========================================
def get_coin_price(coin_name):
    """
    Fetch price and 24h change for a given coin
    Example: bitcoin, ethereum, dogecoin, binancecoin
    """

    url = f"{BASE_URL}/simple/price"

    params = {
        "ids": coin_name.lower(),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if coin_name.lower() not in data:
            # Fallback mock data for demo
            mock_data = {
                "bitcoin": {"usd": 45000, "usd_24h_change": 2.5},
                "ethereum": {"usd": 2500, "usd_24h_change": -1.2},
                "dogecoin": {"usd": 0.08, "usd_24h_change": 5.0},
                "binancecoin": {"usd": 300, "usd_24h_change": 1.8}
            }
            if coin_name.lower() in mock_data:
                coin = mock_data[coin_name.lower()]
            else:
                return None

        else:
            coin = data[coin_name.lower()]

        return {
            "name": coin_name.upper(),
            "price": coin["usd"],
            "change": round(coin["usd_24h_change"], 2)
        }

    except Exception as e:
        # Fallback mock data
        mock_prices = {
            "bitcoin": {"price": 45000, "change": 2.5},
            "ethereum": {"price": 2500, "change": -1.2},
            "dogecoin": {"price": 0.08, "change": 5.0},
            "binancecoin": {"price": 300, "change": 1.8}
        }
        if coin_name.lower() in mock_prices:
            return mock_prices[coin_name.lower()]
        return {"error": str(e)}


# =========================================
# 📊 2. Get BTC + ETH (default quick view)
# =========================================
def get_major_coins():
    coins = ["bitcoin", "ethereum"]

    results = {}

    for coin in coins:
        data = get_coin_price(coin)
        if data:
            results[coin.upper()] = data

    return results


# =========================================
# 🚀 3. Top Gainers & Losers
# =========================================
def get_top_movers(limit=5):
    """
    Returns top gainers and losers in last 24h
    """

    url = f"{BASE_URL}/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "24h"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Sort by 24h change
        sorted_data = sorted(
            data,
            key=lambda x: x.get("price_change_percentage_24h") or 0,
            reverse=True
        )

        top_gainers = sorted_data[:limit]
        top_losers = sorted_data[-limit:]

        gainers = [
            {
                "name": coin["name"],
                "symbol": coin["symbol"],
                "change": round(coin["price_change_percentage_24h"], 2)
            }
            for coin in top_gainers
        ]

        losers = [
            {
                "name": coin["name"],
                "symbol": coin["symbol"],
                "change": round(coin["price_change_percentage_24h"], 2)
            }
            for coin in top_losers
        ]

        return {
            "gainers": gainers,
            "losers": losers
        }

    except Exception as e:
        return {"error": str(e)}


# =========================================
# 📰 4. Trending Coins (News-like signal)
# =========================================
def get_trending_coins():
    """
    Returns trending coins (proxy for news/sentiment)
    """

    url = f"{BASE_URL}/search/trending"

    try:
        response = requests.get(url)
        data = response.json()

        trending = []

        for coin in data.get("coins", [])[:5]:
            item = coin["item"]
            trending.append({
                "name": item["name"],
                "symbol": item["symbol"],
                "rank": item["market_cap_rank"]
            })

        return trending

    except Exception as e:
        return {"error": str(e)}


# =========================================
# 🧠 5. Combined Market Snapshot (VERY USEFUL)
# =========================================
def get_market_summary():
    """
    Combines major coins + movers + trending
    """

    major = get_major_coins()
    movers = get_top_movers()
    trending = get_trending_coins()

    return {
        "major_coins": major,
        "top_movers": movers,
        "trending": trending
    }