from envparse import env

from common.settings import base


class ProductionSettings(base.BaseSettings):
    pass


class SquashBotProductionSettings(ProductionSettings):
    """
    Production settings for the squash bot lambda
    """

    installed_commands = (
        "squash_bot.match_tracker.commands",
        "squash_bot.list_timetable.commands",
        "squash_bot.sessions.commands",
    )

    VERIFIER = "squash_bot.core.verify.NACLVerifier"
    STORAGE_BACKEND = "common.storage.base.S3Storage"

    # Match tracker settings
    MATCH_RESULTS_PATH = "squash-bot"
    MATCH_RESULTS_FILE = "match_tracker/results/match_results.json"

    # Sessions settings
    SESSIONS_PATH = "squash-bot"
    SESSIONS_FILE = "sessions/sessions.json"


class SlashCommandRegisterProductionSettings(ProductionSettings):
    """
    Production settings for the slash command register
    """

    installed_commands = ()

    OUTPUTER = "slash_command_register.outputer.RequestsOutputer"
    SERVER_ID = env.str("SERVER_ID", default="")


class ScheduledActionsProductionSettings(ProductionSettings):
    """
    Production settings for the scheduled actions lambda
    """

    installed_commands = ()
