import enum
import json
import logging
import typing

from squash_bot.core import command as _command
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
    body_dict = json.loads(body)

    try:
        verify_event(event)
    except verify.CouldNotVerifyRequest as e:
        logger.error("Could not verify request")
        return response.Response(
            status_code=401,
            body_data="Could not verify request",
        ).as_dict()

    interaction_type = InteractionTypeEnum(body_dict["type"])
    logger.info(f"Received interaction of type {interaction_type}")

    interaction_handler = {
        InteractionTypeEnum.PING: ping_handler,
        InteractionTypeEnum.APPLICATION_COMMAND: command_handler,
        InteractionTypeEnum.UNKNOWN: unknown_handler,
    }[interaction_type]

    return interaction_handler(body_dict).as_dict()


def verify_event(event: dict[str, typing.Any]) -> None:
    verifier = _verifier_from_settings()
    verifier.verify(event)
    logger.info(f"Request verified with {verifier.__class__.__name__}")


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
    try:
        command_response_data = command.handle(body)
    except _command.CommandVerificationError as e:
        return response.Response(
            status_code=500,
            body_data=str(e),
        )
    except _command.CommandError as e:
        logger.error(f"Error handling command {command_name}: {e}")
        raise e

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


def _verifier_from_settings() -> verify.Verifier:
    verifier_class = settings_base.settings.VERIFIER
    return settings_base.get_class_from_string(verifier_class)()
