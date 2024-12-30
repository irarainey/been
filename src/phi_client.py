import logging
from typing import List
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential


# Phi client class
class PhiClient:
    def __init__(self, endpoint: str, key: str):
        try:
            self.client = ChatCompletionsClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key)
            )
        except Exception as e:
            logging.error(f"Failed to create Phi client: {e}")
            raise

    def send_prompt(self, conversation: List) -> str:
        try:
            response = self.client.complete(conversation)
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Failed to generate trip summary: {e}")
            raise
