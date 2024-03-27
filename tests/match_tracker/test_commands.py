from unittest import mock

from squash_bot.core.data import user
from squash_bot.match_tracker import commands
from squash_bot.match_tracker.data import dataclasses, storage


class TestRecordMatchCommand:
    def test_user_options_include_username(self):
        command = commands.RecordMatchCommand()
        assert command.handle(
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
                }
            }
        ) == {
            "type": 4,
            "data": {"content": "Match recorded: global-user2 11 - 3 global-user1"},
        }

    def test_show_username_when_global_name_unavailable(self):
        command = commands.RecordMatchCommand()
        assert command.handle(
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
                }
            }
        ) == {
            "type": 4,
            "data": {"content": "Match recorded: user2 11 - 3 user1"},
        }

    def test_stores_result(self):
        command = commands.RecordMatchCommand()
        with mock.patch.object(storage, "get_all_match_results_as_dict", return_value={}):
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
                    }
                }
            )

        all_match_results = storage.get_all_match_results()
        assert len(all_match_results) == 1

        match_result = all_match_results[0]
        assert match_result == dataclasses.MatchResult(
            winner=user.User(id="2", global_name="global-user2", username="user2"),
            winner_score=11,
            loser_score=3,
            loser=user.User(id="1", global_name="global-user1", username="user1"),
            played_at=mock.ANY,
            logged_at=mock.ANY,
        )
