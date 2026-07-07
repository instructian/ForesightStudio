# Foresight Studio: Collaborative SaaS Platform Design

**Date:** July 6, 2026  
**Status:** Validated & Approved  
**Version:** 2.0  
**Authors:** Gemini CLI Architect + Ian Pollock  

---

## 1. System Architecture

Foresight Studio is transitioning from a single-user CLI tool to a headless, multi-tenant strategic foresight SaaS engine hosted on **Supabase (PostgreSQL)**. 

```
               +-------------------------------------------------+
               |                Frontend Layer                   |
               | - Multi-tenant Web Workspace (React / Canvas)  |
               | - Replit / External Scenarios & Futures Wheels |
               +-------------------------------------------------+
                                      |
                         HTTP REST / WebSocket Syncs
                                      |
                                      v
               +-------------------------------------------------+
               |              Supabase Gateway & API             |
               | - Native Auth (JWT Cookies)                     |
               | - Row-Level Security (RLS) Policy Gates         |
               +-------------------------------------------------+
                                      |
                                      v
               +-------------------------------------------------+
               |            PostgreSQL Database (pgvector)       |
               | - Relational Signals, Trends & Shadow Nodes     |
               | - Custom Branching Consequence Edges           |
               | - Secure Administrative, Public, & Class Views  |
               +-------------------------------------------------+
```

### Core Technologies
*   **Database:** PostgreSQL 16+ via Supabase.
*   **Vector Searches:** `pgvector` index extension for storing and performing cosine-similarity searches on 384-dimensional dense vectors.
*   **Authentication:** Supabase Auth (JWT, email, and session cookies).
*   **Client Connection:** Supabase Client SDK (supporting real-time database subscription channels).

---

## 2. Database Schema (PostgreSQL with `pgvector`)

We translate our relational model to Postgres tables. RLS is active across all tables.

### 2.1 Table: `terms`
Manages academic quarters and consultation cycles.
```sql
CREATE TABLE terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL, -- e.g., 'Fall 2026'
    invite_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'FALL2026-CCSD'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

### 2.2 Table: `profiles`
Extends Supabase users with system-specific roles.
```sql
CREATE TYPE user_role AS ENUM ('Administrator', 'Student', 'Subscriber');

CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'Student'::user_role NOT NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_approved BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

### 2.3 Table: `nodes`
Stores Signals, Shadows, Trends, and branching Consequences as first-class, graph-mappable entities.
```sql
CREATE TYPE node_type AS ENUM ('Signal', 'Shadow', 'Trend', 'Consequence-1', 'Consequence-2', 'Consequence-3');
CREATE TYPE steep_category AS ENUM ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal');
CREATE TYPE horizon_type AS ENUM ('Near-term', 'Mid-term', 'Long-term');

CREATE TABLE nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category steep_category NOT NULL,
    time_horizon horizon_type NOT NULL,
    node_type node_type DEFAULT 'Shadow'::node_type NOT NULL,
    
    -- Ingestion metadata
    source_url TEXT,
    source_type VARCHAR(100),
    date_observed DATE,
    geography VARCHAR(255),
    sector VARCHAR(255),
    tags TEXT[],
    
    -- Scoring parameters
    confidence_score INTEGER DEFAULT 5,
    novelty_score INTEGER DEFAULT 5,
    impact_score INTEGER DEFAULT 5,
    convergence_score REAL DEFAULT 1.0,
    strategic_relevance TEXT,
    actionability TEXT,
    
    -- Attribution & Collaboration
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    
    -- Deduplication fields
    is_keeper BOOLEAN DEFAULT TRUE NOT NULL,
    keeper_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    
    -- Vector space coordinates
    embedding vector(384),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

### 2.4 Table: `edges`
Estends Postgres into an Obsidian-style Knowledge Graph, tracing citation, consequence, and composition lines.
```sql
CREATE TYPE edge_type AS ENUM ('Cites', 'Consequence', 'Contradicts', 'Aggregates');

