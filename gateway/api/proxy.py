from fastapi import APIRouter, Request, Response, HTTPException
import httpx
from core.config import settings
import logging

logger = logging.getLogger("gateway.proxy")
router = APIRouter()
client = httpx.AsyncClient(base_url=settings.BACKEND_URL)

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_backend(request: Request, path: str):
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    
    # We shouldn't proxy the workflow routes, so let's handle that in main.py
    
    headers = dict(request.headers)
    headers.pop("host", None) # Remove host header so httpx uses the correct one
    
    try:
        content = await request.body()
        response = await client.request(
            request.method,
            url,
            headers=headers,
            content=content,
            timeout=30.0
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as exc:
        logger.error(f"Error proxying request to {exc.request.url!r}: {exc}")
        raise HTTPException(status_code=502, detail="Bad Gateway: Backend service unavailable")
