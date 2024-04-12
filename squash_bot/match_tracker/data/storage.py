import json

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses
from squash_bot.settings import base as settings_base
from squash_bot.storage import base


def get_all_match_results_as_list(guild: core_dataclasses.Guild) -> list:
    file_contents = base.read_file(
        file_path=settings_base.settings.MATCH_RESULTS_PATH,
        file_name=_results_file_name(guild),
        create_if_missing=True,
    )
    return json.loads(file_contents or "[]")


def get_all_match_results(guild: core_dataclasses.Guild) -> dataclasses.Matches:
    return dataclasses.Matches.from_match_results(get_all_match_results_as_list(guild=guild))


def convert_match_results_to_dicts(matches: dataclasses.Matches) -> list[dict]:
    return [match_result.to_dict() for match_result in matches.match_results]


def store_match_result(
    match_result: dataclasses.MatchResult, guild: core_dataclasses.Guild
) -> None:
    """
    Get the current match results, add the new result, and store the updated list
    """
    all_results = get_all_match_results(guild)
    all_results = all_results.add(match_result)

    match_results_as_dicts = convert_match_results_to_dicts(all_results)
    base.store_file(
        file_path=settings_base.settings.MATCH_RESULTS_PATH,
        file_name=_results_file_name(guild),
        contents=json.dumps(match_results_as_dicts),
    )


def replace_match_result(
    match_result: dataclasses.MatchResult, guild: core_dataclasses.Guild
) -> None:
    """
    Get the current match results, replace the existing result with the new one, and store the updated list
    """
    all_results = get_all_match_results(guild)

    modified_results = all_results.replace(match_result)

    match_results_as_dicts = convert_match_results_to_dicts(modified_results)
    base.store_file(
        file_path=settings_base.settings.MATCH_RESULTS_PATH,
        file_name=_results_file_name(guild),
        contents=json.dumps(match_results_as_dicts),
    )


def _results_file_name(guild: core_dataclasses.Guild) -> str:
    return f"{guild.guild_id}/{settings_base.settings.MATCH_RESULTS_FILE}"
