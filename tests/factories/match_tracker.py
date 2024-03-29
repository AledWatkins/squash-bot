import datetime
import uuid

import factory

from squash_bot.match_tracker.data import dataclasses

from tests.factories import core as core_factories


class MatchResultFactory(factory.Factory):
    winner = factory.SubFactory(core_factories.UserFactory)
    winner_score = 11
    loser_score = 3
    loser = factory.SubFactory(core_factories.UserFactory)
    served = factory.SubFactory(core_factories.UserFactory)
    played_at = factory.LazyFunction(datetime.datetime.now)
    logged_at = factory.LazyFunction(datetime.datetime.now)
    logged_by = factory.SubFactory(core_factories.UserFactory)
    result_id = factory.LazyFunction(uuid.uuid4)

    class Meta:
        model = dataclasses.MatchResult
