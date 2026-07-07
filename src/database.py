import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure parent directories exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._enable_foreign_keys()
        self._init_schema()

    def _enable_foreign_keys(self):
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()

    def _init_schema(self):
        cursor = self.conn.cursor()
        
        # 1. Signals/Shadows Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT CHECK(category IN ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal')) NOT NULL,
            source_url TEXT,
            source_type TEXT,
            date_observed TEXT,
            geography TEXT,
            sector TEXT,
            tags TEXT,
            confidence_score INTEGER DEFAULT 5,
            novelty_score INTEGER DEFAULT 5,
            impact_score INTEGER DEFAULT 5,
            strategic_relevance TEXT,
            time_horizon TEXT CHECK(time_horizon IN ('Near-term', 'Mid-term', 'Long-term')) NOT NULL,
            actionability TEXT,
            status TEXT CHECK(status IN ('Signal', 'Shadow')) DEFAULT 'Shadow',
            convergence_score REAL DEFAULT 1.0,
            is_keeper INTEGER DEFAULT 1,
            keeper_id TEXT,
            source_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(keeper_id) REFERENCES signals(id) ON DELETE SET NULL
        );
        """)

        # 2. Trends Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trends (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            summary TEXT NOT NULL,
            category TEXT CHECK(category IN ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal')) NOT NULL,
            time_horizon TEXT CHECK(time_horizon IN ('Near-term', 'Mid-term', 'Long-term')) NOT NULL,
            impact_level TEXT CHECK(impact_level IN ('Low', 'Medium', 'High')) NOT NULL,
            uncertainty_level TEXT CHECK(uncertainty_level IN ('Low', 'Medium', 'High')) NOT NULL,
            convergence_score REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Signal Trend Map
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS signal_trend_map (
            signal_id TEXT,
            trend_id TEXT,
            relationship_type TEXT CHECK(relationship_type IN ('Evidence', 'Contradiction', 'Precursor', 'Adjacent')) DEFAULT 'Evidence',
            strength_score INTEGER CHECK(strength_score BETWEEN 1 AND 10) DEFAULT 5,
            notes TEXT,
            PRIMARY KEY (signal_id, trend_id),
            FOREIGN KEY(signal_id) REFERENCES signals(id) ON DELETE CASCADE,
            FOREIGN KEY(trend_id) REFERENCES trends(id) ON DELETE CASCADE
        );
        """)

        self.conn.commit()

    def add_signal(self, signal: Dict[str, Any]) -> str:
        cursor = self.conn.cursor()
        sig_id = signal.get("id") or f"sig_{os.urandom(4).hex()}"
        
        # Format tags to comma-separated if list
        tags = signal.get("tags")
        if isinstance(tags, list):
            tags_str = ",".join(tags)
        else:
            tags_str = tags or ""

        # Format source_metadata to JSON if dict
        meta = signal.get("source_metadata")
        meta_str = json.dumps(meta) if isinstance(meta, (dict, list)) else (meta or "[]")

        cursor.execute("""
        INSERT OR REPLACE INTO signals (
            id, title, description, category, source_url, source_type, date_observed,
            geography, sector, tags, confidence_score, novelty_score, impact_score,
            strategic_relevance, time_horizon, actionability, status, convergence_score,
            is_keeper, keeper_id, source_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sig_id,
            signal["title"],
            signal["description"],
            signal["category"],
            signal.get("source_url"),
            signal.get("source_type"),
            signal.get("date_observed"),
            signal.get("geography"),
            signal.get("sector"),
            tags_str,
            signal.get("confidence_score", 5),
            signal.get("novelty_score", 5),
            signal.get("impact_score", 5),
            signal.get("strategic_relevance"),
            signal["time_horizon"],
            signal.get("actionability"),
            signal.get("status", "Shadow"),
            signal.get("convergence_score", 1.0),
            signal.get("is_keeper", 1),
            signal.get("keeper_id"),
            meta_str
        ))
        self.conn.commit()
        return sig_id

    def update_signal_deduplication_status(self, sig_id: str, is_keeper: bool, keeper_id: Optional[str], convergence_score: float, status: str, source_metadata: List[Dict[str, Any]]):
        cursor = self.conn.cursor()
        meta_str = json.dumps(source_metadata)
        cursor.execute("""
        UPDATE signals
        SET is_keeper = ?, keeper_id = ?, convergence_score = ?, status = ?, source_metadata = ?
        WHERE id = ?
        """, (1 if is_keeper else 0, keeper_id, convergence_score, status, meta_str, sig_id))
        self.conn.commit()

    def get_signal(self, sig_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM signals WHERE id = ?", (sig_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["source_metadata"] = json.loads(res["source_metadata"] or "[]")
        return res

    def get_all_signals(self, filter_keeper: Optional[bool] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM signals"
        params = []
        conditions = []
        
        if filter_keeper is not None:
            conditions.append("is_keeper = ?")
            params.append(1 if filter_keeper else 0)
        
        if status is not None:
            conditions.append("status = ?")
            params.append(status)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        res = []
        for r in rows:
            d = dict(r)
            d["source_metadata"] = json.loads(d["source_metadata"] or "[]")
            res.append(d)
        return res

    def add_trend(self, trend: Dict[str, Any]) -> str:
        cursor = self.conn.cursor()
        trend_id = trend.get("id") or f"trend_{os.urandom(4).hex()}"
        cursor.execute("""
        INSERT OR REPLACE INTO trends (
            id, name, summary, category, time_horizon, impact_level, uncertainty_level, convergence_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trend_id,
            trend["name"],
            trend["summary"],
            trend["category"],
            trend["time_horizon"],
            trend["impact_level"],
            trend["uncertainty_level"],
            trend.get("convergence_score", 1.0)
        ))
        self.conn.commit()
        return trend_id

    def get_trend(self, trend_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trends WHERE id = ?", (trend_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def map_signal_to_trend(self, signal_id: str, trend_id: str, relationship_type: str = "Evidence", strength_score: int = 5, notes: str = ""):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO signal_trend_map (
            signal_id, trend_id, relationship_type, strength_score, notes
        ) VALUES (?, ?, ?, ?, ?)
        """, (signal_id, trend_id, relationship_type, strength_score, notes))
        self.conn.commit()

    def get_trend_signals(self, trend_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT s.*, m.relationship_type, m.strength_score, m.notes as relationship_notes
        FROM signals s
        JOIN signal_trend_map m ON s.id = m.signal_id
        WHERE m.trend_id = ?
        """, (trend_id,))
        rows = cursor.fetchall()
        res = []
        for r in rows:
            d = dict(r)
            d["source_metadata"] = json.loads(d["source_metadata"] or "[]")
            res.append(d)
        return res

    def close(self):
        self.conn.close()
