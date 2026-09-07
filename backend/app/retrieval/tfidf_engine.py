import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from app.retrieval.preprocessor import TextPreprocessor

_global_preprocessor = TextPreprocessor()

def _tfidf_tokenizer(text: str) -> List[str]:
    """Module-level picklable tokenizer function for TfidfVectorizer"""
    return _global_preprocessor.preprocess(text, remove_stops=True, stem=True)

class TFIDFEngine:
    """
    Vector Space Model retrieval engine using TF-IDF and Cosine Similarity.
    Precomputes sparse TF-IDF matrix over the 20,000 document collection.
    """
    def __init__(self):
        self.preprocessor = _global_preprocessor
        self.vectorizer = TfidfVectorizer(
            tokenizer=_tfidf_tokenizer,
            lowercase=True,
            sublinear_tf=True,
            smooth_idf=True,
            norm="l2",
            max_features=40000,
            token_pattern=None
        )
        self.tfidf_matrix: Optional[csr_matrix] = None
        self.paper_ids: List[str] = []
        self.id_to_idx: Dict[str, int] = {}

    def fit_transform(self, paper_ids: List[str], corpus_texts: List[str]):
        """Fit vectorizer on corpus and store matrix"""
        self.paper_ids = paper_ids
        self.id_to_idx = {pid: idx for idx, pid in enumerate(paper_ids)}
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_texts)

    def score_query(
        self,
        query: str,
        candidate_doc_ids: Optional[List[str]] = None,
        top_k: int = 100
    ) -> List[Tuple[str, float]]:
        """Compute cosine similarity of query vector against document vectors"""
        if self.tfidf_matrix is None or len(self.paper_ids) == 0:
            return []

        query_vec = self.vectorizer.transform([query])
        # Fast sparse dot product
        similarities = (query_vec * self.tfidf_matrix.T).toarray()[0]

        if candidate_doc_ids:
            candidate_indices = [self.id_to_idx[pid] for pid in candidate_doc_ids if pid in self.id_to_idx]
            if not candidate_indices:
                return []
            candidate_sims = similarities[candidate_indices]
            top_sub_idx = np.argsort(candidate_sims)[::-1][:top_k]
            return [(self.paper_ids[candidate_indices[i]], float(candidate_sims[i])) for i in top_sub_idx if candidate_sims[i] > 0]
        else:
            top_indices = np.argsort(similarities)[::-1][:top_k]
            return [(self.paper_ids[i], float(similarities[i])) for i in top_indices if similarities[i] > 0]

    def save(self, filepath: Path):
        """Serialize TF-IDF model and matrix"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "tfidf_matrix": self.tfidf_matrix,
                "paper_ids": self.paper_ids,
                "id_to_idx": self.id_to_idx
            }, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, filepath: Path) -> "TFIDFEngine":
        """Load TF-IDF model and matrix"""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        engine = cls()
        engine.vectorizer = data["vectorizer"]
        engine.tfidf_matrix = data["tfidf_matrix"]
        engine.paper_ids = data["paper_ids"]
        engine.id_to_idx = data["id_to_idx"]
        return engine
