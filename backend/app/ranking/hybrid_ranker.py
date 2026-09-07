import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from app.core.config import settings
from app.retrieval.inverted_index import InvertedIndex
from app.retrieval.bm25_engine import BM25Engine
from app.retrieval.tfidf_engine import TFIDFEngine
from app.retrieval.semantic_engine import SemanticEngine
from app.retrieval.preprocessor import TextPreprocessor
from app.ranking.explainability import ExplainabilityEngine
from app.schemas.search import (
    SearchRequest, SearchResponse, SearchResultItem,
    SearchFacets, FacetItem, SearchFilter, RankingWeights
)

class HybridRanker:
    """
    Multi-stage hybrid ranking pipeline combining BM25, TF-IDF, Semantic embeddings,
    field boosts, recency prior, and citation normalization.
    """
    def __init__(
        self,
        inverted_index: InvertedIndex,
        bm25_engine: BM25Engine,
        tfidf_engine: TFIDFEngine,
        semantic_engine: SemanticEngine
    ):
        self.inverted_index = inverted_index
        self.bm25 = bm25_engine
        self.tfidf = tfidf_engine
        self.semantic = semantic_engine
        self.preprocessor = TextPreprocessor()
        self.explainability = ExplainabilityEngine()

    def _normalize_dict_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Min-Max normalization to [0, 1] range"""
        if not scores:
            return {}
        vals = list(scores.values())
        min_v = min(vals)
        max_v = max(vals)
        if max_v == min_v:
            return {k: 1.0 if max_v > 0 else 0.0 for k in scores}
        return {k: (v - min_v) / (max_v - min_v) for k, v in scores.items()}

    def _apply_filters(self, doc_ids: List[str], filters: Optional[SearchFilter]) -> List[str]:
        """Filter candidates by category, year, citations, venue, authors"""
        if not filters:
            return doc_ids

        filtered = []
        for pid in doc_ids:
            doc = self.inverted_index.doc_metadata.get(pid)
            if not doc:
                continue

            # Year filter
            year = doc.get("publication_year", 0)
            if filters.min_year and year < filters.min_year:
                continue
            if filters.max_year and year > filters.max_year:
                continue

            # Citations filter
            cits = doc.get("citation_count", 0)
            if filters.min_citations and cits < filters.min_citations:
                continue
            if filters.max_citations and cits > filters.max_citations:
                continue

            # Category filter
            if filters.categories:
                doc_cats = [c.lower() for c in doc.get("categories", [])] + [doc.get("primary_category", "").lower()]
                target_cats = [c.lower() for c in filters.categories]
                if not any(tc in doc_cats for tc in target_cats):
                    continue

            # Venue filter
            if filters.venues:
                doc_venue = doc.get("venue", "").lower()
                target_venues = [v.lower() for v in filters.venues]
                if not any(tv in doc_venue for tv in target_venues):
                    continue

            # Authors filter
            if filters.authors:
                doc_authors = [a.lower() for a in doc.get("authors", [])]
                target_authors = [a.lower() for a in filters.authors]
                if not any(any(ta in da for da in doc_authors) for ta in target_authors):
                    continue

            filtered.append(pid)

        return filtered

    def _calculate_facets(self, doc_ids: List[str]) -> SearchFacets:
        """Calculate facets on matched documents"""
        cat_counts: Dict[str, int] = {}
        venue_counts: Dict[str, int] = {}
        year_counts: Dict[str, int] = {}
        cit_ranges = {"0-10": 0, "11-50": 0, "51-200": 0, "201-1000": 0, "1000+": 0}

        for pid in doc_ids:
            doc = self.inverted_index.doc_metadata.get(pid)
            if not doc:
                continue
            
            pcat = doc.get("primary_category") or "Other"
            cat_counts[pcat] = cat_counts.get(pcat, 0) + 1
            
            ven = doc.get("venue") or "Other"
            venue_counts[ven] = venue_counts.get(ven, 0) + 1
            
            yr = doc.get("publication_year")
            if yr:
                yr_str = str(yr)
                year_counts[yr_str] = year_counts.get(yr_str, 0) + 1

            c = doc.get("citation_count", 0)
            if c <= 10:
                cit_ranges["0-10"] += 1
            elif c <= 50:
                cit_ranges["11-50"] += 1
            elif c <= 200:
                cit_ranges["51-200"] += 1
            elif c <= 1000:
                cit_ranges["201-1000"] += 1
            else:
                cit_ranges["1000+"] += 1

        top_cats = [FacetItem(name=k, count=v) for k, v in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        top_venues = [FacetItem(name=k, count=v) for k, v in sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        top_years = [FacetItem(name=k, count=v) for k, v in sorted(year_counts.items(), key=lambda x: int(x[0]), reverse=True)[:10]]
        cit_facet = [FacetItem(name=k, count=v) for k, v in cit_ranges.items()]

        return SearchFacets(categories=top_cats, venues=top_venues, years=top_years, citation_ranges=cit_facet)

    def search(self, req: SearchRequest, latency_start: float = 0.0) -> SearchResponse:
        """
        Execute search across BM25, TF-IDF, Semantic, or Hybrid mode.
        """
        query = req.query.strip()
        base_tokens, expanded_tokens = self.preprocessor.expand_query(query)
        all_query_tokens = base_tokens + expanded_tokens
        exact_phrases = self.preprocessor.extract_phrases(query)

        # Set weights
        w = req.weights or RankingWeights()
        weights_dict = {
            "bm25": w.bm25,
            "tfidf": w.tfidf,
            "semantic": w.semantic,
            "title_match": w.title_match,
            "recency": w.recency,
            "citations": w.citations
        }

        # 1. First-stage Candidate Retrieval
        candidate_pids: Set[str] = set()

        bm25_raw: Dict[str, float] = {}
        tfidf_raw: Dict[str, float] = {}
        sem_raw: Dict[str, float] = {}

        mode = req.mode.lower()

        if mode in ("bm25", "hybrid"):
            bm25_res = self.bm25.score_query(all_query_tokens, top_k=300)
            bm25_raw = {pid: score for pid, score in bm25_res}
            candidate_pids.update(bm25_raw.keys())

        if mode in ("tfidf", "hybrid"):
            tfidf_res = self.tfidf.score_query(query, top_k=300)
            tfidf_raw = {pid: score for pid, score in tfidf_res}
            candidate_pids.update(tfidf_raw.keys())

        if mode in ("semantic", "hybrid"):
            sem_res = self.semantic.score_query(query, top_k=300)
            sem_raw = {pid: score for pid, score in sem_res}
            candidate_pids.update(sem_raw.keys())

        # Exact phrase filter bonus / boost
        if exact_phrases:
            for phrase in exact_phrases:
                phrase_matches = self.inverted_index.phrase_search(phrase, field="title") | self.inverted_index.phrase_search(phrase, field="abstract")
                candidate_pids.update(phrase_matches)

        # If no candidates found, fallback to semantic top candidates
        if not candidate_pids and self.semantic.embeddings_matrix is not None:
            sem_res = self.semantic.score_query(query, top_k=50)
            sem_raw = {pid: score for pid, score in sem_res}
            candidate_pids.update(sem_raw.keys())

        # 2. Apply Filters
        filtered_pids = self._apply_filters(list(candidate_pids), req.filters)
        facets = self._calculate_facets(filtered_pids)

        # 3. Score Normalization & Hybrid Combination
        bm25_norm = self._normalize_dict_scores({pid: bm25_raw.get(pid, 0.0) for pid in filtered_pids})
        tfidf_norm = self._normalize_dict_scores({pid: tfidf_raw.get(pid, 0.0) for pid in filtered_pids})
        sem_norm = self._normalize_dict_scores({pid: sem_raw.get(pid, 0.0) for pid in filtered_pids})

        scored_candidates: List[Tuple[str, float, Dict[str, float]]] = []

        for pid in filtered_pids:
            doc = self.inverted_index.doc_metadata.get(pid, {})
            title = doc.get("title", "")
            title_tokens = set(self.preprocessor.preprocess(title, remove_stops=True, stem=True))
            
            # Title exact match score
            title_overlap = len(set(base_tokens).intersection(title_tokens))
            title_score = title_overlap / max(len(base_tokens), 1)

            # Recency score (2015 -> 0.0, 2025 -> 1.0)
            pub_year = doc.get("publication_year", 2020)
            recency_score = min(max((pub_year - 2015) / 10.0, 0.0), 1.0)

            # Citation score (log-normalized)
            cits = doc.get("citation_count", 0)
            cit_score = min(math.log1p(cits) / math.log1p(50000), 1.0)

            s_bm25 = bm25_norm.get(pid, 0.0)
            s_tfidf = tfidf_norm.get(pid, 0.0)
            s_sem = sem_norm.get(pid, 0.0)

            signals = {
                "bm25": s_bm25,
                "tfidf": s_tfidf,
                "semantic": s_sem,
                "title_match": title_score,
                "recency": recency_score,
                "citations": cit_score
            }

            if mode == "bm25":
                final_score = s_bm25 * 0.8 + title_score * 0.2
            elif mode == "tfidf":
                final_score = s_tfidf * 0.8 + title_score * 0.2
            elif mode == "semantic":
                final_score = s_sem * 0.85 + title_score * 0.15
            else:  # hybrid
                final_score = (
                    weights_dict["bm25"] * s_bm25 +
                    weights_dict["tfidf"] * s_tfidf +
                    weights_dict["semantic"] * s_sem +
                    weights_dict["title_match"] * title_score +
                    weights_dict["recency"] * recency_score +
                    weights_dict["citations"] * cit_score
                )

            scored_candidates.append((pid, final_score, signals))

        # 4. Sorting
        sort_by = req.sort_by.lower()
        if sort_by == "newest":
            scored_candidates.sort(
                key=lambda x: (self.inverted_index.doc_metadata.get(x[0], {}).get("publication_year", 0), x[1]),
                reverse=True
            )
        elif sort_by == "oldest":
            scored_candidates.sort(
                key=lambda x: (self.inverted_index.doc_metadata.get(x[0], {}).get("publication_year", 9999), -x[1])
            )
        elif sort_by == "citations":
            scored_candidates.sort(
                key=lambda x: (self.inverted_index.doc_metadata.get(x[0], {}).get("citation_count", 0), x[1]),
                reverse=True
            )
        else:  # relevance
            scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # 5. Pagination
        total_results = len(scored_candidates)
        page = max(req.page, 1)
        page_size = max(req.page_size, 1)
        total_pages = max(math.ceil(total_results / page_size), 1)
        start_idx = (page - 1) * page_size
        paged_candidates = scored_candidates[start_idx : start_idx + page_size]

        # 6. Build Result Items with Explanations
        result_items: List[SearchResultItem] = []
        for rank_offset, (pid, score, signals) in enumerate(paged_candidates):
            doc = self.inverted_index.doc_metadata.get(pid, {})
            explanation = self.explainability.generate_explanation(
                query=query,
                query_tokens=base_tokens,
                expanded_terms=expanded_tokens,
                paper_dict=doc,
                signals=signals,
                weights=weights_dict,
                final_relevance_score=score
            )
            item = SearchResultItem(
                paper_id=pid,
                title=doc.get("title", ""),
                authors=doc.get("authors", []),
                abstract=doc.get("abstract", ""),
                keywords=doc.get("keywords", []),
                categories=doc.get("categories", []),
                primary_category=doc.get("primary_category", ""),
                publication_year=doc.get("publication_year", 2020),
                venue=doc.get("venue", ""),
                citation_count=doc.get("citation_count", 0),
                doi=doc.get("doi"),
                url=doc.get("url"),
                pdf_url=doc.get("pdf_url"),
                rank=start_idx + rank_offset + 1,
                explanation=explanation
            )
            result_items.append(item)

        import time
        elapsed_ms = (time.time() - latency_start) * 1000.0 if latency_start > 0 else 0.0

        return SearchResponse(
            query=query,
            retrieval_mode=mode,
            total_results=total_results,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            latency_ms=round(elapsed_ms, 2),
            results=result_items,
            facets=facets,
            query_tokens=base_tokens,
            expanded_terms=expanded_tokens
        )
