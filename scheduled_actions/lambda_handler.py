import enum
import json
import logging
import typing

from scheduled_actions import actions

logger = logging.getLogger("scheduled_actions.lambda_handler")
logger.setLevel(logging.INFO)


class ActionTypeEnum(enum.Enum):
    PROMPT_SESSION_BOOKING = "prompt-session-booking"


def lambda_handler(
    event: dict[str, typing.Any], context: dict["str", typing.Any]
) -> dict[str, typing.Any]:
    logger.info(f"Received event: {event}")

    body = event["body"]
    body_dict = json.loads(body)

    action_type = ActionTypeEnum(body_dict["action_type"])
    logger.info(f"Received action of type {action_type}")

    action_handler = action_handlers[action_type]
    try:
        action_handler.run(body_dict)
    except Exception as e:
        logger.error(f"Error running action {action_type}")
        return {"statusCode": 500, "body": f"Error running action {action_type}"}

    return {"statusCode": 200}


action_handlers = {
    ActionTypeEnum.PROMPT_SESSION_BOOKING: actions.PromptSessionBooking(),
}
