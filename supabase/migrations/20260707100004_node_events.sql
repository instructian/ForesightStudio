-- Append-only history so signal evolution (strengthening, decay,
-- verification, reclassification) can be plotted over time.
CREATE TABLE IF NOT EXISTS node_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    actor UUID,
    payload JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS node_events_node_id_idx ON node_events(node_id, created_at);

ALTER TABLE node_events ENABLE ROW LEVEL SECURITY;

-- Clients may only read events for nodes they can already see; writes happen
-- exclusively via the SECURITY DEFINER trigger below (no write policies).
DROP POLICY IF EXISTS node_events_admin_read ON node_events;
CREATE POLICY node_events_admin_read ON node_events
    FOR SELECT TO authenticated
    USING (public.is_administrator());

DROP POLICY IF EXISTS node_events_student_read_term ON node_events;
CREATE POLICY node_events_student_read_term ON node_events
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM nodes
            WHERE nodes.id = node_events.node_id
              AND nodes.term_id = public.current_user_term_id()
        )
    );

CREATE OR REPLACE FUNCTION public.log_node_event()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    changes JSONB := '{}'::jsonb;
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.node_events (node_id, event_type, actor, payload)
        VALUES (NEW.id, 'created', auth.uid(), jsonb_build_object(
            'node_type', NEW.node_type, 'polarity', NEW.polarity,
            'verification', NEW.verification));
        RETURN NEW;
    END IF;

    IF NEW.impact_score IS DISTINCT FROM OLD.impact_score THEN
        changes := changes || jsonb_build_object('impact_score',
            jsonb_build_object('old', OLD.impact_score, 'new', NEW.impact_score));
    END IF;
    IF NEW.uncertainty_score IS DISTINCT FROM OLD.uncertainty_score THEN
        changes := changes || jsonb_build_object('uncertainty_score',
            jsonb_build_object('old', OLD.uncertainty_score, 'new', NEW.uncertainty_score));
    END IF;
    IF NEW.convergence_score IS DISTINCT FROM OLD.convergence_score THEN
        changes := changes || jsonb_build_object('convergence_score',
            jsonb_build_object('old', OLD.convergence_score, 'new', NEW.convergence_score));
    END IF;
    IF NEW.verification IS DISTINCT FROM OLD.verification THEN
        changes := changes || jsonb_build_object('verification',
            jsonb_build_object('old', OLD.verification, 'new', NEW.verification));
    END IF;
    IF NEW.polarity IS DISTINCT FROM OLD.polarity THEN
        changes := changes || jsonb_build_object('polarity',
            jsonb_build_object('old', OLD.polarity, 'new', NEW.polarity));
    END IF;

    IF changes <> '{}'::jsonb THEN
        INSERT INTO public.node_events (node_id, event_type, actor, payload)
        VALUES (NEW.id, 'updated', auth.uid(), changes);
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS log_node_events ON nodes;
CREATE TRIGGER log_node_events
    AFTER INSERT OR UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION public.log_node_event();
