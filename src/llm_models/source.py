from functools import lru_cache

from llm_models.gemini_llm import GeminiLLM
from llm_models.openai_llm import OpenAILLM


class ModelFactory:
    """Factory to get instances of LLMs and Embeddings using Strategy Pattern."""

    _llms = {
        "openai": OpenAILLM(),
        "gemini": GeminiLLM(),
    }

    @staticmethod
    @lru_cache(maxsize=1)
    def get_llm(model_name: str = "gemini"):
        """Returns an LLM instance using the chosen strategy"""
        strategy = ModelFactory._llms.get(model_name)
        if not strategy:
            raise ValueError(f"Unsupported LLM model: {model_name}")
        return strategy.get_model()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_embedding(model_name: str = "gemini"):
        """Returns an Embedding instance using the chosen strategy"""
        strategy = ModelFactory._llms.get(model_name)
        if not strategy:
            raise ValueError(f"Unsupported embedding model: {model_name}")
        return strategy.get_embedding()
