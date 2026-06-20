# main.py
import logging
import time
import threading
from config import LOG_LEVEL, BOT_TOKEN
from database import init_db
from handlers import bot

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Viediet Bypass Bot...")
    init_db()
    logger.info("Database initialized.")
    # Start polling
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"Polling error: {e}")
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
