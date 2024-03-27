from squash_bot.match_tracker import commands


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
