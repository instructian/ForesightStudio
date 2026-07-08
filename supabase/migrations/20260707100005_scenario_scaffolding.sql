-- 2x2 scenario planning scaffolding: a scenario_set is one 2x2 matrix built
-- on two critical-uncertainty axes (trend/signal nodes); each set holds four
-- quadrant scenarios; scenario_nodes ties evidence, drivers, wildcards, and
-- Shadow risks into each scenario narrative.
DO $$
BEGIN
    CREATE TYPE scenario_quadrant AS ENUM ('High-High', 'High-Low', 'Low-High', 'Low-Low');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE scenario_node_role AS ENUM ('Driver', 'Evidence', 'Wildcard', 'Shadow-Risk', 'Implication');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS scenario_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    axis_x_node_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    axis_y_node_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    axis_x_low_label VARCHAR(255),
    axis_x_high_label VARCHAR(255),
    axis_y_low_label VARCHAR(255),
    axis_y_high_label VARCHAR(255),
    horizon_year INTEGER CHECK (horizon_year IS NULL OR horizon_year BETWEEN 2020 AND 2200),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_published BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT distinct_axes CHECK (
        axis_x_node_id IS NULL OR axis_y_node_id IS NULL OR axis_x_node_id <> axis_y_node_id
    )
);

CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_set_id UUID REFERENCES scenario_sets(id) ON DELETE CASCADE NOT NULL,
    quadrant scenario_quadrant NOT NULL,
    title VARCHAR(255) NOT NULL,
    narrative TEXT,
    early_warning_indicators TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (scenario_set_id, quadrant)
);

CREATE TABLE IF NOT EXISTS scenario_nodes (
    scenario_id UUID REFERENCES scenarios(id) ON DELETE CASCADE,
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    role scenario_node_role DEFAULT 'Evidence'::scenario_node_role NOT NULL,
    notes TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (scenario_id, node_id, role)
);

CREATE INDEX IF NOT EXISTS scenario_sets_term_id_idx ON scenario_sets(term_id);
CREATE INDEX IF NOT EXISTS scenarios_set_id_idx ON scenarios(scenario_set_id);
CREATE INDEX IF NOT EXISTS scenario_nodes_node_id_idx ON scenario_nodes(node_id);

DROP TRIGGER IF EXISTS set_scenario_sets_updated_at ON scenario_sets;
CREATE TRIGGER set_scenario_sets_updated_at
    BEFORE UPDATE ON scenario_sets
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_scenarios_updated_at ON scenarios;
CREATE TRIGGER set_scenarios_updated_at
    BEFORE UPDATE ON scenarios
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
