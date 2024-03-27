from squash_bot.settings import base


class Settings(base.BaseSettings):
    """
    Settings class for localdev and testing
    """

    installed_commands = ("squash_bot.match_tracker.commands",)

    OUTPUTER = "squash_bot.slash_command_register.outputer.PrintOutputer"
    VERIFIER = "squash_bot.core.verify.NoopVerifier"

    # Match tracker settings
    MATCH_RESULTS_PATH = base.PROJECT_ROOT / "tests" / "fixtures"
    MATCH_RESULTS_FILE = "match_results.json"
