import enum
import json
import typing

import attrs


class InteractionTypeEnum(enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    UNKNOWN = 99

    @classmethod
    def _missing_(cls, value) -> "InteractionTypeEnum":
        return cls.UNKNOWN


@attrs.frozen
class Response:
    status_code: int
    body_data: dict[str, typing.Any] | str

    def as_dict(self) -> dict[str, typing.Any]:
        return {
            "statusCode": self.status_code,
            "body": json.dumps(self.body_data),
        }


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


def ping_handler(body: dict[str, typing.Any]) -> Response:
    return Response(
        status_code=200,
        body_data={"type": InteractionTypeEnum.PING.value},
    )


def command_handler(body: dict[str, typing.Any]) -> Response:
    pass


def unknown_handler(body: dict[str, typing.Any]) -> Response:
    return Response(
        status_code=400,
        body_data="Unknown interaction type",
    )
