import abc
import datetime
import enum
import typing
import urllib.parse

import attrs
import requests

SESSION_DATETIME_FORMAT = "%H:%M"


class TimeOfDayType(enum.Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    POST_WORK_SESH = "PostWorkSesh"
    POST_WORK_SESH_PLUS = "PostWorkSeshPlus"
    ALL = "All"


@attrs.frozen
class TimetableSession:
    start_datetime: datetime.datetime
    available_slots: int
    schedule_id: int

    def __str__(self) -> str:
        return f"{self.start_datetime.strftime(SESSION_DATETIME_FORMAT)}"


class Timetable(abc.ABC):
    """
    An abstract class used to define squash timetable session implementations
    """

    _API_URL: str = ""
    _API_TIMETABLE_ENDPOINT: str = ""

    @abc.abstractmethod
    def get_sessions(
        self, from_date: datetime.datetime, to_date: datetime.datetime
    ) -> list[TimetableSession]:
        pass

    @abc.abstractmethod
    def get_booking_link(self, schedule_id: int) -> str:
        pass

    @staticmethod
    def filter_sessions(
        sessions: list[TimetableSession],
        time_of_day: TimeOfDayType,
        show_unavailable_slots: bool = False,
    ) -> list[TimetableSession]:
        if not sessions or time_of_day is TimeOfDayType.ALL:
            return sessions

        target_hours = {
            TimeOfDayType.MORNING: range(0, 12),
            TimeOfDayType.AFTERNOON: range(12, 17),
            TimeOfDayType.EVENING: range(17, 24),
            TimeOfDayType.POST_WORK_SESH: 19,
            TimeOfDayType.POST_WORK_SESH_PLUS: range(18, 21),
        }[time_of_day]

        return [
            session
            for session in sessions
            if (show_unavailable_slots or session.available_slots > 0)
            and session.start_datetime.hour in target_hours
        ]


class CelticLeisureTimetable(Timetable):
    """
    A subclass of Timetable to obtain squash timetable information specific to Celtic Leisure
    """

    _API_URL: str = "https://celticleisure.legendonlineservices.co.uk"
    _API_TIMETABLE_ENDPOINT: str = "enterprise/Timetable/GetClassTimeTable"
    _API_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    _API_TIMETABLE_BOOKING_ENDPOINT: str = "enterprise/bookingscentre/membertimetable#Details?"

    _ACTIVITY_ID: str = "87"
    _LOCATION_ID: str = "1917"

    def get_sessions(
        self, from_date: datetime.datetime, to_date: datetime.datetime
    ) -> list[TimetableSession]:
        timetable_dict = self._get_timetable_between_dates(from_date, to_date)
        if not timetable_dict:
            return []

        return self._format_timetable_sessions(timetable_dict)

    def get_booking_link(self, schedule_id: int) -> str:
        return urllib.parse.urljoin(
            self._API_URL,
            f"{self._API_TIMETABLE_BOOKING_ENDPOINT}&ResourceScheduleId={schedule_id}",
        )

    def _get_timetable_between_dates(
        self, from_date: datetime.datetime, to_date: datetime.datetime
    ) -> dict[str, typing.Any]:
        return requests.post(
            urllib.parse.urljoin(self._API_URL, self._API_TIMETABLE_ENDPOINT),
            json={
                "ResourceSubTypeIdList": self._ACTIVITY_ID,
                "FacilityLocationIdList": self._LOCATION_ID,
                "DateFrom": from_date.strftime(self._API_DATETIME_FORMAT),
                "DateTo": to_date.strftime(self._API_DATETIME_FORMAT),
            },
        ).json()

    def _format_timetable_sessions(
        self, timetable: dict[str, typing.Any]
    ) -> list[TimetableSession]:
        sessions = []
        for result in timetable.get("Results", []):
            if not (available_slots := result.get("AvailableSlots")):
                continue

            if not (start_datetime_str := result.get("start")):
                continue

            if not (schedule_id := result.get("ResourceScheduleId")):
                continue

            sessions.append(
                TimetableSession(
                    datetime.datetime.strptime(start_datetime_str, self._API_DATETIME_FORMAT),
                    available_slots,
                    schedule_id,
                )
            )

        return sessions
