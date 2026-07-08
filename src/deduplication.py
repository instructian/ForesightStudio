import json
import math
import re
import collections
from typing import List, Dict, Any, Tuple, Optional

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class FallbackTFIDF:
    """
    A pure Python TF-IDF Vectorizer & Cosine Similarity engine to act as
    a zero-dependency fallback when sentence-transformers is not installed.
    """
    def __init__(self, stop_words: Optional[set] = None):
        self.stop_words = stop_words or {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "be", "been", "of", "to", "for", "in", "on", "at", "by", "with",
            "this", "that", "these", "those", "it", "its", "as", "from"
        }

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, strip punctuation, and split on whitespace
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        tokens = cleaned.split()
        return [t for t in tokens if t not in self.stop_words]

    def compute_similarity_matrix(self, documents: List[str]) -> List[List[float]]:
        num_docs = len(documents)
        if num_docs == 0:
            return []

        # 1. Tokenize all documents and build vocabulary
        tokenized_docs = [self._tokenize(doc) for doc in documents]
        vocab = sorted(list(set(term for doc in tokenized_docs for term in doc)))
        vocab_index = {term: idx for idx, term in enumerate(vocab)}

        # 2. Compute Document Frequency (DF) for IDF
        df = collections.defaultdict(int)
        for doc in tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1

        # 3. Compute IDF
        idf = {}
        for term, count in df.items():
            idf[term] = math.log((1.0 + num_docs) / (1.0 + count)) + 1.0

        # 4. Generate TF-IDF vectors
        vectors = []
        for doc in tokenized_docs:
            vector = [0.0] * len(vocab)
            tf = collections.Counter(doc)
            for term, count in tf.items():
                if term in vocab_index:
                    idx = vocab_index[term]
                    vector[idx] = count * idf[term]
            # L2 Normalize the vector
            norm = math.sqrt(sum(val ** 2 for val in vector))
            if norm > 0:
                vector = [val / norm for val in vector]
            vectors.append(vector)

        # 5. Compute pairwise cosine similarity matrix
        matrix = [[0.0] * num_docs for _ in range(num_docs)]
        for i in range(num_docs):
            matrix[i][i] = 1.0
            for j in range(i + 1, num_docs):
                # Cosine similarity of normalized vectors is simply their dot product
                sim = sum(vectors[i][k] * vectors[j][k] for k in range(len(vocab)))
                matrix[i][j] = sim
                matrix[j][i] = sim

        return matrix


