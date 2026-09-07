from fastapi import APIRouter

from app.api.endpoints.search import router as search_router
from app.api.endpoints.papers import router as papers_router
from app.api.endpoints.analytics import router as analytics_router
from app.api.endpoints.evaluation import router as evaluation_router
from app.api.endpoints.history import router as history_router
from app.api.endpoints.system import router as system_router

api_router = APIRouter()

api_router.include_router(search_router)
api_router.include_router(papers_router)
api_router.include_router(analytics_router)
api_router.include_router(evaluation_router)
api_router.include_router(history_router)
api_router.include_router(system_router)
