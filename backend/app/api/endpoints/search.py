import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.indexing.indexer import IndexManager
from app.schemas.search import SearchRequest, SearchResponse
from app.models.history import SearchHistoryModel
from app.core.logging import logger

router = APIRouter(prefix="/search", tags=["Search & Retrieval"])

@router.post("", response_model=SearchResponse)
def execute_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Execute multi-mode academic search with customizable hybrid weights,
    faceted filtering, signal breakdown explainability, and pagination.
    """
    t0 = time.time()
    indexer = IndexManager.get_instance()
    
    if not indexer.hybrid_ranker:
        raise HTTPException(status_code=503, detail="Search engine is still initializing indexes.")

    # Execute search
    response = indexer.hybrid_ranker.search(request, latency_start=t0)

    # Record search history asynchronously in DB
    try:
        history_entry = SearchHistoryModel(
            query=request.query,
            retrieval_mode=request.mode,
            filters_applied=request.filters.model_dump() if request.filters else None,
            result_count=response.total_results,
            latency_ms=response.latency_ms
        )
        db.add(history_entry)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to record search history: {e}")
        db.rollback()

    return response

@router.get("/autocomplete")
def get_autocomplete_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Query prefix to suggest terms for"),
    limit: int = Query(8, ge=1, le=20)
) -> List[Dict[str, Any]]:
    """
    Provide rapid prefix autocompletions from indexed terms, discovered topics, and key concepts.
    """
    indexer = IndexManager.get_instance()
    if not indexer.inverted_index:
        return []

    prefix = q.strip().lower()
    if not prefix:
        return []

    suggestions: List[Dict[str, Any]] = []
    seen: set[str] = set()

    # 1. Check topic clusters
    if indexer.topic_modeler and indexer.topic_modeler.topic_clusters:
        for cluster in indexer.topic_modeler.topic_clusters:
            if prefix in cluster.name.lower():
                if cluster.name not in seen:
                    suggestions.append({
                        "text": cluster.name,
                        "type": "topic",
                        "count": cluster.paper_count
                    })
                    seen.add(cluster.name)

    # 2. Check indexed terms matching prefix
    matching_terms = [
        (term, count)
        for term, count in indexer.inverted_index.doc_freq.items()
        if term.startswith(prefix) and len(term) > len(prefix)
    ]
    # Sort by document frequency
    matching_terms.sort(key=lambda x: x[1], reverse=True)

    for term, count in matching_terms[:limit]:
        if term not in seen:
            suggestions.append({
                "text": term,
                "type": "keyword",
                "count": count
            })
            seen.add(term)
        if len(suggestions) >= limit:
            break

    return suggestions[:limit]

@router.post("/expand")
def preview_query_expansion(query: str = Query(..., min_length=1)) -> Dict[str, Any]:
    """
    Preview tokenization, stop-word elimination, stemming, and domain query expansion.
    """
    indexer = IndexManager.get_instance()
    preprocessor = indexer.hybrid_ranker.preprocessor if indexer.hybrid_ranker else None
    
    if not preprocessor:
        from app.retrieval.preprocessor import TextPreprocessor
        preprocessor = TextPreprocessor()

    base_tokens, expanded_tokens = preprocessor.expand_query(query)
    phrases = preprocessor.extract_phrases(query)

    return {
        "original_query": query,
        "base_tokens": base_tokens,
        "expanded_synonyms": expanded_tokens,
        "exact_phrases": phrases
    }
