import logging

import requests

from common.settings import base
from scheduled_actions import dataclasses

logger = logging.getLogger("scheduled_actions.send")
logger.setLevel(logging.INFO)


class DiscordClient:
    BASE_URL = "https://discord.com/api"
    API_VERSION = "v10"

    MESSAGE_ENDPOINT = f"{BASE_URL}/{API_VERSION}/channels/{{channel_id}}/messages"

    def __init__(self, token: str):
        self.token = token

    def send_message_to_channel(
        self, channel: dataclasses.Channel, message: dataclasses.Message
    ) -> None:
        logger.info(f"Sending message to channel {channel.id}")
        requests.post(
            self.MESSAGE_ENDPOINT.format(channel_id=channel.id),
            data={
                "content": message.content,
            },
            headers=self._headers(),
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bot {self.token}",
            "User-Agent": "DiscordBot",
        }


def get_client() -> DiscordClient:
    return DiscordClient(token=base.settings.BOT_TOKEN)


def send_message_to_channel(*, channel: dataclasses.Channel, message: dataclasses.Message) -> None:
    get_client().send_message_to_channel(channel, message)
