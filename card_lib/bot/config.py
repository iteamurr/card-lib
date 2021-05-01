"""
    Bot configuration module.
"""
import os

POSTGRESQL_DATABASE_URL = os.environ.get("DATABASE_URL")
USERS_DATABASE = os.environ.get("USERS_DATABASE_NAME")
COLLECTIONS_DATABASE = os.environ.get("COLLECTIONS_DATABASE_NAME")
MESSAGES_DATABASE = os.environ.get("MESSAGES_DATABASE_NAME")

TELEGRAM_TOKEN = os.environ.get("TOKEN")
TELEGRAM_URL = "https://api.telegram.org/bot{}/{}"

COLLECTIONS_PER_PAGE = 8
CARDS_PER_PAGE = 8
