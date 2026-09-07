from typing import List
from fastapi import APIRouter, HTTPException

from app.indexing.indexer import IndexManager
from app.schemas.analytics import AnalyticsOverview, TopicCluster, TrendItem

router = APIRouter(prefix="/analytics", tags=["Corpus Intelligence & Research Trends"])

@router.get("/overview", response_model=AnalyticsOverview)
def get_corpus_analytics_overview():
    """
    Retrieve comprehensive statistical overview, category distribution,
    publication timeline, top venues, and citation tier metrics.
    """
    indexer = IndexManager.get_instance()
    if not indexer.corpus_analytics:
        if indexer.inverted_index:
            from app.analytics.corpus_analytics import CorpusAnalytics
            indexer.corpus_analytics = CorpusAnalytics(list(indexer.inverted_index.doc_metadata.values()))
        else:
            raise HTTPException(status_code=503, detail="Corpus analytics engine is not ready.")

    return indexer.corpus_analytics.get_overview()

@router.get("/topics", response_model=List[TopicCluster])
def get_topic_clusters():
    """
    Retrieve discovered topic clusters generated via unsupervised MiniBatchKMeans and c-TF-IDF keyword extraction.
    """
    indexer = IndexManager.get_instance()
    if not indexer.topic_modeler or not indexer.topic_modeler.topic_clusters:
        raise HTTPException(status_code=503, detail="Topic modeler is not ready.")

    return indexer.topic_modeler.topic_clusters

@router.get("/trends", response_model=List[TrendItem])
def get_research_trends():
    """
    Retrieve temporal research trajectory trends, CAGR compound growth metrics,
    and momentum status (Emerging, Accelerating, Stable, Declining) across 2018-2025.
    """
    indexer = IndexManager.get_instance()
    if not indexer.trend_analyzer or not indexer.trend_analyzer.trend_items:
        raise HTTPException(status_code=503, detail="Trend analyzer is not ready.")

    return indexer.trend_analyzer.trend_items
