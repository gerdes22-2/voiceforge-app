from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoiceForge"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/voiceforge"
    
    # Auth
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_GLOBAL: str = "100/minute"
    
        
    # Storage
    STORAGE_PROVIDER: str = "local"
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_REGION_NAME: str = "auto"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

settings = Settings()
