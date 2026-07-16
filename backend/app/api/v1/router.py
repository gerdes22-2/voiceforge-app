from fastapi import APIRouter
from app.api.v1 import auth, projects, songs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(songs.router, prefix="/songs", tags=["songs"])
from app.api.v1 import jobs
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
