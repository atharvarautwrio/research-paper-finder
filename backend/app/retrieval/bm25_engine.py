import math
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from app.retrieval.inverted_index import InvertedIndex
from app.retrieval.preprocessor import TextPreprocessor

class BM25Engine:
    """
    Okapi BM25 and Multi-Field BM25 (BM25F) retrieval engine.
    Supports field boosting, configurable k1 and b parameters.
    """
    def __init__(
        self,
        inverted_index: InvertedIndex,
        k1: float = 1.5,
        b: float = 0.75,
        field_weights: Optional[Dict[str, float]] = None
    ):
        self.index = inverted_index
        self.k1 = k1
        self.b = b
        self.field_weights = field_weights or {
            "title": 2.5,
            "abstract": 1.0,
            "keywords": 2.0,
            "categories": 1.5,
            "authors": 0.8
        }
        self.preprocessor = TextPreprocessor()

    def score_query(
        self,
        query_tokens: List[str],
        candidate_doc_ids: Optional[List[str]] = None,
        top_k: int = 100
    ) -> List[Tuple[str, float]]:
        """
        Calculate BM25 scores for documents matching query tokens.
        Returns sorted list of (doc_id, score).
        """
        if not query_tokens or self.index.num_docs == 0:
            return []

        doc_scores: Dict[str, float] = defaultdict(float)
        candidate_set = set(candidate_doc_ids) if candidate_doc_ids else None

        for term in query_tokens:
            postings = self.index.get_postings(term)
            if not postings:
                continue

            idf = self.index.get_idf(term)
            if idf <= 0:
                continue

            for doc_id, fields_data in postings.items():
                if candidate_set and doc_id not in candidate_set:
                    continue

                # Calculate weighted term frequency and effective length across fields
                weighted_tf = 0.0
                effective_len_ratio = 0.0
                total_weight = 0.0

                for field, data in fields_data.items():
                    w = self.field_weights.get(field, 1.0)
                    tf = data["tf"]
                    field_len = self.index.doc_field_lengths[doc_id].get(field, 1)
                    avg_len = max(self.index.avg_field_lengths.get(field, 1.0), 1.0)
                    
                    weighted_tf += w * tf
                    effective_len_ratio += w * (field_len / avg_len)
                    total_weight += w

                if total_weight > 0:
                    effective_len_ratio /= total_weight

                # BM25 numerator and denominator
                numerator = weighted_tf * (self.k1 + 1.0)
                denominator = weighted_tf + self.k1 * (1.0 - self.b + self.b * effective_len_ratio)

                if denominator > 0:
                    term_score = idf * (numerator / denominator)
                    doc_scores[doc_id] += term_score

        # Sort descending by score
        ranked = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
