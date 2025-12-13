#!/usr/bin/env python3
"""
Скрипт для быстрого деплоя и настройки бота на Replit.
Автоматически проверяет конфигурацию и запускает бота.
"""

import os
import sys
import time
from config import Config

def check_replit_environment():
    """Проверка среды Replit."""
    print("🔍 Проверка среды Replit...")
    
    # Проверка переменных Replit
    if os.getenv('REPL_SLUG'):
        print(f"✅ Replit проект: {os.getenv('REPL_SLUG')}")
    else:
        print("⚠️  Не обнаружена среда Replit")
    
    if os.getenv('REPL_OWNER'):
        print(f"✅ Владелец: {os.getenv('REPL_OWNER')}")
    
    return True

def check_secrets():
    """Проверка секретов Replit."""
    print("\n🔐 Проверка секретов...")
    
    required_secrets = ['TELEGRAM_BOT_TOKEN']
    optional_secrets = ['ADMIN_IDS']
    
    missing_required = []
    
    for secret in required_secrets:
        if os.getenv(secret):
            print(f"✅ {secret}: настроен")
        else:
            print(f"❌ {secret}: не найден")
            missing_required.append(secret)
    
    for secret in optional_secrets:
        if os.getenv(secret):
            print(f"✅ {secret}: настроен")
        else:
            print(f"⚠️  {secret}: не настроен (опционально)")
    
    if missing_required:
        print(f"\n❌ Отсутствуют обязательные секреты: {', '.join(missing_required)}")
        print("\nДля добавления секретов:")
        print("1. Откройте вкладку 'Secrets' (🔒) в левой панели")
        print("2. Добавьте каждый секрет:")
        for secret in missing_required:
            print(f"   - Key: {secret}")
            print(f"   - Value: <ваше_значение>")
        return False
    
    return True

def setup_database():
    """Инициализация базы данных."""
    print("\n💾 Настройка базы данных...")
    
    try:
        from db import Database
        
        db = Database("bot_database.db")
        db.init_db()
        print("✅ База данных инициализирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

def test_bot_config():
    """Тестирование конфигурации бота."""
    print("\n🤖 Тестирование конфигурации бота...")
    
    try:
        config = Config()
        print(f"✅ Токен бота: {config.telegram_bot_token[:10]}...{config.telegram_bot_token[-10:]}")
        
        if config.admin_ids:
            print(f"✅ Администраторы: {config.admin_ids}")
        else:
            print("⚠️  Администраторы не настроены")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def show_deployment_info():
    """Показать информацию о деплое."""
    print("\n" + "="*50)
    print("🚀 ИНФОРМАЦИЯ О ДЕПЛОЕ")
    print("="*50)
    
    print(f"📅 Время деплоя: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Среда: Replit")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    if os.getenv('REPL_SLUG'):
        repl_url = f"https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER', 'user')}.repl.co"
        print(f"🔗 URL проекта: {repl_url}")
    
    print("\n📋 Следующие шаги:")
    print("1. Найдите вашего бота в Telegram")
    print("2. Отправьте команду /start")
    print("3. Проверьте работу основных функций")
    print("4. Для непрерывной работы включите 'Always On'")
    
    print("\n🔧 Полезные команды:")
    print("- python validate_config.py  # Проверка конфигурации")
    print("- python test_db.py          # Тест базы данных")
    print("- tail -f bot.log            # Просмотр логов")

def main():
    """Основная функция деплоя."""
    print("🚀 Replit Deploy Script для Telegram Bot")
    print("="*50)
    
    # Проверки
    checks = [
        ("Среда Replit", check_replit_environment),
        ("Секреты", check_secrets),
        ("База данных", setup_database),
        ("Конфигурация бота", test_bot_config),
    ]
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}...")
        if not check_func():
            print(f"\n❌ Ошибка в проверке: {check_name}")
            print("Исправьте ошибки и запустите скрипт снова")
            return False
    
    # Показать информацию о деплое
    show_deployment_info()
    
    print(f"\n✅ Деплой завершен успешно!")
    print("🤖 Запуск бота...")
    
    return True

if __name__ == "__main__":
    if main():
        # Запуск бота после успешного деплоя
        try:
            from main import main as run_bot
            run_bot()
        except KeyboardInterrupt:
            print("\n👋 Бот остановлен пользователем")
        except Exception as e:
            print(f"\n❌ Ошибка запуска бота: {e}")
    else:
        sys.exit(1)