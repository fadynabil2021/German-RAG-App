
from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CoHereProvider
import cohere

class LLMProviderFactory:
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            api_key = self.config.OPENAI_API_KEY.get_secret_value() if self.config.OPENAI_API_KEY else None
            return OpenAIProvider(
                api_key = api_key,
                api_url = self.config.OPENAI_API_URL,
                default_input_max_characters=1000, # Hardcoded default as config removed it
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        if provider == LLMEnums.COHERE.value:
            api_key = self.config.COHERE_API_KEY.get_secret_value() if self.config.COHERE_API_KEY else None
            return CoHereProvider(
                api_key = api_key,
                default_input_max_characters=1000,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None
