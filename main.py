#!/usr/bin/env python3
"""
Telegram Ticket Booking Bot

A production-ready Telegram bot for event ticket booking with admin features.

Setup:
1. Set environment variables:
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export ADMIN_IDS="12345678,987654321"  # comma-separated admin user IDs
   
2. Run the bot:
   python main.py

Features:
- View event schedule with category filtering
- Book tickets with step-by-step flow
- View booking status and history
- Leave feedback for attended events
- Admin booking management and confirmation
- SQLite database with proper schema
"""

import logging
import sys
from typing import Optional

from config import Config
from db import Database
from bot import TelegramBot


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    """Main entry point for the bot application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Initialize database
        db = Database(config.db_path)
        db.init_db()
        logger.info("Database initialized successfully")
        
        # Create and start bot
        telegram_bot = TelegramBot(config, db)
        logger.info("Starting Telegram bot...")
        telegram_bot.start_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()