CREATE TABLE edges (
    source_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    relationship_type edge_type DEFAULT 'Cites'::edge_type NOT NULL,
    strength_score INTEGER CHECK (strength_score BETWEEN 1 AND 10) DEFAULT 5,
    notes TEXT,
    PRIMARY KEY (source_node_id, target_node_id)
);
```

---

## 3. Row-Level Security (RLS) Policies

To protect privacy, validate access, and lock enterprise reports behind gates, Row-Level Security is configured at the SQL engine level:

### 3.1 Administrators (Facilitators)
*   **Policy:** Maintain full administrative access.
    ```sql
    CREATE POLICY admin_all ON nodes
        FOR ALL TO authenticated
        USING (EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'Administrator'));
    ```

### 3.2 Students (Contributors)
*   **Policy:** Students can submit and update their own signals, see term-appropriate shadows, and read verified Signals.
    ```sql
    CREATE POLICY student_select ON nodes
        FOR SELECT TO authenticated
        USING (
            -- Student can see any verified keeper
            (is_keeper = true AND node_type = 'Signal') OR
            -- Or any node generated in their current class term
            (term_id = (SELECT term_id FROM profiles WHERE profiles.id = auth.uid() AND profiles.is_approved = true))
        );

    CREATE POLICY student_insert ON nodes
        FOR INSERT TO authenticated
        WITH CHECK (
            -- Student must be approved and inserting for their own active term
            EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.is_approved = true AND profiles.term_id = nodes.term_id)
        );
    ```

### 3.3 Subscribers (Enterprise Viewers)
*   **Policy:** Subscribers have strict Read-Only permission gated only to verified Keeper Signals.
    ```sql
    CREATE POLICY subscriber_select ON nodes
        FOR SELECT TO authenticated
        USING (
            is_keeper = true AND node_type = 'Signal' AND
            EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'Subscriber' AND profiles.is_approved = true)
        );
    ```

---

## 4. API Endpoints (Structural Postgres Views)

To easily integrate external Replit wizards, story scenario widgets, and interactive canvas renderers while controlling data anonymization and privacy:

### 4.1 View: `public_radar_view` (Headless Viewer API)
Exposes fully anonymized radar node coordinates and visual parameters. Strips student names and original provenance logs.
```sql
CREATE OR REPLACE VIEW public_radar_view AS
SELECT 
    id, title, category, time_horizon, impact_score, convergence_score,
    -- Simple projection calculations for client polar charts
    CASE 
        WHEN category = 'Social' THEN 30.0
        WHEN category = 'Technological' THEN 90.0
        WHEN category = 'Economic' THEN 150.0
        WHEN category = 'Environmental' THEN 210.0
        WHEN category = 'Political' THEN 270.0
        WHEN category = 'Legal' THEN 330.0
    END as theta_degrees,
    CASE
        WHEN time_horizon = 'Near-term' THEN 1.0
        WHEN time_horizon = 'Mid-term' THEN 2.0
        WHEN time_horizon = 'Long-term' THEN 3.0
    END as radius,
    (8.0 + (2.0 * impact_score)) as visual_size,
    ln(1.0 + convergence_score) as visual_glow
FROM nodes
WHERE is_keeper = true AND node_type = 'Signal';
```

### 4.2 View: `classroom_signals_view` (Internal Class & Grading API)
Exposes complete data maps, including student IDs, comments, and un-deduplicated shadow data.
```sql
CREATE OR REPLACE VIEW classroom_signals_view AS
SELECT 
    n.*,
    p.full_name as contributor_name,
    t.name as academic_term
FROM nodes n
LEFT JOIN profiles p ON n.created_by = p.id
LEFT JOIN terms t ON n.term_id = t.id;
-- Row level security automatically applies checking requester credentials
```

---

## 5. Algorithmic Functions

### 5.1 Obsidian-Style Related Nodes Query
Surfaces semantically similar nodes inside the database instantly using `pgvector` cosine distance `<=>`:
```sql
CREATE OR REPLACE FUNCTION surface_related_nodes(
    target_embedding vector(384), 
    match_threshold float, 
    match_count int
)
RETURNS TABLE (
    id UUID, title TEXT, category steep_category, 
    node_type node_type, similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nodes.id, nodes.title, nodes.category, nodes.node_type,
        (1.0 - (nodes.embedding <=> target_embedding)) as similarity
    FROM nodes
    WHERE (1.0 - (nodes.embedding <=> target_embedding)) > match_threshold
    ORDER BY nodes.embedding <=> target_embedding ASC
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 6. Implementation & Transition Milestones

To implement this design, we will proceed through three structural milestones:
1.  **Migration Script (Phase 1):** Write a Python schema adapter inside `/src/` that translates current local SQLite data structures into SQL migrations matching the PostgreSQL tables above.
2.  **External Scaffold Ingest (Phase 2):** Adapt `src/cli.py` to support remote Supabase clients, syncing data securely using API tokens.
3.  **Futures Wheel API Hooks (Phase 3):** Expose `/api/v1/public/radar` and local functions to the Replit app to load active signal contexts.
