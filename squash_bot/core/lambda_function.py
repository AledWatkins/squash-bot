import enum
import logging
import typing

from squash_bot.core import command_registry, response, verify
from squash_bot.settings import base as settings_base

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
    body = event["body"]
    try:
        verify_body(body)
    except verify.CouldNotVerifyRequest as e:
        logger.error("Could not verify request")
        return response.Response(
            status_code=401,
            body_data="Could not verify request",
        ).as_dict()

    interaction_type = InteractionTypeEnum(body["type"])
    logger.info(f"Received interaction of type {interaction_type}")

    interaction_handler = {
        InteractionTypeEnum.PING: ping_handler,
        InteractionTypeEnum.APPLICATION_COMMAND: command_handler,
        InteractionTypeEnum.UNKNOWN: unknown_handler,
    }[interaction_type]

    return interaction_handler(body).as_dict()


def verify_body(body: dict[str, typing.Any]) -> None:
    verifyier = _verifyier_from_settings()
    verifyier.verify(body)


def ping_handler(body: dict[str, typing.Any]) -> response.Response:
    logger.info("Handling ping")
    return response.Response(
        status_code=200,
        body_data={"type": InteractionResponseType.PONG.value},
    )


def command_handler(body: dict[str, typing.Any]) -> response.Response:
    command_name = body["data"]["name"]
    try:
        command = command_registry.command_by_name(command_name)
    except command_registry.UnknownCommand:
        logger.info(f"Unknown command {command_name}")
        return response.Response(
            status_code=400,
            body_data="Unknown command",
        )
    logger.info(f"Handling command {command_name}")
    command_response_data = command.handle(body)
    return response.Response(
        status_code=200,
        body_data=command_response_data,
    )


def unknown_handler(body: dict[str, typing.Any]) -> response.Response:
    logger.info("Handling unknown interaction type")
    return response.Response(
        status_code=400,
        body_data="Unknown interaction type",
    )


def _verifyier_from_settings() -> verify.Verifyier:
    verifyier_class = settings_base.settings.VERIFYIER
    return settings_base.get_class_from_string(verifyier_class)()
