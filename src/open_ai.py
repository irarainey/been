import logging
from openai import AzureOpenAI
from constants import GPT_MODEL
from typing import List


# OpenAI client class
class OpenAIClient:
    """
    A class to interact with the Azure OpenAI API.

    Attributes:
        client (AzureOpenAI): The Azure OpenAI client instance.
    """

    def __init__(self, endpoint: str, key: str, version: str):
        """
        Initialize the Azure OpenAI client.

        Args:
            endpoint (str): The Azure endpoint.
            key (str): The API key.
            version (str): The API version.
        """
        try:
            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=key,
                api_version=version,
            )
        except Exception as e:
            logging.error(f"Failed to create OpenAI client: {e}")
            raise

    def send_prompt(self, conversation: List) -> str:
        """
        Send a conversation prompt to the OpenAI API.

        Args:
            conversation (List): The conversation messages.

        Returns:
            str: The response from the OpenAI API.
        """
        logging.info("Sending prompt...")
        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=conversation,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Failed to generate trip summary: {e}")
            raise
