import feedparser
import urllib.parse
from datetime import datetime
import time

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
            
        # Clean up HTML tags from summary if needed (basic string manipulation or just raw text)
        # For simplicity in this v1, we'll keep it as is or do basic truncation if it's too long.
        # But Streamlit/Markdown can handle some HTML or we can use a library if needed.
        # Here we just truncate if absolutely massive, but usually RSS summaries are okay.
            
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "source": source_name,
            "summary": summary,
            "timestamp": time.mktime(entry.published_parsed) if hasattr(entry, 'published_parsed') and entry.published_parsed else (time.mktime(entry.updated_parsed) if hasattr(entry, 'updated_parsed') and entry.updated_parsed else 0)
        })
    return news_items

def fetch_meti_rss():
    """
    Fetch official METI news RSS.
    """
    url = "https://www.meti.go.jp/ml_index_release_atom.xml"
    feed = feedparser.parse(url)
    if feed.bozo:
        # Handle potential XML parsing errors or connection issues
        # feedparser often sets bozo=1 for minor XML issues too, so we check if entries exist
        if not feed.entries:
            return None
    return standardize_news(feed.entries, "経済産業省")

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
    
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        return None
        
    return standardize_news(feed.entries, "Google News")
