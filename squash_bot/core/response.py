import json
import typing

import attrs


@attrs.frozen
class Response:
    status_code: int
    body_data: dict[str, typing.Any] | str

    def as_dict(self) -> dict[str, typing.Any]:
        return {
            "statusCode": self.status_code,
            "body": json.dumps(self.body_data),
        }
