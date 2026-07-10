-- Peer validation: students generate verification; admins audit.
-- A validation row is the ONLY student path to Verified (guard_node_write
-- still blocks direct verification writes by non-admins).
CREATE TABLE IF NOT EXISTS validations (
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    validator UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    checklist JSONB NOT NULL,
    confidence INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 10),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (node_id, validator),
    CONSTRAINT checklist_keys_present CHECK (
        checklist ? 'source_checked'
        AND checklist ? 'not_duplicate'
        AND checklist ? 'signal_logic'
        AND checklist ? 'classification_justified'
    )
);

CREATE INDEX IF NOT EXISTS validations_validator_idx ON validations(validator, created_at);

ALTER TABLE validations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS validations_admin_all ON validations;
CREATE POLICY validations_admin_all ON validations
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

DROP POLICY IF EXISTS validations_student_read_term ON validations;
CREATE POLICY validations_student_read_term ON validations
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM nodes
            WHERE nodes.id = validations.node_id
              AND nodes.term_id = public.current_user_term_id()
        )
    );

-- Peer-only: validator is the caller, node is a classmate's Raw signal in-term.
DROP POLICY IF EXISTS validations_student_insert_peer ON validations;
CREATE POLICY validations_student_insert_peer ON validations
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND validator = auth.uid()
        AND EXISTS (
            SELECT 1 FROM nodes
            WHERE nodes.id = validations.node_id
              AND nodes.term_id = public.current_user_term_id()
              AND nodes.created_by <> auth.uid()
              AND nodes.verification = 'Raw'
        )
    );

CREATE OR REPLACE FUNCTION public.apply_validation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    PERFORM set_config('foresight.apply_validation_trigger', 'true', false);
    UPDATE public.nodes
    SET verification = 'Verified'
    WHERE id = NEW.node_id AND verification = 'Raw';
    PERFORM set_config('foresight.apply_validation_trigger', 'false', false);
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS apply_validation_on_insert ON validations;
CREATE TRIGGER apply_validation_on_insert
    AFTER INSERT ON validations
    FOR EACH ROW EXECUTE FUNCTION public.apply_validation();

-- Instructor correction note: admin-writable, term-visible.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS instructor_note TEXT;

-- Extend the node write guard to protect instructor_note.
-- Copy the existing function body from 20260707100002_verification_status.sql
-- and add to the UPDATE-branch check:
--    OR NEW.instructor_note IS DISTINCT FROM OLD.instructor_note
CREATE OR REPLACE FUNCTION public.guard_node_write()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    IF public.is_administrator() THEN
        RETURN NEW;
    END IF;

    -- Allow apply_validation trigger to bypass the guard for the specific case
    -- of promoting verification from 'Raw' to 'Verified' with no other changes.
    IF current_setting('foresight.apply_validation_trigger', true) = 'true' THEN
        IF NEW.verification = 'Verified'::verification_status
           AND OLD.verification = 'Raw'::verification_status
           AND NEW.node_type IS NOT DISTINCT FROM OLD.node_type
           AND NEW.is_keeper IS NOT DISTINCT FROM OLD.is_keeper
           AND NEW.convergence_score IS NOT DISTINCT FROM OLD.convergence_score
           AND NEW.keeper_id IS NOT DISTINCT FROM OLD.keeper_id
           AND NEW.created_by IS NOT DISTINCT FROM OLD.created_by
           AND NEW.term_id IS NOT DISTINCT FROM OLD.term_id
           AND NEW.assessed_at IS NOT DISTINCT FROM OLD.assessed_at
           AND NEW.assessed_by IS NOT DISTINCT FROM OLD.assessed_by
           AND NEW.instructor_note IS NOT DISTINCT FROM OLD.instructor_note THEN
            RETURN NEW;
        END IF;
    END IF;

    IF TG_OP = 'INSERT' THEN
        IF NEW.node_type = 'Trend' THEN
            RAISE EXCEPTION 'Not authorized to create Trend nodes';
        END IF;
        IF NEW.verification IS DISTINCT FROM 'Raw'::verification_status THEN
            RAISE EXCEPTION 'Not authorized to create pre-verified nodes';
        END IF;
        IF NEW.assessed_at IS NOT NULL OR NEW.assessed_by IS NOT NULL THEN
            RAISE EXCEPTION 'Not authorized to set assessment provenance';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.node_type IS DISTINCT FROM OLD.node_type
       OR NEW.verification IS DISTINCT FROM OLD.verification
       OR NEW.is_keeper IS DISTINCT FROM OLD.is_keeper
       OR NEW.convergence_score IS DISTINCT FROM OLD.convergence_score
       OR NEW.keeper_id IS DISTINCT FROM OLD.keeper_id
       OR NEW.created_by IS DISTINCT FROM OLD.created_by
       OR NEW.term_id IS DISTINCT FROM OLD.term_id
       OR NEW.assessed_at IS DISTINCT FROM OLD.assessed_at
       OR NEW.assessed_by IS DISTINCT FROM OLD.assessed_by
       OR NEW.instructor_note IS DISTINCT FROM OLD.instructor_note THEN
        RAISE EXCEPTION 'Not authorized to modify verification or attribution fields';
    END IF;

    RETURN NEW;
END;
$$;

GRANT SELECT, INSERT ON validations TO authenticated;
