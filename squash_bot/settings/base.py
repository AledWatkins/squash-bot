import os
import importlib


class BaseSettings:
    """
    Base settings class
    """


settings_module = os.environ["SETTINGS_MODULE"]
settings = importlib.import_module(settings_module).Settings()
