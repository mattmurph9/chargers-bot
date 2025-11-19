"""
Configuration settings for the Chargers Bot.
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
        "name": "ESPN",
        "url": "https://www.espn.com/espn/rss/nfl/news?team=SD",
        "keywords": ["chargers", "herbert"]
    },
    {
        "name": "PFF",
        "url": "https://www.pff.com/feed/teams/27",
        "keywords": ["chargers", "herbert"]
    }, 
    {
        "name": "LA Daily News",
        "url": "https://www.dailynews.com/sports/nfl/los-angeles-chargers/feed/",
        "keywords": ["chargers", "herbert"]
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

