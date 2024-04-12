import datetime
from unittest import mock

import time_machine

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker import commands, queries
from squash_bot.match_tracker.data import dataclasses, storage

from tests.factories import core as core_factories
from tests.factories import match_tracker as match_tracker_factories


class TestRecordMatchCommand:
    def test_user_options_include_username(self):
        command = commands.RecordMatchCommand()
        response = command.handle(
            {
                "data": {
                    "options": [
                        {"name": "player-one", "type": 6, "value": "1"},
                        {"name": "player-one-score", "type": 4, "value": 3},
                        {"name": "player-two", "type": 6, "value": "2"},
                        {"name": "player-two-score", "type": 4, "value": 11},
                    ],
                    "resolved": {
                        "users": {
                            "1": {
                                "id": "1",
                                "username": "user1",
                                "global_name": "global1",
                            },
                            "2": {
                                "id": "2",
                                "username": "user2",
                                "global_name": "global2",
                            },
                        }
                    },
                    "guild_id": "1",
                },
                "member": {
                    "user": {
                        "id": "1",
                        "username": "different-name",
                        "global_name": "different-global-name",
                    }
                },
            }
        ).as_dict()

        assert "global1" in response["data"]["content"]
        assert "global2" in response["data"]["content"]

    def test_show_username_when_global_name_unavailable(self):
        command = commands.RecordMatchCommand()
        response = command.handle(
            {
                "data": {
                    "options": [
                        {"name": "player-one", "type": 6, "value": "1"},
                        {"name": "player-one-score", "type": 4, "value": 3},
                        {"name": "player-two", "type": 6, "value": "2"},
                        {"name": "player-two-score", "type": 4, "value": 11},
                    ],
                    "resolved": {
                        "users": {
                            "1": {
                                "id": "1",
                                "username": "user1",
                                "global_name": None,
                            },
                            "2": {
                                "id": "2",
                                "username": "user2",
                                "global_name": None,
                            },
                        }
                    },
                    "guild_id": "1",
                },
                "member": {
                    "user": {
                        "id": "1",
                        "username": "different-name",
                        "global_name": "different-global-name",
                    }
                },
            }
        ).as_dict()

        assert "user1" in response["data"]["content"]
        assert "user2" in response["data"]["content"]

    def test_stores_result(self):
        command = commands.RecordMatchCommand()
        with mock.patch.object(storage, "get_all_match_results_as_list", return_value=[]):
            command.handle(
                {
                    "data": {
                        "options": [
                            {"name": "player-one", "type": 6, "value": "1"},
                            {"name": "player-one-score", "type": 4, "value": 3},
                            {"name": "player-two", "type": 6, "value": "2"},
                            {"name": "player-two-score", "type": 4, "value": 11},
                        ],
                        "resolved": {
                            "users": {
                                "1": {
                                    "id": "1",
                                    "username": "user1",
                                    "global_name": "global-user1",
                                },
                                "2": {
                                    "id": "2",
                                    "username": "user2",
                                    "global_name": "global-user2",
                                },
                            }
                        },
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        all_match_results = storage.get_all_match_results(
            guild=core_dataclasses.Guild(guild_id="1")
        ).match_results

        assert len(all_match_results) == 1

        match_result = all_match_results[0]
        assert match_result == dataclasses.MatchResult(
            winner=core_dataclasses.User(id="2", global_name="global-user2", username="user2"),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(id="1", global_name="global-user1", username="user1"),
            served=core_dataclasses.User(id="1", global_name="global-user1", username="user1"),
            played_at=mock.ANY,
            logged_at=mock.ANY,
            logged_by=core_dataclasses.User(
                id="1", global_name="different-global-name", username="different-name"
            ),
            result_id=mock.ANY,
        )


class TestShowMatches:
    def test_show_matches_with_no_matches(self):
        command = commands.ShowMatchesCommand()
        with mock.patch.object(storage, "get_all_match_results_as_list", return_value=[]):
            response = command.handle(
                {
                    "data": {
                        "options": [{"name": "sort-by", "value": ""}],
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        assert "No matches have been recorded" in response["data"]["content"]

    def test_show_matches(self):
        match_one_played_at = datetime.datetime(2021, 1, 1, 12, 0)
        paul = core_factories.UserFactory(id="1", username="Paul", global_name="Paul!")
        john = core_factories.UserFactory(id="2", username="John", global_name="John!")
        match_one = match_tracker_factories.MatchResultFactory(
            winner=paul, loser=john, served=john, played_at=match_one_played_at
        )

        match_two_played_at = datetime.datetime(2021, 1, 2, 12, 0)
        match_two = match_tracker_factories.MatchResultFactory(
            winner=paul, loser=john, served=john, played_at=match_two_played_at
        )

        matches = dataclasses.Matches(match_results=[match_one, match_two])

        command = commands.ShowMatchesCommand()
        with mock.patch.object(queries, "get_matches", return_value=matches):
            response = command.handle(
                {
                    "data": {
                        "options": [{"name": "sort-by", "value": ""}],
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        content = response["data"]["content"]
        assert (
            content
            == "```\n\nFriday, 1 January 2021:\n  John!  3  -  11  Paul!\n\nSaturday, 2 January 2021:\n  John!  3  -  11  Paul!```"
        )

    def test_show_matches_with_id(self):
        match_one_played_at = datetime.datetime(2021, 1, 1, 12, 0)
        paul = core_factories.UserFactory(id="1", username="Paul", global_name="Paul!")
        john = core_factories.UserFactory(id="2", username="John", global_name="John!")
        match_one = match_tracker_factories.MatchResultFactory(
            winner=paul, loser=john, served=john, played_at=match_one_played_at
        )
        matches = dataclasses.Matches(match_results=[match_one])

        command = commands.ShowMatchesCommand()
        with mock.patch.object(queries, "get_matches", return_value=matches):
            response = command.handle(
                {
                    "data": {
                        "options": [
                            {"name": "sort-by", "value": ""},
                            {"name": "with-ids", "value": "true"},
                        ],
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        content = response["data"]["content"]
        assert (
            content
            == f"```\n\nFriday, 1 January 2021:\n  John!  3  -  11  Paul!  ({match_one.result_id})```"
        )


class TestLeagueTable:
    def test_league_table_with_no_matches(self):
        command = commands.LeagueTableCommand()
        with mock.patch.object(storage, "get_all_match_results_as_list", return_value=[]):
            response = command.handle(
                {
                    "data": {
                        "options": [],
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        assert "No matches have been recorded" in response["data"]["content"]

    def test_league_table_with_matches(self):
        user_one = core_dataclasses.User(id="1", username="user1", global_name="global-user1")
        user_two = core_dataclasses.User(id="2", username="user2", global_name="global-user2")

        match_one = match_tracker_factories.MatchResultFactory(
            winner=user_one, winner_score=11, loser=user_two, loser_score=5
        )
        match_two = match_tracker_factories.MatchResultFactory(
            winner=user_two, loser=user_one, winner_score=13, loser_score=11
        )

        matches = dataclasses.Matches(match_results=[match_one, match_two])

        command = commands.LeagueTableCommand()
        with mock.patch.object(queries, "get_matches", return_value=matches):
            response = command.handle(
                {
                    "data": {
                        "options": [],
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        content = response["data"]["content"]
        table_data = _extract_data_from_table_string(content)
        assert ["global-user2", "1", "1", "50%"] in table_data
        assert ["global-user1", "1", "1", "50%"] in table_data

    def test_league_table_with_datetime_filter(self):
        user_one = core_dataclasses.User(id="1", username="user1", global_name="global-user1")
        user_two = core_dataclasses.User(id="2", username="user2", global_name="global-user2")

        match_one = match_tracker_factories.MatchResultFactory(
            winner=user_one,
            winner_score=11,
            loser=user_two,
            loser_score=5,
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
        )
        match_two = match_tracker_factories.MatchResultFactory(
            winner=user_two,
            loser=user_one,
            winner_score=13,
            loser_score=11,
            played_at=datetime.datetime(2021, 2, 1, 12, 0),
        )

        matches = dataclasses.Matches(match_results=[match_one, match_two])

        command = commands.LeagueTableCommand()
        with mock.patch.object(queries, "get_matches", return_value=matches):
            response = command.handle(
                {
                    "data": {
                        "options": [{"name": "include-matches-from", "value": "2021-01-02"}],
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        content = response["data"]["content"]
        table_data = _extract_data_from_table_string(content)
        assert ["global-user2", "1", "0", "100%"] in table_data
        assert ["global-user1", "0", "1", "0%"] in table_data


class TestHeadToHead:
    def test_head_to_head_with_matches(self):
        player_one = core_factories.UserFactory(id="1", username="player one")
        player_two = core_factories.UserFactory(id="2", username="player two")
        matches = match_tracker_factories.build_match_history_between(player_one, player_two)

        command = commands.HeadToHeadCommand()
        with mock.patch.object(queries, "get_matches", return_value=matches):
            response = command.handle(
                {
                    "data": {
                        "options": [
                            {"name": "player-one", "type": 6, "value": "1"},
                            {"name": "player-two", "type": 6, "value": "2"},
                        ],
                        "resolved": {
                            "users": {
                                "1": {
                                    "id": "1",
                                    "username": "player one",
                                    "global_name": "Player One",
                                },
                                "2": {
                                    "id": "2",
                                    "username": "player two",
                                    "global_name": "Player Two",
                                },
                            }
                        },
                        "guild_id": "1",
                    },
                    "member": {
                        "user": {
                            "id": "1",
                            "username": "different-name",
                            "global_name": "different-global-name",
                        }
                    },
                }
            ).as_dict()

        content = response["data"]["content"]

        # Check that the table contains the expected headers
        assert "Wins" in content
        assert "Win rate" in content
        assert "Win rate (serving)" in content
        assert "Point diff." in content
        assert "Avg. score" in content
        assert "Current win streak" in content
        assert "Highest win streak" in content
        assert "Last win" in content

        assert "Last 5 matches" in content

    def test_head_to_head_last_win(self):
        player_one = core_factories.UserFactory(id="1", username="player one")
        player_two = core_factories.UserFactory(id="2", username="player two")
        player_three = core_factories.UserFactory(id="3", username="player three")
        player_four = core_factories.UserFactory(id="4", username="player four")

        # Build a match history between all the players to make sure only the ones we want are returned
        matches = match_tracker_factories.build_match_history_between(player_one, player_three, 1)
        matches += match_tracker_factories.build_match_history_between(player_one, player_four, 1)
        matches += match_tracker_factories.build_match_history_between(player_two, player_three, 1)
        matches += match_tracker_factories.build_match_history_between(player_two, player_four, 1)

        match_one = match_tracker_factories.MatchResultFactory(
            winner=player_one, loser=player_two, played_at=datetime.datetime(2021, 1, 1, 12, 0)
        )
        match_two = match_tracker_factories.MatchResultFactory(
            winner=player_one, loser=player_two, played_at=datetime.datetime(2021, 1, 7, 12, 0)
        )
        match_three = match_tracker_factories.MatchResultFactory(
            winner=player_two, loser=player_one, played_at=datetime.datetime(2021, 1, 14, 12, 0)
        )
        matches += dataclasses.Matches([match_one, match_two, match_three])

        command = commands.HeadToHeadCommand()
        with mock.patch.object(queries, "get_matches", return_value=matches):
            with time_machine.travel(datetime.datetime(2021, 1, 15, 11, 0)):
                response = command.handle(
                    {
                        "data": {
                            "options": [
                                {"name": "player-one", "type": 6, "value": "1"},
                                {"name": "player-two", "type": 6, "value": "2"},
                            ],
                            "resolved": {
                                "users": {
                                    "1": {
                                        "id": "1",
                                        "username": "player one",
                                        "global_name": "Player One",
                                    },
                                    "2": {
                                        "id": "2",
                                        "username": "player two",
                                        "global_name": "Player Two",
                                    },
                                }
                            },
                            "guild_id": "1",
                        },
                        "member": {
                            "user": {
                                "id": "1",
                                "username": "different-name",
                                "global_name": "different-global-name",
                            }
                        },
                    }
                ).as_dict()

        content = response["data"]["content"]
        assert "8 days ago        Last win        Yesterday" in content


def _extract_data_from_table_string(
    table_string: str, column_separator: str = "│"
) -> list[list[str]]:
    data = []
    for line in table_string.replace("```", "").split("\n"):
        parts = line.split(column_separator)
        data.append([part.strip() for part in parts if part.strip()])
    return data
