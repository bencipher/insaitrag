import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from llm_models.base import LLMStrategy


class OpenAILLM(LLMStrategy):
    """Strategy for OpenAI LLM"""

    def get_model(self):
        return ChatOpenAI(model_name="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

    def get_embedding(self):
        return OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
