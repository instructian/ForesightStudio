-- Scenario planning needs impact x uncertainty; the schema previously had no
-- uncertainty dimension on nodes (it was lost when SQLite trends were folded
-- into the unified nodes table). NULL means "not yet assessed" — deliberately
-- no DEFAULT so unassessed nodes cannot contaminate analytics.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS uncertainty_score INTEGER;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS nodes_uncertainty_score_range;
ALTER TABLE nodes ADD CONSTRAINT nodes_uncertainty_score_range
    CHECK (uncertainty_score IS NULL OR uncertainty_score BETWEEN 1 AND 10);

-- Relative horizons (Near/Mid/Long) decay in meaning over time; anchor with
-- an estimated calendar year.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS horizon_year INTEGER;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS nodes_horizon_year_range;
ALTER TABLE nodes ADD CONSTRAINT nodes_horizon_year_range
    CHECK (horizon_year IS NULL OR horizon_year BETWEEN 2020 AND 2200);

-- Assessment provenance: distinguishes pipeline-scored from self-scored nodes.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS assessed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS assessed_by VARCHAR(100);
