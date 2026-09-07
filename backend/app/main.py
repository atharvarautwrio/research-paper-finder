from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import logger
from app.api.router import api_router
from app.indexing.indexer import IndexManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    Initializes dataset generation, Inverted Index, BM25, TF-IDF, and Semantic embeddings on startup.
    """
    logger.info("Initializing ResearchFinder IR Engines & Knowledge Base...")
    try:
        indexer = IndexManager.get_instance()
        indexer.initialize()
        logger.info("ResearchFinder Backend is fully initialized and operational!")
    except Exception as e:
        logger.error(f"Error during startup indexing: {e}", exc_info=True)
    
    yield
    
    logger.info("ResearchFinder Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-performance hybrid Information Retrieval platform and paper discovery engine for 20,000 academic research papers.",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    return response

@app.get("/", tags=["Health & Status"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health", tags=["Health & Status"])
def health_check():
    indexer = IndexManager.get_instance()
    is_ready = indexer.inverted_index is not None and indexer.inverted_index.num_docs > 0
    return {
        "status": "healthy" if is_ready else "initializing",
        "indexed_papers": indexer.inverted_index.num_docs if indexer.inverted_index else 0,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
