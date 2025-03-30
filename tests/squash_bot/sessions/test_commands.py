import datetime
from unittest import mock

import time_machine

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.sessions import commands, dataclasses, storage


class TestBookSession:
    def test_stores_session_data(self, tmp_path):
        command = commands.BookSession()
        with time_machine.travel("2025-03-30 12:00:00"):
            with mock.patch.object(storage.settings_base.settings, "SESSIONS_PATH", tmp_path):
                command.handle(
                    {
                        "data": {
                            "options": [
                                {"name": "when", "type": 3, "value": "Monday at 6pm"},
                            ],
                            "resolved": {},
                            "guild_id": "1",
                        },
                        "member": {
                            "user": {
                                "id": "1",
                                "username": "name",
                                "global_name": "global-name",
                            }
                        },
                    }
                )

                all_sessions = storage.all_sessions(
                    guild=core_dataclasses.Guild(guild_id="1")
                ).sessions

        assert len(all_sessions) == 1

        session = all_sessions[0]
        assert session == dataclasses.Session(
            start_datetime=datetime.datetime(2025, 3, 31, 18, 0),
            booked_by=core_dataclasses.User(id="1", username="name", global_name="global-name"),
            session_id=mock.ANY,
        )
