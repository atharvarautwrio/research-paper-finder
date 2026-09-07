import os
import time
import psutil
from fastapi import APIRouter, BackgroundTasks

from app.core.config import settings
from app.indexing.indexer import IndexManager
from app.schemas.system import SystemStats

router = APIRouter(prefix="/system", tags=["System Diagnostics & Index Management"])

@router.get("/stats", response_model=SystemStats)
def get_system_stats():
    """
    Retrieve real-time index metrics, memory consumption, vocabulary stats, and index file statuses.
    """
    indexer = IndexManager.get_instance()
    process = psutil.Process(os.getpid())
    mem_mb = round(process.memory_info().rss / (1024 * 1024), 2)

    num_docs = indexer.inverted_index.num_docs if indexer.inverted_index else 0
    vocab_size = len(indexer.inverted_index.index) if indexer.inverted_index else 0
    total_postings = sum(len(postings) for postings in indexer.inverted_index.index.values()) if indexer.inverted_index else 0

    emb_shape = list(indexer.semantic_engine.embeddings_matrix.shape) if (indexer.semantic_engine and indexer.semantic_engine.embeddings_matrix is not None) else []

    index_files = {
        "inverted_index": "Present" if settings.INVERTED_INDEX_PATH.exists() else "Missing",
        "tfidf_matrix": "Present" if settings.TFIDF_MATRIX_PATH.exists() else "Missing",
        "embeddings_matrix": "Present" if settings.EMBEDDINGS_PATH.exists() else "Missing",
        "database": "Present" if (settings.DATA_DIR / "researchfinder.db").exists() else "Missing",
        "topics": "Present" if settings.TOPICS_PATH.exists() else "Missing",
        "trends": "Present" if settings.TRENDS_PATH.exists() else "Missing"
    }

    uptime = round(time.time() - indexer.start_time, 1)

    return SystemStats(
        indexed_papers_count=num_docs,
        vocabulary_size=vocab_size,
        total_postings_count=total_postings,
        categories_count=len(indexer.corpus_analytics.get_overview().papers_by_category) if indexer.corpus_analytics else 8,
        venues_count=len(indexer.corpus_analytics.get_overview().top_venues) if indexer.corpus_analytics else 20,
        embedding_dimension=settings.EMBEDDING_DIM,
        embeddings_matrix_shape=emb_shape,
        memory_usage_mb=mem_mb,
        index_files=index_files,
        system_status="Operational" if num_docs > 0 else "Initializing",
        uptime_seconds=uptime,
        cache_stats={
            "cache_hits": indexer.cache_hits,
            "cache_misses": indexer.cache_misses,
            "cached_items": len(indexer.cache)
        }
    )

@router.post("/reindex")
def trigger_reindex(background_tasks: BackgroundTasks):
    """
    Trigger full background dataset generation and re-indexing pipeline.
    """
    indexer = IndexManager.get_instance()
    background_tasks.add_task(indexer.initialize, force_rebuild=True)
    return {"message": "Re-indexing pipeline initiated in background."}
