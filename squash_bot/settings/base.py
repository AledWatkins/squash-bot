import importlib
import os

from envparse import env


class ImproperlyConfigured(Exception):
    """
    An exception raised when a setting is improperly configured.
    """


env.read_envfile(path=os.environ.get("ENV_FILE_PATH", ".env"))


class BaseSettings:
    """
    Base settings class
    """

    installed_commands: tuple[str] = ()

    APP_ID: str = env.str("APP_ID")
    SERVER_ID: str = env.str("SERVER_ID")
    BOT_TOKEN: str = env.str("BOT_TOKEN")
    PUBLIC_KEY: str = env.str("PUBLIC_KEY")

    # Outputer for registering slash commands
    OUTPUTER: str

    # Verifier for verifying event body
    VERIFIER: str

    def install_commands(self) -> None:
        """
        Install all commands in the installed_commands list.
        """
        for command_module_string in self.installed_commands:
            importlib.import_module(command_module_string)


try:
    settings_module = os.environ["SETTINGS_MODULE"]
except KeyError as e:
    raise ImproperlyConfigured("SETTINGS_MODULE environment variable is not set") from e

settings = importlib.import_module(settings_module).Settings()
settings.install_commands()


def get_class_from_string(class_path: str) -> type[object]:
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
