from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for localdev and testing
    """

    installed_commands = ("squash_bot.match_tracker.commands",)

    OUTPUTER = "slash_command_register.outputer.PrintOutputer"
    VERIFIER = "squash_bot.core.verify.NoopVerifier"
    STORAGE_BACKEND = "squash_bot.storage.base.LocalStorage"

    # Match tracker settings
    MATCH_RESULTS_PATH = base.PROJECT_ROOT / "tests" / "fixtures" / "local_testing"
    MATCH_RESULTS_FILE = "match_results.json"
