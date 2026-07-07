import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS_DIR = os.path.join(REPO_ROOT, "supabase", "migrations")

INIT_SCHEMA = "20260706000000_init_saas_schema.sql"
AUTH_TRIGGERS = "20260706000001_auth_sync_triggers.sql"
RLS_POLICIES = "20260706000002_rls_policies.sql"
SEMANTIC = "20260706000003_semantic_recommender.sql"


def read_migration(filename):
    with open(os.path.join(MIGRATIONS_DIR, filename), "r", encoding="utf-8") as fh:
        return fh.read()


class TestMigrationFilesExist(unittest.TestCase):
    def test_migrations_directory_exists(self):
        self.assertTrue(os.path.isdir(MIGRATIONS_DIR))

    def test_all_migration_files_present(self):
        for filename in (INIT_SCHEMA, AUTH_TRIGGERS, RLS_POLICIES, SEMANTIC):
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


if __name__ == "__main__":
    unittest.main()
