from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.history import SearchHistoryModel, SavedPaperModel
from app.indexing.indexer import IndexManager

router = APIRouter(prefix="/history", tags=["Search History & Saved Library"])

class SavePaperRequest(BaseModel):
    paper_id: str
    notes: Optional[str] = None

@router.get("/searches")
def get_search_history(
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve user search history with timestamps, modes, and result counts.
    """
    searches = db.query(SearchHistoryModel).order_by(SearchHistoryModel.created_at.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "query": s.query,
            "retrieval_mode": s.retrieval_mode,
            "filters_applied": s.filters_applied,
            "result_count": s.result_count,
            "latency_ms": s.latency_ms,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in searches
    ]

@router.get("/saved")
def get_saved_papers(db: Session = Depends(get_db)):
    """
    Retrieve all bookmarked papers in the user library.
    """
    saved = db.query(SavedPaperModel).order_by(SavedPaperModel.saved_at.desc()).all()
    return [
        {
            "paper_id": s.paper_id,
            "title": s.title,
            "authors": s.authors,
            "publication_year": s.publication_year,
            "primary_category": s.primary_category,
            "venue": s.venue,
            "notes": s.notes,
            "saved_at": s.saved_at.isoformat() if s.saved_at else None
        }
        for s in saved
    ]

@router.post("/save")
def save_paper(
    payload: SavePaperRequest,
    db: Session = Depends(get_db)
):
    """
    Save or bookmark a paper with optional researcher notes.
    """
    indexer = IndexManager.get_instance()
    paper_meta = indexer.inverted_index.doc_metadata.get(payload.paper_id) if indexer.inverted_index else None

    if not paper_meta:
        raise HTTPException(status_code=404, detail=f"Paper with ID '{payload.paper_id}' not found.")

    existing = db.query(SavedPaperModel).filter(SavedPaperModel.paper_id == payload.paper_id).first()
    if existing:
        existing.notes = payload.notes
        db.commit()
        return {"status": "updated", "paper_id": payload.paper_id}

    saved = SavedPaperModel(
        paper_id=payload.paper_id,
        title=paper_meta.get("title", ""),
        authors=paper_meta.get("authors", []),
        publication_year=paper_meta.get("publication_year", 2020),
        primary_category=paper_meta.get("primary_category", "Computer Science"),
        venue=paper_meta.get("venue", "arXiv"),
        notes=payload.notes
    )
    db.add(saved)
    db.commit()
    return {"status": "saved", "paper_id": payload.paper_id}

@router.delete("/saved/{paper_id}")
def remove_saved_paper(paper_id: str, db: Session = Depends(get_db)):
    """
    Remove a paper from bookmarks library.
    """
    existing = db.query(SavedPaperModel).filter(SavedPaperModel.paper_id == paper_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Saved paper not found.")

    db.delete(existing)
    db.commit()
    return {"status": "deleted", "paper_id": paper_id}
