"""
Test script to tweet the most recent Chargers article.
This bypasses all filters (age, duplicate checks) and just posts the latest article.
"""
import sys
from bot import ChargersNewsBot

if __name__ == "__main__":
    try:
        print("🧪 Running test tweet...")
        print("=" * 60)
        bot = ChargersNewsBot()
        bot.run_test()
    except KeyboardInterrupt:
        print("\n❌ Test stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

