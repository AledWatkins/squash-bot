import json

from common.settings import base as settings_base
from common.storage import base as storage_base
from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.sessions import dataclasses


def all_sessions_data_as_list(guild: core_dataclasses.Guild) -> list:
    file_contents = storage_base.read_file(
        file_path=settings_base.settings.SESSIONS_PATH,
        file_name=_sessions_file_name(guild),
        create_if_missing=True,
    )
    return json.loads(file_contents or "[]")


def all_sessions(guild: core_dataclasses.Guild) -> dataclasses.Sessions:
    return dataclasses.Sessions(
        [
            dataclasses.Session.from_dict(session)
            for session in all_sessions_data_as_list(guild=guild)
        ]
    )


def convert_sessions_to_dicts(sessions: dataclasses.Sessions) -> list[dict]:
    return [session.to_dict() for session in sessions.sessions]


def store_session(session: dataclasses.Session, guild: core_dataclasses.Guild) -> None:
    """
    Get the current sessions, add the new sessions, and store the updated list
    """
    storage_base.store_file(
        file_path=settings_base.settings.SESSIONS_PATH,
        file_name=_sessions_file_name(guild),
        contents=json.dumps(convert_sessions_to_dicts(all_sessions(guild).add(session))),
    )


def _sessions_file_name(guild: core_dataclasses.Guild) -> str:
    return f"{guild.guild_id}/{settings_base.settings.SESSIONS_FILE}"
