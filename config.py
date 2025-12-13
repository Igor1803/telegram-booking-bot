"""Configuration module for the Telegram bot."""

import os
from typing import List, Optional


def load_env_file(env_path: str = ".env") -> None:
    """Load environment variables from .env file if it exists."""
    if not os.path.exists(env_path):
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):  # Don't override existing env vars
                        os.environ[key] = value
    except Exception:
        pass  # Silently ignore .env file errors


class Config:
    """Configuration class that loads settings from environment variables."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Try to load .env file first
        load_env_file()
        
        self.telegram_bot_token = self._get_required_env("TELEGRAM_BOT_TOKEN")
        self.admin_ids = self._parse_admin_ids()
        self.db_path = os.getenv("DB_PATH", "bot_database.db")
        
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _parse_admin_ids(self) -> List[int]:
        """Parse comma-separated admin IDs from environment variable."""
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if not admin_ids_str:
            return []
        
        try:
            return [int(id_str.strip()) for id_str in admin_ids_str.split(",") if id_str.strip()]
        except ValueError as e:
            raise ValueError(f"Invalid ADMIN_IDS format: {e}")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user ID is in admin list."""
        return user_id in self.admin_ids