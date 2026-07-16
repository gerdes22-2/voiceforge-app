from fastapi import FastAPI
from api.proxy import router as proxy_router
from core.config import settings
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from shared.logging.logger import setup_logger

logger = setup_logger("gateway.main")

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/health")
def health_check():
    logger.info("Gateway health check")
    return {"status": "ok", "service": "gateway"}

# Workflows will be mounted here
# app.include_router(workflow_router, prefix="/api/v1/workflows")

# Mount proxy last as a catch-all
app.include_router(proxy_router, tags=["proxy"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
