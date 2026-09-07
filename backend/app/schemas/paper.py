from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PaperBase(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    keywords: List[str]
    categories: List[str]
    primary_category: str
    publication_year: int
    venue: str
    citation_count: int = 0
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None

class PaperDetail(PaperBase):
    pass

class PaperRecommendation(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    publication_year: int
    venue: str
    citation_count: int
    primary_category: str
    similarity_score: float
    similarity_percentage: float
    reasons: List[str]
    signal_breakdown: Dict[str, float]
