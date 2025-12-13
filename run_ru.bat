@echo off
chcp 65001 >nul
echo Telegram Бот для Бронирования Билетов
echo =====================================
echo.

REM Проверка переменных окружения
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo ОШИБКА: Переменная окружения TELEGRAM_BOT_TOKEN не установлена
    echo.
    echo Пожалуйста, установите её сначала:
    echo set TELEGRAM_BOT_TOKEN=ваш_токен_бота
    echo.
    echo Или создайте файл .env с токеном
    echo.
    pause
    exit /b 1
)

if "%ADMIN_IDS%"=="" (
    echo ПРЕДУПРЕЖДЕНИЕ: Переменная окружения ADMIN_IDS не установлена
    echo Функции администратора будут недоступны
    echo.
    echo Для включения функций администратора:
    echo set ADMIN_IDS=ваш_user_id
    echo.
)

echo Проверка конфигурации...
python validate_config_ru.py
if %errorlevel% neq 0 (
    echo.
    echo Проверка конфигурации не пройдена!
    echo Пожалуйста, исправьте ошибки перед запуском
    pause
    exit /b 1
)

echo.
echo =====================================
echo Запуск бота...
echo =====================================
echo.
echo Нажмите Ctrl+C для остановки бота
echo.

python main.py

echo.
echo Бот остановлен.
pause