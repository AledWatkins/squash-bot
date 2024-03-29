import json

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses
from squash_bot.settings import base as settings_base
from squash_bot.storage import base


def get_all_match_results_as_dict(guild: core_dataclasses.Guild) -> dict:
    file_contents = base.read_file(
        file_path=settings_base.settings.MATCH_RESULTS_PATH,
        file_name=_results_file_name(guild),
        create_if_missing=True,
    )
    return json.loads(file_contents or "{}")


def get_all_match_results(guild: core_dataclasses.Guild) -> list[dataclasses.MatchResult]:
    return [
        dataclasses.MatchResult.from_dict(result)
        for result in get_all_match_results_as_dict(guild=guild)
    ]


def convert_match_results_to_dicts(results: list[dataclasses.MatchResult]) -> list[dict]:
    return [result.to_dict() for result in results]


def store_match_result(
    match_result: dataclasses.MatchResult, guild: core_dataclasses.Guild
) -> None:
    """
    Get the current match results, add the new result, and store the updated list
    """
    all_results = get_all_match_results(guild)
    all_results.append(match_result)

    match_results_as_dicts = convert_match_results_to_dicts(all_results)
    base.store_file(
        file_path=settings_base.settings.MATCH_RESULTS_PATH,
        file_name=_results_file_name(guild),
        contents=json.dumps(match_results_as_dicts),
    )


def _results_file_name(guild: core_dataclasses.Guild) -> str:
    return f"{guild.guild_id}/{settings_base.settings.MATCH_RESULTS_FILE}"