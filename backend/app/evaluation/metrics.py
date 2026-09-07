import math
from typing import List, Set, Dict, Any

class IREvaluationMetrics:
    """
    Standard Information Retrieval Evaluation Metrics.
    Implements Precision@K, Recall@K, F1@K, MAP, MRR, and NDCG@K.
    """

    @staticmethod
    def precision_at_k(retrieved_doc_ids: List[str], ground_truth_relevant_ids: Set[str], k: int) -> float:
        """
        Precision@K = (Relevant documents in top K) / K
        """
        if k <= 0:
            return 0.0
        top_k = retrieved_doc_ids[:k]
        if not top_k:
            return 0.0
        relevant_in_k = sum(1 for doc_id in top_k if doc_id in ground_truth_relevant_ids)
        return float(relevant_in_k) / float(k)

    @staticmethod
    def recall_at_k(retrieved_doc_ids: List[str], ground_truth_relevant_ids: Set[str], k: int) -> float:
        """
        Recall@K = (Relevant documents in top K) / (Total relevant documents)
        """
        if not ground_truth_relevant_ids or k <= 0:
            return 0.0
        top_k = retrieved_doc_ids[:k]
        relevant_in_k = sum(1 for doc_id in top_k if doc_id in ground_truth_relevant_ids)
        return float(relevant_in_k) / float(len(ground_truth_relevant_ids))

    @staticmethod
    def f1_at_k(precision: float, recall: float) -> float:
        """
        F1-Score = 2 * (P * R) / (P + R)
        """
        if (precision + recall) == 0.0:
            return 0.0
        return 2.0 * (precision * recall) / (precision + recall)

    @staticmethod
    def average_precision(retrieved_doc_ids: List[str], ground_truth_relevant_ids: Set[str]) -> float:
        """
        Average Precision (AP) = sum_{k=1}^N (P@k * rel(k)) / |Relevant|
        """
        if not ground_truth_relevant_ids or not retrieved_doc_ids:
            return 0.0

        hits = 0
        sum_precisions = 0.0

        for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
            if doc_id in ground_truth_relevant_ids:
                hits += 1
                precision_at_rank = float(hits) / float(rank)
                sum_precisions += precision_at_rank

        return sum_precisions / float(len(ground_truth_relevant_ids))

    @staticmethod
    def reciprocal_rank(retrieved_doc_ids: List[str], ground_truth_relevant_ids: Set[str]) -> float:
        """
        Reciprocal Rank (RR) = 1 / rank of the first relevant document
        """
        for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
            if doc_id in ground_truth_relevant_ids:
                return 1.0 / float(rank)
        return 0.0

    @staticmethod
    def dcg_at_k(retrieved_doc_ids: List[str], relevance_scores_map: Dict[str, float], k: int) -> float:
        """
        Discounted Cumulative Gain: DCG@K = sum_{i=1}^K (2^{rel_i} - 1) / log2(i + 1)
        """
        top_k = retrieved_doc_ids[:k]
        dcg = 0.0
        for i, doc_id in enumerate(top_k, start=1):
            rel = relevance_scores_map.get(doc_id, 0.0)
            dcg += (math.pow(2.0, rel) - 1.0) / math.log2(i + 1)
        return dcg

    @classmethod
    def ndcg_at_k(cls, retrieved_doc_ids: List[str], relevance_scores_map: Dict[str, float], k: int) -> float:
        """
        Normalized Discounted Cumulative Gain: NDCG@K = DCG@K / IDCG@K
        """
        actual_dcg = cls.dcg_at_k(retrieved_doc_ids, relevance_scores_map, k)
        
        # Ideal DCG (sort relevance scores descending)
        ideal_scores = sorted(relevance_scores_map.values(), reverse=True)[:k]
        idcg = 0.0
        for i, rel in enumerate(ideal_scores, start=1):
            idcg += (math.pow(2.0, rel) - 1.0) / math.log2(i + 1)

        if idcg == 0.0:
            return 0.0
        return min(actual_dcg / idcg, 1.0)
