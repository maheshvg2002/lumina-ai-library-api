from app.core.interfaces import LLMProvider, StorageProvider
from app.infrastructure.services.local_storage_service import LocalDiskStorage
from app.infrastructure.services.ollama_service import OllamaService


def get_llm_service() -> LLMProvider:
    """Injects the current LLM provider (Ollama)."""
    return OllamaService()


def get_storage_service() -> StorageProvider:
    """Injects the current Storage provider (Local Disk)."""
    return LocalDiskStorage()
