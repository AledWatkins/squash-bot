from common.settings import base


class ProductionSettings(base.BaseSettings):
    pass


class SquashBotProductionSettings(ProductionSettings):
    """
    Settings class for production
    """

    installed_commands = (
        "squash_bot.match_tracker.commands",
        "squash_bot.list_timetable.commands",
    )

    OUTPUTER = "slash_command_register.outputer.RequestsOutputer"
    VERIFIER = "squash_bot.core.verify.NACLVerifier"
    STORAGE_BACKEND = "common.storage.base.S3Storage"

    # Match tracker settings
    MATCH_RESULTS_PATH = "squash-bot"
    MATCH_RESULTS_FILE = "match_tracker/results/match_results.json"
