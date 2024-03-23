import os
import importlib


class ImproperlyConfigured(Exception):
    """
    An exception raised when a setting is improperly configured.
    """


class BaseSettings:
    """
    Base settings class
    """

    installed_commands: list[str] = []

    APP_ID: str | None
    SERVER_ID: str | None
    BOT_TOKEN: str | None

    # Outputer for registering slash commands
    OUTPUTER: str

    def install_commands(self) -> None:
        """
        Install all commands in the installed_commands list.
        """
        for command_module_string in self.installed_commands:
            importlib.import_module(command_module_string)


try:
    settings_module = os.environ["SETTINGS_MODULE"]
except KeyError:
    raise ImproperlyConfigured("SETTINGS_MODULE environment variable is not set")

settings = importlib.import_module(settings_module).Settings()
settings.install_commands()


def get_class_from_string(class_path: str) -> type[object]:
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
