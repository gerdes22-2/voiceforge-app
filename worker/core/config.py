import os

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "rediss://default:gQAAAAAAAnW6AAIgcDI3MjVkNjU3YzA2Nzg0NDQ0ODM5YmFiOWYzYTg3NGVkNQ@dominant-terrier-161210.upstash.io:6379")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rediss://default:gQAAAAAAAnW6AAIgcDI3MjVkNjU3YzA2Nzg0NDQ0ODM5YmFiOWYzYTg3NGVkNQ@dominant-terrier-161210.upstash.io:6379")

settings = Settings()
