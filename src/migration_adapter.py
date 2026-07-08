import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional

try:
    from supabase import create_client
except ImportError:
    create_client = None

from src.deduplication import FallbackTFIDF

EMBEDDING_DIMENSIONS = 384

SIGNAL_COLUMNS = [
    "id", "title", "description", "category", "source_url", "source_type",
    "date_observed", "geography", "sector", "tags", "confidence_score",
    "novelty_score", "impact_score", "strategic_relevance", "time_horizon",
    "actionability", "status", "convergence_score", "is_keeper", "keeper_id",
    "source_metadata", "created_at",
]


class MigrationAdapter:
    """Adapt local SQLite ``signals`` rows into Supabase ``nodes`` payloads.

    The adapter never requires a live Supabase connection during tests: pass a
    ``supabase_client`` (real client or mock) to bypass network creation.

    The Supabase ``nodes`` schema has no dedicated provenance column, so the
    deduplication ``source_metadata`` is only serialized into the payload when
    ``node_metadata_field`` names a column the target schema actually supports.
    """

    def __init__(
        self,
        sqlite_path: str,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        supabase_client: Any = None,
        node_metadata_field: Optional[str] = None,
    ):
        self.sqlite_path = sqlite_path
        self.node_metadata_field = node_metadata_field
        self.tfidf = FallbackTFIDF()

        if supabase_client is not None:
            self.supabase = supabase_client
        elif supabase_url and supabase_key:
            if create_client is None:
                raise ImportError("supabase package is required to create a live client")
            self.supabase = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None

    def read_signal_rows(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM signals")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def generate_embedding(self, text: str) -> List[float]:
        vector = [0.0] * EMBEDDING_DIMENSIONS
        words = self.tfidf._tokenize(text or "")
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
            magnitude = int.from_bytes(digest[4:6], "big") / 65535.0
            vector[index] += magnitude
        norm = sum(value * value for value in vector) ** 0.5
        if norm > 0:
            vector = [value / norm for value in vector]
        return vector

    def _format_tags(self, raw_tags: Any) -> List[str]:
        if isinstance(raw_tags, list):
            return [str(tag).strip() for tag in raw_tags if str(tag).strip()]
        if not raw_tags:
            return []
        return [tag.strip() for tag in str(raw_tags).split(",") if tag.strip()]

    def _resolve_node_type(self, row: Dict[str, Any]) -> str:
        if int(row.get("is_keeper", 1) or 0) == 1:
            return "Signal"
        return "Shadow"

    def _resolve_verification(self, row: Dict[str, Any]) -> str:
        if int(row.get("is_keeper", 1) or 0) == 1 and row.get("status") == "Signal":
            return "Verified"
        return "Raw"

    def _parse_provenance(self, row: Dict[str, Any]) -> Any:
        raw = row.get("source_metadata")
        if isinstance(raw, (dict, list)):
            return raw
        if not raw:
            return []
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return []

    def build_node_payload(self, row: Dict[str, Any]) -> Dict[str, Any]:
        text = f"{row.get('title', '')} {row.get('description', '')}".strip()
        payload = {
            "title": row.get("title"),
            "description": row.get("description"),
            "category": row.get("category"),
            "time_horizon": row.get("time_horizon"),
            "node_type": self._resolve_node_type(row),
            "source_url": row.get("source_url"),
            "source_type": row.get("source_type"),
            "date_observed": row.get("date_observed"),
            "geography": row.get("geography"),
            "sector": row.get("sector"),
            "tags": self._format_tags(row.get("tags")),
            "confidence_score": row.get("confidence_score"),
            "novelty_score": row.get("novelty_score"),
            "impact_score": row.get("impact_score"),
            "convergence_score": row.get("convergence_score"),
            "strategic_relevance": row.get("strategic_relevance"),
            "actionability": row.get("actionability"),
            "uncertainty_score": row.get("uncertainty_score"),
            "horizon_year": row.get("horizon_year"),
            "polarity": row.get("polarity") or "Emergent",
            "shadow_type": row.get("shadow_type"),
            "mitigation_notes": row.get("mitigation_notes"),
            "verification": self._resolve_verification(row),
            "is_keeper": int(row.get("is_keeper", 1) or 0) == 1,
            "embedding": self.generate_embedding(text),
            "source_metadata": {
                "source_signal_id": row.get("id"),
                "keeper_id": row.get("keeper_id"),
                "provenance": self._parse_provenance(row),
            },
        }

        if self.node_metadata_field is not None and self.node_metadata_field != "source_metadata":
            payload[self.node_metadata_field] = payload["source_metadata"]

        return payload

    def migrate_signals(self) -> int:
        if self.supabase is None:
            raise RuntimeError("No Supabase client configured for migration")

        rows = self.read_signal_rows()
        migrated = 0
        for row in rows:
            payload = self.build_node_payload(row)
            self.supabase.table("nodes").insert(payload).execute()
            migrated += 1
        return migrated
