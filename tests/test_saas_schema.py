import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS_DIR = os.path.join(REPO_ROOT, "supabase", "migrations")

INIT_SCHEMA = "20260706000000_init_saas_schema.sql"
AUTH_TRIGGERS = "20260706000001_auth_sync_triggers.sql"
RLS_POLICIES = "20260706000002_rls_policies.sql"
SEMANTIC = "20260706000003_semantic_recommender.sql"
HARDENING = "20260706000004_rls_hardening.sql"
PROVENANCE_EDGE_INTEGRITY = "20260706000005_provenance_and_edge_integrity.sql"
ASSESSMENT_DIMENSIONS = "20260707100000_assessment_dimensions.sql"
SHADOW_AFFORDANCES = "20260707100001_shadow_affordances.sql"
VERIFICATION_STATUS = "20260707100002_verification_status.sql"


def read_migration(filename):
    with open(os.path.join(MIGRATIONS_DIR, filename), "r", encoding="utf-8") as fh:
        return fh.read()


class TestMigrationFilesExist(unittest.TestCase):
    def test_migrations_directory_exists(self):
        self.assertTrue(os.path.isdir(MIGRATIONS_DIR))

    def test_all_migration_files_present(self):
        for filename in (INIT_SCHEMA, AUTH_TRIGGERS, RLS_POLICIES, SEMANTIC, HARDENING, PROVENANCE_EDGE_INTEGRITY, ASSESSMENT_DIMENSIONS, SHADOW_AFFORDANCES, VERIFICATION_STATUS):
            path = os.path.join(MIGRATIONS_DIR, filename)
            self.assertTrue(os.path.isfile(path), f"Missing migration: {filename}")
            self.assertGreater(os.path.getsize(path), 0, f"Empty migration: {filename}")


class TestInitSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(INIT_SCHEMA)

    def test_pgvector_extension_enabled(self):
        self.assertIn("CREATE EXTENSION IF NOT EXISTS vector", self.sql)

    def test_user_role_enum_reconciled(self):
        self.assertIn("CREATE TYPE user_role AS ENUM", self.sql)
        self.assertIn("'Administrator'", self.sql)
        self.assertIn("'Student'", self.sql)
        self.assertIn("'Subscriber'", self.sql)

    def test_supporting_enums_defined(self):
        for enum in ("node_type", "steep_category", "horizon_type", "edge_type"):
            self.assertIn(f"CREATE TYPE {enum} AS ENUM", self.sql)

    def test_core_tables_created(self):
        for table in ("terms", "profiles", "nodes", "edges"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", self.sql)

    def test_profiles_references_auth_users(self):
        self.assertIn("REFERENCES auth.users(id)", self.sql)

    def test_nodes_embedding_dimension(self):
        self.assertIn("embedding vector(384)", self.sql)


class TestAuthTriggers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(AUTH_TRIGGERS)

    def test_handle_new_user_function(self):
        self.assertIn("FUNCTION public.handle_new_user()", self.sql)
        self.assertIn("SECURITY DEFINER", self.sql)

    def test_inserts_into_profiles(self):
        self.assertIn("INSERT INTO public.profiles", self.sql)

    def test_trigger_on_auth_users(self):
        self.assertIn("on_auth_user_created", self.sql)
        self.assertIn("AFTER INSERT ON auth.users", self.sql)


class TestRlsPolicies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(RLS_POLICIES)

    def test_rls_enabled_on_all_tables(self):
        for table in ("terms", "profiles", "nodes", "edges"):
            self.assertIn(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY", self.sql)

    def test_profiles_self_read_and_update(self):
        self.assertIn("FOR SELECT", self.sql)
        self.assertIn("FOR UPDATE", self.sql)
        self.assertIn("auth.uid() = id", self.sql)

    def test_admin_full_access(self):
        self.assertIn("FOR ALL", self.sql)
        self.assertIn("'Administrator'", self.sql)

    def test_student_term_policies(self):
        self.assertIn("is_approved = true", self.sql)
        self.assertIn("term_id", self.sql)

    def test_subscriber_read_only_policy(self):
        self.assertIn("'Subscriber'", self.sql)
        self.assertIn("is_keeper = true", self.sql)
        self.assertIn("node_type = 'Signal'", self.sql)

    def test_terms_policies_present(self):
        self.assertIn("ON terms", self.sql)


class TestSemanticRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(SEMANTIC)

    def test_function_defined(self):
        self.assertIn("FUNCTION surface_related_nodes", self.sql)

    def test_uses_cosine_distance_operator(self):
        self.assertIn("<=>", self.sql)

    def test_accepts_384_dim_vector(self):
        self.assertIn("vector(384)", self.sql)


class TestRlsHardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(HARDENING)

    def test_profile_self_update_guard_blocks_privilege_fields(self):
        self.assertIn("guard_profile_self_update", self.sql)
        self.assertIn("NEW.role IS DISTINCT FROM OLD.role", self.sql)
        self.assertIn("NEW.is_approved IS DISTINCT FROM OLD.is_approved", self.sql)
        self.assertIn("NEW.term_id IS DISTINCT FROM OLD.term_id", self.sql)

    def test_node_write_guard_blocks_self_verification(self):
        self.assertIn("guard_node_write", self.sql)
        self.assertIn("NEW.node_type IN ('Signal', 'Trend')", self.sql)
        self.assertIn("NEW.is_keeper IS DISTINCT FROM OLD.is_keeper", self.sql)
        self.assertIn("NEW.convergence_score IS DISTINCT FROM OLD.convergence_score", self.sql)
        self.assertIn("NEW.created_by IS DISTINCT FROM OLD.created_by", self.sql)

    def test_signup_defaults_to_unapproved_student(self):
        self.assertIn("'Student'::user_role", self.sql)
        self.assertIn("false", self.sql)
        self.assertNotIn("raw_user_meta_data->>'role'", self.sql)

    def test_recommender_is_security_invoker(self):
        self.assertIn("FUNCTION surface_related_nodes", self.sql)
        self.assertIn("SECURITY INVOKER", self.sql)

    def test_updated_at_triggers_present(self):
        self.assertIn("set_profiles_updated_at", self.sql)
        self.assertIn("set_nodes_updated_at", self.sql)


class TestProvenanceAndEdgeIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(PROVENANCE_EDGE_INTEGRITY)

    def test_provenance_column_added(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS source_metadata JSONB", self.sql)
        self.assertIn("nodes_source_metadata_idx", self.sql)

    def test_edge_term_consistency_guard(self):
        self.assertIn("guard_edge_term_consistency", self.sql)
        self.assertIn("source_term IS DISTINCT FROM target_term", self.sql)
        self.assertIn("BEFORE INSERT OR UPDATE ON edges", self.sql)


class TestAssessmentDimensions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(ASSESSMENT_DIMENSIONS)

    def test_uncertainty_score_column(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS uncertainty_score INTEGER", self.sql)
        self.assertIn("uncertainty_score BETWEEN 1 AND 10", self.sql)

    def test_horizon_year_column(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS horizon_year INTEGER", self.sql)
        self.assertIn("horizon_year BETWEEN 2020 AND 2200", self.sql)

    def test_assessment_provenance_columns(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS assessed_at TIMESTAMP WITH TIME ZONE", self.sql)
        self.assertIn("ADD COLUMN IF NOT EXISTS assessed_by VARCHAR(100)", self.sql)

    def test_no_default_five(self):
        self.assertNotIn("uncertainty_score INTEGER DEFAULT", self.sql)


class TestShadowAffordances(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(SHADOW_AFFORDANCES)

    def test_polarity_enum(self):
        self.assertIn("CREATE TYPE signal_polarity AS ENUM ('Emergent', 'Shadow')", self.sql)

    def test_shadow_type_enum(self):
        self.assertIn(
            "CREATE TYPE shadow_type AS ENUM ('Declining-System', 'Obsolete-Behavior', 'Worst-Case-Future', 'Disruption')",
            self.sql,
        )

    def test_polarity_column_not_null_default_emergent(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS polarity signal_polarity", self.sql)
        self.assertIn("'Emergent'::signal_polarity NOT NULL", self.sql)

    def test_shadow_fields_constraint(self):
        self.assertIn("shadow_fields_require_shadow_polarity", self.sql)
        self.assertIn("polarity = 'Shadow'", self.sql)

    def test_shadow_partial_index(self):
        self.assertIn("nodes_shadow_polarity_idx", self.sql)


class TestVerificationStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(VERIFICATION_STATUS)

    def test_verification_enum(self):
        self.assertIn("CREATE TYPE verification_status AS ENUM ('Raw', 'Verified', 'Archived')", self.sql)

    def test_backfill_from_node_type(self):
        self.assertIn("UPDATE nodes SET verification", self.sql)
        self.assertIn("node_type = 'Signal'", self.sql)

    def test_retires_shadow_node_type(self):
        self.assertIn("SET node_type = 'Signal'", self.sql)
        self.assertIn("WHERE node_type = 'Shadow'", self.sql)

    def test_policies_use_verification(self):
        self.assertIn("nodes_subscriber_read_verified_signals", self.sql)
        self.assertIn("verification = 'Verified'", self.sql)

    def test_student_update_excludes_verified(self):
        self.assertIn("nodes_student_update_own_term", self.sql)
        self.assertIn("verification <> 'Verified'", self.sql)

    def test_guard_protects_verification(self):
        self.assertIn("NEW.verification IS DISTINCT FROM OLD.verification", self.sql)


if __name__ == "__main__":
    unittest.main()
