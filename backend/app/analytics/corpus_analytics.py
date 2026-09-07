from typing import List, Dict, Any
from collections import Counter
import numpy as np
from app.schemas.analytics import (
    AnalyticsOverview, YearlyCount, CategoryCount, KeywordCount, VenueCount
)

class CorpusAnalytics:
    """
    Computes statistical and aggregate analytics across the 20,000-paper corpus.
    """
    def __init__(self, papers: List[Dict[str, Any]]):
        self.papers = papers

    def get_overview(self) -> AnalyticsOverview:
        """Compute full dataset distribution and summary statistics"""
        total = len(self.papers)
        if total == 0:
            return AnalyticsOverview(
                total_papers=0, total_authors=0, total_venues=0, total_categories=0,
                avg_citations=0.0, max_citations=0, median_citations=0.0,
                year_range=[2015, 2025], papers_by_year=[], papers_by_category=[],
                top_keywords=[], top_venues=[], citation_distribution=[]
            )

        authors_set = set()
        venues_set = set()
        categories_set = set()
        years_counter = Counter()
        cat_counter = Counter()
        kw_counter = Counter()
        venue_counter = Counter()
        citations_list: List[int] = []

        for p in self.papers:
            for a in p.get("authors", []):
                authors_set.add(a)
            
            ven = p.get("venue", "Other")
            if ven:
                venues_set.add(ven)
                venue_counter[ven] += 1

            pcat = p.get("primary_category", "Other")
            categories_set.add(pcat)
            cat_counter[pcat] += 1

            for c in p.get("categories", []):
                categories_set.add(c)

            yr = p.get("publication_year", 2020)
            years_counter[yr] += 1

            for kw in p.get("keywords", []):
                if kw:
                    kw_counter[kw.lower()] += 1

            cit = p.get("citation_count", 0)
            citations_list.append(cit)

        avg_cits = float(np.mean(citations_list)) if citations_list else 0.0
        max_cits = int(max(citations_list)) if citations_list else 0
        median_cits = float(np.median(citations_list)) if citations_list else 0.0

        min_year = min(years_counter.keys()) if years_counter else 2015
        max_year = max(years_counter.keys()) if years_counter else 2025

        papers_by_year = [
            YearlyCount(year=y, count=c)
            for y, c in sorted(years_counter.items(), key=lambda x: x[0])
        ]

        papers_by_category = [
            CategoryCount(category=cat, count=cnt, percentage=round((cnt / total) * 100, 2))
            for cat, cnt in sorted(cat_counter.items(), key=lambda x: x[1], reverse=True)
        ]

        top_keywords = [
            KeywordCount(keyword=kw, count=cnt)
            for kw, cnt in sorted(kw_counter.items(), key=lambda x: x[1], reverse=True)[:25]
        ]

        top_venues = [
            VenueCount(venue=v, count=cnt)
            for v, cnt in sorted(venue_counter.items(), key=lambda x: x[1], reverse=True)[:15]
        ]

        # Citation tiers distribution
        cit_tiers = [
            {"tier": "0 - 10", "count": sum(1 for c in citations_list if c <= 10)},
            {"tier": "11 - 50", "count": sum(1 for c in citations_list if 10 < c <= 50)},
            {"tier": "51 - 200", "count": sum(1 for c in citations_list if 50 < c <= 200)},
            {"tier": "201 - 1,000", "count": sum(1 for c in citations_list if 200 < c <= 1000)},
            {"tier": "1,000+", "count": sum(1 for c in citations_list if c > 1000)},
        ]

        return AnalyticsOverview(
            total_papers=total,
            total_authors=len(authors_set),
            total_venues=len(venues_set),
            total_categories=len(categories_set),
            avg_citations=round(avg_cits, 1),
            max_citations=max_cits,
            median_citations=round(median_cits, 1),
            year_range=[min_year, max_year],
            papers_by_year=papers_by_year,
            papers_by_category=papers_by_category,
            top_keywords=top_keywords,
            top_venues=top_venues,
            citation_distribution=cit_tiers
        )
