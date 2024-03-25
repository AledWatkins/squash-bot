from squash_bot.match_tracker import commands


class TestRecordMatchCommand:
    def test_user_options_include_username(self):
        command = commands.RecordMatchCommand()
        assert command.handle(
            {
                "data": {
                    "options": [
                        {"name": "winner", "type": 6, "value": "1"},
                        {"name": "winner-score", "type": 4, "value": 11},
                        {"name": "loser", "type": 6, "value": "2"},
                        {"name": "loser-score", "type": 4, "value": 3},
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
            "data": {"content": "Match recorded: user1 11 - 3 user2"},
        }
