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

    APP_ID: str | None = os.environ.get("APP_ID")
    SERVER_ID: str | None = os.environ.get("SERVER_ID")
    BOT_TOKEN: str | None = os.environ.get("BOT_TOKEN")

    def install_commands(self) -> None:
        """
        Install all commands in the installed_commands list.
        """
        for command in self.installed_commands:
            importlib.import_module(command)


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
