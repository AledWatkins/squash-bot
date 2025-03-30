from __future__ import annotations

import datetime
import uuid
from typing import Any

import attrs

from squash_bot.core.data import dataclasses


@attrs.frozen
class Session:
    start_datetime: datetime.datetime
    booked_by: dataclasses.User
    session_id: uuid.UUID = attrs.Factory(uuid.uuid4)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        return cls(
            start_datetime=datetime.datetime.fromisoformat(data["start_datetime"]),
            booked_by=dataclasses.User.from_dict(data["booked_by"]),
            session_id=uuid.UUID(data["session_id"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_datetime": self.start_datetime.isoformat(),
            "booked_by": dataclasses.User.to_dict(self.booked_by),
            "session_id": str(self.session_id),
        }


@attrs.frozen
class Sessions:
    sessions: list[Session]

    @classmethod
    def from_sessions(cls, sessions: list[Session]) -> Sessions:
        return cls(sessions=sessions)

    # Query methods

    def for_date(self, date: datetime.date) -> list[Session]:
        return [s for s in self.sessions if s.start_datetime.date() == date]

    def for_today(self) -> list[Session]:
        return self.for_date(datetime.date.today())

    # Mutation methods

    def add(self, session: Session) -> Sessions:
        return Sessions(sessions=self.sessions + [session])

    def remove(self, session: Session) -> Sessions:
        return Sessions(sessions=[s for s in self.sessions if s.session_id != session.session_id])
