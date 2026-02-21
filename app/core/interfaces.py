from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Contract for any AI/LLM service."""

    @abstractmethod
    async def generate_summary(self, text: str) -> str:
        pass

    @abstractmethod
    async def analyze_sentiment(self, review_text: str) -> str:
        pass


class StorageProvider(ABC):
    """Contract for any file storage service (Local disk, AWS S3, etc.)."""

    @abstractmethod
    async def save_file(self, filename: str, content: bytes) -> str:
        pass
