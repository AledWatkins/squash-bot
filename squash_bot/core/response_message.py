import enum
import typing


class InteractionResponseType(enum.Enum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    PREMIUM_REQUIRED = 10


class ResponseFlags(enum.Enum):
    """
    Bitwise flag operations - see https://discord.com/developers/docs/resources/channel#message-object-message-flags
    """

    EPHEMERAL = 1 << 6
    LOADING = 1 << 7


class ResponseBody:
    def __init__(self, response_type: InteractionResponseType, content: str):
        self._response_type = response_type
        self.content = content

    def as_dict(self) -> dict[str, typing.Any]:
        return {"type": self._response_type.value, "data": {"content": self.content}}


class ChannelMessageResponseBody(ResponseBody):
    """
    A message response to the channel where the command was called
    """

    def __init__(self, content):
        super().__init__(InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE, content)


class EphemeralChannelMessageResponseBody(ChannelMessageResponseBody):
    """
    A message response to only the user that called the command in the channel where the command was called
    """

    def __init__(self, content):
        super().__init__(content)

    def as_dict(self) -> dict[str, typing.Any]:
        base_dict = super().as_dict()
        base_dict["data"]["flags"] = ResponseFlags.EPHEMERAL.value
        return base_dict
