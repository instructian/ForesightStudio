# Foresight Studio: Supabase SaaS Migration & RLS Trigger Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish a complete, production-grade hosted multi-tenant SaaS architecture on Supabase (PostgreSQL) with a Python database schema adapter, Row-Level Security (RLS) authentication profiles, custom Postgres related-node queries, and testing frameworks.

**Architecture:**
*   **Hosted Core:** Transpose relational SQLite tables to Supabase tables (`terms`, `profiles`, `nodes`, `edges`) with type enums.
*   **Identity Layer:** Map Supabase Auth accounts to profiles with User Roles (`Administrator`, `Student`, `Subscriber`) using a Postgres trigger `on_auth_user_created`.
*   **Security Gating:** Protect records by writing Row-Level Security (RLS) rules verifying approval states and terms rosters.
*   **Migration Script:** Construct a Python schema adapter `src/migration_adapter.py` utilizing the Supabase Python SDK and local FallbackTFIDF/HuggingFace embeddings to populate the remote database.

**Tech Stack:** Supabase (PostgreSQL 16, pgvector), Python 3.12, Supabase-py SDK, unittest.

---

### Task 1: Supabase Database Migration Schema & Setup

**Files:**
- Create: `supabase/migrations/20260706000000_init_saas_schema.sql`
- Test: `tests/test_saas_schema.py`

**Step 1: Write the Postgres Migration script**

Write SQL declarations enabling `pgvector` and installing tables/enums:

```sql
-- Enable the pgvector extension to work with dense embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Create Enums
CREATE TYPE user_role AS ENUM ('Administrator', 'Student', 'Subscriber');
CREATE TYPE node_type AS ENUM ('Signal', 'Shadow', 'Trend', 'Consequence-1', 'Consequence-2', 'Consequence-3');
CREATE TYPE steep_category AS ENUM ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal');
CREATE TYPE horizon_type AS ENUM ('Near-term', 'Mid-term', 'Long-term');
CREATE TYPE edge_type AS ENUM ('Cites', 'Consequence', 'Contradicts', 'Aggregates');

-- 2. Terms Table
CREATE TABLE IF NOT EXISTS terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    invite_code VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'Student'::user_role NOT NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_approved BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Nodes Table (pgvector embedding mapped to 384-dimensions)
CREATE TABLE IF NOT EXISTS nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category steep_category NOT NULL,
    time_horizon horizon_type NOT NULL,
    node_type node_type DEFAULT 'Shadow'::node_type NOT NULL,
    source_url TEXT,
    source_type VARCHAR(100),
    date_observed DATE,
    geography VARCHAR(255),
    sector VARCHAR(255),
    tags TEXT[],
    confidence_score INTEGER DEFAULT 5,
    novelty_score INTEGER DEFAULT 5,
    impact_score INTEGER DEFAULT 5,
    convergence_score REAL DEFAULT 1.0,
    strategic_relevance TEXT,
    actionability TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_keeper BOOLEAN DEFAULT TRUE NOT NULL,
    keeper_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Edges Table
CREATE TABLE IF NOT EXISTS edges (
    source_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    relationship_type edge_type DEFAULT 'Cites'::edge_type NOT NULL,
    strength_score INTEGER CHECK (strength_score BETWEEN 1 AND 10) DEFAULT 5,
    notes TEXT,
    PRIMARY KEY (source_node_id, target_node_id)
);
```

**Step 2: Run test to verify SQL execution syntax locally**
Run: `pg_virtualenv` or local Postgres verification if available.

**Step 3: Commit**
```bash
git add supabase/
git commit -m "feat: establish hosted Supabase Postgres schema migrations"
```

---

### Task 2: Supabase Authentication Profile Sync Triggers

**Files:**
- Create: `supabase/migrations/20260706000001_auth_sync_triggers.sql`

**Step 1: Write SQL Profile Trigger**

