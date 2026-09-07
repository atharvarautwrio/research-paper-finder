from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchFilter(BaseModel):
    categories: Optional[List[str]] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    min_citations: Optional[int] = None
    max_citations: Optional[int] = None
    venues: Optional[List[str]] = None
    authors: Optional[List[str]] = None

class RankingWeights(BaseModel):
    bm25: float = 0.35
    tfidf: float = 0.15
    semantic: float = 0.35
    title_match: float = 0.10
    recency: float = 0.03
    citations: float = 0.02

class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"  # "hybrid", "bm25", "tfidf", "semantic"
    filters: Optional[SearchFilter] = None
    sort_by: str = "relevance"  # "relevance", "newest", "oldest", "citations"
    page: int = 1
    page_size: int = 10
    weights: Optional[RankingWeights] = None

class MatchExplanation(BaseModel):
    relevance_score: float
    relevance_percentage: float
    signals: Dict[str, float]  # bm25, tfidf, semantic, title_match, recency, citations
    matched_query_terms: List[str]
    title_match_terms: List[str]
    reasons: List[str]
    query_expansion_used: List[str] = []

class SearchResultItem(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    keywords: List[str]
    categories: List[str]
    primary_category: str
    publication_year: int
    venue: str
    citation_count: int
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    rank: int
    explanation: MatchExplanation

class FacetItem(BaseModel):
    name: str
    count: int

class SearchFacets(BaseModel):
    categories: List[FacetItem]
    venues: List[FacetItem]
    years: List[FacetItem]
    citation_ranges: List[FacetItem]

class SearchResponse(BaseModel):
    query: str
    retrieval_mode: str
    total_results: int
    page: int
    page_size: int
    total_pages: int
    latency_ms: float
    results: List[SearchResultItem]
    facets: SearchFacets
    query_tokens: List[str]
    expanded_terms: List[str]
