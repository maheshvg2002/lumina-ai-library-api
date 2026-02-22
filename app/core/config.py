from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LuminaLib"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- DATABASE ---
    # Reads the beautifully encoded URL directly from .env or docker-compose
    DATABASE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # --- SECURITY ---
    # No default value! Forces the app to safely load it from .env
    SECRET_KEY: str = "dev_fallback_secret_key_for_testing_only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- AI SERVICE ---
    OLLAMA_BASE_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