class DeduplicationEngine:
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold
        self.model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Lazy-load transformer model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Failed to load sentence-transformers model: {e}. Using TF-IDF fallback.")
                self.model = None

    def compute_similarity(self, titles_and_descriptions: List[str]) -> List[List[float]]:
        if not titles_and_descriptions:
            return []

        if HAS_SENTENCE_TRANSFORMERS and self.model is not None:
            # 1. Dense embeddings similarity
            embeddings = self.model.encode(titles_and_descriptions, convert_to_numpy=True)
            # L2 Normalize
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normalized_embeddings = np.where(norms > 0, embeddings / norms, 0.0)
            # Matrix multiplication gives cosine similarities
            similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
            return similarity_matrix.tolist()
        else:
            # 2. Heuristic TF-IDF similarity
            fallback = FallbackTFIDF()
            return fallback.compute_similarity_matrix(titles_and_descriptions)

    def cluster_signals(self, signals: List[Dict[str, Any]]) -> List[List[int]]:
        """
        Group indices of signals that are semantically similar.
        Returns a list of clusters, where each cluster is a list of signal indices.
        """
        if not signals:
            return []

        texts = [f"{s['title']}\n{s['description']}" for s in signals]
        matrix = self.compute_similarity(texts)
        num_signals = len(signals)

        # Simple single-linkage / connected-components clustering based on similarity threshold
        visited = set()
        clusters = []

        for idx in range(num_signals):
            if idx in visited:
                continue

            # BFS/DFS to find all connected signals
            cluster = []
            queue = [idx]
            while queue:
                curr = queue.pop(0)
                if curr in visited:
                    continue
                visited.add(curr)
                cluster.append(curr)

                # Scan for neighbors matching threshold
                for other in range(num_signals):
                    if other not in visited and matrix[curr][other] >= self.threshold:
                        queue.append(other)

            clusters.append(cluster)

        return clusters

    def deduplicate_database(self, db) -> Tuple[int, int]:
        """
        Runs deduplication on all signals in the database.
        Finds clusters, isolates medoids as Keepers, marks duplicates, and updates database.
        Returns (num_keepers_updated, num_duplicates_updated)
        """
        # Load all signals from DB (both shadows and verified signals)
        signals = db.get_all_signals()
        if not signals:
            return 0, 0

        clusters = self.cluster_signals(signals)
        texts = [f"{s['title']}\n{s['description']}" for s in signals]
        matrix = self.compute_similarity(texts)

        keepers_count = 0
        duplicates_count = 0

        for cluster in clusters:
            if len(cluster) == 1:
                # Singleton: keeper of itself, but an uncorroborated observation
                # is NOT verified — it stays a Shadow-status research point, and
                # its existing provenance is preserved untouched.
                idx = cluster[0]
                sig = signals[idx]
                db.update_signal_deduplication_status(
                    sig_id=sig["id"],
                    is_keeper=True,
                    keeper_id=None,
                    convergence_score=1.0,
                    status=sig.get("status") or "Shadow",
                    source_metadata=sig.get("source_metadata") or []
                )
                keepers_count += 1
                continue

            # Multi-node cluster: Select medoid as the central Keeper
            medoid_idx = -1
            max_avg_sim = -1.0

            for i in cluster:
                # Compute average similarity to all other members in the cluster
                total_sim = sum(matrix[i][j] for j in cluster)
                avg_sim = total_sim / len(cluster)
                if avg_sim > max_avg_sim:
                    max_avg_sim = avg_sim
                    medoid_idx = i

            keeper_sig = signals[medoid_idx]
            duplicate_indices = [idx for idx in cluster if idx != medoid_idx]

            # Merge, never erase: keeper keeps its own prior provenance plus a
            # snapshot of each duplicate (including the duplicate's provenance).
            # This must be idempotent: running dedup again on an already-merged
            # keeper must not re-append entries that are already present.
            duplicate_ids = {signals[d_idx]["id"] for d_idx in duplicate_indices}

            provenance_metadata: List[Dict[str, Any]] = []
            seen_keys = set()

            def _entry_key(entry: Dict[str, Any]) -> Any:
                # Snapshot dicts are identified by their duplicate id; arbitrary
                # note-style entries are identified by their content.
                if isinstance(entry, dict) and "id" in entry:
                    return ("id", entry["id"])
                return ("json", json.dumps(entry, sort_keys=True))

            def _add_entry(entry: Dict[str, Any]) -> None:
                key = _entry_key(entry)
                if key in seen_keys:
                    return
                seen_keys.add(key)
                provenance_metadata.append(entry)

            # (a) Keeper's own pre-existing entries that did NOT come from a
            # tracked duplicate in this cluster (i.e. not a snapshot dict for
            # one of these duplicate ids).
            for entry in keeper_sig.get("source_metadata") or []:
                if isinstance(entry, dict) and entry.get("id") in duplicate_ids:
                    continue
                _add_entry(entry)

            for d_idx in duplicate_indices:
                d_sig = signals[d_idx]
                # (b) One snapshot dict per duplicate.
                _add_entry({
                    "id": d_sig["id"],
                    "title": d_sig["title"],
                    "description": d_sig["description"],
                    "source_url": d_sig.get("source_url"),
                    "date_observed": d_sig.get("date_observed"),
                    "geography": d_sig.get("geography"),
                    "sector": d_sig.get("sector"),
                })
                # (c) The duplicate's own prior metadata entries, flattened in
                # and de-duplicated.
                for entry in d_sig.get("source_metadata") or []:
                    _add_entry(entry)

            # Calculate dynamic convergence score based on duplicate density
            # Convergence = 1.0 + 0.5 * number of duplicates
            convergence_score = 1.0 + 0.5 * len(duplicate_indices)

            # 1. Update Keeper
            db.update_signal_deduplication_status(
                sig_id=keeper_sig["id"],
                is_keeper=True,
                keeper_id=None,
                convergence_score=convergence_score,
                status="Signal", # Elevate to a verified "Signal"
                source_metadata=provenance_metadata
            )
            keepers_count += 1

            # 2. Update Duplicates pointing to Keeper
            for d_idx in duplicate_indices:
                d_sig = signals[d_idx]
                db.update_signal_deduplication_status(
                    sig_id=d_sig["id"],
                    is_keeper=False,
                    keeper_id=keeper_sig["id"],
                    convergence_score=1.0,
                    status="Shadow", # Remain as supporting Shadow research data
                    source_metadata=d_sig.get("source_metadata") or []
                )
                duplicates_count += 1

        return keepers_count, duplicates_count
