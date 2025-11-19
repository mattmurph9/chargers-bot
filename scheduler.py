"""
Scheduler to run the bot periodically.
"""
import schedule
import time
import logging
from bot import ChargersNewsBot
from config import CHECK_INTERVAL_HOURS, DEBUG

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_bot():
    """Run the bot once."""
    try:
        bot = ChargersNewsBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")


def main():
    """Schedule and run the bot periodically."""
    logger.info(f"Starting scheduler - checking every {CHECK_INTERVAL_HOURS} hours")
    
    # Run immediately on start
    run_bot()
    
    # Schedule periodic runs
    schedule.every(CHECK_INTERVAL_HOURS).hours.do(run_bot)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")

