from typing import List, Dict, Any, Set
from app.schemas.search import MatchExplanation
from app.retrieval.preprocessor import TextPreprocessor

class ExplainabilityEngine:
    """
    Generates transparent, human-interpretable explanations and signal breakdowns
    for each retrieved paper in the search results.
    """
    def __init__(self):
        self.preprocessor = TextPreprocessor()

    def generate_explanation(
        self,
        query: str,
        query_tokens: List[str],
        expanded_terms: List[str],
        paper_dict: Dict[str, Any],
        signals: Dict[str, float],
        weights: Dict[str, float],
        final_relevance_score: float
    ) -> MatchExplanation:
        """
        Explain why the document matched the query and how its score was formed.
        """
        title = paper_dict.get("title", "")
        abstract = paper_dict.get("abstract", "")
        keywords = paper_dict.get("keywords", [])
        categories = paper_dict.get("categories", [])
        citation_count = paper_dict.get("citation_count", 0)
        pub_year = paper_dict.get("publication_year", 2020)

        # Tokenize document fields for overlap analysis
        title_tokens = set(self.preprocessor.preprocess(title, remove_stops=True, stem=True))
        abstract_tokens = set(self.preprocessor.preprocess(abstract, remove_stops=True, stem=True))
        keyword_tokens = set()
        for kw in keywords:
            keyword_tokens.update(self.preprocessor.preprocess(kw, remove_stops=True, stem=True))

        query_set = set(query_tokens)
        
        # Matched terms
        matched_in_title = list(query_set.intersection(title_tokens))
        matched_in_abstract = list(query_set.intersection(abstract_tokens))
        matched_in_keywords = list(query_set.intersection(keyword_tokens))
        all_matched_query_terms = list(query_set.intersection(title_tokens | abstract_tokens | keyword_tokens))

        # Check expanded terms
        matched_expanded = [t for t in expanded_terms if t in (title_tokens | abstract_tokens)]

        # Generate reasons
        reasons: List[str] = []

        if len(matched_in_title) > 0:
            reasons.append(f"Title matches key query concept{'s' if len(matched_in_title) > 1 else ''} ({', '.join(matched_in_title[:3])})")

        if len(matched_in_abstract) >= 3:
            reasons.append(f"{len(matched_in_abstract)} distinct query terms matched in abstract")
        elif len(matched_in_abstract) > 0:
            reasons.append(f"Abstract discusses query topic ({', '.join(matched_in_abstract[:3])})")

        sem_score = signals.get("semantic", 0.0)
        if sem_score >= 0.75:
            reasons.append(f"Exceptional semantic alignment with research intent ({int(sem_score * 100)}% similarity)")
        elif sem_score >= 0.50:
            reasons.append(f"Strong contextual semantic match ({int(sem_score * 100)}% similarity)")

        bm25_score = signals.get("bm25", 0.0)
        if bm25_score >= 0.65:
            reasons.append("High BM25 lexical term density score")

        if len(matched_in_keywords) > 0:
            reasons.append(f"Author keywords match research subject ({', '.join(keywords[:2])})")

        if len(matched_expanded) > 0:
            reasons.append(f"Matched domain-expanded terminology ({', '.join(matched_expanded[:2])})")

        if citation_count > 1000:
            reasons.append(f"Highly cited foundational paper ({citation_count:,} citations)")
        elif citation_count > 100:
            reasons.append(f"Widely referenced work ({citation_count} citations)")

        if pub_year >= 2023:
            reasons.append(f"Recent research publication ({pub_year})")

        if not reasons:
            reasons.append("Matched via contextual semantic similarity")

        relevance_percentage = round(min(max(final_relevance_score * 100, 5.0), 99.5), 1)

        return MatchExplanation(
            relevance_score=round(final_relevance_score, 4),
            relevance_percentage=relevance_percentage,
            signals={k: round(v, 4) for k, v in signals.items()},
            matched_query_terms=all_matched_query_terms,
            title_match_terms=matched_in_title,
            reasons=reasons,
            query_expansion_used=matched_expanded
        )
