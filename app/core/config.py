# app/core/config.py
from urllib.parse import quote_plus  # <--- IMPORT THIS

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LuminaLib"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./lumina_fallback.db"

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # Computed Database URL (Now Safe!)
    @property
    def DATABASE_URL(self) -> str:
        # We encoded the password to handle symbols like '@', '%', etc.
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{encoded_password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Service
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
