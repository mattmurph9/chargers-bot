"""
Configuration settings for the Chargers News Bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API Credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Bot Settings
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "6"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# News Sources - RSS Feeds focused on Chargers news
NEWS_SOURCES = [
    {
        "name": "ESPN - Chargers",
        "url": "https://www.espn.com/espn/rss/nfl/news?team=SD",
        "keywords": ["chargers", "bolt", "herbert", "staley"]
    },
    {
        "name": "NFL.com - Chargers",
        "url": "https://www.nfl.com/feeds/rs/articles",
        "keywords": ["chargers", "los angeles"]
    },
    {
        "name": "The Athletic - Chargers",
        "url": "https://theathletic.com/rss/teams/chargers/",
        "keywords": ["chargers"]
    }
]

# File to track posted articles (to avoid duplicates)
POSTED_ARTICLES_FILE = "posted_articles.txt"

def validate_config():
    """Validate that all required configuration is present."""
    required_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET"
    ]
    
    missing = []
    for var in required_vars:
        if not globals().get(var):
            missing.append(var)
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True

