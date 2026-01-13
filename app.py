import streamlit as st
from utils import fetch_meti_rss, fetch_google_news_rss

# --- Page Config ---
st.set_page_config(
    page_title="経済産業省・関連ニュース収集ダッシュボード",
    page_icon="📰",
    layout="wide"
)

# --- CSS for Card Design ---
st.markdown("""
<style>
    .news-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box_shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .news-source {
        font-size: 0.8em;
        color: #666;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .news-date {
        font-size: 0.8em;
        color: #888;
        margin-bottom: 10px;
    }
    .news-title {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
        color: #1a73e8;
        text-decoration: none;
    }
    .news-title a {
        color: #1a73e8;
        text-decoration: none;
    }
    .news-title a:hover {
        text-decoration: underline;
    }
    .news-summary {
        font-size: 0.95em;
        color: #333;
        line-height: 1.5;
    }
    
    /* Dark mode adjustments (rudimentary) */
    @media (prefers-color-scheme: dark) {
        .news-card {
            background-color: #262730;
            border-color: #444;
        }
        .news-source {
            color: #aaa;
        }
        .news-date {
            color: #bbb;
        }
        .news-title, .news-title a {
            color: #8ab4f8;
        }
        .news-summary {
            color: #ddd;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("検索設定")

search_query = st.sidebar.text_input("検索ワード", value="経済産業省")

filter_option = st.sidebar.radio(
    "表示フィルタ",
    ("すべて", "公式情報のみ", "Google Newsのみ")
)

st.sidebar.markdown("---")
st.sidebar.info("経済産業省の公式RSSとGoogle Newsを統合して表示します。")

# --- Main Content ---
st.title("📰 経済産業省・関連ニュース")

# --- Fetch Data ---
# --- Fetch Data ---
with st.status("ニュースを取得中...", expanded=True) as status:
    all_news = []
    
    # Fetch METI Data
    if filter_option in ["すべて", "公式情報のみ"]:
        st.write("経済産業省のRSSを取得中...")
        meti_news = fetch_meti_rss()
        if meti_news:
            st.write("✅ 経済産業省: 取得成功")
            all_news.extend(meti_news)
        else:
            st.write("⚠️ 経済産業省: 取得失敗 (または更新なし)")
            
    # Fetch Google News Data
    if filter_option in ["すべて", "Google Newsのみ"]:
        if search_query:
            st.write(f"Google News ('{search_query}') を取得中...")
            google_news = fetch_google_news_rss(search_query)
            if google_news:
                st.write("✅ Google News: 取得成功")
                all_news.extend(google_news)
            else:
                 st.write("⚠️ Google News: 取得失敗")

    status.update(label="ニュース取得完了", state="complete", expanded=False)

    # Sort by date (newest first)
    # Using timestamp we created in utils.py
    # If standardizing dates was imperfect, this might be mixed, 
    # but standardize_news tries to capture published_parsed.
    all_news.sort(key=lambda x: x['timestamp'], reverse=True)

# --- Display Data ---
if not all_news:
    st.warning("ニュースが見つかりませんでした。検索ワードを変更するか、しばらく待ってから再試行してください。")
else:
    for news in all_news:
        # Create a container for the card
        # We use standard markdown to inject the HTML/CSS class structure we defined
        
        # Truncate summary for display if it's too long
        display_summary = news['summary']
        if len(display_summary) > 200:
            display_summary = display_summary[:200] + "..."
            
        # Clean simple HTML tags for safety if coming from unreliable sources, 
        # though feedparser handles some. For this demo, we trust standard feeds relatively well,
        # but displaying as HTML in unsafe_allow_html requires care. 
        # We will strip HTML tags for safety in standard text display or just use st.write
        # But to match the "Card" requirement with CSS, we construct HTML.
        
        # Basic HTML stripping for summary to prevent breaking card layout
        import re
        clean_summary = re.sub('<[^<]+?>', '', display_summary)
        
        card_html = f"""
        <div class="news-card">
            <div class="news-source">{news['source']}</div>
            <div class="news-title"><a href="{news['link']}" target="_blank">{news['title']}</a></div>
            <div class="news-date">{news['published']}</div>
            <div class="news-summary">{clean_summary}</div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

