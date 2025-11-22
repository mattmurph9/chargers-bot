# Los Angeles Chargers Bot ⚡

A Twitter bot that automatically tweets out Los Angeles Chargers news from various RSS feeds.

## Features

- 📰 Fetches news from multiple RSS sources (ESPN, NFL.com, The Athletic)
- 🤖 Automatically posts new Chargers-related articles to Twitter
- 🚫 Prevents duplicate posts by tracking previously posted articles
- ⏰ Runs on a schedule (configurable interval)
- 🔍 Filters articles by Chargers-related keywords
- 🤖 **AI-Powered Threads**: Generates detailed tweet threads about past heartbreaking Chargers losses using AI (Groq, Gemini, or OpenAI)

## Prerequisites

- Python 3.8 or higher
- Twitter Developer Account with API access
- Internet connection
- AI Provider API Key (for AI-powered threads): Groq (free), Google Gemini (free), or OpenAI (paid)

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

3. (Optional) Add AI Provider credentials for AI-powered threads:
   ```
   # For Groq (FREE - Recommended)
   AI_PROVIDER=groq
   GROQ_API_KEY=your_groq_api_key_here
   
   # OR for Google Gemini (FREE)
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # OR for OpenAI (Paid)
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   See [FREE_AI_SETUP.md](FREE_AI_SETUP.md) for detailed setup instructions.

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

### Dry Run (Preview Tweet)

To see what the bot would tweet **without actually posting**:

```bash
python bot.py --dry-run
```

Or use the dry run script:

```bash
python dry_run.py
```

This will:
- Find the most recent Chargers article from all sources
- Draft the tweet and display it
- Show article details (title, source, link, publish date)
- Display the full tweet text and character count
- **Does NOT post to Twitter** - perfect for testing!

### Test Tweet (Actually Posts)

To test the bot by tweeting the most recent Chargers article (regardless of age or if already posted):

```bash
python bot.py --test
```

Or use the test script:

```bash
python test_tweet.py
```

This will:
- Find the most recent Chargers article from all sources
- Tweet it immediately (bypasses age and duplicate checks)
- **Does NOT** save it to the posted articles list (won't interfere with normal bot operation)

### AI-Powered Heartbreaking Loss Thread

Generate and post a detailed tweet thread about a past heartbreaking Chargers loss using AI:

**Preview (Dry Run):**
```bash
python bot.py --heartbreak-dry-run
```

**Post Live:**
```bash
python bot.py --heartbreak
```

This feature:
- Uses AI to generate an 8-12 tweet thread telling the complete story of a game
- Includes context: teams, location, date, and what the game meant
- Fact-checks using Pro-Football-Reference.com for accuracy
- Tells the full story with key moments, scores, and turning points
- Posts as a proper Twitter thread (linked tweets)

**Requirements:**
- AI provider API key (Groq, Gemini, or OpenAI)
- See [FREE_AI_SETUP.md](FREE_AI_SETUP.md) for setup instructions

**Schedule with GitHub Actions:**
- Can be scheduled to run automatically (e.g., weekly)
- See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for setup

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

### AI Provider Settings

Edit `.env` to configure AI provider:
- `AI_PROVIDER`: Choose `groq` (default, free), `gemini` (free), or `openai` (paid)
- `GROQ_API_KEY`: Your Groq API key (if using Groq)
- `GROQ_MODEL`: Model to use (default: `groq/compound`)
- `GEMINI_API_KEY`: Your Gemini API key (if using Gemini)
- `GEMINI_MODEL`: Model to use (default: `gemini-pro`)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `OPENAI_MODEL`: Model to use (default: `gpt-3.5-turbo`)

See [FREE_AI_SETUP.md](FREE_AI_SETUP.md) for detailed AI provider setup.

## File Structure

```
chargers-bot/
├── bot.py                    # Main bot logic (includes AI thread generation)
├── scheduler.py              # Scheduler for periodic runs
├── dry_run.py                # Dry run script to draft tweets without posting
├── test_tweet.py             # Test script to tweet most recent article
├── test_bot.py               # Test script to preview what would be posted
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── env.example               # Example environment variables
├── .env                      # Your actual credentials (not in git)
├── .gitignore                # Git ignore rules
├── posted_articles.txt       # Track posted articles (auto-generated)
├── FREE_AI_SETUP.md          # AI provider setup guide
├── GITHUB_ACTIONS_SETUP.md   # GitHub Actions deployment guide
├── .github/
│   └── workflows/
│       └── heartbreak-thread.yml  # GitHub Actions workflow for scheduled threads
└── README.md                 # This file
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

### AI Provider Issues

- **Model not found**: Check that your API key is valid and you have access to the model
- **Request too large**: The prompt may be too long. Try a different model or reduce prompt size
- **Inaccurate facts**: The AI uses web search to fact-check, but may still have errors. Consider reviewing before posting
- **API errors**: Verify your API key is correct and has sufficient credits/quota
- See [FREE_AI_SETUP.md](FREE_AI_SETUP.md) for troubleshooting specific providers

## Deployment

Want to deploy this bot for free? Check out **GitHub Actions** - it's completely free and perfect for this bot!

- 🎯 **GitHub Actions** (Recommended) - Completely free, runs on schedule
- 🚂 **Railway** - Free $5/month credit
- 🐍 **PythonAnywhere** - Free tier available
- ☁️ **Render/Fly.io** - Other free options

The easiest way is **GitHub Actions** - just push to GitHub and add your secrets!

## Next Steps

- Set up AI provider for heartbreaking loss threads (see [FREE_AI_SETUP.md](FREE_AI_SETUP.md))
- Deploy to GitHub Actions for scheduled threads (see [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md))
- Add more news sources
- Implement better article filtering
- Add retry logic for failed posts
- Set up monitoring/alerting

## License

This project is open source and available for personal use.

## Disclaimer

Make sure to comply with Twitter's API Terms of Service and rate limits. Use responsibly!

