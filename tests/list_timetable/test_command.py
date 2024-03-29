import json
from unittest import mock

import responses

from squash_bot.list_timetable import commands

from tests import utils


class TestCommand:
    def test_list_timetable(self):
        api_url = "https://foo.com"
        with responses.RequestsMock() as requests:
            requests.post(
                url=f"{api_url}/enterprise/Timetable/GetClassTimeTable",
                status=200,
                json=json.load(
                    open(utils.fixture_path("example-list-timetable-api-response.json"))
                ),
            )
            command = commands.ListTimetableCommand()
            with mock.patch.object(command, "_api_url", return_value=api_url):
                response = command.handle(
                    {
                        "data": {
                            "options": [
                                {
                                    "type": 3,
                                    "name": "from-date",
                                    "value": "2024-03-24T18:00:00+00:00",
                                },
                                {
                                    "type": 3,
                                    "name": "to-date",
                                    "value": "2024-03-24T21:45:00+00:00",
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
                )

        assert response == {
            "content": f"2024-03-24T18:00:00+00:00 - 2024-03-24T21:45:00+00:00:\n* [2024-03-25T21:00:00]({api_url}/enterprise/bookingscentre/membertimetable#Details?&ResourceScheduleId=1900373)",
            "type": 4,
        }

    def test_no_available_sessions(self):
        api_url = "https://foo.com"
        with responses.RequestsMock() as requests:
            requests.post(
                url=f"{api_url}/enterprise/Timetable/GetClassTimeTable",
                status=200,
                json={"Results": []},
            )
            command = commands.ListTimetableCommand()
            with mock.patch.object(command, "_api_url", return_value=api_url):
                response = command.handle(
                    {
                        "data": {
                            "options": [
                                {
                                    "type": 3,
                                    "name": "from-date",
                                    "value": "2024-03-24T18:00:00+00:00",
                                },
                                {
                                    "type": 3,
                                    "name": "to-date",
                                    "value": "2024-03-24T21:45:00+00:00",
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
                )

        assert response == {
            "content": "No available sessions between 2024-03-24T18:00:00+00:00 and 2024-03-24T21:45:00+00:00",
            "type": 4,
        }
