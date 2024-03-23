import json

from squash_bot.core import main


class TestLambdaHandler:
    def test_ping_response(self):
        response = main.lambda_handler(
            {
                "body": json.dumps({"type": 1}),
            },
            {},
        )
        assert response == {
            "statusCode": 200,
            "body": json.dumps({"type": 1}),
        }

    def test_unknown_type_response(self):
        response = main.lambda_handler(
            {
                "body": json.dumps({"type": 31}),
            },
            {},
        )
        assert response == {
            "statusCode": 400,
            "body": '"Unknown interaction type"',
        }