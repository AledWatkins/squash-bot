from squash_bot.core import response_message


class TestResponseMessage:
    def test_channel_response_message_body(self):
        test_str = "This is a test"
        channel_message_response_body = response_message.ChannelMessageResponseBody(test_str)
        assert channel_message_response_body.as_dict() == {
            "type": 4,
            "data": {"content": test_str},
        }

    def test_ephemeral_channel_response_message_body(self):
        test_str = "This is another test"
        ephemeral_channel_message_response_body = response_message.EphemeralChannelMessageResponseBody(
            test_str
        )
        assert ephemeral_channel_message_response_body.as_dict() == {
            "type": 4,
            "data": {"content": test_str, "flags": 64},
        }
