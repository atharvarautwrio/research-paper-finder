import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.schemas.analytics import TrendItem
from app.core.logging import logger

CORE_RESEARCH_TOPICS = [
    {"name": "Large Language Models & Transformers", "keywords": ["transformer", "llm", "large language", "prompt", "gpt", "bert", "rag"]},
    {"name": "Generative AI & Diffusion Models", "keywords": ["diffusion", "generative", "gan", "latent diffusion", "generation", "text-to-image"]},
    {"name": "Cloud Computing & Enterprise DevOps (MCA)", "keywords": ["kubernetes", "docker", "serverless", "devops", "cloud", "microservices", "terraform"]},
    {"name": "Database Management & Data Warehousing (MCA)", "keywords": ["sql", "rdbms", "database", "sharding", "nosql", "olap", "concurrency", "postgresql"]},
    {"name": "Full-Stack Web & Mobile Architectures (MCA)", "keywords": ["react", "flutter", "graphql", "websockets", "mobile", "rest api", "pwa"]},
    {"name": "Big Data Analytics & Stream Processing (MCA)", "keywords": ["spark", "hadoop", "business intelligence", "etl", "data mining", "tableau", "kafka"]},
    {"name": "Cybersecurity & Zero Trust Architecture", "keywords": ["cybersecurity", "zero trust", "vulnerability", "cryptography", "owasp", "intrusion"]},
    {"name": "Biomedical Discovery, CRISPR & Genomics", "keywords": ["crispr", "genetics", "medical", "vaccine", "biomarker", "oncology", "clinical"]},
    {"name": "Behavioral Economics & Decision Sciences", "keywords": ["prospect theory", "behavioral economics", "asset pricing", "governance", "monetary", "auctions"]},
    {"name": "Quantum Physics, Astrophysics & Climate", "keywords": ["quantum", "physics", "climate", "gravitational", "superconductivity", "photovoltaic"]},
    {"name": "Reinforcement Learning & Autonomous Systems", "keywords": ["reinforcement learning", "q-learning", "policy gradient", "rl", "agent", "robotics", "slam"]},
    {"name": "Information Retrieval & Neural Search", "keywords": ["information retrieval", "retrieval", "ranking", "bm25", "dense retrieval", "search", "recommender"]},
    {"name": "Computer Vision & Object Detection", "keywords": ["object detection", "segmentation", "yolo", "vit", "vision transformer", "image classification"]}
]

class TrendAnalyzer:
    """
    Temporal Research Trend Analyzer computing yearly trajectories,
    CAGR (Compound Annual Growth Rate), and momentum classification.
    """
    def __init__(self, years: Optional[List[int]] = None):
        self.years = years or [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
        self.trend_items: List[TrendItem] = []

    def analyze(self, papers: List[Dict[str, Any]]) -> List[TrendItem]:
        """Compute trajectory and growth momentum for key research topics"""
        logger.info(f"Computing research trends over years {self.years[0]}-{self.years[-1]} on {len(papers)} papers...")
        
        topic_year_counts: Dict[str, Dict[int, int]] = {
            t["name"]: {y: 0 for y in self.years} for t in CORE_RESEARCH_TOPICS
        }
        topic_totals: Dict[str, int] = defaultdict(int)

        for p in papers:
            year = p.get("publication_year", 2020)
            if year not in topic_year_counts[CORE_RESEARCH_TOPICS[0]["name"]]:
                continue

            text_corpus = f"{p.get('title', '')} {p.get('abstract', '')} {' '.join(p.get('keywords', []))}".lower()

            for topic_def in CORE_RESEARCH_TOPICS:
                topic_name = topic_def["name"]
                if any(kw in text_corpus for kw in topic_def["keywords"]):
                    topic_year_counts[topic_name][year] += 1
                    topic_totals[topic_name] += 1

        trends: List[TrendItem] = []

        for topic_def in CORE_RESEARCH_TOPICS:
            name = topic_def["name"]
            counts = [topic_year_counts[name][y] for y in self.years]
            total_papers = topic_totals[name]

            # Calculate CAGR between early period (2018-2020 avg) and recent period (2023-2025 avg)
            start_val = max(float(sum(counts[:3]) / 3.0), 1.0)
            end_val = max(float(sum(counts[-3:]) / 3.0), 1.0)
            num_periods = len(self.years) - 1

            cagr = ((end_val / start_val) ** (1.0 / num_periods) - 1.0) * 100.0

            # Momentum classification
            if cagr >= 25.0:
                status = "Emerging"
            elif cagr >= 10.0:
                status = "Accelerating"
            elif cagr >= -5.0:
                status = "Stable"
            else:
                status = "Declining"

            trends.append(TrendItem(
                topic=name,
                trajectory=counts,
                years=self.years,
                cagr=round(cagr, 1),
                status=status,
                total_papers=total_papers
            ))

        trends.sort(key=lambda x: x.cagr, reverse=True)
        self.trend_items = trends
        return trends

    def save(self, filepath: Path):
        """Save trends to JSON"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in self.trend_items], f, indent=2)

    def load(self, filepath: Path) -> List[TrendItem]:
        """Load trends from JSON"""
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.trend_items = [TrendItem(**item) for item in data]
            return self.trend_items
        return []
