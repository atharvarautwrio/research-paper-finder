from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class YearlyCount(BaseModel):
    year: int
    count: int

class CategoryCount(BaseModel):
    category: str
    count: int
    percentage: float

class KeywordCount(BaseModel):
    keyword: str
    count: int

class VenueCount(BaseModel):
    venue: str
    count: int

class TopicCluster(BaseModel):
    topic_id: int
    name: str
    top_terms: List[str]
    paper_count: int
    sample_titles: List[str]

class TrendItem(BaseModel):
    topic: str
    trajectory: List[int]
    years: List[int]
    cagr: float
    status: str  # "Emerging", "Accelerating", "Stable", "Declining"
    total_papers: int

class AnalyticsOverview(BaseModel):
    total_papers: int
    total_authors: int
    total_venues: int
    total_categories: int
    avg_citations: float
    max_citations: int
    median_citations: float
    year_range: List[int]
    papers_by_year: List[YearlyCount]
    papers_by_category: List[CategoryCount]
    top_keywords: List[KeywordCount]
    top_venues: List[VenueCount]
    citation_distribution: List[Dict[str, Any]]
