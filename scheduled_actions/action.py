import abc


class Action(abc.ABC):
    code: str

    @abc.abstractmethod
    def run(self, context: dict) -> None: ...
