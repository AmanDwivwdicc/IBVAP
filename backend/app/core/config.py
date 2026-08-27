from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "IBVAP Central Server"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str  # Needed for backend admin operations

    # Storage Settings
    STORAGE_BUCKET_EVIDENCE: str = "evidence"
    STORAGE_BUCKET_CROPS: str = "ai-crops"

    # Security
    RATE_LIMIT_PER_DEVICE: int = 100
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
