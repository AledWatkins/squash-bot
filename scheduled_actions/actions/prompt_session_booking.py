import datetime
import logging
from collections.abc import Collection, Iterable

import attrs

from common.settings import base as settings_base
from common.timetable import timetable
from common.vendors.openai import client as openai_client
from scheduled_actions import action, dataclasses, send

logger = logging.getLogger("scheduled_actions.actions")
logger.setLevel(logging.INFO)


class PromptSessionBooking(action.Action):
    code = "prompt-session-booking"

    _week_days = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    def run(self, context: dict) -> None:
        sessions = self._get_sessions()
        message = dataclasses.Message(
            content=self._build_message_content(sessions),
        )
        for channel in self._channels_to_notify():
            logger.info(f"{self.__class__.__name__} - Sending message to channel {channel.id}")
            send.send_message_to_channel(channel=channel, message=message)

    def _channels_to_notify(self) -> Iterable[dataclasses.Channel]:
        logger.info(
            f"{self.__class__.__name__} - Got channels: {settings_base.settings.PROMPT_SESSION_BOOKING_CHANNEL_IDS}"
        )
        yield from [
            dataclasses.Channel(
                id=channel_id,
            )
            for channel_id in settings_base.settings.PROMPT_SESSION_BOOKING_CHANNEL_IDS
        ]

    def _get_sessions(self) -> list[timetable.TimetableSession]:
        sessions = timetable.CelticLeisureTimetable().get_sessions(
            from_date=datetime.datetime.now(),
            to_date=datetime.datetime.now() + datetime.timedelta(days=7),
        )
        logger.info(f"{self.__class__.__name__} - Got {len(sessions)} sessions from API")

        # We only want to notify about sessions at 6pm on weekdays
        time_of_day = [18, 19]
        days = timetable.DayType.WEEKDAY
        return timetable.CelticLeisureTimetable.filter_sessions(sessions, time_of_day, days=days)

    def _build_message_content(self, sessions: list[timetable.TimetableSession]) -> str:
        # Use GPT to build the message content if the feature is enabled
        # Otherwise, use the default method
        # If we fail to build the content via GPT, we fall back to the default method
        if settings_base.settings.feature_enabled(
            settings_base.FlaggedFeature.USE_GPT_FOR_PROMPT_SESSION_BOOKING
        ):
            session_context = self.SessionsContext(
                sessions=sessions,
                preferred_time="6pm",
                fallback_time="7pm",
                notes=settings_base.settings.PROMPT_SESSION_BOOKING_GPT_NOTES,
            )
            try:
                return self._build_content_via_openai(session_context)
            except Exception as e:
                print(e)
                logger.error(f"{self.__class__.__name__} - Error building content via OpenAI: {e}")

        return self._build_content(sessions)

    @attrs.frozen
    class SessionsContext:
        sessions: Collection[timetable.TimetableSession]
        preferred_time: str
        fallback_time: str
        notes: Collection[str]

    def _build_content_via_openai(self, context: SessionsContext) -> str:
        lines = [
            f"You are helping a group of friends organise a weekly squash game. The current date is {datetime.date.today().isoformat()}. ",
            "Here is a list of available court sessions for next week at their local gym:",
        ]
        sessions_by_day = {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
        }
        for session in context.sessions:
            start = session.start_datetime
            weekday = self._week_days[start.weekday()]
            sessions_by_day[weekday].append(start)

        # Add session data
        for day, start_datetimes in sessions_by_day.items():
            if start_datetimes:
                lines.append(
                    f"{day}: {', '.join([str(start.hour) + ':00' for start in start_datetimes])}"
                )
            else:
                lines.append(f"{day}: No sessions available")

        # Add preferred and fallback times
        lines.append(
            f"They play at {context.preferred_time}. Only mention {context.fallback_time} if there are very few options. "
        )

        # Add message guidelines
        lines.append(
            "Based on this information, provide the information that's required for the group to make a decision on when to play. "
            f"Keep it short and to the point. Don't be cringe and over-the-top. Don't add information that's not relevant, e.g. if there are more than 1 day have {context.preferred_time} sessions, you don't need to mention {context.fallback_time}. "
            "Only suggest sessions that are actually listed above. "
        )

        # Add notes
        if context.notes:
            lines.append("Some notes:")
            lines.append(context.notes)
            lines.append(
                "Don't include these notes in the message, just use them to help you write it."
            )

        # Add example message
        lines.append(
            "An example of a message might be, 'Are we playing squash this week? Monday or Wednesday are free.' "
            "Another example might be, 'Squash? We can do 6pm on Tuesday without [friend] or all of us on Monday at 7.' "
        )

        return openai_client.get_client().get_response("\n".join(lines))

    def _build_content(self, sessions: list[timetable.TimetableSession]) -> str:
        base_msg = "Are we playing squash this week?"

        available_week_days = list(
            set(self._week_days[session.start_datetime.weekday()] for session in sessions)
        )
        non_available_days = set(self._week_days.values()) - set(available_week_days)
        if not available_week_days:
            return base_msg + " All 6pm sessions are already booked this week 💀"
        elif len(non_available_days) <= 2:
            return (
                base_msg + f" 6pm is free every day other than {' and '.join(non_available_days)}"
            )
        else:
            return (
                base_msg
                + f" 6pm is free on {', '.join(available_week_days[:-1]) + ' and ' + available_week_days[-1]}"
            )
