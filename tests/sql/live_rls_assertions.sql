\set ON_ERROR_STOP on
\set QUIET on

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION public.test_assert(condition boolean, message text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT condition THEN
        RAISE EXCEPTION 'RLS assertion failed: %', message;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION public.test_expect_denied(statement text, message text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    BEGIN
        EXECUTE statement;
    EXCEPTION
        WHEN insufficient_privilege OR check_violation OR raise_exception THEN
            RETURN;
    END;
    RAISE EXCEPTION 'RLS assertion failed: expected denial for %', message;
END;
$$;

SET LOCAL ROLE postgres;

INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, created_at, updated_at, raw_user_meta_data)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'admin@example.test', '', now(), now(), now(), '{}'::jsonb),
    ('00000000-0000-0000-0000-000000000002', 'student-a@example.test', '', now(), now(), now(), '{}'::jsonb),
    ('00000000-0000-0000-0000-000000000003', 'student-b@example.test', '', now(), now(), now(), '{}'::jsonb),
    ('00000000-0000-0000-0000-000000000004', 'subscriber@example.test', '', now(), now(), now(), '{}'::jsonb),
    ('00000000-0000-0000-0000-000000000005', 'unapproved@example.test', '', now(), now(), now(), '{}'::jsonb)
ON CONFLICT (id) DO NOTHING;

INSERT INTO terms (id, name, invite_code, is_active)
VALUES
    ('10000000-0000-0000-0000-000000000001', 'Term A', 'TERM-A', true),
    ('10000000-0000-0000-0000-000000000002', 'Term B', 'TERM-B', true)
ON CONFLICT (id) DO NOTHING;

ALTER TABLE profiles DISABLE TRIGGER guard_profiles_update;

UPDATE profiles SET full_name='Admin', role='Administrator', is_approved=true, term_id='10000000-0000-0000-0000-000000000001'
WHERE id='00000000-0000-0000-0000-000000000001';
UPDATE profiles SET full_name='Student A', role='Student', is_approved=true, term_id='10000000-0000-0000-0000-000000000001'
WHERE id='00000000-0000-0000-0000-000000000002';
UPDATE profiles SET full_name='Student B', role='Student', is_approved=true, term_id='10000000-0000-0000-0000-000000000002'
WHERE id='00000000-0000-0000-0000-000000000003';
UPDATE profiles SET full_name='Subscriber', role='Subscriber', is_approved=true, term_id=NULL
WHERE id='00000000-0000-0000-0000-000000000004';
UPDATE profiles SET full_name='Unapproved', role='Student', is_approved=false, term_id='10000000-0000-0000-0000-000000000001'
WHERE id='00000000-0000-0000-0000-000000000005';

ALTER TABLE profiles ENABLE TRIGGER guard_profiles_update;
ALTER TABLE nodes DISABLE TRIGGER guard_nodes_write;

INSERT INTO nodes (id, title, description, category, time_horizon, node_type, verification, is_keeper, impact_score, created_by, term_id, embedding)
VALUES
    ('20000000-0000-0000-0000-000000000001', 'Verified A', 'Verified signal in term A', 'Social', 'Near-term', 'Signal', 'Verified', true, 8, '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', array_fill(0.01::real, ARRAY[384])::vector),
    ('20000000-0000-0000-0000-000000000002', 'Shadow A', 'Shadow in term A', 'Social', 'Near-term', 'Signal', 'Raw', false, 5, '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', array_fill(0.02::real, ARRAY[384])::vector),
    ('20000000-0000-0000-0000-000000000003', 'Verified B', 'Verified signal in term B', 'Social', 'Near-term', 'Signal', 'Verified', true, 8, '00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', array_fill(0.03::real, ARRAY[384])::vector),
    ('20000000-0000-0000-0000-000000000004', 'Draft B', 'Unverified draft in term B', 'Technological', 'Mid-term', 'Signal', 'Raw', false, 5, '00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', array_fill(0.04::real, ARRAY[384])::vector)
ON CONFLICT (id) DO NOTHING;

ALTER TABLE nodes ENABLE TRIGGER guard_nodes_write;

