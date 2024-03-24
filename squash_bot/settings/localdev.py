from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for localdev and testing
    """

    installed_commands = [
        "squash_bot.match_tracker.commands",
    ]

    OUTPUTER = "squash_bot.slash_command_register.outputer.PrintOutputer"
    VERIFYIER = "squash_bot.core.verify.NoopVerifier"
