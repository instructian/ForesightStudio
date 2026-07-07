CREATE OR REPLACE FUNCTION public.current_user_role()
RETURNS user_role
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT role FROM public.profiles WHERE id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION public.current_user_term_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT term_id FROM public.profiles WHERE id = auth.uid() AND is_approved = true;
$$;

CREATE OR REPLACE FUNCTION public.current_user_is_approved()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COALESCE((SELECT is_approved FROM public.profiles WHERE id = auth.uid()), false);
$$;

CREATE OR REPLACE FUNCTION public.is_administrator()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COALESCE((SELECT role = 'Administrator'::user_role AND is_approved = true FROM public.profiles WHERE id = auth.uid()), false);
$$;

CREATE OR REPLACE FUNCTION public.is_student()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COALESCE((SELECT role = 'Student'::user_role AND is_approved = true FROM public.profiles WHERE id = auth.uid()), false);
$$;

CREATE OR REPLACE FUNCTION public.is_subscriber()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COALESCE((SELECT role = 'Subscriber'::user_role AND is_approved = true FROM public.profiles WHERE id = auth.uid()), false);
$$;

ALTER TABLE terms ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE edges ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS terms_admin_all ON terms;
DROP POLICY IF EXISTS terms_approved_read_own ON terms;
DROP POLICY IF EXISTS profiles_admin_all ON profiles;
DROP POLICY IF EXISTS profiles_self_read ON profiles;
DROP POLICY IF EXISTS profiles_self_update ON profiles;
DROP POLICY IF EXISTS nodes_admin_all ON nodes;
DROP POLICY IF EXISTS nodes_subscriber_read_verified_signals ON nodes;
DROP POLICY IF EXISTS nodes_student_read_term_or_verified_signals ON nodes;
DROP POLICY IF EXISTS nodes_student_insert_own_term ON nodes;
DROP POLICY IF EXISTS nodes_student_update_own_term ON nodes;
DROP POLICY IF EXISTS edges_admin_all ON edges;
DROP POLICY IF EXISTS edges_subscriber_read_verified_signal_edges ON edges;
DROP POLICY IF EXISTS edges_student_read_term_edges ON edges;
DROP POLICY IF EXISTS edges_student_insert_own_term ON edges;

CREATE POLICY terms_admin_all ON terms
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

CREATE POLICY terms_approved_read_own ON terms
    FOR SELECT TO authenticated
    USING (id = public.current_user_term_id() AND is_active = true);

CREATE POLICY profiles_admin_all ON profiles
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

CREATE POLICY profiles_self_read ON profiles
    FOR SELECT TO authenticated
    USING (auth.uid() = id);

CREATE POLICY profiles_self_update ON profiles
    FOR UPDATE TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY nodes_admin_all ON nodes
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

CREATE POLICY nodes_subscriber_read_verified_signals ON nodes
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND is_keeper = true
        AND node_type = 'Signal'
    );

CREATE POLICY nodes_student_read_term_or_verified_signals ON nodes
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND (
            (is_keeper = true AND node_type = 'Signal')
            OR term_id = public.current_user_term_id()
        )
    );

CREATE POLICY nodes_student_insert_own_term ON nodes
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
    );

CREATE POLICY nodes_student_update_own_term ON nodes
    FOR UPDATE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
    );

CREATE POLICY edges_admin_all ON edges
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

CREATE POLICY edges_subscriber_read_verified_signal_edges ON edges
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND EXISTS (
            SELECT 1
            FROM nodes source_node
            JOIN nodes target_node ON target_node.id = edges.target_node_id
            WHERE source_node.id = edges.source_node_id
              AND source_node.is_keeper = true
              AND source_node.node_type = 'Signal'
              AND target_node.is_keeper = true
              AND target_node.node_type = 'Signal'
        )
    );

CREATE POLICY edges_student_read_term_edges ON edges
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND (
            term_id = public.current_user_term_id()
            OR EXISTS (
                SELECT 1
                FROM nodes source_node
                JOIN nodes target_node ON target_node.id = edges.target_node_id
                WHERE source_node.id = edges.source_node_id
                  AND source_node.is_keeper = true
                  AND source_node.node_type = 'Signal'
                  AND target_node.is_keeper = true
                  AND target_node.node_type = 'Signal'
            )
        )
    );

CREATE POLICY edges_student_insert_own_term ON edges
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
    );
