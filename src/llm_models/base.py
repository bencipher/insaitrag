from abc import ABC, abstractmethod


class LLMStrategy(ABC):
    """Abstract class for different LLM strategies."""

    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    def get_embedding(self):
        pass
