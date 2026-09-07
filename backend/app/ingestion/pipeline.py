import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

from app.core.config import settings
from app.core.logging import logger
from app.database.session import engine, Base, SessionLocal
from app.models.paper import PaperModel
from app.models.history import SearchHistoryModel, SavedPaperModel
from app.ingestion.dataset_loader import generate_30k_papers
from app.ingestion.cleaner import DatasetCleaner
from app.retrieval.inverted_index import InvertedIndex
from app.retrieval.tfidf_engine import TFIDFEngine
from app.retrieval.semantic_engine import SemanticEngine
from app.analytics.corpus_analytics import CorpusAnalytics
from app.analytics.topic_modeler import TopicModeler
from app.analytics.trend_analyzer import TrendAnalyzer

def run_ingestion_pipeline(target_count: int = settings.TARGET_PAPERS_COUNT, force_rebuild: bool = True):
    """
    Complete end-to-end dataset ingestion and indexing pipeline for 30,000 papers.
    """
    logger.info("=" * 60)
    logger.info(f"Starting ResearchFinder Ingestion Pipeline for {target_count:,} papers")
    logger.info("=" * 60)
    start_time = time.time()

    # Step 1: Raw Data Generation / Loading
    if not settings.RAW_DATA_PATH.exists() or force_rebuild:
        logger.info(f"Generating raw research paper records (target: {target_count:,})...")
        raw_papers = generate_30k_papers(target_count=target_count)
        settings.RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.RAW_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(raw_papers, f)
        logger.info(f"Saved {len(raw_papers):,} raw papers to {settings.RAW_DATA_PATH}")
    else:
        logger.info(f"Loading existing raw papers from {settings.RAW_DATA_PATH}...")
        with open(settings.RAW_DATA_PATH, "r", encoding="utf-8") as f:
            raw_papers = json.load(f)

    # Step 2: Cleaning & Validation
    logger.info("Cleaning and validating dataset...")
    cleaner = DatasetCleaner()
    cleaned_papers, clean_stats = cleaner.validate_and_clean(raw_papers)
    logger.info(f"Cleaned {len(cleaned_papers):,} papers. Stats: {clean_stats}")

    with open(settings.PROCESSED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_papers, f)

    # Step 3: Database Storage (SQLite)
    logger.info("Populating relational database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check existing count
        existing_count = db.query(PaperModel).count()
        if existing_count < len(cleaned_papers) or force_rebuild:
            logger.info(f"Seeding {len(cleaned_papers):,} papers into database...")
            db.query(PaperModel).delete()
            db.commit()

            # Batch insert in chunks of 1000
            batch_size = 1000
            for i in range(0, len(cleaned_papers), batch_size):
                chunk = cleaned_papers[i : i + batch_size]
                models = [
                    PaperModel(
                        paper_id=p["paper_id"],
                        title=p["title"],
                        authors=p["authors"],
                        abstract=p["abstract"],
                        keywords=p["keywords"],
                        categories=p["categories"],
                        primary_category=p["primary_category"],
                        publication_year=p["publication_year"],
                        venue=p["venue"],
                        citation_count=p["citation_count"],
                        doi=p["doi"],
                        url=p["url"],
                        pdf_url=p["pdf_url"]
                    )
                    for p in chunk
                ]
                db.bulk_save_objects(models)
                db.commit()
            logger.info(f"Successfully seeded {len(cleaned_papers):,} papers into SQLite database.")
        else:
            logger.info(f"Database already contains {existing_count:,} papers.")
    finally:
        db.close()

    # Step 4: Build Inverted Index
    logger.info("Building field-aware Inverted Index...")
    inv_index = InvertedIndex()
    for p in cleaned_papers:
        fields = {
            "title": p["title"],
            "abstract": p["abstract"],
            "keywords": " ".join(p["keywords"]),
            "categories": " ".join(p["categories"]),
            "authors": " ".join(p["authors"])
        }
        inv_index.add_document(p["paper_id"], fields=fields, metadata=p)
    inv_index.finalize()
    inv_index.save(settings.INVERTED_INDEX_PATH)
    logger.info(f"Inverted Index built: {inv_index.num_docs:,} docs, {len(inv_index.index):,} indexed terms. Saved to {settings.INVERTED_INDEX_PATH}")

    # Step 5: Build TF-IDF Model
    logger.info("Building TF-IDF Vector Space Index...")
    tfidf_engine = TFIDFEngine()
    paper_ids = [p["paper_id"] for p in cleaned_papers]
    corpus_texts = [
        f"{p['title']} {p['title']} {p['abstract']} {' '.join(p['keywords'])} {' '.join(p['categories'])}"
        for p in cleaned_papers
    ]
    tfidf_engine.fit_transform(paper_ids, corpus_texts)
    tfidf_engine.save(settings.TFIDF_MATRIX_PATH)
    logger.info(f"TF-IDF matrix built with shape {tfidf_engine.tfidf_matrix.shape}. Saved to {settings.TFIDF_MATRIX_PATH}")

    # Step 6: Semantic Embeddings Generation
    logger.info("Generating / Loading Dense Semantic Embeddings...")
    semantic_engine = SemanticEngine()
    
    if not settings.EMBEDDINGS_PATH.exists() or force_rebuild:
        logger.info(f"Generating 384-dimensional dense vectors for {len(cleaned_papers):,} papers...")
        # Prepare rich embedding input texts (Title + Abstract)
        emb_texts = [f"{p['title']}. {p['abstract']}" for p in cleaned_papers]
        
        try:
            embeddings_matrix = semantic_engine.encode_texts(emb_texts, batch_size=128)
        except Exception as e:
            logger.warning(f"Transformer model encoding failed ({e}). Falling back to fast TruncatedSVD dense embedding projection...")
            from sklearn.decomposition import TruncatedSVD
            from sklearn.preprocessing import normalize
            svd = TruncatedSVD(n_components=settings.EMBEDDING_DIM, random_state=42)
            dense_proj = svd.fit_transform(tfidf_engine.tfidf_matrix)
            embeddings_matrix = normalize(dense_proj, norm="l2", axis=1).astype(np.float32)

        semantic_engine.set_embeddings(paper_ids, embeddings_matrix)
        semantic_engine.save(settings.EMBEDDINGS_PATH, settings.PAPER_IDS_MAP_PATH)
        logger.info(f"Saved dense embeddings (shape {embeddings_matrix.shape}) to {settings.EMBEDDINGS_PATH}")
    else:
        logger.info(f"Loading dense embeddings from {settings.EMBEDDINGS_PATH}...")
        semantic_engine.load(settings.EMBEDDINGS_PATH, settings.PAPER_IDS_MAP_PATH)

    # Step 7: Topic Discovery & Clustering
    logger.info("Executing Topic Discovery & Modeling...")
    topic_modeler = TopicModeler(num_topics=16)
    topic_modeler.fit(cleaned_papers)
    topic_modeler.save(settings.TOPICS_PATH)
    logger.info(f"Discovered {len(topic_modeler.topic_clusters)} topic clusters. Saved to {settings.TOPICS_PATH}")

    # Step 8: Trend Analysis
    logger.info("Computing Research Trend Trajectories and CAGR...")
    trend_analyzer = TrendAnalyzer()
    trend_analyzer.analyze(cleaned_papers)
    trend_analyzer.save(settings.TRENDS_PATH)
    logger.info(f"Saved {len(trend_analyzer.trend_items)} trend trajectories to {settings.TRENDS_PATH}")

    # Step 9: Corpus Analytics & Dataset Statistics Report
    logger.info("Generating Comprehensive Dataset Statistics Report...")
    analytics = CorpusAnalytics(cleaned_papers)
    overview = analytics.get_overview()

    elapsed = round(time.time() - start_time, 2)
    stats_report = {
        "pipeline_execution_time_seconds": elapsed,
        "dataset": {
            "total_papers_indexed": len(cleaned_papers),
            "target_papers_count": target_count,
            "vocabulary_size": len(inv_index.index),
            "total_categories": overview.total_categories,
            "total_venues": overview.total_venues,
            "total_authors": overview.total_authors,
            "year_range": overview.year_range,
            "avg_citations": overview.avg_citations,
            "max_citations": overview.max_citations,
            "median_citations": overview.median_citations
        },
        "indexes": {
            "inverted_index_terms": len(inv_index.index),
            "tfidf_matrix_shape": list(tfidf_engine.tfidf_matrix.shape),
            "embeddings_matrix_shape": list(semantic_engine.embeddings_matrix.shape) if semantic_engine.embeddings_matrix is not None else [],
            "embedding_dimension": settings.EMBEDDING_DIM
        },
        "data_cleaning_summary": clean_stats
    }

    with open(settings.STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats_report, f, indent=2)

    logger.info(f"Ingestion Pipeline completed in {elapsed}s! Report saved to {settings.STATS_PATH}")
    logger.info("=" * 60)
    return stats_report

if __name__ == "__main__":
    run_ingestion_pipeline()
