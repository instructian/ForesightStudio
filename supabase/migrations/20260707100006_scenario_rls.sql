ALTER TABLE scenario_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_nodes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS scenario_sets_admin_all ON scenario_sets;
CREATE POLICY scenario_sets_admin_all ON scenario_sets
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

DROP POLICY IF EXISTS scenario_sets_student_term ON scenario_sets;
CREATE POLICY scenario_sets_student_term ON scenario_sets
    FOR ALL TO authenticated
    USING (
        public.is_student()
        AND term_id = public.current_user_term_id()
    )
    WITH CHECK (
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

DROP POLICY IF EXISTS scenarios_student_term ON scenarios;
CREATE POLICY scenarios_student_term ON scenarios
    FOR ALL TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.term_id = public.current_user_term_id()
        )
    )
    WITH CHECK (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
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

DROP POLICY IF EXISTS scenario_nodes_student_term ON scenario_nodes;
CREATE POLICY scenario_nodes_student_term ON scenario_nodes
    FOR ALL TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
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
