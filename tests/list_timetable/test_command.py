import datetime
import json

import responses
import time_machine

from squash_bot.list_timetable import commands, timetable

from tests import utils

TEST_DATETIME = datetime.datetime(2024, 3, 25, 12)


class TestCommand:
    def test_list_timetable(self):
        api_url = "https://foo.com"
        api_endpoint = timetable.CelticLeisureTimetable._API_TIMETABLE_ENDPOINT
        with responses.RequestsMock() as requests:
            requests.post(
                url=f"{api_url}/{api_endpoint}",
                status=200,
                json=json.load(
                    open(utils.fixture_path("example-list-timetable-api-response.json"))
                ),
            )
            command = commands.ListTimetableCommand()
            command._timetable._API_URL = api_url
            with time_machine.travel(TEST_DATETIME):
                response = command.handle(
                    {
                        "data": {
                            "options": [
                                {
                                    "type": 4,
                                    "name": "days",
                                    "value": "1",
                                },
                                {
                                    "type": 3,
                                    "name": "time-of-day",
                                    "value": "All",
                                },
                            ],
                            "resolved": {
                                "users": {
                                    "1": {
                                        "id": "1",
                                        "username": "user1",
                                        "global_name": "global1",
                                    },
                                    "2": {
                                        "id": "2",
                                        "username": "user2",
                                        "global_name": "global2",
                                    },
                                }
                            },
                            "guild_id": "1",
                        },
                        "member": {
                            "user": {
                                "id": "1",
                                "username": "different-name",
                                "global_name": "different-global-name",
                            }
                        },
                    }
                ).as_dict()

        assert response == {
            "type": 4,
            "data": {
                "content": f"All slots (25-03):\n* [25-03 21:00: 2 slots available]({api_url}/enterprise/bookingscentre/membertimetable#Details?&ResourceScheduleId=1900373)",
            },
        }

    def test_no_available_sessions(self):
        api_url = "https://foo.com"
        api_endpoint = timetable.CelticLeisureTimetable._API_TIMETABLE_ENDPOINT
        with responses.RequestsMock() as requests:
            requests.post(
                url=f"{api_url}/{api_endpoint}",
                status=200,
                json={"Results": []},
            )
            command = commands.ListTimetableCommand()
            command._timetable._API_URL = api_url
            with time_machine.travel(TEST_DATETIME):
                response = command.handle(
                    {
                        "data": {
                            "options": [
                                {
                                    "type": 4,
                                    "name": "days",
                                    "value": "1",
                                },
                                {
                                    "type": 3,
                                    "name": "time-of-day",
                                    "value": "All",
                                },
                            ],
                            "resolved": {
                                "users": {
                                    "1": {
                                        "id": "1",
                                        "username": "user1",
                                        "global_name": "global1",
                                    },
                                    "2": {
                                        "id": "2",
                                        "username": "user2",
                                        "global_name": "global2",
                                    },
                                }
                            },
                            "guild_id": "1",
                        },
                        "member": {
                            "user": {
                                "id": "1",
                                "username": "different-name",
                                "global_name": "different-global-name",
                            }
                        },
                    }
                ).as_dict()

        assert response == {
            "type": 4,
            "data": {
                "content": "No available sessions on 25-03",
            },
        }
