import attrs


@attrs.frozen
class User:
    id: str
    username: str
    global_name: str

    @property
    def name(self) -> str:
        return self.global_name or self.username
