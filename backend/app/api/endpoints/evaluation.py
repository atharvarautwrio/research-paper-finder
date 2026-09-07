from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from app.indexing.indexer import IndexManager
from app.schemas.evaluation import BenchmarkReport
from app.evaluation.relevance_judgments import EVALUATION_QUERIES

router = APIRouter(prefix="/evaluation", tags=["IR Benchmarking & Evaluation"])

@router.get("/benchmark", response_model=BenchmarkReport)
def run_or_get_benchmark(
    force_rerun: bool = Query(False, description="Force re-running live benchmark queries")
):
    """
    Run comprehensive IR Evaluation Benchmark comparing BM25, TF-IDF, Semantic Dense,
    and Hybrid Ranking across MAP, MRR, NDCG@5, NDCG@10, Precision@5/10, Recall, and Latency.
    """
    indexer = IndexManager.get_instance()
    if not indexer.benchmark_runner:
        raise HTTPException(status_code=503, detail="Benchmark runner is not ready.")

    cache_key = "latest_benchmark_report"
    if not force_rerun and cache_key in indexer.cache:
        indexer.cache_hits += 1
        return indexer.cache[cache_key]

    indexer.cache_misses += 1
    report = indexer.benchmark_runner.run_benchmark()
    indexer.cache[cache_key] = report
    return report

@router.get("/queries")
def get_benchmark_queries() -> List[Dict[str, Any]]:
    """
    Retrieve benchmark test queries and category taxonomy used for relevance judgments.
    """
    return EVALUATION_QUERIES
