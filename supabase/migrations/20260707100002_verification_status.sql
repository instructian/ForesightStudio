-- Decouple verification state from node structure. Historically
-- node_type='Shadow' meant "raw/unverified", colliding with the product
-- meaning of Shadow (decline-polarity signal, see 20260707100001).
-- After this migration node_type='Shadow' is retired (enum value remains,
-- Postgres cannot drop it — never write it again).
DO $$
BEGIN
    CREATE TYPE verification_status AS ENUM ('Raw', 'Verified', 'Archived');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE nodes ADD COLUMN IF NOT EXISTS verification verification_status;

UPDATE nodes SET verification =
    CASE WHEN node_type = 'Signal' AND is_keeper THEN 'Verified'::verification_status
         ELSE 'Raw'::verification_status END
WHERE verification IS NULL;

-- Old-world "Shadow" rows were raw scanning points, not decline signals:
-- restore their structural type and leave polarity as-is (default Emergent;
-- curators reclassify true decline signals via polarity).
UPDATE nodes SET node_type = 'Signal' WHERE node_type = 'Shadow';

ALTER TABLE nodes ALTER COLUMN verification SET DEFAULT 'Raw'::verification_status;
ALTER TABLE nodes ALTER COLUMN verification SET NOT NULL;

CREATE INDEX IF NOT EXISTS nodes_verification_idx ON nodes(verification, is_keeper);

-- Recreate read policies on verification instead of node_type.
DROP POLICY IF EXISTS nodes_subscriber_read_verified_signals ON nodes;
CREATE POLICY nodes_subscriber_read_verified_signals ON nodes
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND is_keeper = true
        AND verification = 'Verified'
    );

DROP POLICY IF EXISTS nodes_student_read_term_or_verified_signals ON nodes;
CREATE POLICY nodes_student_read_term_or_verified_signals ON nodes
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND (
            (is_keeper = true AND verification = 'Verified')
            OR term_id = public.current_user_term_id()
        )
    );

-- Close the post-verification content-mutation hole: students may no longer
-- edit nodes once they are Verified.
DROP POLICY IF EXISTS nodes_student_update_own_term ON nodes;
CREATE POLICY nodes_student_update_own_term ON nodes
    FOR UPDATE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND verification <> 'Verified'
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND verification <> 'Verified'
    );

-- Extend the write guard: verification and assessment provenance are owned
-- by the pipeline/administrators.
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
       OR NEW.assessed_by IS DISTINCT FROM OLD.assessed_by THEN
        RAISE EXCEPTION 'Not authorized to modify verification or attribution fields';
    END IF;

    RETURN NEW;
END;
$$;
