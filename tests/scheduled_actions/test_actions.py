import json
from unittest import mock

import responses

from common.timetable import timetable
from scheduled_actions.actions import prompt_session_booking

from tests import utils


class TestPromptBookingSessions:
    @mock.patch.object(prompt_session_booking.send, "send_message_to_channel")
    def test_prompt_booking_sessions(self, mock_send_message_to_channel):
        api_url = timetable.CelticLeisureTimetable._API_URL
        api_endpoint = timetable.CelticLeisureTimetable._API_TIMETABLE_ENDPOINT
        with responses.RequestsMock() as requests:
            requests.post(
                url=f"{api_url}/{api_endpoint}",
                status=200,
                json=json.load(
                    open(utils.fixture_path("example-list-timetable-api-response.json"))
                ),
            )

            prompt_session_booking.PromptSessionBooking().run({})

        mock_send_message_to_channel.assert_called_once()
