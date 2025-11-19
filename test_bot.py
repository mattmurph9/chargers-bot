"""
Test script to preview what the bot would post without actually posting.
"""
import feedparser
import re
from datetime import datetime
from config import NEWS_SOURCES, POSTED_ARTICLES_FILE
import os

def load_posted_articles():
    """Load list of already posted article URLs."""
    if not os.path.exists(POSTED_ARTICLES_FILE):
        return set()
    try:
        with open(POSTED_ARTICLES_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def is_recent_article(entry, hours_threshold=24):
    """Check if article was published within the last N hours."""
    try:
        if not entry.get('published_parsed'):
            return True
        published_time = datetime(*entry['published_parsed'][:6])
        time_diff = (datetime.now() - published_time.replace(tzinfo=None)).total_seconds() / 3600
        return time_diff <= hours_threshold
    except:
        return True

def format_tweet(title, link):
    """Format article into a tweet (max 280 characters)."""
    title = re.sub(r'<[^>]+>', '', title)
    max_title_length = 280 - len(link) - 10
    if len(title) > max_title_length:
        title = title[:max_title_length - 3] + "..."
    return f"{title}\n\n{link}"

print("🔍 Testing Chargers News Bot...\n")
print("=" * 60)

posted_articles = load_posted_articles()
new_articles = []

for source in NEWS_SOURCES:
    print(f"\n📰 Fetching from: {source['name']}")
    try:
        feed = feedparser.parse(source['url'])
        print(f"   Found {len(feed.entries)} articles in feed")
        
        for entry in feed.entries:
            title = entry.get('title', '').lower()
            summary = entry.get('summary', '').lower()
            text_content = f"{title} {summary}"
            
            if any(keyword.lower() in text_content for keyword in source['keywords']):
                link = entry.get('link', '')
                if link not in posted_articles and is_recent_article(entry, 24):
                    article = {
                        'title': entry.get('title', 'No title'),
                        'link': link,
                        'published': entry.get('published', ''),
                        'source': source['name']
                    }
                    new_articles.append(article)
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print(f"\n📊 Results: Found {len(new_articles)} new Chargers articles to post\n")

if new_articles:
    print("Would post these tweets:\n")
    for i, article in enumerate(new_articles, 1):
        tweet = format_tweet(article['title'], article['link'])
        print(f"{i}. Source: {article['source']}")
        print(f"   Tweet: {tweet[:100]}...")
        print(f"   Link: {article['link']}\n")
else:
    print("✅ No new articles found (they may have already been posted or are older than 24 hours)")

