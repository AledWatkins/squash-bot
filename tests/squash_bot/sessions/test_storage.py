import datetime
import json
import uuid
from unittest import mock

from common.storage import base as storage_base
from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.sessions import dataclasses, storage


class TestAllSessions:
    def test_gets_sessions(self, tmp_path):
        session = dataclasses.Session(
            start_datetime=datetime.datetime(2023, 10, 1, 12, 0),
            booked_by=core_dataclasses.User(
                id="1", username="player_1", global_name="global-player_1"
            ),
            session_id=uuid.uuid4(),
        )
        fake_sessions = [session.to_dict()]
        guild = core_dataclasses.Guild(guild_id="1")
        storage_base.LocalStorage().store_file(
            file_path=tmp_path,
            file_name=storage._sessions_file_name(guild),
            contents=json.dumps(fake_sessions),
        )

        with mock.patch.object(storage.settings_base.settings, "SESSIONS_PATH", tmp_path):
            assert storage.all_sessions(guild).sessions == [session]


class TestStoreSession:
    def test_can_store_new_session(self, tmp_path):
        session = dataclasses.Session(
            start_datetime=datetime.datetime(2023, 10, 1, 12, 0),
            booked_by=core_dataclasses.User(
                id="1", username="player_1", global_name="global-player_1"
            ),
            session_id=uuid.uuid4(),
        )
        guild = core_dataclasses.Guild(guild_id="1")

        with mock.patch.object(storage.settings_base.settings, "SESSIONS_PATH", tmp_path):
            storage.store_session(session, guild)

            assert storage.all_sessions(guild).sessions == [session]

    def test_can_append_sessions(self, tmp_path):
        prev_session = dataclasses.Session(
            start_datetime=datetime.datetime(2023, 10, 1, 12, 0),
            booked_by=core_dataclasses.User(
                id="1", username="player_1", global_name="global-player_1"
            ),
            session_id=uuid.uuid4(),
        )
        fake_sessions = [prev_session.to_dict()]
        guild = core_dataclasses.Guild(guild_id="1")
        storage_base.LocalStorage().store_file(
            file_path=tmp_path,
            file_name=storage._sessions_file_name(guild),
            contents=json.dumps(fake_sessions),
        )

        new_session = dataclasses.Session(
            start_datetime=datetime.datetime(2023, 11, 1, 12, 0),
            booked_by=core_dataclasses.User(
                id="2", username="player_2", global_name="global-player_2"
            ),
            session_id=uuid.uuid4(),
        )
        guild = core_dataclasses.Guild(guild_id="1")

        with mock.patch.object(storage.settings_base.settings, "SESSIONS_PATH", tmp_path):
            storage.store_session(new_session, guild)

            assert storage.all_sessions(guild).sessions == [prev_session, new_session]
