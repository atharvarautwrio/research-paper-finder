from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.paper import PaperModel
from app.indexing.indexer import IndexManager
from app.schemas.paper import PaperDetail, PaperRecommendation

router = APIRouter(prefix="/papers", tags=["Paper Intelligence & Recommendations"])

@router.get("/recent", response_model=List[PaperDetail])
def get_recent_papers(
    limit: int = Query(12, ge=1, le=50),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve landmark and high-impact recent research papers across domains.
    """
    indexer = IndexManager.get_instance()
    if not indexer.inverted_index:
        raise HTTPException(status_code=503, detail="Index not ready.")

    papers = list(indexer.inverted_index.doc_metadata.values())
    
    if category:
        papers = [p for p in papers if category.lower() in p.get("primary_category", "").lower()]

    # Sort by high citations and recency
    papers.sort(
        key=lambda x: (x.get("citation_count", 0) * 0.7 + (x.get("publication_year", 2020) - 2015) * 500),
        reverse=True
    )
    
    return [PaperDetail(**p) for p in papers[:limit]]

@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper_by_id(paper_id: str, db: Session = Depends(get_db)):
    """
    Retrieve detailed metadata and abstract for a specific research paper by ID.
    """
    indexer = IndexManager.get_instance()
    if indexer.inverted_index and paper_id in indexer.inverted_index.doc_metadata:
        doc = indexer.inverted_index.doc_metadata[paper_id]
        return PaperDetail(**doc)

    # Fallback to SQLite DB
    paper = db.query(PaperModel).filter(PaperModel.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper with ID '{paper_id}' not found.")
    
    return PaperDetail(**paper.to_dict())

@router.get("/{paper_id}/recommendations", response_model=List[PaperRecommendation])
def get_paper_recommendations(
    paper_id: str,
    top_k: int = Query(6, ge=1, le=20)
):
    """
    Compute multi-signal paper recommendations combining dense semantic vectors,
    lexical TF-IDF overlap, category alignment, and author/venue relations.
    """
    indexer = IndexManager.get_instance()
    if not indexer.recommender:
        raise HTTPException(status_code=503, detail="Recommender engine is not ready.")

    recs = indexer.recommender.recommend_similar_papers(paper_id, top_k=top_k)
    return recs
