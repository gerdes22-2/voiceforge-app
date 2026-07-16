import os

class Settings:
    PROJECT_NAME = "VoiceForge Gateway"
    BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:3000")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")

settings = Settings()
