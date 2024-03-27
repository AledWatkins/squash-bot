import attrs


@attrs.frozen
class User:
    id: str
    username: str
    global_name: str

    @property
    def name(self) -> str:
        return self.global_name or self.username

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "User":
        return User(
            id=data["id"],
            username=data["username"],
            global_name=data["global_name"],
        )