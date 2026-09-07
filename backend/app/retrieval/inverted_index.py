import pickle
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from app.retrieval.preprocessor import TextPreprocessor

class InvertedIndex:
    """
    Field-aware Inverted Index for academic papers.
    Tracks postings for fields: 'title', 'abstract', 'keywords', 'authors', 'categories'.
    Stores term frequencies, positions, document lengths, and document frequencies.
    """
    def __init__(self):
        # term -> {doc_id -> {field -> {"tf": count, "positions": [int]}}}
        self.index: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(lambda: defaultdict(dict))
        # term -> int (number of documents containing term across any field)
        self.doc_freq: Dict[str, int] = defaultdict(int)
        # doc_id -> {field -> length_in_tokens}
        self.doc_field_lengths: Dict[str, Dict[str, int]] = defaultdict(dict)
        # field -> average_length
        self.avg_field_lengths: Dict[str, float] = defaultdict(float)
        # Total number of documents indexed
        self.num_docs: int = 0
        # doc_id -> full metadata dict for quick reference
        self.doc_metadata: Dict[str, Dict[str, Any]] = {}
        # Preprocessor instance
        self.preprocessor = TextPreprocessor()

    def add_document(self, doc_id: str, fields: Dict[str, str], metadata: Optional[Dict[str, Any]] = None):
        """Index a single document with multiple fields"""
        self.num_docs += 1
        if metadata:
            self.doc_metadata[doc_id] = metadata

        terms_in_doc: Set[str] = set()

        for field_name, field_text in fields.items():
            if not field_text:
                self.doc_field_lengths[doc_id][field_name] = 0
                continue

            tokens = self.preprocessor.preprocess(str(field_text), remove_stops=True, stem=True)
            self.doc_field_lengths[doc_id][field_name] = len(tokens)

            term_positions = defaultdict(list)
            for pos, token in enumerate(tokens):
                term_positions[token].append(pos)
                terms_in_doc.add(token)

            for token, positions in term_positions.items():
                self.index[token][doc_id][field_name] = {
                    "tf": len(positions),
                    "positions": positions
                }

        for term in terms_in_doc:
            self.doc_freq[term] += 1

    def finalize(self):
        """Compute aggregate statistics like average document and field lengths"""
        field_totals = defaultdict(int)
        for doc_id, field_lens in self.doc_field_lengths.items():
            for field, length in field_lens.items():
                field_totals[field] += length

        if self.num_docs > 0:
            for field, total_len in field_totals.items():
                self.avg_field_lengths[field] = total_len / float(self.num_docs)

    def get_postings(self, term: str) -> Dict[str, Dict[str, Any]]:
        """Return postings dictionary for a given term"""
        return self.index.get(term, {})

    def get_doc_freq(self, term: str) -> int:
        """Return document frequency of term"""
        return self.doc_freq.get(term, 0)

    def get_idf(self, term: str) -> float:
        """Calculate standard smoothed IDF"""
        df = self.get_doc_freq(term)
        if df == 0 or self.num_docs == 0:
            return 0.0
        return math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))

    def phrase_search(self, phrase: str, field: str = "title") -> Set[str]:
        """Exact phrase search using positional postings"""
        tokens = self.preprocessor.preprocess(phrase, remove_stops=False, stem=True)
        if not tokens:
            return set()
        
        # Start with docs containing first token in target field
        first_postings = self.get_postings(tokens[0])
        candidate_docs = {doc_id for doc_id, f_data in first_postings.items() if field in f_data}

        matching_docs: Set[str] = set()

        for doc_id in candidate_docs:
            # Check if successive tokens appear at consecutive positions
            positions = first_postings[doc_id][field]["positions"]
            for pos in positions:
                match = True
                for i in range(1, len(tokens)):
                    next_postings = self.get_postings(tokens[i])
                    if doc_id not in next_postings or field not in next_postings[doc_id]:
                        match = False
                        break
                    next_positions = next_postings[doc_id][field]["positions"]
                    if (pos + i) not in next_positions:
                        match = False
                        break
                if match:
                    matching_docs.add(doc_id)
                    break

        return matching_docs

    def save(self, filepath: Path):
        """Serialize index to disk"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({
                "index": dict(self.index),
                "doc_freq": dict(self.doc_freq),
                "doc_field_lengths": dict(self.doc_field_lengths),
                "avg_field_lengths": dict(self.avg_field_lengths),
                "num_docs": self.num_docs,
                "doc_metadata": self.doc_metadata
            }, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, filepath: Path) -> "InvertedIndex":
        """Load index from serialized file"""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        idx = cls()
        idx.index = defaultdict(lambda: defaultdict(dict), data["index"])
        idx.doc_freq = defaultdict(int, data["doc_freq"])
        idx.doc_field_lengths = defaultdict(dict, data["doc_field_lengths"])
        idx.avg_field_lengths = defaultdict(float, data["avg_field_lengths"])
        idx.num_docs = data["num_docs"]
        idx.doc_metadata = data.get("doc_metadata", {})
        return idx
