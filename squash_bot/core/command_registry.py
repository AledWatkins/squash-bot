from squash_bot.core import command as _command


class ImproperlyConfigured(Exception):
    """
    An exception raised when a Command is improperly configured.
    """


class UnknownCommand(Exception):
    """
    An exception raised when a command is not found in the registry.
    """


class Registry:
    """
    A registry for Commands.

    Example usage:
        @command_registry.registry.register
        class Command:
            ...
    """

    _commands: dict[str, _command.Command]

    def __init__(self):
        self._commands = {}

    def register(self, command_class: type[_command.Command]) -> type[_command.Command]:
        """
        Adds a command class to the registry keyed by the command's `name` attribute.
        """
        command = command_class()

        # Check if a command with the same name already exists and raise an error if it does
        if command.name in self.commands:
            raise ImproperlyConfigured(f"Command with name {command.name} already exists")

        self.commands[command.name] = command
        return command_class

    @property
    def commands(self):
        return self._commands


def command_by_name(name: str) -> _command.Command:
    """
    Return the command with the given name.
    """
    try:
        return registry.commands[name]
    except KeyError as e:
        raise UnknownCommand(f"Command with name {name} not found") from e


def all_commands() -> list[_command.Command]:
    """
    Return all registered commands.
    """
    return list(registry.commands.values())


registry = Registry()
