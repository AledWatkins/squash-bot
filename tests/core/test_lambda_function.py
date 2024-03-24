import json

from squash_bot.core import lambda_function
from tests import utils


class TestLambdaHandler:
    def test_ping_response(self):
        response = lambda_function.lambda_handler(
            {
                "body": {"type": 1},
            },
            {},
        )
        assert response == {
            "statusCode": 200,
            "body": json.dumps({"type": 1}),
        }

    def test_unknown_type_response(self):
        response = lambda_function.lambda_handler(
            {
                "body": {"type": 31},
            },
            {},
        )
        assert response == {
            "statusCode": 400,
            "body": json.dumps("Unknown interaction type"),
        }

    def test_with_unknown_command(self):
        path = utils.fixture_path("example-unknown-event.json")
        with open(path) as f:
            example_event = json.load(f)

        response = lambda_function.lambda_handler(
            example_event,
            {},
        )
        assert response == {
            "statusCode": 400,
            "body": json.dumps("Unknown command"),
        }
