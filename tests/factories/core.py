import factory

from squash_bot.core.data import dataclasses


class UserFactory(factory.Factory):
    id = factory.Sequence(lambda n: n)
    username = "paul"
    global_name = factory.LazyAttribute(lambda user: user.username.title())

    class Meta:
        model = dataclasses.User


class GuildFactory(factory.Factory):
    guild_id = "1"

    class Meta:
        model = dataclasses.Guild