Write a database function that automatically populates the `profiles` table when a new user registers in Supabase Auth, mapping their email to initial full_name:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, role, is_approved)
  VALUES (
    new.id,
    COALESCE(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
    COALESCE((new.raw_user_meta_data->>'role')::user_role, 'Student'::user_role),
    -- Auto-approve local workspace admin if needed, others start unapproved
    CASE WHEN new.email LIKE '%@csueastbay.edu' THEN true ELSE false END
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Map trigger to auth.users insertions
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

**Step 2: Verify Trigger Schema matches profiles columns**
Ensure all constraints are met.

**Step 3: Commit**
```bash
git add supabase/
git commit -m "feat: add user registration profile sync triggers"
```

---

### Task 3: Row-Level Security (RLS) Policy Gates

**Files:**
- Create: `supabase/migrations/20260706000002_rls_policies.sql`

**Step 1: Write SQL RLS Policies**

Enable Row-Level Security across all tables and apply strict role gates:

```sql
-- Enable RLS
ALTER TABLE terms ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE edges ENABLE ROW LEVEL SECURITY;

-- 1. Profiles Table Policies
CREATE POLICY "Users can read all profiles" ON profiles
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Users can edit their own profiles" ON profiles
    FOR UPDATE TO authenticated USING (auth.uid() = id);

-- 2. Nodes Table Policies
CREATE POLICY "Admins have full access" ON nodes
    FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'Administrator'));

CREATE POLICY "Students can read verified keepers or term-specific shadows" ON nodes
    FOR SELECT TO authenticated
    USING (
        (is_keeper = true AND node_type = 'Signal') OR
        (term_id = (SELECT term_id FROM profiles WHERE profiles.id = auth.uid() AND profiles.is_approved = true))
    );

CREATE POLICY "Students can submit signals for their own approved terms" ON nodes
    FOR INSERT TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
              AND profiles.is_approved = true 
              AND profiles.term_id = nodes.term_id
        )
    );
```

**Step 2: Commit**
```bash
git add supabase/
git commit -m "feat: configure Postgres Row-Level Security policies"
```

---

### Task 4: Postgres pgvector Semantic Recommender Function

**Files:**
- Create: `supabase/migrations/20260706000003_semantic_recommender.sql`

**Step 1: Write SQL related node fetcher**

Create the postgres procedural function to perform cosine similarity queries natively on Supabase using `<=>` distance operator:

```sql
CREATE OR REPLACE FUNCTION surface_related_nodes(
    target_embedding vector(384), 
    match_threshold float, 
    match_count int
)
RETURNS TABLE (
    id UUID, title VARCHAR, category steep_category, 
    node_type node_type, similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nodes.id, nodes.title, nodes.category, nodes.node_type,
        (1.0 - (nodes.embedding <=> target_embedding))::float as similarity
    FROM nodes
    WHERE (1.0 - (nodes.embedding <=> target_embedding)) > match_threshold
    ORDER BY nodes.embedding <=> target_embedding ASC
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Step 2: Commit**
```bash
git add supabase/
git commit -m "feat: implement pgvector semantic recommender procedure"
```

---

### Task 5: Database Migration & Schema Adapter Script

**Files:**
- Create: `src/migration_adapter.py`
- Create: `requirements.txt` (append `supabase>=2.0.0`)
- Test: `tests/test_migration_adapter.py`

**Step 1: Write a failing Python adapter test**

Verify adapter can open SQLite records, tokenize text, retrieve/calculate mock 384 embeddings, and format Supabase inserts.

**Step 2: Implement Python Migration Adapter**

Use standard python vector computation (with `FallbackTFIDF` as vector size loader, or lightweight padding up to 384 dimensions to guarantee schema conformity if HuggingFace isn't running) to write the migration script:

```python
import sqlite3
import os
from supabase import create_client, Client
from src.deduplication import FallbackTFIDF

class MigrationAdapter:
    def __init__(self, sqlite_path: str, supabase_url: str, supabase_key: str):
        self.sqlite_path = sqlite_path
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.tfidf = FallbackTFIDF()

    def generate_embedding_placeholder(self, text: str) -> list:
        # Generate clean 384 dimensions dense vector
        # Compute dynamic tokens hash and pad with zeroes to meet pgvector(384) requirements
        words = self.tfidf._tokenize(text)
        vector = [0.0] * 384
        for idx, word in enumerate(words[:384]):
            # Simple deterministic hashing to fill float dimensions
            vector[idx] = float(abs(hash(word)) % 1000) / 1000.0
        return vector

    def migrate_signals(self):
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM signals")
        rows = cursor.fetchall()
        
        migrated = 0
        for r in rows:
            text = f"{r['title']} {r['description']}"
            vector = self.generate_embedding_placeholder(text)
            
            payload = {
                "title": r["title"],
                "description": r["description"],
                "category": r["category"],
                "time_horizon": r["time_horizon"],
                "node_type": "Signal" if r["is_keeper"] == 1 else "Shadow",
                "source_url": r["source_url"],
                "source_type": r["source_type"],
                "impact_score": r["impact_score"],
                "convergence_score": r["convergence_score"],
                "embedding": vector
            }
            # Upload via Supabase REST API
            self.supabase.table("nodes").insert(payload).execute()
            migrated += 1
            
        conn.close()
        return migrated
```

**Step 3: Verify and execute unit tests**
Run: `PYTHONPATH=. python3 -m unittest tests/test_migration_adapter.py`

**Step 4: Commit**
```bash
git add src/migration_adapter.py tests/test_migration_adapter.py requirements.txt
git commit -m "feat: implement sqlite to supabase schema migration adapter"
```
