import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime
import time
import requests

def standardize_news(entries, source_name):
    """
    Standardize feed entries into a consistent dictionary structure.
    """
    news_items = []
    for entry in entries:
        # Parse date
        published = "Unknown Date"
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6]).strftime("%Y/%m/%d")
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
             published = datetime(*entry.updated_parsed[:6]).strftime("%Y/%m/%d")
        
        # Get summary if available (prefer summary, then description)
        summary = ""
        if hasattr(entry, 'summary'):
            summary = entry.summary
        elif hasattr(entry, 'description'):
            summary = entry.description
            
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "source": source_name,
            "summary": summary,
            "timestamp": time.mktime(entry.published_parsed) if hasattr(entry, 'published_parsed') and entry.published_parsed else (time.mktime(entry.updated_parsed) if hasattr(entry, 'updated_parsed') and entry.updated_parsed else 0)
        })
    return news_items

def fetch_feed(url):
    """
    Helper to fetch feed content with proper timeout and headers.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    try:
        # Connect timeout 5s, Read timeout 15s
        response = requests.get(url, headers=headers, timeout=(5.0, 15.0))
        response.raise_for_status()
        return feedparser.parse(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_meti_rss():
    """
    Fetch official METI news RSS.
    """
    url = "https://www.meti.go.jp/ml_index_release_atom.xml"
    feed = fetch_feed(url)
    
    if not feed or (feed.bozo and not feed.entries):
        return None
        
    return standardize_news(feed.entries, "経済産業省")

@st.cache_data(ttl=600, show_spinner=False)
def fetch_google_news_rss(query):
    """
    Fetch Google News RSS for a specific query with Japanese settings.
    """
    base_url = "https://news.google.com/rss/search"
    params = {
        "q": query,
        "hl": "ja",
        "gl": "JP",
        "ceid": "JP:ja"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    feed = fetch_feed(url)
    
    if not feed or (feed.bozo and not feed.entries):
        return None
        
    return standardize_news(feed.entries, "Google News")
