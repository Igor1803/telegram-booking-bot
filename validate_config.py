#!/usr/bin/env python3
"""
Configuration validation script.
Run this to check if your bot configuration is correct before starting.
"""

import sys
from config import Config


def validate_config():
    """Validate bot configuration."""
    print("🔍 Validating bot configuration...")
    
    try:
        config = Config()
        
        # Check bot token format
        if not config.telegram_bot_token:
            print("❌ TELEGRAM_BOT_TOKEN is empty")
            return False
        
        if len(config.telegram_bot_token.split(':')) != 2:
            print("❌ TELEGRAM_BOT_TOKEN format is invalid (should be like 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)")
            return False
        
        print(f"✅ Bot token: {config.telegram_bot_token[:10]}...{config.telegram_bot_token[-10:]}")
        
        # Check admin IDs
        if not config.admin_ids:
            print("⚠️  No admin IDs configured - admin features will be disabled")
        else:
            print(f"✅ Admin IDs: {config.admin_ids}")
        
        # Check database path
        print(f"✅ Database path: {config.db_path}")
        
        print("\n🎉 Configuration is valid!")
        return True
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    print("Telegram Ticket Booking Bot - Configuration Validator")
    print("=" * 55)
    
    success = validate_config()
    
    if success:
        print("\n✅ Ready to start the bot!")
        print("Run: python main.py")
    else:
        print("\n❌ Please fix configuration issues before starting the bot.")
        print("\nSetup instructions:")
        print("1. Get bot token from @BotFather on Telegram")
        print("2. Set TELEGRAM_BOT_TOKEN environment variable")
        print("3. Set ADMIN_IDS environment variable (optional)")
        print("4. Or create .env file with these values")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)