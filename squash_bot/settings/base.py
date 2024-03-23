import os
import importlib


class BaseSettings:
    """
    Base settings class
    """


settings_module = os.environ["SETTINGS_MODULE"]
settings = importlib.import_module(settings_module).Settings()


def get_class_from_string(class_path: str) -> type[object]:
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
