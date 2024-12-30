import logging
from openai import AzureOpenAI
from constants import GPT_MODEL
from typing import List


# OpenAI GPT client class
class OpenAIClient:
    def __init__(self, endpoint: str, key: str, version: str):
        try:
            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=key,
                api_version=version,
            )
        except Exception as e:
            logging.error(f"Failed to create OpenAI GPT client: {e}")
            raise

    def send_prompt(self, conversation: List) -> str:
        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=conversation,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Failed to generate trip summary: {e}")
            raise
