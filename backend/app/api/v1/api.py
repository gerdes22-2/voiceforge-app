from fastapi import APIRouter
from app.api.v1 import auth, projects, uploads

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
from app.api.v1 import datasets
api_router.include_router(datasets.router, prefix='/datasets', tags=['datasets'])
from app.api.v1 import workflows
api_router.include_router(workflows.router, prefix='/workflows', tags=['workflows'])
from app.api.v1 import voice_models
api_router.include_router(voice_models.router, prefix='/voice-models', tags=['voice-models'])
api_router.include_router(feedbacks.router, prefix='/feedbacks', tags=['feedbacks'])
