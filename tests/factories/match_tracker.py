import datetime
import uuid

import factory

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
