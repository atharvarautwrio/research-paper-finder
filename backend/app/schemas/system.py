from pydantic import BaseModel
from typing import Dict, Any, List

class SystemStats(BaseModel):
    indexed_papers_count: int
    vocabulary_size: int
    total_postings_count: int
    categories_count: int
    venues_count: int
    embedding_dimension: int
    embeddings_matrix_shape: List[int]
    memory_usage_mb: float
    index_files: Dict[str, str]
    system_status: str
    uptime_seconds: float
    cache_stats: Dict[str, Any]
