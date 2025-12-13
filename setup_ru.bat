@echo off
chcp 65001 >nul
echo Установка Telegram Бота для Бронирования Билетов
echo ================================================
echo.

echo Проверка установки Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не установлен или не добавлен в PATH
    echo.
    echo Пожалуйста, установите Python 3.10+ с https://python.org/downloads/
    echo Обязательно отметьте "Add Python to PATH" при установке
    echo.
    pause
    exit /b 1
)

echo Python найден!
python --version

echo.
echo Установка зависимостей...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Не удалось установить зависимости
    echo Попробуйте запустить: pip install --upgrade pip
    echo Затем повторите установку
    pause
    exit /b 1
)

echo.
echo Проверка установки...
python -c "import telebot; print('✅ pyTelegramBotAPI установлен успешно')"

echo.
echo ================================================
echo Установка завершена успешно!
echo ================================================
echo.
echo Следующие шаги:
echo.
echo 1. Получите токен бота от @BotFather в Telegram:
echo    - Найдите @BotFather
echo    - Отправьте /newbot
echo    - Следуйте инструкциям
echo    - Скопируйте токен
echo.
echo 2. Получите ваш User ID от @userinfobot:
echo    - Найдите @userinfobot
echo    - Отправьте любое сообщение
echo    - Скопируйте User ID
echo.
echo 3. Установите переменные окружения:
echo    set TELEGRAM_BOT_TOKEN=ваш_токен_бота
echo    set ADMIN_IDS=ваш_user_id
echo.
echo 4. Или создайте файл .env с этими данными
echo.
echo 5. Запустите бота:
echo    run_ru.bat
echo.
echo Для проверки конфигурации: python validate_config.py
echo.
pause