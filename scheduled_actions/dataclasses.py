import attrs


@attrs.frozen
class Guild:
    id: str


@attrs.frozen
class Channel:
    id: str


@attrs.frozen
class Message:
    content: str
