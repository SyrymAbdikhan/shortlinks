from fastapi import APIRouter

from app.api.routes import health, links

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(links.router)
