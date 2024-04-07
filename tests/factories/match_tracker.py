import datetime
import random
import uuid

import factory

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses

from tests.factories import core as core_factories


class MatchResultFactory(factory.Factory):
    winner = factory.SubFactory(
        core_factories.UserFactory, id=1, username="Paul", global_name="Paul!"
    )
    winner_score = 11
    loser_score = 3
    loser = factory.SubFactory(
        core_factories.UserFactory, id=2, username="John", global_name="John!"
    )
    served = factory.LazyAttribute(lambda r: random.choice([r.winner, r.loser]))
    played_at = factory.LazyFunction(datetime.datetime.now)
    logged_at = factory.LazyFunction(datetime.datetime.now)
    logged_by = factory.SubFactory(core_factories.UserFactory)
    result_id = factory.LazyFunction(uuid.uuid4)

    class Meta:
        model = dataclasses.MatchResult

    class Params:
        loser_served = factory.Trait(served=factory.SelfAttribute("loser"))
        winner_served = factory.Trait(served=factory.SelfAttribute("winner"))


def build_match_history_between(
    user_one: core_dataclasses.User, user_two: core_dataclasses.User, games_played: int = 10
) -> dataclasses.Matches:
    """
    Build a realistic match history between two users, where the winner is randomly chosen.
    """
    results = []
    for _ in range(games_played):
        winner_score = 11
        loser_score = random.randint(0, 9)
        winner = random.choice([user_one, user_two])
        loser = user_one if winner == user_two else user_two
        results.append(
            MatchResultFactory(
                winner=winner, winner_score=winner_score, loser=loser, loser_score=loser_score
            )
        )

    return dataclasses.Matches(match_results=results)
