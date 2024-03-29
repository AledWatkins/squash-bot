from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses, storage


def get_matches(guild: core_dataclasses.Guild) -> dataclasses.Matches:
    return storage.get_all_match_results(guild=guild)
