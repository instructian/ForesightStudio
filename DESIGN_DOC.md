# System Design Document: Foresight Studio Pipeline Engine

**Date:** July 6, 2026  
**Status:** Approved  
**Version:** 2.0  
**Target Architecture:** Python 3.12 (Local/CLI), Supabase PostgreSQL 16 (Hosted/SaaS)

---

## 1. System Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                     Foresight Studio Engine                                     |
|                                                                                                 |
|   +---------------------+        +-------------------------+        +-----------------------+   |
|   |   1. Ingestion CLI  | -----> | 2. Multi-Model Assess   | -----> | 3. Semantic Dedupl.   |   |
|   |  - JSON/CSV reader  |        |  - Gemini API (Model)   |        |  - SentenceTransformer|   |
|   |  - RSS Feed parser  |        |  - Heuristic (Fallback) |        |  - TF-IDF (Fallback)  |   |
|   +---------------------+        +-------------------------+        +-----------------------+   |
|                                                                                 |               |
|                                                                                 v               |
|   +---------------------+        +-------------------------+        +-----------------------+   |
|   |  5. Output / Radar  | <----- | 4. Supabase SaaS DB     | <----- |   Medoid Clustering   |   |
|   |  - Anonymized API   |        |  - Single-table Nodes   |        |  - "Keeper" isolation |   |
|   |  - Polar JSON state |        |  - pgvector embeddings  |        |  - Dup nesting        |   |
|   +---------------------+        +-------------------------+        +-----------------------+   |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Supabase PostgreSQL Schema

To support multi-tenancy, collaborative grading, and robust security, we use Supabase (PostgreSQL 16) with standard RLS gates and type enums.

```sql
-- Enable pgvector for embedding searches
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Enum Definitions
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
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Profiles Table (Auth Synced)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'Student'::user_role NOT NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_approved BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Nodes Table (Unified single-table hierarchy with first-class JSONB provenance metadata)
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
    confidence_score INTEGER DEFAULT 5 CHECK (confidence_score BETWEEN 1 AND 10),
    novelty_score INTEGER DEFAULT 5 CHECK (novelty_score BETWEEN 1 AND 10),
    impact_score INTEGER DEFAULT 5 CHECK (impact_score BETWEEN 1 AND 10),
    convergence_score REAL DEFAULT 1.0,
    strategic_relevance TEXT,
    actionability TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_keeper BOOLEAN DEFAULT TRUE NOT NULL,
    keeper_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    embedding vector(384),
    source_metadata JSONB DEFAULT '[]'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT keeper_not_self CHECK (keeper_id IS NULL OR keeper_id <> id)
);

-- 5. Edges Table (Knowledge Graph Links)
CREATE TABLE IF NOT EXISTS edges (
    source_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    relationship_type edge_type DEFAULT 'Cites'::edge_type NOT NULL,
    strength_score INTEGER CHECK (strength_score BETWEEN 1 AND 10) DEFAULT 5,
    notes TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (source_node_id, target_node_id),
    CONSTRAINT edge_not_self CHECK (source_node_id <> target_node_id)
);
```

---

## 3. Row-Level Security (RLS) & Column-Level Guards

To protect user environments, prevent client-side privilege escalation, and lock verification integrity, the following triggers and policies are enforced:

### 3.1 Profile Self-Update Guard
Non-admin users are strictly blocked from editing their own `role`, `is_approved`, or `term_id` assignments:
```sql
CREATE OR REPLACE FUNCTION public.guard_profile_self_update()
RETURNS trigger AS $$
BEGIN
    IF public.is_administrator() THEN
        RETURN NEW;
    END IF;

    IF NEW.role IS DISTINCT FROM OLD.role
       OR NEW.is_approved IS DISTINCT FROM OLD.is_approved
       OR NEW.term_id IS DISTINCT FROM OLD.term_id THEN
        RAISE EXCEPTION 'Not authorized to modify role, approval status, or term assignment';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3.2 Node Integrity & Self-Verification Guard
Students and subscribers cannot self-verify weak signals into `Signal` or `Trend` nodes, nor modify attribution metadata (such as `is_keeper`, `keeper_id`, or `convergence_score`), which are computed exclusively by the deduplication engine and administrators:
```sql
CREATE OR REPLACE FUNCTION public.guard_node_write()
RETURNS trigger AS $$
BEGIN
    IF public.is_administrator() THEN
        RETURN NEW;
    END IF;

    IF TG_OP = 'INSERT' THEN
        IF NEW.node_type IN ('Signal', 'Trend') THEN
            RAISE EXCEPTION 'Not authorized to create verified % nodes', NEW.node_type;
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.node_type IS DISTINCT FROM OLD.node_type
       OR NEW.is_keeper IS DISTINCT FROM OLD.is_keeper
       OR NEW.convergence_score IS DISTINCT FROM OLD.convergence_score
       OR NEW.keeper_id IS DISTINCT FROM OLD.keeper_id
       OR NEW.created_by IS DISTINCT FROM OLD.created_by
       OR NEW.term_id IS DISTINCT FROM OLD.term_id THEN
        RAISE EXCEPTION 'Not authorized to modify verification or attribution fields';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3.3 Same-Term Edge Consistency Guard
Edges cannot connect nodes across different academic terms, and an edge's own `term_id` (when set) must match the endpoint nodes' terms:
```sql
CREATE OR REPLACE FUNCTION public.guard_edge_term_consistency()
RETURNS trigger AS $$
DECLARE
    source_term UUID;
    target_term UUID;
BEGIN
    SELECT term_id INTO source_term FROM public.nodes WHERE id = NEW.source_node_id;
    SELECT term_id INTO target_term FROM public.nodes WHERE id = NEW.target_node_id;

    IF source_term IS DISTINCT FROM target_term THEN
        RAISE EXCEPTION 'Edge endpoints must belong to the same term';
    END IF;

    IF NEW.term_id IS NOT NULL AND NEW.term_id IS DISTINCT FROM source_term THEN
        RAISE EXCEPTION 'Edge term_id must match its endpoint nodes'' term';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 4. Algorithmic Functions

### 4.1 Obsidian-Style Related Nodes Query
Surfaces semantically similar nodes inside the database instantly using `pgvector` cosine distance `<=>`. It runs as a `SECURITY INVOKER` function to ensure results are restricted by the caller's active RLS boundaries, preventing tenant leakage:
```sql
CREATE OR REPLACE FUNCTION surface_related_nodes(
    target_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id UUID,
    title VARCHAR,
    category steep_category,
    node_type node_type,
    similarity float
)
LANGUAGE plpgsql
SECURITY INVOKER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        nodes.id,
        nodes.title,
        nodes.category,
        nodes.node_type,
        (1.0 - (nodes.embedding <=> target_embedding))::float AS similarity
    FROM nodes
    WHERE nodes.embedding IS NOT NULL
      AND (1.0 - (nodes.embedding <=> target_embedding)) > match_threshold
    ORDER BY nodes.embedding <=> target_embedding ASC
    LIMIT match_count;
END;
$$;
```

### 4.2 Deduplication Medoid Clustering Formulation
Within each similarity cluster $C$ derived from dense embeddings or fallback TF-IDF overlap matrix values:
$$k = \arg\max_{i \in C} \frac{1}{|C|} \sum_{j \in C} S_{i,j}$$
*   The isolated medoid is elevated to `node_type = 'Signal'` (`is_keeper = true`).
*   Duplicate observations remain as `node_type = 'Shadow'` with `keeper_id` remapped to the medoid.
*   The Keeper's convergence score scales logarithmically for rendering:
    $$G = \log(1.0 + (1.0 + \alpha \cdot (|C| - 1)))$$
*   Provenance histories are packed natively into the Keeper node's first-class JSONB `source_metadata` column to enforce Design Justice.
