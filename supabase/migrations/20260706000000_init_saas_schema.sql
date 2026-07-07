CREATE EXTENSION IF NOT EXISTS vector;

DO $$
BEGIN
    CREATE TYPE user_role AS ENUM ('Administrator', 'Student', 'Subscriber');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE node_type AS ENUM ('Signal', 'Shadow', 'Trend', 'Consequence-1', 'Consequence-2', 'Consequence-3');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE steep_category AS ENUM ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE horizon_type AS ENUM ('Near-term', 'Mid-term', 'Long-term');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE edge_type AS ENUM ('Cites', 'Consequence', 'Contradicts', 'Aggregates');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    invite_code VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'Student'::user_role NOT NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_approved BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT keeper_not_self CHECK (keeper_id IS NULL OR keeper_id <> id)
);

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

CREATE INDEX IF NOT EXISTS profiles_term_id_idx ON profiles(term_id);
CREATE INDEX IF NOT EXISTS profiles_role_idx ON profiles(role);
CREATE INDEX IF NOT EXISTS nodes_created_by_idx ON nodes(created_by);
CREATE INDEX IF NOT EXISTS nodes_term_id_idx ON nodes(term_id);
CREATE INDEX IF NOT EXISTS nodes_keeper_idx ON nodes(is_keeper, node_type);
CREATE INDEX IF NOT EXISTS nodes_category_horizon_idx ON nodes(category, time_horizon);
CREATE INDEX IF NOT EXISTS edges_target_node_id_idx ON edges(target_node_id);
CREATE INDEX IF NOT EXISTS edges_term_id_idx ON edges(term_id);
CREATE INDEX IF NOT EXISTS nodes_embedding_idx ON nodes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
