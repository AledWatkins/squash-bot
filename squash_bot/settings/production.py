from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for production
    """

    installed_commands = ("squash_bot.match_tracker.commands",)

    OUTPUTER = "slash_command_register.outputer.RequestsOutputer"
    VERIFIER = "squash_bot.core.verify.NACLVerifier"
