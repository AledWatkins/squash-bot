from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for localdev and testing
    """

    installed_commands = [
        "squash_bot.match_tracker.commands",
    ]

    APP_ID = "[APP_ID]"
    SERVER_ID = "[SERVER_ID]"
    BOT_TOKEN = "[BOT_TOKEN]"

    OUTPUTER = "squash_bot.slash_command_register.outputer.PrintOutputer"
