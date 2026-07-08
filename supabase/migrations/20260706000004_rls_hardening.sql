-- RLS hardening: close privilege-escalation and verification-integrity gaps
-- discovered in schema/RLS audit (see HISTORY.md 2026-07-06 audit entry).
--
-- RLS policies cannot restrict which columns an authenticated user may change,
-- so column-level protection is enforced with BEFORE INSERT/UPDATE triggers.

-- 1. Prevent users from escalating their own role / approval / tenant.
CREATE OR REPLACE FUNCTION public.guard_profile_self_update()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
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
$$;

DROP TRIGGER IF EXISTS guard_profiles_update ON profiles;

CREATE TRIGGER guard_profiles_update
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION public.guard_profile_self_update();

-- 2. Prevent non-admins from self-verifying nodes or rewriting attribution.
--    Verification status (node_type Signal/Trend, is_keeper, convergence_score,
--    keeper_id) is owned by the deduplication pipeline and administrators.
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
$$;

DROP TRIGGER IF EXISTS guard_nodes_write ON nodes;

CREATE TRIGGER guard_nodes_write
    BEFORE INSERT OR UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION public.guard_node_write();

-- 3. Stop self-signup role escalation: profiles are always created as an
--    unapproved Student. Administrators/Subscribers are assigned deliberately
--    by an administrator after signup.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, role, is_approved)
    VALUES (
        new.id,
        COALESCE(NULLIF(new.raw_user_meta_data->>'full_name', ''), split_part(new.email, '@', 1), 'New user'),
        'Student'::user_role,
        false
    )
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

-- 4. Make the semantic recommender respect RLS. As SECURITY INVOKER the
--    embedded SELECT runs with the caller's privileges, so callers cannot see
--    nodes their RLS policies would otherwise hide.
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
SET search_path = public
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

-- 5. Keep updated_at accurate on mutation.
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := timezone('utc'::text, now());
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS set_profiles_updated_at ON profiles;
CREATE TRIGGER set_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_nodes_updated_at ON nodes;
CREATE TRIGGER set_nodes_updated_at
    BEFORE UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 6. Supporting index for provenance / keeper lookups.
CREATE INDEX IF NOT EXISTS nodes_keeper_id_idx ON nodes(keeper_id);
