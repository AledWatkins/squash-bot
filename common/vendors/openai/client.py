import enum

import openai

from common.settings import base as settings_base
from common.vendors import exceptions


class OpenAIError(exceptions.VendorError):
    pass


class OpenAIModel(enum.Enum):
    GPT_4 = "gpt-4"
    GPT_4o = "gpt-4o"


class OpenAIClient:
    _client: openai.OpenAI | None = None

    model: OpenAIModel = OpenAIModel.GPT_4
    max_tokens: int = 500
    temperature: float = 0.5

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_response(self, prompt: str, instructions: str | None = None) -> str:
        try:
            response = self.client.responses.create(
                model=self.model.value,
                instructions=instructions,
                input=prompt,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except openai.APIError as e:
            raise OpenAIError(f"OpenAI error: {e}") from e

        return response.output_text

    @property
    def client(self) -> openai.OpenAI:
        if self._client is None:
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client


def get_client() -> OpenAIClient:
    return OpenAIClient(api_key=settings_base.settings.OPENAI_API_KEY)
