from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoiceForge"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://neondb_owner:npg_rlOf1Nn7UgMa@ep-morning-star-au3r4qba.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require"

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL

    
    # Auth
    SECRET_KEY: str = "9i7nTR8cMYNWVAO9UMH5gpBvr9nUVLbjOsdL5WiW3Ic"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Celery - Optional, defaults to local
    CELERY_BROKER_URL: str = "rediss://default:gQAAAAAAAnW6AAIgcDI3MjVkNjU3YzA2Nzg0NDQ0ODM5YmFiOWYzYTg3NGVkNQ@dominant-terrier-161210.upstash.io:6379"
    CELERY_RESULT_BACKEND: str = "rediss://default:gQAAAAAAAnW6AAIgcDI3MjVkNjU3YzA2Nzg0NDQ0ODM5YmFiOWYzYTg3NGVkNQ@dominant-terrier-161210.upstash.io:6379"
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_GLOBAL: str = "100/minute"
    
    # Storage - Optional, defaults to local
    STORAGE_PROVIDER: str = "s3"
    S3_ENDPOINT_URL: Optional[str] = "https://9a20e9cc38517978a315b32fab96dcc1.r2.cloudflarestorage.com"
    S3_ACCESS_KEY_ID: Optional[str] = "eb4bfae93068e8a5a7728ed04a4e76bf"
    S3_SECRET_ACCESS_KEY: Optional[str] = "0fc34aa7e772f38cb9690828f241356fa6062114fb6f0c3f18bb01bb1f84e575"
    S3_BUCKET_NAME: Optional[str] = "voiceforge"
    S3_REGION_NAME: Optional[str] = "auto"

    # External APIs
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    HUGGING_FACE_API_KEY: Optional[str] = None
    RUNPOD_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

settings = Settings()
