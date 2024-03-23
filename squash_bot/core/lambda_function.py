import enum
import json
import typing

from squash_bot.core import response


class InteractionTypeEnum(enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    UNKNOWN = 99

    @classmethod
    def _missing_(cls, value) -> "InteractionTypeEnum":
        return cls.UNKNOWN


class InteractionResponseType(enum.Enum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4


def lambda_handler(
    event: dict[str, typing.Any], context: dict["str", typing.Any]
) -> dict[str, typing.Any]:
    body = json.loads(event["body"])

    interaction_type = InteractionTypeEnum(body["type"])
    interaction_handler = {
        InteractionTypeEnum.PING: ping_handler,
        InteractionTypeEnum.APPLICATION_COMMAND: command_handler,
        InteractionTypeEnum.UNKNOWN: unknown_handler,
    }[interaction_type]

    return interaction_handler(body).as_dict()


def ping_handler(body: dict[str, typing.Any]) -> response.Response:
    return response.Response(
        status_code=200,
        body_data={"type": InteractionResponseType.PONG.value},
    )


def command_handler(body: dict[str, typing.Any]) -> response.Response:
    pass


def unknown_handler(body: dict[str, typing.Any]) -> response.Response:
    return response.Response(
        status_code=400,
        body_data="Unknown interaction type",
    )
