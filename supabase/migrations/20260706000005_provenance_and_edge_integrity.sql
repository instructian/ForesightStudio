-- Fix #6: first-class provenance column for Design Justice attribution.
-- Fix #10: enforce that an edge connects two nodes in the same term.

-- 6. Provenance / source metadata as first-class JSONB on nodes.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS source_metadata JSONB DEFAULT '[]'::jsonb NOT NULL;

CREATE INDEX IF NOT EXISTS nodes_source_metadata_idx ON nodes USING gin (source_metadata);

-- 10. Edge term consistency: source and target nodes must belong to the same
--     term, and the edge's own term_id (when set) must match. Runs as a
--     BEFORE INSERT/UPDATE trigger since CHECK constraints cannot subquery.
CREATE OR REPLACE FUNCTION public.guard_edge_term_consistency()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
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
$$;

DROP TRIGGER IF EXISTS guard_edges_term_consistency ON edges;

CREATE TRIGGER guard_edges_term_consistency
    BEFORE INSERT OR UPDATE ON edges
    FOR EACH ROW EXECUTE FUNCTION public.guard_edge_term_consistency();
