from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for production
    """

    installed_commands = (
        "squash_bot.match_tracker.commands",
        "squash_bot.list_timetable.commands",
    )

    OUTPUTER = "slash_command_register.outputer.RequestsOutputer"
    VERIFIER = "squash_bot.core.verify.NACLVerifier"
    STORAGE_BACKEND = "squash_bot.storage.base.S3Storage"

    # Match tracker settings
    MATCH_RESULTS_PATH = "squash-bot"
    MATCH_RESULTS_FILE = "match_tracker/results/match_results.json"

    API_URL = "https://celticleisure.legendonlineservices.co.uk"
    ACTIVITY_ID = "87"
    LOCATION_ID = "1917"
