from common.settings import base


class LocalDevSettings(base.BaseSettings):
    pass


class SquashBotLocalDevSettings(LocalDevSettings):
    """
    Settings class for localdev and testing
    """

    installed_commands = (
        "squash_bot.match_tracker.commands",
        "squash_bot.list_timetable.commands",
        "squash_bot.sessions.commands",
    )

    OUTPUTER = "slash_command_register.outputer.PrintOutputer"
    VERIFIER = "squash_bot.core.verify.NoopVerifier"
    STORAGE_BACKEND = "common.storage.base.LocalStorage"

    # Match tracker settings
    MATCH_RESULTS_PATH = str(base.PROJECT_ROOT / "tests" / "fixtures" / "local_testing")
    MATCH_RESULTS_FILE = "match_results.json"

    # Sessions settings
    SESSIONS_PATH = str(base.PROJECT_ROOT / "tests" / "fixtures" / "local_testing")
    SESSIONS_FILE = "sessions.json"


class SlashCommandRegisterLocalDevSettings(LocalDevSettings):
    """
    Localdev settings for the slash command register
    """

    # This is a list of command modules to be registered, they should mirror the
    # installed_commands in the squash_bot settings
    installed_commands = SquashBotLocalDevSettings.installed_commands

    OUTPUTER = "slash_command_register.outputer.PrintOutputer"
    SERVER_ID = "123456789012345678"


class ScheduledActionsLocalDevSettings(LocalDevSettings):
    """
    Localdev settings for the scheduled actions lambda
    """

    installed_commands = ()

    PROMPT_SESSION_BOOKING_CHANNEL_IDS = ("123456789012345678",)
