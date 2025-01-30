import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from llm_models.base import LLMStrategy


class GeminiLLM(LLMStrategy):
    """Strategy for Gemini LLM"""

    def get_model(self):
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY")
        )

    def get_embedding(self):
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=os.getenv("GEMINI_API_KEY")
        )
