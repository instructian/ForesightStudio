-- Score constraint enhancements: convergence_score minimum and edges.strength_score NOT NULL

-- 1. Add CHECK constraint on nodes.convergence_score to enforce convergence >= 1.0
--    (convergence is 1.0 + 0.5 per duplicate, so minimum is always 1.0).
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS convergence_score_min;
ALTER TABLE nodes ADD CONSTRAINT convergence_score_min CHECK (convergence_score >= 1.0);

-- 2. Ensure edges.strength_score is NOT NULL (defaults to 5, has CHECK BETWEEN 1 AND 10).
--    First backfill any nulls with the default, then apply NOT NULL constraint.
UPDATE edges SET strength_score = 5 WHERE strength_score IS NULL;
ALTER TABLE edges ALTER COLUMN strength_score SET NOT NULL;
