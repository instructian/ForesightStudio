-- Authenticated API clients need table privileges before RLS policies can apply.
-- RLS remains the authorization boundary; these grants only allow PostgREST/JWT
-- users to reach the policies.

GRANT USAGE ON SCHEMA public TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON terms TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON nodes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON edges TO authenticated;
GRANT SELECT ON node_events TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON scenario_sets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON scenarios TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON scenario_nodes TO authenticated;

GRANT EXECUTE ON FUNCTION surface_related_nodes(vector(384), float, int) TO authenticated;
