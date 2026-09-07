import re
import string
import unicodedata
from typing import List, Set, Dict, Tuple

# Comprehensive standard stop words list for academic IR
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves",
    # Academic noise stopwords
    "paper", "study", "propose", "proposed", "presents", "show", "shows", "result", "results",
    "using", "method", "methods", "approach", "approaches", "based", "via", "towards"
}

# Domain specific query expansion synonyms for Computer Science & AI
QUERY_EXPANSION_MAP: Dict[str, List[str]] = {
    "nlp": ["natural", "language", "processing", "linguistic", "text"],
    "llm": ["large", "language", "model", "transformer", "generative"],
    "llms": ["large", "language", "models", "transformers"],
    "cv": ["computer", "vision", "image", "visual"],
    "dl": ["deep", "learning", "neural", "network"],
    "ml": ["machine", "learning", "model", "algorithm"],
    "ir": ["information", "retrieval", "search", "ranking"],
    "cnn": ["convolutional", "neural", "network", "image"],
    "cnns": ["convolutional", "neural", "networks"],
    "rnn": ["recurrent", "neural", "network", "sequence"],
    "rnns": ["recurrent", "neural", "networks"],
    "gan": ["generative", "adversarial", "network"],
    "gans": ["generative", "adversarial", "networks"],
    "gnn": ["graph", "neural", "network", "node"],
    "gnns": ["graph", "neural", "networks"],
    "rl": ["reinforcement", "learning", "policy", "agent"],
    "vit": ["vision", "transformer", "patch", "attention"],
    "rag": ["retrieval", "augmented", "generation", "knowledge"],
    "recommendation": ["recommender", "collaborative", "filtering", "ranking"],
    "recommender": ["recommendation", "collaborative", "filtering"],
    "classification": ["classifier", "predicting", "categorization"],
    "segmentation": ["semantic", "instance", "mask", "pixel"],
    "detection": ["detector", "bounding", "box", "localization"],
    "medical": ["clinical", "healthcare", "biomedical", "disease", "patient"],
    "healthcare": ["medical", "clinical", "hospital", "patient"],
    "security": ["cybersecurity", "vulnerability", "attack", "privacy"],
    "robotics": ["robot", "autonomous", "manipulation", "navigation"]
}

# Simple and fast Porter Stemmer implementation
class PorterStemmer:
    def stem(self, word: str) -> str:
        word = word.lower()
        if len(word) <= 2:
            return word
        
        # Step 1a
        if word.endswith("sses"):
            word = word[:-2]
        elif word.endswith("ies"):
            word = word[:-2]
        elif word.endswith("ss"):
            pass
        elif word.endswith("s"):
            word = word[:-1]
            
        # Step 1b
        if word.endswith("eed"):
            if len(word) > 4:
                word = word[:-1]
        elif (word.endswith("ed") or word.endswith("ing")) and len(word) > 4:
            if word.endswith("ed"):
                word = word[:-2]
            else:
                word = word[:-3]
            if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
                word += "e"
            elif len(word) > 2 and word[-1] == word[-2] and word[-1] not in "lsz":
                word = word[:-1]
                
        # Step 1c
        if word.endswith("y") and len(word) > 2 and word[-2] not in "aeiou":
            word = word[:-1] + "i"
            
        # Step 2
        step2_map = {
            "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance",
            "izer": "ize", "abli": "able", "alli": "al", "entli": "ent",
            "eli": "e", "ousli": "ous", "ization": "ize", "ation": "ate",
            "ator": "ate", "alism": "al", "iveness": "ive", "fulness": "ful",
            "ousness": "ous", "aliti": "al", "iviti": "ive", "biliti": "ble"
        }
        for suffix, replacement in step2_map.items():
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                word = word[:-len(suffix)] + replacement
                break
                
        # Step 3
        step3_map = {
            "icate": "ic", "ative": "", "alize": "al", "iciti": "ic",
            "ical": "ic", "ful": "", "ness": ""
        }
        for suffix, replacement in step3_map.items():
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                word = word[:-len(suffix)] + replacement
                break

        return word


class TextPreprocessor:
    def __init__(self, use_stemmer: bool = True):
        self.use_stemmer = use_stemmer
        self.stemmer = PorterStemmer()
        self.stop_words = STOP_WORDS
        self.token_pattern = re.compile(r"[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*")

    def normalize(self, text: str) -> str:
        """Unicode normalization and lowercase"""
        if not text:
            return ""
        text = unicodedata.normalize("NFKD", text)
        return text.lower()

    def tokenize(self, text: str) -> List[str]:
        """Extract alphanumeric tokens and hyphenated terms"""
        normalized = self.normalize(text)
        return self.token_pattern.findall(normalized)

    def preprocess(self, text: str, remove_stops: bool = True, stem: bool = True) -> List[str]:
        """Complete NLP preprocessing pipeline: normalize -> tokenize -> stop-word removal -> stem"""
        tokens = self.tokenize(text)
        processed: List[str] = []
        for token in tokens:
            if remove_stops and token in self.stop_words:
                continue
            if len(token) < 2 and not token.isdigit():
                continue
            if stem and self.use_stemmer:
                token = self.stemmer.stem(token)
            processed.append(token)
        return processed

    def expand_query(self, query: str) -> Tuple[List[str], List[str]]:
        """Expand user query with relevant domain synonyms.
        Returns: (base_tokens, expanded_tokens)"""
        base_tokens = self.preprocess(query, remove_stops=True, stem=True)
        raw_tokens = self.tokenize(query)
        
        expanded_set: Set[str] = set()
        for raw in raw_tokens:
            if raw in QUERY_EXPANSION_MAP:
                for syn in QUERY_EXPANSION_MAP[raw]:
                    stems = self.preprocess(syn, remove_stops=True, stem=True)
                    expanded_set.update(stems)
                    
        # Remove duplicates already in base_tokens
        expanded_tokens = [t for t in expanded_set if t not in base_tokens]
        return base_tokens, expanded_tokens

    def extract_phrases(self, query: str) -> List[str]:
        """Extract quoted phrases from query (e.g. "deep learning")"""
        matches = re.findall(r'"([^"]*)"', query)
        return [m.strip().lower() for m in matches if len(m.strip()) > 0]
