import factory

from squash_bot.core.data import dataclasses


class UserFactory(factory.Factory):
    id = 1
    username = "paul"
    global_name = "Paul"

    class Meta:
        model = dataclasses.User


class GuildFactory(factory.Factory):
    guild_id = "1"

    class Meta:
        model = dataclasses.Guild
