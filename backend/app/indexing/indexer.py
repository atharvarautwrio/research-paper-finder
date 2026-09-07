import time
from typing import Optional, Dict, Any
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger
from app.retrieval.inverted_index import InvertedIndex
from app.retrieval.bm25_engine import BM25Engine
from app.retrieval.tfidf_engine import TFIDFEngine
from app.retrieval.semantic_engine import SemanticEngine
from app.ranking.hybrid_ranker import HybridRanker
from app.recommendation.recommender import PaperRecommender
from app.evaluation.benchmark import IREvaluationBenchmark
from app.analytics.topic_modeler import TopicModeler
from app.analytics.trend_analyzer import TrendAnalyzer
from app.analytics.corpus_analytics import CorpusAnalytics
from app.ingestion.pipeline import run_ingestion_pipeline

class IndexManager:
    """
    Central Index Manager serving the singleton IR engines, Hybrid Ranker,
    Recommender, and Benchmark suite.
    """
    _instance: Optional["IndexManager"] = None

    def __init__(self):
        self.inverted_index: Optional[InvertedIndex] = None
        self.bm25_engine: Optional[BM25Engine] = None
        self.tfidf_engine: Optional[TFIDFEngine] = None
        self.semantic_engine: Optional[SemanticEngine] = None
        self.hybrid_ranker: Optional[HybridRanker] = None
        self.recommender: Optional[PaperRecommender] = None
        self.benchmark_runner: Optional[IREvaluationBenchmark] = None
        self.topic_modeler: Optional[TopicModeler] = None
        self.trend_analyzer: Optional[TrendAnalyzer] = None
        self.corpus_analytics: Optional[CorpusAnalytics] = None
        self.start_time: float = time.time()
        self.cache: Dict[str, Any] = {}
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    @classmethod
    def get_instance(cls) -> "IndexManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, force_rebuild: bool = False):
        """Load all precomputed indexes or trigger ingestion pipeline if not found"""
        logger.info("Initializing IndexManager...")

        indexes_exist = (
            settings.INVERTED_INDEX_PATH.exists() and
            settings.TFIDF_MATRIX_PATH.exists() and
            settings.EMBEDDINGS_PATH.exists() and
            settings.STATS_PATH.exists()
        )

        if not indexes_exist or force_rebuild:
            logger.info("One or more index files missing. Running ingestion pipeline...")
            run_ingestion_pipeline(target_count=settings.TARGET_PAPERS_COUNT, force_rebuild=force_rebuild)

        # 1. Load Inverted Index
        logger.info(f"Loading Inverted Index from {settings.INVERTED_INDEX_PATH}...")
        self.inverted_index = InvertedIndex.load(settings.INVERTED_INDEX_PATH)
        logger.info(f"Loaded {self.inverted_index.num_docs:,} papers, {len(self.inverted_index.index):,} vocabulary terms.")

        # 2. Init BM25 Engine
        self.bm25_engine = BM25Engine(
            inverted_index=self.inverted_index,
            k1=settings.BM25_K1,
            b=settings.BM25_B
        )

        # 3. Load TF-IDF Engine
        logger.info(f"Loading TF-IDF Engine from {settings.TFIDF_MATRIX_PATH}...")
        self.tfidf_engine = TFIDFEngine.load(settings.TFIDF_MATRIX_PATH)

        # 4. Load Semantic Engine
        logger.info(f"Loading Semantic Embeddings from {settings.EMBEDDINGS_PATH}...")
        self.semantic_engine = SemanticEngine()
        self.semantic_engine.load(settings.EMBEDDINGS_PATH, settings.PAPER_IDS_MAP_PATH)

        # 5. Initialize Hybrid Ranker & Recommender
        self.hybrid_ranker = HybridRanker(
            inverted_index=self.inverted_index,
            bm25_engine=self.bm25_engine,
            tfidf_engine=self.tfidf_engine,
            semantic_engine=self.semantic_engine
        )

        self.recommender = PaperRecommender(
            inverted_index=self.inverted_index,
            tfidf_engine=self.tfidf_engine,
            semantic_engine=self.semantic_engine
        )

        # 6. Initialize Benchmark Runner
        self.benchmark_runner = IREvaluationBenchmark(
            ranker=self.hybrid_ranker,
            inverted_index=self.inverted_index
        )

        # 7. Initialize Topic Modeler & Trend Analyzer
        self.topic_modeler = TopicModeler()
        self.topic_modeler.load(settings.TOPICS_PATH)

        self.trend_analyzer = TrendAnalyzer()
        self.trend_analyzer.load(settings.TRENDS_PATH)

        # 8. Initialize Corpus Analytics
        papers_list = list(self.inverted_index.doc_metadata.values())
        self.corpus_analytics = CorpusAnalytics(papers_list)

        logger.info("All IndexManager components initialized successfully!")
