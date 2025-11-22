"""
Los Angeles Chargers Bot

This bot fetches news from RSS feeds and tweets about Chargers-related news.
"""
import os
import re
import time
import feedparser
import tweepy
import logging
from datetime import datetime
from typing import List, Dict, Set
from openai import OpenAI
import google.generativeai as genai
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN,
    AI_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    NEWS_SOURCES,
    POSTED_ARTICLES_FILE,
    DEBUG
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChargersNewsBot:
    def __init__(self):
        """Initialize the Twitter bot."""
        self.setup_twitter_api()
        self.setup_ai_client()
        self.posted_articles = self.load_posted_articles()
    
    def setup_ai_client(self):
        """Set up AI provider client (OpenAI, Groq, or Gemini)."""
        self.ai_client = None
        self.ai_provider = AI_PROVIDER.lower()
        
        try:
            if self.ai_provider == "groq":
                if GROQ_API_KEY:
                    # Groq uses OpenAI-compatible API
                    self.ai_client = OpenAI(
                        api_key=GROQ_API_KEY,
                        base_url="https://api.groq.com/openai/v1"
                    )
                    logger.info(f"Groq API client initialized successfully (model: {GROQ_MODEL})")
                else:
                    logger.warning("Groq API key not found - AI features will be unavailable")
                    
            elif self.ai_provider == "gemini":
                if GEMINI_API_KEY:
                    genai.configure(api_key=GEMINI_API_KEY)
                    self.ai_client = genai.GenerativeModel(GEMINI_MODEL)
                    logger.info(f"Google Gemini API client initialized successfully (model: {GEMINI_MODEL})")
                else:
                    logger.warning("Gemini API key not found - AI features will be unavailable")
                    
            elif self.ai_provider == "openai":
                if OPENAI_API_KEY:
                    self.ai_client = OpenAI(api_key=OPENAI_API_KEY)
                    logger.info(f"OpenAI API client initialized successfully (model: {OPENAI_MODEL})")
                else:
                    logger.warning("OpenAI API key not found - AI features will be unavailable")
            else:
                logger.error(f"Unknown AI provider: {self.ai_provider}. Use 'groq', 'gemini', or 'openai'")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI provider ({self.ai_provider}): {e}")
            self.ai_client = None
        
    def setup_twitter_api(self):
        """Set up Twitter API v2 client."""
        try:
            self.client = tweepy.Client(
                bearer_token=TWITTER_BEARER_TOKEN,
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            logger.info("Twitter API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
    
    def load_posted_articles(self) -> Set[str]:
        """Load list of already posted article URLs to avoid duplicates."""
        if not os.path.exists(POSTED_ARTICLES_FILE):
            return set()
        
        try:
            with open(POSTED_ARTICLES_FILE, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            logger.error(f"Error loading posted articles: {e}")
            return set()
    
    def save_posted_article(self, url: str):
        """Save article URL to prevent duplicate posts."""
        self.posted_articles.add(url)
        try:
            with open(POSTED_ARTICLES_FILE, 'a') as f:
                f.write(f"{url}\n")
        except Exception as e:
            logger.error(f"Error saving posted article: {e}")
    
    def fetch_news(self) -> List[Dict]:
        """Fetch news from all configured RSS feeds."""
        all_articles = []
        
        for source in NEWS_SOURCES:
            try:
                logger.info(f"Fetching news from {source['name']}")
                feed = feedparser.parse(source['url'])
                
                for entry in feed.entries:
                    # Check if article is about Chargers
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    text_content = f"{title} {summary}"
                    
                    # Check for keywords
                    if any(keyword.lower() in text_content for keyword in source['keywords']):
                        article = {
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'published_parsed': entry.get('published_parsed'),
                            'summary': entry.get('summary', ''),
                            'source': source['name']
                        }
                        all_articles.append(article)
                
                logger.info(f"Found {len(feed.entries)} articles from {source['name']}")
                
            except Exception as e:
                logger.error(f"Error fetching from {source['name']}: {e}")
        
        return all_articles
    
    def format_tweet(self, article: Dict) -> str:
        """Format article into a tweet (max 280 characters)."""
        title = article['title']
        link = article['link']
        
        # Remove HTML tags from title
        title = re.sub(r'<[^>]+>', '', title)
        
        # Truncate title if needed to fit in tweet with link
        max_title_length = 280 - len(link) - 10  # 10 chars for "..." and spacing
        
        if len(title) > max_title_length:
            title = title[:max_title_length - 3] + "..."
        
        tweet = f"{title}\n\n{link}"
        
        return tweet
    
    def is_recent_article(self, article: Dict, hours_threshold: int = 24) -> bool:
        """Check if article was published within the last N hours."""
        try:
            if not article.get('published_parsed'):
                # If no date available, assume it's recent
                return True
            
            published_time = datetime(*article['published_parsed'][:6])
            time_diff = (datetime.now() - published_time.replace(tzinfo=None)).total_seconds() / 3600
            return time_diff <= hours_threshold
        except Exception as e:
            logger.warning(f"Error parsing article date: {e}")
            # If we can't parse the date, assume it's recent
            return True
    
    def post_tweet(self, tweet_text: str) -> bool:
        """Post a tweet to Twitter."""
        try:
            response = self.client.create_tweet(text=tweet_text)
            logger.info(f"Tweet posted successfully: {response.data['id']}")
            return True
        except tweepy.TweepyException as e:
            logger.error(f"Error posting tweet: {e}")
            return False
    
    def post_tweet_thread(self, tweet_texts: List[str]) -> bool:
        """Post a thread of tweets to Twitter, linking them together."""
        if not tweet_texts:
            logger.error("No tweets to post in thread")
            return False
        
        try:
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(tweet_texts, 1):
                # If this is not the first tweet, reply to the previous one
                if previous_tweet_id:
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    response = self.client.create_tweet(text=tweet_text)
                
                tweet_id = response.data['id']
                logger.info(f"Thread tweet {i}/{len(tweet_texts)} posted: {tweet_id}")
                previous_tweet_id = tweet_id
                
                # Wait a bit between tweets to ensure proper threading
                if i < len(tweet_texts):
                    time.sleep(2)
            
            logger.info(f"Thread posted successfully with {len(tweet_texts)} tweets")
            return True
        except tweepy.TweepyException as e:
            logger.error(f"Error posting tweet thread: {e}")
            return False
    
    def generate_heartbreaking_loss_thread(self) -> List[str]:
        """Generate a tweet thread about a past heartbreaking Chargers loss using AI."""
        # Debug: Check environment variables (without exposing full API keys)
        logger.info(f"AI_PROVIDER: {AI_PROVIDER}")
        logger.info(f"GROQ_API_KEY set: {bool(GROQ_API_KEY)} (length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0})")
        logger.info(f"TWITTER_API_KEY set: {bool(TWITTER_API_KEY)} (length: {len(TWITTER_API_KEY) if TWITTER_API_KEY else 0})")
        logger.info(f"GEMINI_API_KEY set: {bool(GEMINI_API_KEY)} (length: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0})")
        logger.info(f"OPENAI_API_KEY set: {bool(OPENAI_API_KEY)} (length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0})")
        
        # Also check raw environment variables
        import os
        logger.info(f"Raw env AI_PROVIDER: {os.getenv('AI_PROVIDER', 'NOT SET')}")
        logger.info(f"Raw env GROQ_API_KEY: {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}")  
        if not self.ai_client:
            provider_name = AI_PROVIDER.lower()
            # Check if the API key is actually set
            if AI_PROVIDER == "groq":
                if not GROQ_API_KEY:
                    raise ValueError(f"{provider_name} API client not initialized. Please set GROQ_API_KEY as an environment variable or in your .env file.")
                else:
                    raise ValueError(f"{provider_name} API client failed to initialize. Check that GROQ_API_KEY is valid.")
            elif AI_PROVIDER == "gemini":
                if not GEMINI_API_KEY:
                    raise ValueError(f"{provider_name} API client not initialized. Please set GEMINI_API_KEY as an environment variable or in your .env file.")
                else:
                    raise ValueError(f"{provider_name} API client failed to initialize. Check that GEMINI_API_KEY is valid.")
            else:
                if not OPENAI_API_KEY:
                    raise ValueError(f"{provider_name} API client not initialized. Please set OPENAI_API_KEY as an environment variable or in your .env file.")
                else:
                    raise ValueError(f"{provider_name} API client failed to initialize. Check that OPENAI_API_KEY is valid.")
        
        # Some famous heartbreaking Chargers losses to give context
        prompt = """Generate a Twitter thread (8-12 tweets) about a past heartbreaking Chargers loss.

CRITICAL: Search Pro-Football-Reference.com to verify ALL facts. Only include verified information.

Thread structure:
1. START: Context (who, where, when, what it meant) - verify from Pro-Football-Reference.com
2. Tell the full game story chronologically with key moments
3. Include actual scores, players, plays - all verified from Pro-Football-Reference.com
4. Build tension toward the heartbreaking ending

Requirements:
- Verify scores, player names, dates, stadium from Pro-Football-Reference.com
- Each tweet under 280 characters
- Number tweets (1/8, 2/8, etc.)
- Conversational fan voice
- If you can't verify it from Pro-Football-Reference.com, don't include it

Format: One tweet per line, ready to post."""

        try:
            system_prompt = "You are a passionate Los Angeles Chargers fan who loves to commiserate about heartbreaking losses. You write engaging, emotional Twitter threads that tell the complete story of games. Always start by establishing context: which teams are playing, where the game was played, and what the game meant (playoff implications, rivalry, must-win situation, etc.). Then include all key moments, scores, plays, and turning points. You have an encyclopedic knowledge of Chargers history and can recount games in vivid detail, taking readers through the entire game experience moment by moment."
            
            if self.ai_provider == "gemini":
                logger.info(f"Generating thread using Google Gemini ({GEMINI_MODEL})...")
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = self.ai_client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.8,
                        "max_output_tokens": 2000,
                    }
                )
                thread_text = response.text.strip()
            else:
                # OpenAI-compatible API (OpenAI or Groq)
                model = GROQ_MODEL if self.ai_provider == "groq" else OPENAI_MODEL
                logger.info(f"Generating thread using {self.ai_provider.upper()} ({model})...")
                
                response = self.ai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=2000
                )
                thread_text = response.choices[0].message.content.strip()
            
            # Split into individual tweets (assuming they're separated by newlines)
            tweets = [tweet.strip() for tweet in thread_text.split('\n') if tweet.strip()]
            
            # Clean up any numbering that might be in the format
            cleaned_tweets = []
            for tweet in tweets:
                # Remove any leading numbering like "1/5" or "Tweet 1:" if present
                tweet = re.sub(r'^\d+/\d+\s*[-:]?\s*', '', tweet)
                tweet = re.sub(r'^Tweet\s+\d+:\s*', '', tweet, flags=re.IGNORECASE)
                tweet = tweet.strip()
                if tweet and len(tweet) <= 280:
                    cleaned_tweets.append(tweet)
            
            if not cleaned_tweets:
                raise ValueError("No valid tweets generated from ChatGPT response")
            
            logger.info(f"Generated thread with {len(cleaned_tweets)} tweets")
            return cleaned_tweets
            
        except Exception as e:
            logger.error(f"Error generating thread with ChatGPT: {e}")
            raise
    
    def post_heartbreaking_loss_thread(self, dry_run: bool = False) -> bool:
        """Generate and post a tweet thread about a heartbreaking Chargers loss."""
        try:
            logger.info("Generating and posting heartbreaking loss thread...")
            tweets = self.generate_heartbreaking_loss_thread()
            
            print("\n" + "=" * 60)
            if dry_run:
                print("💔 HEARTBREAKING LOSS THREAD (DRY RUN - NOT POSTING)")
            else:
                print("💔 HEARTBREAKING LOSS THREAD")
            print("=" * 60 + "\n")
            print(f"Generated {len(tweets)} tweets:\n")
            for i, tweet in enumerate(tweets, 1):
                print(f"Tweet {i}/{len(tweets)} ({len(tweet)} chars):")
                print("-" * 60)
                print(tweet)
                print("-" * 60 + "\n")
            
            if dry_run:
                print("✅ DRY RUN COMPLETE - Thread would be posted in live mode")
                print("=" * 60 + "\n")
                return True
            
            if self.post_tweet_thread(tweets):
                logger.info("✅ Heartbreaking loss thread posted successfully!")
                print("✅ Thread posted successfully!")
                return True
            else:
                logger.error("❌ Failed to post thread")
                print("❌ Failed to post thread")
                return False
                
        except Exception as e:
            logger.error(f"Error in post_heartbreaking_loss_thread: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def get_article_publish_time(self, article: Dict) -> datetime:
        """Get the publish time of an article for sorting."""
        try:
            if article.get('published_parsed'):
                return datetime(*article['published_parsed'][:6])
            else:
                # If no date, return a very old date so they sort last
                return datetime(2000, 1, 1)
        except:
            return datetime(2000, 1, 1)
    
    def run_dry_run(self):
        """Dry run mode: Gets the most recent Chargers article and drafts a tweet (does NOT post)."""
        logger.info("Starting Chargers Bot in DRY RUN MODE...")
        print("\n" + "=" * 60)
        print("🔍 DRY RUN MODE - No tweets will be posted")
        print("=" * 60 + "\n")
        
        articles = self.fetch_news()
        logger.info(f"Found {len(articles)} total Chargers-related articles")
        
        if not articles:
            logger.warning("No Chargers articles found!")
            print("❌ No Chargers articles found to draft a tweet from.")
            return False
        
        # Sort articles by publish date (most recent first)
        articles.sort(key=self.get_article_publish_time, reverse=True)
        
        # Get the most recent article
        test_article = articles[0]
        
        logger.info(f"DRY RUN: Found most recent article: {test_article['title']}")
        
        # Format the tweet
        try:
            tweet_text = self.format_tweet(test_article)
            
            # Print the draft tweet
            print("📰 ARTICLE:")
            print(f"   Title: {test_article['title']}")
            print(f"   Source: {test_article['source']}")
            print(f"   Published: {test_article.get('published', 'Unknown date')}")
            print(f"   Link: {test_article['link']}")
            print()
            print("📝 DRAFT TWEET:")
            print("-" * 60)
            print(tweet_text)
            print("-" * 60)
            print(f"\n📊 Tweet length: {len(tweet_text)} / 280 characters")
            print(f"\n✅ DRY RUN COMPLETE - Tweet would be posted in live mode")
            print("=" * 60 + "\n")
            
            return True
        except Exception as e:
            logger.error(f"❌ DRY RUN FAILED: Error processing article: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def run_test(self):
        """Test mode: Gets the most recent Chargers article and tweets it (regardless of age or if already posted)."""
        logger.info("Starting Chargers Bot in TEST MODE...")
        
        articles = self.fetch_news()
        logger.info(f"Found {len(articles)} total Chargers-related articles")
        
        if not articles:
            logger.warning("No Chargers articles found to test with!")
            return
        
        # Sort articles by publish date (most recent first)
        articles.sort(key=self.get_article_publish_time, reverse=True)
        
        # Get the most recent article
        test_article = articles[0]
        
        logger.info(f"TEST MODE: Found most recent article: {test_article['title']}")
        logger.info(f"Source: {test_article['source']}")
        logger.info(f"Link: {test_article['link']}")
        
        # Format and post the tweet
        try:
            tweet_text = self.format_tweet(test_article)
            logger.info(f"Tweet text: {tweet_text[:100]}...")
            
            if self.post_tweet(tweet_text):
                logger.info("✅ TEST SUCCESS: Tweet posted successfully!")
                # Note: In test mode, we DON'T save it to posted_articles
                # so it won't interfere with normal bot operation
                return True
            else:
                logger.error("❌ TEST FAILED: Could not post tweet")
                return False
        except Exception as e:
            logger.error(f"❌ TEST FAILED: Error processing article: {e}")
            return False
    
    def run(self):
        """Main bot execution: fetch news and tweet about new articles."""
        logger.info("Starting Chargers Bot...")
        
        articles = self.fetch_news()
        logger.info(f"Found {len(articles)} total Chargers-related articles")
        
        # Filter out already posted articles and old articles
        new_articles = []
        for article in articles:
            if article['link'] not in self.posted_articles:
                # Only post recent articles (within last 24 hours)
                if self.is_recent_article(article, hours_threshold=24):
                    new_articles.append(article)
        
        logger.info(f"Found {len(new_articles)} new articles to post")
        
        # Post tweets for new articles
        for article in new_articles:
            try:
                tweet_text = self.format_tweet(article)
                if self.post_tweet(tweet_text):
                    self.save_posted_article(article['link'])
                    logger.info(f"Posted: {article['title']}")
                    # Wait a bit between tweets to avoid rate limits
                    time.sleep(30)
                else:
                    logger.warning(f"Failed to post: {article['title']}")
            except Exception as e:
                logger.error(f"Error processing article {article['title']}: {e}")
        
        logger.info("Bot run completed")


if __name__ == "__main__":
    import sys
    try:
        # Check for command line flags
        if len(sys.argv) > 1:
            flag = sys.argv[1]
            bot = ChargersNewsBot()
            
            if flag == "--dry-run":
                bot.run_dry_run()
            elif flag == "--test":
                bot.run_test()
            elif flag == "--heartbreak" or flag == "--heartbreaking-loss":
                bot.post_heartbreaking_loss_thread(dry_run=False)
            elif flag == "--heartbreak-dry-run" or flag == "--heartbreaking-loss-dry-run":
                bot.post_heartbreaking_loss_thread(dry_run=True)
            else:
                print(f"Unknown flag: {flag}")
                print("Usage: python bot.py [--dry-run|--test|--heartbreak|--heartbreak-dry-run]")
                sys.exit(1)
        else:
            bot = ChargersNewsBot()
            bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

