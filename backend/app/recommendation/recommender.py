from typing import List, Dict, Any, Optional
import numpy as np
from app.retrieval.inverted_index import InvertedIndex
from app.retrieval.tfidf_engine import TFIDFEngine
from app.retrieval.semantic_engine import SemanticEngine
from app.schemas.paper import PaperRecommendation

class PaperRecommender:
    """
    Intelligent Paper-to-Paper Recommendation Engine combining:
    - Dense Semantic Embedding similarity
    - TF-IDF lexical overlap
    - Category & Topic matching
    - Shared Authors & Venues
    """
    def __init__(
        self,
        inverted_index: InvertedIndex,
        tfidf_engine: TFIDFEngine,
        semantic_engine: SemanticEngine
    ):
        self.index = inverted_index
        self.tfidf = tfidf_engine
        self.semantic = semantic_engine

    def recommend_similar_papers(
        self,
        paper_id: str,
        top_k: int = 6
    ) -> List[PaperRecommendation]:
        """Retrieve top similar papers for a given target paper ID"""
        target_doc = self.index.doc_metadata.get(paper_id)
        if not target_doc:
            return []

        target_cats = set(target_doc.get("categories", []) + [target_doc.get("primary_category", "")])
        target_authors = set(target_doc.get("authors", []))
        target_venue = target_doc.get("venue", "")
        target_kws = set(target_doc.get("keywords", []))

        # 1. Semantic similarities
        sem_scores: Dict[str, float] = {}
        if self.semantic.embeddings_matrix is not None and paper_id in self.semantic.id_to_idx:
            target_idx = self.semantic.id_to_idx[paper_id]
            target_vec = self.semantic.embeddings_matrix[target_idx]
            sims = np.dot(self.semantic.embeddings_matrix, target_vec)
            # Top candidate indices
            top_cand_indices = np.argsort(sims)[::-1][:150]
            for idx in top_cand_indices:
                pid = self.semantic.paper_ids[idx]
                if pid != paper_id:
                    sem_scores[pid] = float(sims[idx])

        # 2. TF-IDF similarities
        tfidf_scores: Dict[str, float] = {}
        if self.tfidf.tfidf_matrix is not None and paper_id in self.tfidf.id_to_idx:
            target_t_idx = self.tfidf.id_to_idx[paper_id]
            target_row = self.tfidf.tfidf_matrix[target_t_idx]
            t_sims = (target_row * self.tfidf.tfidf_matrix.T).toarray()[0]
            top_t_indices = np.argsort(t_sims)[::-1][:150]
            for idx in top_t_indices:
                pid = self.tfidf.paper_ids[idx]
                if pid != paper_id:
                    tfidf_scores[pid] = float(t_sims[idx])

        # Candidate pool
        candidate_ids = set(sem_scores.keys()).union(set(tfidf_scores.keys()))

        recommendations: List[PaperRecommendation] = []

        for pid in candidate_ids:
            doc = self.index.doc_metadata.get(pid)
            if not doc or pid == paper_id:
                continue

            s_sem = sem_scores.get(pid, 0.0)
            s_tfidf = tfidf_scores.get(pid, 0.0)

            # Category overlap score
            doc_cats = set(doc.get("categories", []) + [doc.get("primary_category", "")])
            cat_overlap = len(target_cats.intersection(doc_cats))
            cat_score = min(cat_overlap / max(len(target_cats), 1), 1.0)

            # Author/Venue/Keyword relationships
            doc_authors = set(doc.get("authors", []))
            doc_kws = set(doc.get("keywords", []))
            
            author_overlap = len(target_authors.intersection(doc_authors)) > 0
            venue_overlap = (doc.get("venue") == target_venue) and bool(target_venue)
            kw_overlap = len(target_kws.intersection(doc_kws))

            relation_score = 0.0
            if author_overlap:
                relation_score += 0.4
            if venue_overlap:
                relation_score += 0.3
            if kw_overlap > 0:
                relation_score += min(kw_overlap * 0.2, 0.3)

            # Combined hybrid recommendation score
            final_sim = (
                0.45 * max(s_sem, 0.0) +
                0.25 * max(s_tfidf, 0.0) +
                0.15 * cat_score +
                0.15 * min(relation_score, 1.0)
            )

            reasons: List[str] = []
            if s_sem > 0.70:
                reasons.append(f"High conceptual semantic similarity ({int(s_sem * 100)}%)")
            if cat_overlap > 0:
                reasons.append(f"Shared research field ({doc.get('primary_category')})")
            if kw_overlap > 0:
                reasons.append(f"Shared keywords ({', '.join(list(target_kws.intersection(doc_kws))[:2])})")
            if author_overlap:
                reasons.append(f"Authored by same research group")
            if venue_overlap:
                reasons.append(f"Published at same venue ({target_venue})")

            if not reasons:
                reasons.append("Related methodology and domain concepts")

            recommendations.append(PaperRecommendation(
                paper_id=pid,
                title=doc.get("title", ""),
                authors=doc.get("authors", []),
                abstract=doc.get("abstract", ""),
                publication_year=doc.get("publication_year", 2020),
                venue=doc.get("venue", ""),
                citation_count=doc.get("citation_count", 0),
                primary_category=doc.get("primary_category", "Computer Science"),
                similarity_score=round(final_sim, 4),
                similarity_percentage=round(min(max(final_sim * 100, 10.0), 99.0), 1),
                reasons=reasons,
                signal_breakdown={
                    "semantic": round(s_sem, 3),
                    "tfidf": round(s_tfidf, 3),
                    "category": round(cat_score, 3),
                    "relations": round(relation_score, 3)
                }
            ))

        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        return recommendations[:top_k]
