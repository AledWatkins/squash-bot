import typing
from urllib.parse import urljoin

import requests

from squash_bot.core import command as _command
from squash_bot.core import command_registry, lambda_function
from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.settings import base as settings_base


@command_registry.registry.register
class ListTimetableCommand(_command.Command):
    name = "list-timetable"
    description = "List the timetable between two datetimes "
    options = (
        _command.CommandOption(
            name="from-date",
            description="Datetime string in the format YYYY-MM-DDTHH:mm:ss+00:00",
            type=_command.CommandOptionType.STRING,
            required=True,
        ),
        _command.CommandOption(
            name="to-date",
            description="Datetime string in the format YYYY-MM-DDTHH:mm:ss+00:00",
            type=_command.CommandOptionType.STRING,
            required=True,
        ),
    )

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> dict[str, typing.Any]:
        from_date = options["from-date"]
        to_date = options["to-date"]
        timetable = self._get_timetable(from_date, to_date)

        message = f"{from_date} - {to_date}:\n"
        available_sessions = []

        for result in timetable["Results"]:
            if result["AvailableSlots"] <= 0:
                continue
            available_sessions.append(
                f"* [{result['start']}]({self._booking_link(result['ResourceScheduleId'])})"
            )

        if not available_sessions:
            return {
                "content": f"No available sessions between {from_date} and {to_date}",
                "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            }

        message += "\n".join(available_sessions)
        return {
            "content": message,
            "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
        }

    def _get_timetable(self, from_date: str, to_date: str) -> dict[str, typing.Any]:
        return requests.post(
            urljoin(self._api_url(), "enterprise/Timetable/GetClassTimeTable"),
            json={
                "ResourceSubTypeIdList": settings_base.settings.ACTIVITY_ID,
                "FacilityLocationIdList": settings_base.settings.LOCATION_ID,
                "DateFrom": from_date,
                "DateTo": to_date,
            },
        ).json()

    def _api_url(self) -> str:
        return settings_base.settings.API_URL

    def _booking_link(self, schedule_id: int) -> str:
        return urljoin(
            self._api_url(),
            f"enterprise/bookingscentre/membertimetable#Details?&ResourceScheduleId={schedule_id}",
        )
