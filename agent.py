from openai import OpenAI
from data import get_coin_price, get_top_movers, get_trending_coins, get_major_coins

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

def analyze_crypto(question):  
    if not question or not isinstance(question, str) or not question.strip():
        return "Please enter a valid crypto question, such as 'BTC price' or 'top gainers'."

    q = question.lower()

    # Decide what data to fetch
    if "gainer" in q or "loser" in q:
        movers = get_top_movers()
        context = f"""
        Top Gainers: {movers['gainers']}
        Top Losers: {movers['losers']}
        """

    elif "trend" in q or "news" in q:
        trending = get_trending_coins()
        context = f"Trending Coins: {trending}"

    elif "doge" in q:
        coin = get_coin_price("dogecoin")
        context = f"DOGE: {coin}"

    elif "bnb" in q:
        coin = get_coin_price("binancecoin")
        context = f"BNB: {coin}"

    elif "eth" in q:
        coin = get_coin_price("ethereum")
        context = f"ETH: {coin}"

    elif "btc" in q or "bitcoin" in q:
        coin = get_coin_price("bitcoin")
        context = f"BTC: {coin}"

    else:
        # Default fallback
        data = get_major_coins()
        context = f"Major Coins: {data}"

    # Prompt
    prompt = f"""
    You are a crypto market research analyst.

    You analyze data and explain insights clearly like a professional.

    Context:
    {context}

    User Question:
    {question}

    Give:
    - Summary
    - Key Insight
    - Market Sentiment (Bullish/Bearish/Neutral)
    """

    try:
        response = client.chat.completions.create(
            model="gemma-1b",
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as exc:
        return f"Unable to get AI response: {exc}"

    if not response:
        return "No response received from AI server. Check if LM Studio is running."

    if not hasattr(response, "choices") or not response.choices:
        return f"Invalid response structure: {type(response)} - {response}"

    choice = response.choices[0]
    if hasattr(choice, "message") and choice.message and hasattr(choice.message, "content"):
        return choice.message.content

    # Some OpenAI-compatible clients return a text field instead
    if hasattr(choice, "text"):
        return choice.text

    return f"Unexpected response format: {choice}"
