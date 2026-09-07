import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import numpy as np
from app.core.config import settings
from app.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class SemanticEngine:
    """
    Semantic Retrieval Engine utilizing dense transformer embeddings.
    Embeddings are L2-normalized so dot products compute exact cosine similarities.
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None
        self.embeddings_matrix: Optional[np.ndarray] = None  # shape (N, 384)
        self.paper_ids: List[str] = []
        self.id_to_idx: Dict[str, int] = {}

    @property
    def model(self):
        if self._model is None and SentenceTransformer is not None:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode_texts(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """Encode list of texts into normalized float32 vectors"""
        if self.model is None:
            raise RuntimeError("SentenceTransformer is not available.")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode single search query into normalized float32 vector"""
        if self.model is None:
            raise RuntimeError("SentenceTransformer is not available.")
        vec = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
        return vec.astype(np.float32)

    def set_embeddings(self, paper_ids: List[str], embeddings_matrix: np.ndarray):
        """Load in-memory embeddings matrix and paper IDs map"""
        self.paper_ids = paper_ids
        self.id_to_idx = {pid: idx for idx, pid in enumerate(paper_ids)}
        # Ensure L2 normalized
        norms = np.linalg.norm(embeddings_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings_matrix = (embeddings_matrix / norms).astype(np.float32)

    def score_query(
        self,
        query: str,
        query_vector: Optional[np.ndarray] = None,
        candidate_doc_ids: Optional[List[str]] = None,
        top_k: int = 100
    ) -> List[Tuple[str, float]]:
        """
        Compute cosine similarity between query embedding and paper embeddings.
        Returns sorted list of (paper_id, score).
        """
        if self.embeddings_matrix is None or len(self.paper_ids) == 0:
            return []

        if query_vector is None:
            query_vector = self.encode_query(query)

        # Exact cosine similarity via matrix-vector multiplication
        sims = np.dot(self.embeddings_matrix, query_vector)

        if candidate_doc_ids:
            cand_indices = [self.id_to_idx[pid] for pid in candidate_doc_ids if pid in self.id_to_idx]
            if not cand_indices:
                return []
            cand_sims = sims[cand_indices]
            top_sub_idx = np.argsort(cand_sims)[::-1][:top_k]
            return [(self.paper_ids[cand_indices[i]], float(cand_sims[i])) for i in top_sub_idx]
        else:
            top_indices = np.argsort(sims)[::-1][:top_k]
            return [(self.paper_ids[i], float(sims[i])) for i in top_indices]

    def save(self, matrix_path: Path, map_path: Path):
        """Save embeddings matrix and paper IDs mapping"""
        matrix_path.parent.mkdir(parents=True, exist_ok=True)
        if self.embeddings_matrix is not None:
            np.save(matrix_path, self.embeddings_matrix)
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(self.paper_ids, f)

    def load(self, matrix_path: Path, map_path: Path):
        """Load precomputed embeddings matrix and paper IDs mapping"""
        if matrix_path.exists() and map_path.exists():
            self.embeddings_matrix = np.load(matrix_path)
            with open(map_path, "r", encoding="utf-8") as f:
                self.paper_ids = json.load(f)
            self.id_to_idx = {pid: idx for idx, pid in enumerate(self.paper_ids)}
            logger.info(f"Loaded {len(self.paper_ids)} embeddings (shape {self.embeddings_matrix.shape}).")
        else:
            logger.warning(f"Embeddings file {matrix_path} or {map_path} not found.")
