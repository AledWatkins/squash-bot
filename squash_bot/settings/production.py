import os

from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for production
    """

    installed_commands = [
        "squash_bot.match_tracker.commands",
    ]

    APP_ID = os.environ.get("APP_ID")
    SERVER_ID = os.environ.get("SERVER_ID")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    OUTPUTER = "squash_bot.slash_command_register.outputer.RequestsOutputer"
    VERIFYIER = "squash_bot.core.verify.NACLVerifier"
