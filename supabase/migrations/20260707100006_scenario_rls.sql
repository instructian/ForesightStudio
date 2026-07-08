ALTER TABLE scenario_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_nodes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS scenario_sets_admin_all ON scenario_sets;
CREATE POLICY scenario_sets_admin_all ON scenario_sets
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

-- Legacy single FOR ALL student policy (broken: DELETE and UPDATE row-targeting
-- are governed by USING, which did not enforce ownership or unpublished state).
DROP POLICY IF EXISTS scenario_sets_student_term ON scenario_sets;

DROP POLICY IF EXISTS scenario_sets_student_read ON scenario_sets;
CREATE POLICY scenario_sets_student_read ON scenario_sets
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND term_id = public.current_user_term_id()
    );

DROP POLICY IF EXISTS scenario_sets_student_insert ON scenario_sets;
CREATE POLICY scenario_sets_student_insert ON scenario_sets
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND is_published = false
    );

DROP POLICY IF EXISTS scenario_sets_student_update ON scenario_sets;
CREATE POLICY scenario_sets_student_update ON scenario_sets
    FOR UPDATE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND is_published = false
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND is_published = false
    );

DROP POLICY IF EXISTS scenario_sets_student_delete ON scenario_sets;
CREATE POLICY scenario_sets_student_delete ON scenario_sets
    FOR DELETE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND is_published = false
    );

DROP POLICY IF EXISTS scenario_sets_subscriber_read_published ON scenario_sets;
CREATE POLICY scenario_sets_subscriber_read_published ON scenario_sets
    FOR SELECT TO authenticated
    USING (public.is_subscriber() AND is_published = true);

-- Child tables inherit visibility through their parent set.
DROP POLICY IF EXISTS scenarios_admin_all ON scenarios;
CREATE POLICY scenarios_admin_all ON scenarios
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

-- Legacy single FOR ALL student policy (broken: see scenario_sets note above).
DROP POLICY IF EXISTS scenarios_student_term ON scenarios;

DROP POLICY IF EXISTS scenarios_student_read ON scenarios;
CREATE POLICY scenarios_student_read ON scenarios
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.term_id = public.current_user_term_id()
        )
    );

DROP POLICY IF EXISTS scenarios_student_insert ON scenarios;
CREATE POLICY scenarios_student_insert ON scenarios
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.created_by = auth.uid()
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenarios_student_update ON scenarios;
CREATE POLICY scenarios_student_update ON scenarios
    FOR UPDATE TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.created_by = auth.uid()
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    )
    WITH CHECK (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.created_by = auth.uid()
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenarios_student_delete ON scenarios;
CREATE POLICY scenarios_student_delete ON scenarios
    FOR DELETE TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.created_by = auth.uid()
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenarios_subscriber_read_published ON scenarios;
CREATE POLICY scenarios_subscriber_read_published ON scenarios
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id AND ss.is_published = true
        )
    );

DROP POLICY IF EXISTS scenario_nodes_admin_all ON scenario_nodes;
CREATE POLICY scenario_nodes_admin_all ON scenario_nodes
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

-- Legacy single FOR ALL student policy (broken: see scenario_sets note above).
DROP POLICY IF EXISTS scenario_nodes_student_term ON scenario_nodes;

DROP POLICY IF EXISTS scenario_nodes_student_read ON scenario_nodes;
CREATE POLICY scenario_nodes_student_read ON scenario_nodes
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
        )
    );

DROP POLICY IF EXISTS scenario_nodes_student_insert ON scenario_nodes;
CREATE POLICY scenario_nodes_student_insert ON scenario_nodes
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenario_nodes_student_update ON scenario_nodes;
CREATE POLICY scenario_nodes_student_update ON scenario_nodes
    FOR UPDATE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenario_nodes_student_delete ON scenario_nodes;
CREATE POLICY scenario_nodes_student_delete ON scenario_nodes
    FOR DELETE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenario_nodes_subscriber_read_published ON scenario_nodes;
CREATE POLICY scenario_nodes_subscriber_read_published ON scenario_nodes
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id AND ss.is_published = true
        )
    );
