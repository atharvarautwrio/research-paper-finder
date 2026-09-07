import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "indexes"

# Ensure directories exist
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchFinder"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/researchfinder.db"
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    RAW_DATA_PATH: Path = RAW_DATA_DIR / "papers_30k_raw.json"
    PROCESSED_DATA_PATH: Path = PROCESSED_DATA_DIR / "papers_30k_processed.json"
    INDEX_DIR: Path = INDEX_DIR
    
    INVERTED_INDEX_PATH: Path = INDEX_DIR / "inverted_index.pkl"
    TFIDF_MATRIX_PATH: Path = INDEX_DIR / "tfidf_model.pkl"
    BM25_INDEX_PATH: Path = INDEX_DIR / "bm25_index.pkl"
    EMBEDDINGS_PATH: Path = INDEX_DIR / "embeddings_matrix.npy"
    PAPER_IDS_MAP_PATH: Path = INDEX_DIR / "paper_ids_map.json"
    STATS_PATH: Path = INDEX_DIR / "dataset_stats.json"
    TOPICS_PATH: Path = INDEX_DIR / "discovered_topics.json"
    TRENDS_PATH: Path = INDEX_DIR / "trend_analytics.json"
    
    # Dataset Target Size
    TARGET_PAPERS_COUNT: int = 30000
    
    # Retrieval Hyperparameters
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    
    # Default Hybrid Weights
    DEFAULT_WEIGHT_BM25: float = 0.35
    DEFAULT_WEIGHT_TFIDF: float = 0.15
    DEFAULT_WEIGHT_SEMANTIC: float = 0.35
    DEFAULT_WEIGHT_TITLE: float = 0.10
    DEFAULT_WEIGHT_RECENCY: float = 0.03
    DEFAULT_WEIGHT_CITATIONS: float = 0.02
    
    # Embedding model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"]

    class Config:
        case_sensitive = True


settings = Settings()