SET LOCAL ROLE authenticated;
SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000002';
SELECT public.test_expect_denied(
    $$UPDATE profiles SET role='Administrator' WHERE id='00000000-0000-0000-0000-000000000002'$$,
    'student role escalation'
);
SELECT public.test_expect_denied(
    $$UPDATE profiles SET is_approved=false WHERE id='00000000-0000-0000-0000-000000000002'$$,
    'student approval self-change'
);
SELECT public.test_expect_denied(
    $$UPDATE profiles SET term_id='10000000-0000-0000-0000-000000000002' WHERE id='00000000-0000-0000-0000-000000000002'$$,
    'student term reassignment'
);
SELECT public.test_expect_denied(
    $$INSERT INTO nodes (title, description, category, time_horizon, node_type, verification, is_keeper, created_by, term_id) VALUES ('Bad verified', 'bad', 'Social', 'Near-term', 'Signal', 'Verified', true, '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001')$$,
    'student verified node insert'
);
SELECT public.test_expect_denied(
    $$UPDATE nodes SET is_keeper=true WHERE id='20000000-0000-0000-0000-000000000002'$$,
    'student self keeper promotion'
);
SELECT public.test_expect_denied(
    $$UPDATE nodes SET convergence_score=9 WHERE id='20000000-0000-0000-0000-000000000002'$$,
    'student convergence rewrite'
);

INSERT INTO nodes (id, title, description, category, time_horizon, node_type, verification, is_keeper, created_by, term_id)
VALUES ('20000000-0000-0000-0000-000000000005', 'Student A draft', 'Allowed draft', 'Social', 'Near-term', 'Signal', 'Raw', false, '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001');
SELECT public.test_assert(EXISTS (SELECT 1 FROM nodes WHERE id='20000000-0000-0000-0000-000000000005'), 'student can insert own draft');
SELECT public.test_assert(NOT EXISTS (SELECT 1 FROM nodes WHERE id='20000000-0000-0000-0000-000000000004'), 'student A cannot read term B draft');

SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000004';
SELECT public.test_assert((SELECT count(*) FROM nodes WHERE title LIKE '%Verified%') = 2, 'subscriber can read verified keepers');
SELECT public.test_assert(NOT EXISTS (SELECT 1 FROM nodes WHERE title='Shadow A'), 'subscriber cannot read shadow/unverified node');
SELECT public.test_assert(NOT EXISTS (SELECT 1 FROM nodes WHERE title='Draft B'), 'subscriber cannot read drafts');
SELECT public.test_assert((SELECT count(*) FROM surface_related_nodes(array_fill(0.01::real, ARRAY[384])::vector, -1, 20)) = 2, 'semantic recommender respects subscriber RLS');

SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000001';
SELECT public.test_expect_denied(
    $$INSERT INTO edges (source_node_id, target_node_id, relationship_type, term_id, created_by) VALUES ('20000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000003', 'Cites', '10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001')$$,
    'cross-term edge insert'
);

SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000005';
SELECT public.test_assert((SELECT count(*) FROM nodes) = 0, 'unapproved student cannot read nodes');

-- Peer validation assertions - create test data as postgres first
SET LOCAL ROLE postgres;
ALTER TABLE nodes DISABLE TRIGGER guard_nodes_write;
INSERT INTO nodes (id, title, description, category, time_horizon, node_type, verification, is_keeper, created_by, term_id, embedding)
VALUES ('20000000-0000-0000-0000-000000000006', 'Peer test node', 'For peer validation testing', 'Social', 'Near-term', 'Signal', 'Raw', false, '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', array_fill(0.05::real, ARRAY[384])::vector);
ALTER TABLE nodes ENABLE TRIGGER guard_nodes_write;

SET LOCAL ROLE authenticated;
SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000002';
SELECT public.test_expect_denied(
    $$INSERT INTO validations (node_id, validator, checklist, confidence) VALUES ('20000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000002', '{"source_checked": true, "not_duplicate": true, "signal_logic": true, "classification_justified": true}'::jsonb, 8)$$,
    'student cannot validate own node'
);

INSERT INTO validations (node_id, validator, checklist, confidence) VALUES ('20000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000002', '{"source_checked": true, "not_duplicate": true, "signal_logic": true, "classification_justified": true}'::jsonb, 8);
SELECT public.test_assert((SELECT verification FROM nodes WHERE id='20000000-0000-0000-0000-000000000006') = 'Verified', 'student validation triggers node verification');

SELECT public.test_expect_denied(
    $$UPDATE nodes SET verification='Verified' WHERE id='20000000-0000-0000-0000-000000000005'$$,
    'student direct verification update still rejected'
);

SELECT public.test_expect_denied(
    $$INSERT INTO validations (node_id, validator, checklist, confidence) VALUES ('20000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000002', '{"source_checked": true, "not_duplicate": true, "signal_logic": true, "classification_justified": true}'::jsonb, 9)$$,
    'second validation for verified node rejected by policy'
);

SELECT public.test_expect_denied(
    $$UPDATE nodes SET instructor_note='test note' WHERE id='20000000-0000-0000-0000-000000000005'$$,
    'student cannot write instructor_note'
);

ROLLBACK;

\echo 'M2.1b live RLS assertions passed'
