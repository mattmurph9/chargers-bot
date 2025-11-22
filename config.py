"""
Configuration settings for the Chargers Bot.
"""
import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# In GitHub Actions, environment variables are set directly, so this won't override them
load_dotenv()

# Helper function to get env var, treating empty strings as None
def get_env(key, default=None):
    """Get environment variable, treating empty strings as None."""
    value = os.getenv(key, default)
    return value if value else default

# Twitter API Credentials
TWITTER_API_KEY = get_env("TWITTER_API_KEY")
TWITTER_API_SECRET = get_env("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = get_env("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = get_env("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = get_env("TWITTER_BEARER_TOKEN")

# AI Provider Settings
# Options: "openai", "groq", "gemini"
AI_PROVIDER = get_env("AI_PROVIDER", "groq")  # Default to Groq (free tier)

# OpenAI API Credentials
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_MODEL = get_env("OPENAI_MODEL", "gpt-3.5-turbo")

# Groq API Credentials (FREE TIER - 14,400 requests/day)
GROQ_API_KEY = get_env("GROQ_API_KEY")
# Available models: 
# - groq/compound (supports web search - use for factual accuracy)
# - groq/compound-mini (faster, single tool call)
# - llama-3.3-70b-versatile (standard, no web search)
# - llama-3.1-8b-instant (faster, smaller)
# - mixtral-8x7b-32768 (alternative)
# Note: For accurate facts, groq/compound is recommended as it can search the web
GROQ_MODEL = get_env("GROQ_MODEL", "groq/compound")

# Google Gemini API Credentials (FREE TIER - 60 requests/minute)
GEMINI_API_KEY = get_env("GEMINI_API_KEY")
GEMINI_MODEL = get_env("GEMINI_MODEL", "gemini-pro")

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

def validate_openai_config():
    """Validate that OpenAI API key is present."""
    if not OPENAI_API_KEY:
        raise ValueError("Missing required environment variable: OPENAI_API_KEY")
    return True

