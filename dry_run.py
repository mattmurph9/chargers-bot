"""
Dry run script to draft a tweet without posting.
This gets the latest Chargers article and shows what would be tweeted.
"""
import sys
from bot import ChargersNewsBot

if __name__ == "__main__":
    try:
        bot = ChargersNewsBot()
        bot.run_dry_run()
    except KeyboardInterrupt:
        print("\n❌ Dry run stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

