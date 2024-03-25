import json
import typing

from nacl import exceptions, signing

from squash_bot.settings import base as settings_base


class CouldNotVerifyRequest(Exception):
    """
    Raised when the request could not be verified
    """


class Verifyier:
    def verify(self, event: dict[str, typing.Any]) -> None:
        """
        Verify a request event

        :raises CouldNotVerifyRequest: If the request could not be verified
        """
        raise NotImplementedError


class NACLVerifyier(Verifyier):
    def verify(self, event: dict[str, typing.Any]) -> None:
        signature = event["headers"]["x-signature-ed25519"]
        timestamp = event["headers"]["x-signature-timestamp"]

        public_key = settings_base.settings.PUBLIC_KEY

        verify_key = signing.VerifyKey(bytes.fromhex(public_key))
        body_json = json.loads(event["body"])
        message = timestamp + json.dumps(body_json, separators=(",", ":"))

        try:
            verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
        except exceptions.BadSignatureError as e:
            raise CouldNotVerifyRequest from e


class NoopVerifier(Verifyier):
    def verify(self, body: dict[str, typing.Any]) -> None: ...
