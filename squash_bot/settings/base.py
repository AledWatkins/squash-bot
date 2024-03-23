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


try:
    settings_module = os.environ["SETTINGS_MODULE"]
except KeyError:
    raise ImproperlyConfigured("SETTINGS_MODULE environment variable is not set")

settings = importlib.import_module(settings_module).Settings()


def get_class_from_string(class_path: str) -> type[object]:
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
