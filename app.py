import streamlit as st
from agent import analyze_crypto
from data import get_coin_price, get_top_movers, get_trending_coins, get_major_coins
import time

# Page config
st.set_page_config(
    page_title="Crypto Research Agent",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean fintech theme: Navy Blue, White, Accent Green
st.markdown("""
<style>
    .stApp {
        background-color: #1B263B !important;
        color: #F5F5F5;
    }
    .main .block-container {
        background-color: #1B263B !important;
    }
    .stMetric {
        background-color: #F5F5F5 !important;
        border: 2px solid #00A86B !important;
        border-radius: 10px;
        padding: 15px;
        color: #1B263B;
        box-shadow: 0 2px 8px rgba(0, 168, 107, 0.2);
    }
    .stButton>button {
        background-color: #00A86B !important;
        color: #F5F5F5 !important;
        border: none !important;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0, 168, 107, 0.3);
    }
    .stButton>button:hover {
        background-color: #008B5A !important;
        box-shadow: 0 4px 8px rgba(0, 168, 107, 0.4);
    }
    .sidebar .sidebar-content {
        background-color: #F5F5F5 !important;
        color: #1B263B;
        border-right: 2px solid #00A86B;
    }
    .stTextInput input {
        background-color: #F5F5F5 !important;
        color: #1B263B !important;
        border: 2px solid #00A86B !important;
        border-radius: 8px;
    }
    .stSelectbox select {
        background-color: #F5F5F5 !important;
        color: #1B263B !important;
        border: 2px solid #00A86B !important;
        border-radius: 8px;
    }
    .stChatMessage {
        background-color: #F5F5F5 !important;
        border: 1px solid #00A86B !important;
        border-radius: 10px;
        color: #1B263B;
    }
    h1, h2, h3 {
        color: #00A86B !important;
    }
    .stMarkdown {
        color: #F5F5F5 !important;
    }
    .stSubheader {
        color: #00A86B !important;
    }
    .stContainer {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Sidebar navigation
st.sidebar.title("🚀 Crypto Agent")
page = st.sidebar.radio("Navigation", ["Chat", "Market Dashboard", "Trending", "Settings"])

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.session_state.last_refresh = time.time()
    st.rerun()

# Suggested prompts
suggested_prompts = ["BTC price", "Top gainers today", "ETH market trend", "Trending coins"]

def show_chat():
    st.title("🤖 AI Chat Assistant")
    st.caption("Ask questions about crypto markets")

    # Suggested prompts
    st.subheader("💡 Quick Prompts")
    cols = st.columns(len(suggested_prompts))
    for i, prompt in enumerate(suggested_prompts):
        if cols[i].button(prompt):
            st.session_state.chat.append(("user", prompt))
            with st.spinner("Analyzing..."):
                response = analyze_crypto(prompt)
            st.session_state.chat.append(("ai", response))
            st.rerun()

    # Chat interface
    st.divider()
    chat_container = st.container(height=400)
    with chat_container:
        for role, message in st.session_state.chat:
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message)
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message)

    # Chat input
    if prompt := st.chat_input("Ask about crypto..."):
        st.session_state.chat.append(("user", prompt))
        with st.spinner("Thinking..."):
            response = analyze_crypto(prompt)
        st.session_state.chat.append(("ai", response))
        st.rerun()

def show_market_dashboard():
    st.title("📊 Market Dashboard")
    st.caption("Real-time crypto market overview")

    try:
        # Major coins metrics
        btc_data = get_coin_price("bitcoin")
        eth_data = get_coin_price("ethereum")

        col1, col2 = st.columns(2)
        with col1:
            if btc_data and 'price' in btc_data and isinstance(btc_data['price'], (int, float)):
                change = btc_data.get('change', 0)
                change_color = "inverse" if change < 0 else "normal"
                st.metric(
                    "Bitcoin (BTC)",
                    f"${btc_data['price']:.2f}",
                    f"{change:.2f}%",
                    delta_color=change_color
                )
            else:
                error_msg = btc_data.get('error', 'Failed to load BTC data') if btc_data else 'No data available'
                st.metric("Bitcoin (BTC)", error_msg, "N/A")
        with col2:
            if eth_data and 'price' in eth_data and isinstance(eth_data['price'], (int, float)):
                change = eth_data.get('change', 0)
                change_color = "inverse" if change < 0 else "normal"
                st.metric(
                    "Ethereum (ETH)",
                    f"${eth_data['price']:.2f}",
                    f"{change:.2f}%",
                    delta_color=change_color
                )
            else:
                error_msg = eth_data.get('error', 'Failed to load ETH data') if eth_data else 'No data available'
                st.metric("Ethereum (ETH)", error_msg, "N/A")

        st.divider()

        # Top movers
        movers = get_top_movers()
        if movers:
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("📈 Top Gainers")
                if 'gainers' in movers:
                    for coin in movers['gainers'][:5]:
                        st.write(f"**{coin['name']} ({coin['symbol'].upper()})**: +{coin.get('change', 0):.2f}%")
            with col4:
                st.subheader("📉 Top Losers")
                if 'losers' in movers:
                    for coin in movers['losers'][:5]:
                        st.write(f"**{coin['name']} ({coin['symbol'].upper()})**: {coin.get('change', 0):.2f}%")

    except Exception as e:
        st.error(f"Error loading market data: {e}")

def show_trending():
    st.title("🔥 Trending Coins")
    st.caption("Most searched coins on CoinGecko")

    try:
        trending = get_trending_coins()
        if trending:
            for i, coin in enumerate(trending[:10], 1):
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 2])
                    col1.metric(f"#{i}", coin.get('symbol', '').upper())
                    col2.write(f"**{coin.get('name', 'Unknown')}**")
                    col3.write(f"Rank: {coin.get('market_cap_rank', 'N/A')}")
                st.divider()
        else:
            st.info("No trending data available")
    except Exception as e:
        st.error(f"Error loading trending data: {e}")

def show_settings():
    st.title("⚙️ Settings")
    st.caption("Configure your crypto agent")

    st.subheader("AI Model")
    model = st.selectbox("Select model", ["gemma-1b", "gemma-2b", "other"], index=0)
    st.info("Note: Ensure the selected model is loaded in LM Studio")

    st.subheader("API Configuration")
    st.text_input("LM Studio URL", value="http://127.0.0.1:1234/v1", disabled=True)
    st.text_input("API Key", value="lm-studio", type="password", disabled=True)

    st.subheader("Coin Search")
    search_coin = st.text_input("Search for a coin (e.g., bitcoin)")
    if st.button("Search") and search_coin:
        try:
            coin_data = get_coin_price(search_coin.lower())
            if coin_data:
                st.success(f"Found: {coin_data.get('name', 'Unknown')}")
                st.metric(
                    f"{coin_data.get('name', 'Unknown')} ({coin_data.get('symbol', '').upper()})",
                    f"${coin_data.get('current_price', 'N/A'):.2f}",
                    f"{coin_data.get('price_change_percentage_24h', 0):.2f}%"
                )
            else:
                st.error("Coin not found")
        except Exception as e:
            st.error(f"Search error: {e}")

# Main app logic
if page == "Chat":
    show_chat()
elif page == "Market Dashboard":
    show_market_dashboard()
elif page == "Trending":
    show_trending()
elif page == "Settings":
    show_settings()