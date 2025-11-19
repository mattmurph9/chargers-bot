# Los Angeles Chargers News Twitter Bot ⚡

A Twitter bot that automatically tweets out Los Angeles Chargers news from various RSS feeds.

## Features

- 📰 Fetches news from multiple RSS sources (ESPN, NFL.com, The Athletic)
- 🤖 Automatically posts new Chargers-related articles to Twitter
- 🚫 Prevents duplicate posts by tracking previously posted articles
- ⏰ Runs on a schedule (configurable interval)
- 🔍 Filters articles by Chargers-related keywords

## Prerequisites

- Python 3.8 or higher
- Twitter Developer Account with API access
- Internet connection

## Setup Instructions

### 1. Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Navigate to "Keys and Tokens"
4. Generate the following credentials:
   - API Key and API Secret
   - Access Token and Access Token Secret
   - Bearer Token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Twitter API credentials:
   ```
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

### 4. Verify Configuration

```bash
python -c "from config import validate_config; validate_config(); print('Config valid!')"
```

## Usage

### Run Once

To fetch news and post once:

```bash
python bot.py
```

### Run on Schedule

To run the bot continuously and check for news at regular intervals:

```bash
python scheduler.py
```

By default, it checks every 6 hours. You can change this in your `.env` file by setting `CHECK_INTERVAL_HOURS`.

### Run in Background (Linux/Mac)

To run the scheduler in the background:

```bash
nohup python scheduler.py > bot.log 2>&1 &
```

Or use a process manager like `systemd` or `supervisord` for production.

## How It Works

1. **News Fetching**: The bot checks RSS feeds from configured news sources
2. **Filtering**: Only articles containing Chargers-related keywords are kept
3. **Duplicate Prevention**: Article URLs are tracked in `posted_articles.txt` to avoid reposting
4. **Tweet Formatting**: Articles are formatted into tweets (max 280 characters) with title and link
5. **Posting**: New articles are posted to Twitter with rate limiting protection

## Configuration

### News Sources

Edit `config.py` to add or modify news sources. Each source should have:
- `name`: Display name
- `url`: RSS feed URL
- `keywords`: List of keywords to filter Chargers-related articles

### Bot Settings

Edit `.env` to configure:
- `CHECK_INTERVAL_HOURS`: How often to check for news (default: 6)
- `DEBUG`: Enable debug logging (default: False)

## File Structure

```
chargers-news-bot/
├── bot.py              # Main bot logic
├── scheduler.py        # Scheduler for periodic runs
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── env.example         # Example environment variables
├── .env                # Your actual credentials (not in git)
├── .gitignore          # Git ignore rules
├── posted_articles.txt # Track posted articles (auto-generated)
└── README.md           # This file
```

## Troubleshooting

### Twitter API Errors

- **401 Unauthorized**: Check your API credentials in `.env`
- **403 Forbidden**: Your app may not have write permissions. Check Twitter Developer Portal settings
- **Rate Limits**: The bot automatically handles rate limits with `wait_on_rate_limit=True`

### RSS Feed Issues

- Some RSS feeds may require authentication or have rate limits
- Check feed URLs in `config.py` are still valid
- Enable `DEBUG=True` in `.env` to see detailed logs

### Duplicate Posts

- The bot tracks posted articles in `posted_articles.txt`
- If you want to reset, delete this file (but you'll risk reposting old articles)

## Deployment

Want to deploy this bot for free? Check out **[DEPLOYMENT.md](DEPLOYMENT.md)** for several free hosting options:

- 🎯 **GitHub Actions** (Recommended) - Completely free, runs on schedule
- 🚂 **Railway** - Free $5/month credit
- 🐍 **PythonAnywhere** - Free tier available
- ☁️ **Render/Fly.io** - Other free options

The easiest way is **GitHub Actions** - just push to GitHub and add your secrets!

## Next Steps

- Deploy to a free hosting service (see DEPLOYMENT.md)
- Add more news sources
- Implement better article filtering
- Add retry logic for failed posts
- Set up monitoring/alerting

## License

This project is open source and available for personal use.

## Disclaimer

Make sure to comply with Twitter's API Terms of Service and rate limits. Use responsibly!

