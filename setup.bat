@echo off
echo Telegram Ticket Booking Bot Setup
echo ==================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found!
python --version

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To run the bot:
echo 1. Set environment variables:
echo    set TELEGRAM_BOT_TOKEN=your_bot_token_here
echo    set ADMIN_IDS=12345678,987654321
echo.
echo 2. Run the bot:
echo    python main.py
echo.
pause