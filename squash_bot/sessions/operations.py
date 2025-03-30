import datetime

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.sessions import dataclasses, storage


def record_session_at(
    *, at: datetime.datetime, guild: core_dataclasses.Guild, booked_by: core_dataclasses.User
) -> dataclasses.Session:
    """
    Record a session on a specific date and time.
    """
    session = dataclasses.Session(start_datetime=at, booked_by=booked_by)
    storage.store_session(session=session, guild=guild)
    return session
