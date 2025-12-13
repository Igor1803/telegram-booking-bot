# Telegram Ticket Booking Bot

A production-ready Telegram bot for event ticket booking with admin features.

> 🇷🇺 **Русская версия:** [README_RU.md](README_RU.md) | [Подробная инструкция по установке](INSTALL_RU.md)

## Features

- 📅 View event schedule with category filtering (concerts, movies, plays)
- 🎫 Step-by-step ticket booking flow
- 📋 View and manage booking status
- 💳 Payment method selection (stub implementation)
- 💬 Leave feedback for attended events
- 👨‍💼 Admin booking management and confirmation

## Setup

### Prerequisites

- Python 3.10+ installed from [python.org](https://python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### Quick Setup (Windows)

1. **Run setup script:**
   ```cmd
   setup.bat
   ```

2. **Set environment variables:**
   ```cmd
   set TELEGRAM_BOT_TOKEN=your_bot_token_here
   set ADMIN_IDS=12345678,987654321
   ```

3. **Run the bot:**
   ```cmd
   run.bat
   ```

### Quick Setup (Replit - Cloud)

1. **Create new Repl** at [replit.com](https://replit.com) with Python template
2. **Upload all project files** to your Repl
3. **Add Secrets** in Replit:
   - `TELEGRAM_BOT_TOKEN` = your bot token from @BotFather
   - `ADMIN_IDS` = your user ID from @userinfobot
4. **Click Run** ▶️ - the bot will auto-deploy and start

📖 **Detailed Replit Guide:** [REPLIT_RU.md](REPLIT_RU.md)

### Manual Setup

#### 1. Install Dependencies

**Linux/Mac:**
```bash
pip install -r requirements.txt
```

**Windows:**
```cmd
pip install -r requirements.txt
```

#### 2. Set Environment Variables

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export ADMIN_IDS="12345678,987654321"  # comma-separated admin user IDs
```

**Windows:**
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
set ADMIN_IDS=12345678,987654321
```

Optional:
```bash
export DB_PATH="custom_database.db"  # default: bot_database.db
```

#### 3. Run the Bot

```bash
python main.py
```

## Usage

### User Commands

- `/start` - Welcome message and main menu
- `/help` - Help and command list
- `/events` - View event schedule
- `/book` - Start booking flow
- `/mybookings` - View your bookings
- `/feedback` - Leave feedback for attended events
- `/cancel` - Cancel current operation

### Admin Commands

- `/admin_bookings` - View and manage recent bookings
- `/admin_events` - List all events with IDs
- `/event_feedback <event_id>` - View feedback for specific event

## Project Structure

- `main.py` - Entry point and application setup
- `config.py` - Configuration and environment variables
- `db.py` - SQLite database operations
- `bot.py` - Telegram bot handlers and logic
- `states.py` - State management for user conversations
- `requirements.txt` - Python dependencies

## Database Schema

### Events Table
- id, date, time, title, category, base_ticket_price

### Bookings Table  
- id, event_id, user_id, username, customer_name, customer_phone
- tickets_count, notes, payment_method, total_price, status
- created_at, updated_at

### Feedback Table
- id, event_id, user_id, text, rating, created_at

## Sample Data

The bot comes with sample events and bookings for testing:
- Wine tasting events (concerts)
- Movie screenings
- Theater plays

## Development

The bot uses a clean, modular architecture:
- Separation of concerns between bot logic, database, and configuration
- State management for multi-step user flows
- Comprehensive error handling and logging
- Type hints and docstrings for maintainability

## License

This project is provided as-is for educational and commercial use.