import os

from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for production
    """

    APP_ID = os.environ.get("APP_ID")
    SERVER_ID = os.environ.get("SERVER_ID")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
