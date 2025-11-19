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
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN,
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
        self.posted_articles = self.load_posted_articles()
        
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
            else:
                print(f"Unknown flag: {flag}")
                print("Usage: python bot.py [--dry-run|--test]")
                sys.exit(1)
        else:
            bot = ChargersNewsBot()
            bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

