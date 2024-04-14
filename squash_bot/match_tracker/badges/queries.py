import datetime

from squash_bot.match_tracker.data import dataclasses as dataclasses

from . import badge, badge_definitions


def collect_badges(
    matches: dataclasses.Matches, badges: list[type[badge.Badge]]
) -> list[badge.Badge]:
    """
    This function will collect all the badges that the players have earned.
    """
    # Fetch all the `Collectors` required for the requested badges
    collectors = [badge_definitions.badge_collector_mapping[badge]() for badge in badges]

    # Loop over all the matches and allow each collector to update their contexts
    for match in matches.match_results:
        for collector in collectors:
            collector.mutate_context_for_match(match)

    # Collect the badges
    collected_badges = []
    for collector in collectors:
        collected_badges.extend(collector.collect())

    return collected_badges


def filter_badges_by_session(
    badges: list[badge.Badge], session_date: datetime.date
) -> list[badge.Badge]:
    """
    This function will filter the badges to only include those that were earned in games played on the given date.
    """
    return [badge for badge in badges if badge.badge_earned_in.played_on == session_date]


def filter_badges_by_result_id(badges: list[badge.Badge], result_id: str) -> list[badge.Badge]:
    """
    This function will filter the badges to only include those that were earned in the specified match.
    """
    return [badge for badge in badges if badge.badge_earned_in.result_id == result_id]
