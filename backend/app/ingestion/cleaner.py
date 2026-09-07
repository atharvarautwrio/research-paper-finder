import re
from typing import List, Dict, Any, Tuple

class DatasetCleaner:
    """
    Validates, deduplicates, and normalizes raw research paper records.
    """
    def __init__(self):
        self.seen_titles = set()
        self.seen_ids = set()

    def clean_text(self, text: str) -> str:
        """Strip whitespace and collapse multiple spaces"""
        if not text:
            return ""
        return re.sub(r"\s+", " ", str(text)).strip()

    def validate_and_clean(self, raw_papers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Validate schema, remove duplicate titles/IDs, and normalize fields.
        Returns (cleaned_papers, statistics_report)
        """
        cleaned_papers: List[Dict[str, Any]] = []
        stats = {
            "total_raw": len(raw_papers),
            "duplicates_removed": 0,
            "invalid_schema_dropped": 0,
            "total_cleaned": 0
        }

        for p in raw_papers:
            # Check required fields
            title = self.clean_text(p.get("title", ""))
            abstract = self.clean_text(p.get("abstract", ""))
            paper_id = self.clean_text(p.get("paper_id", ""))

            if not title or not abstract or not paper_id:
                stats["invalid_schema_dropped"] += 1
                continue

            # Deduplicate by normalized title
            title_norm = title.lower()
            if title_norm in self.seen_titles or paper_id in self.seen_ids:
                stats["duplicates_removed"] += 1
                continue

            self.seen_titles.add(title_norm)
            self.seen_ids.add(paper_id)

            cleaned = {
                "paper_id": paper_id,
                "title": title,
                "authors": [self.clean_text(a) for a in p.get("authors", []) if self.clean_text(a)],
                "abstract": abstract,
                "keywords": [self.clean_text(k) for k in p.get("keywords", []) if self.clean_text(k)],
                "categories": [self.clean_text(c) for c in p.get("categories", []) if self.clean_text(c)],
                "primary_category": self.clean_text(p.get("primary_category", "Computer Science")),
                "publication_year": int(p.get("publication_year", 2020)),
                "venue": self.clean_text(p.get("venue", "arXiv")),
                "citation_count": max(int(p.get("citation_count", 0)), 0),
                "doi": self.clean_text(p.get("doi", "")),
                "url": self.clean_text(p.get("url", "")),
                "pdf_url": self.clean_text(p.get("pdf_url", ""))
            }

            cleaned_papers.append(cleaned)

        stats["total_cleaned"] = len(cleaned_papers)
        return cleaned_papers, stats
