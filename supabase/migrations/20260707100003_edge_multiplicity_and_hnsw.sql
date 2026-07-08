-- A node pair can hold multiple relationship types simultaneously
-- (e.g. Cites AND Contradicts); the old two-column PK forbade that.
ALTER TABLE edges ALTER COLUMN source_node_id SET NOT NULL;
ALTER TABLE edges ALTER COLUMN target_node_id SET NOT NULL;
ALTER TABLE edges DROP CONSTRAINT IF EXISTS edges_pkey;
ALTER TABLE edges ADD PRIMARY KEY (source_node_id, target_node_id, relationship_type);

-- ivfflat with lists=100 on a near-empty table has poor recall and needs
-- retraining as data grows; HNSW needs no list tuning.
DROP INDEX IF EXISTS nodes_embedding_idx;
CREATE INDEX IF NOT EXISTS nodes_embedding_hnsw_idx
    ON nodes USING hnsw (embedding vector_cosine_ops);
