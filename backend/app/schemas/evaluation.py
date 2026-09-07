from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MethodMetrics(BaseModel):
    method_name: str
    precision_at_5: float
    precision_at_10: float
    recall_at_5: float
    recall_at_10: float
    recall_at_20: float
    f1_score: float
    map_score: float  # Mean Average Precision
    mrr_score: float  # Mean Reciprocal Rank
    ndcg_at_5: float
    ndcg_at_10: float
    avg_latency_ms: float

class QueryEvaluationDetail(BaseModel):
    query: str
    category: str
    num_judgments: int
    methods: Dict[str, Dict[str, float]]

class BenchmarkReport(BaseModel):
    num_queries: int
    methods: List[MethodMetrics]
    query_details: List[QueryEvaluationDetail]
    best_overall_method: str
    summary_analysis: str
