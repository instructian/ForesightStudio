-- Shadows are weak signals of declining systems, obsolete behaviors, and
-- unwanted "worst-case" or disrupted futures. Capturing them prevents
-- strategic blind spots and lets organizations mitigate risks early.
-- Polarity is orthogonal to verification: a Shadow can be Raw or Verified.
DO $$
BEGIN
    CREATE TYPE signal_polarity AS ENUM ('Emergent', 'Shadow');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE shadow_type AS ENUM ('Declining-System', 'Obsolete-Behavior', 'Worst-Case-Future', 'Disruption');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE nodes ADD COLUMN IF NOT EXISTS polarity signal_polarity
    DEFAULT 'Emergent'::signal_polarity NOT NULL;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS shadow_type shadow_type;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS mitigation_notes TEXT;

ALTER TABLE nodes DROP CONSTRAINT IF EXISTS shadow_fields_require_shadow_polarity;
ALTER TABLE nodes ADD CONSTRAINT shadow_fields_require_shadow_polarity
    CHECK (polarity = 'Shadow' OR (shadow_type IS NULL AND mitigation_notes IS NULL));

CREATE INDEX IF NOT EXISTS nodes_shadow_polarity_idx ON nodes(polarity)
    WHERE polarity = 'Shadow';
