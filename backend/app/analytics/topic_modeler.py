import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from app.schemas.analytics import TopicCluster
from app.core.logging import logger

DOMAIN_KEYWORDS_MAP = [
    (["transformer", "llm", "language", "nlp", "prompt", "translation", "dialogue"], "Natural Language Processing & LLMs"),
    (["vision", "image", "detection", "segmentation", "diffusion", "nerf"], "Computer Vision & Visual Generative AI"),
    (["reinforcement", "robotics", "motion", "slam", "control", "agent"], "Robotics, Autonomy & Control Systems"),
    (["retrieval", "ranking", "bm25", "search", "recommender", "index"], "Information Retrieval & Neural Search"),
    (["cybersecurity", "privacy", "adversarial", "vulnerability", "cryptography"], "Cybersecurity, Cryptography & Privacy"),
    (["database", "sql", "rdbms", "sharding", "nosql", "olap", "concurrency"], "Database Systems & Data Warehousing (MCA)"),
    (["microservices", "patterns", "agile", "architecture", "cicd", "enterprise"], "Enterprise Software Architecture & DevOps (MCA)"),
    (["cloud", "kubernetes", "serverless", "docker", "terraform", "finops"], "Cloud Computing, Virtualization & Containers (MCA)"),
    (["web", "react", "graphql", "mobile", "flutter", "websocket"], "Full-Stack Web & Mobile Engineering (MCA)"),
    (["economics", "pricing", "market", "finance", "monetary", "auctions"], "Economics, Finance & Strategic Management"),
    (["crispr", "genetics", "medical", "vaccine", "clinical", "biomarker"], "Medicine, Genomics & Healthcare"),
    (["quantum", "physics", "climate", "gravitational", "superconductivity"], "Physics, Quantum Science & Climate"),
    (["psychology", "cognitive", "dissonance", "social", "behavioral", "mindset"], "Psychology, Behavioral & Cognitive Sciences"),
    (["spark", "hadoop", "mining", "analytics", "stream", "dashboard"], "Big Data Analytics & Business Intelligence (MCA)"),
    (["iot", "sensor", "mqtt", "protocols", "campus", "embedded"], "Applied Computer Networks & IoT (MCA)"),
    (["hospital", "erp", "ecommerce", "governance", "fintech", "portal"], "Enterprise Application Systems & Case Studies (MCA)")
]

def derive_cluster_title(top_terms: List[str], topic_idx: int) -> str:
    terms_set = set(top_terms)
    for keywords, title in DOMAIN_KEYWORDS_MAP:
        if any(kw in terms_set or any(kw in t for t in top_terms) for kw in keywords):
            return title
    # Fallback to top 2-3 capitalized terms
    return f"Topic: {', '.join(top_terms[:3]).title()}"

class TopicModeler:
    """
    Topic Discovery and Modeling module using MiniBatchKMeans and TF-IDF keyword extraction.
    """
    def __init__(self, num_topics: int = 16):
        self.num_topics = num_topics
        self.vectorizer = TfidfVectorizer(max_features=15000, stop_words="english", max_df=0.7, min_df=5)
        self.kmeans = MiniBatchKMeans(n_clusters=num_topics, random_state=42, batch_size=1024)
        self.topic_clusters: List[TopicCluster] = []

    def fit(self, papers: List[Dict[str, Any]]) -> List[TopicCluster]:
        """Fit topic model on paper abstracts and extract representative terms"""
        logger.info(f"Fitting TopicModeler with {self.num_topics} clusters on {len(papers)} papers...")
        corpus = [f"{p.get('title', '')} {p.get('abstract', '')} {' '.join(p.get('keywords', []))}" for p in papers]
        
        tfidf_mat = self.vectorizer.fit_transform(corpus)
        labels = self.kmeans.fit_predict(tfidf_mat)

        terms = np.array(self.vectorizer.get_feature_names_out())
        clusters: List[TopicCluster] = []
        assigned_names = set()

        for topic_idx in range(self.num_topics):
            # Centroid top features
            center = self.kmeans.cluster_centers_[topic_idx]
            top_term_indices = np.argsort(center)[::-1][:12]
            top_terms = list(terms[top_term_indices])

            # Filter papers in this cluster
            matching_indices = [i for i, lbl in enumerate(labels) if lbl == topic_idx]
            paper_count = len(matching_indices)
            sample_titles = [papers[i].get("title", "") for i in matching_indices[:4]]

            base_name = derive_cluster_title(top_terms, topic_idx)
            name = base_name
            suffix = 2
            while name in assigned_names:
                name = f"{base_name} (Cluster {suffix})"
                suffix += 1
            assigned_names.add(name)

            clusters.append(TopicCluster(
                topic_id=topic_idx,
                name=name,
                top_terms=top_terms,
                paper_count=paper_count,
                sample_titles=sample_titles
            ))

        self.topic_clusters = clusters
        return clusters

    def save(self, filepath: Path):
        """Save discovered topics to JSON"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in self.topic_clusters], f, indent=2)

    def load(self, filepath: Path) -> List[TopicCluster]:
        """Load discovered topics from JSON"""
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.topic_clusters = [TopicCluster(**item) for item in data]
            return self.topic_clusters
        return []
