@echo off
echo Telegram Ticket Booking Bot
echo ===========================
echo.

REM Check if environment variables are set
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo ERROR: TELEGRAM_BOT_TOKEN environment variable is not set
    echo.
    echo Please set it first:
    echo set TELEGRAM_BOT_TOKEN=your_bot_token_here
    echo.
    pause
    exit /b 1
)

if "%ADMIN_IDS%"=="" (
    echo WARNING: ADMIN_IDS environment variable is not set
    echo Admin features will not be available
    echo.
    echo To enable admin features:
    echo set ADMIN_IDS=12345678,987654321
    echo.
)

echo Validating configuration...
python validate_config.py
if %errorlevel% neq 0 (
    echo.
    echo Configuration validation failed!
    pause
    exit /b 1
)

echo.
echo Starting bot...
python main.py

pause