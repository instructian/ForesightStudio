CREATE OR REPLACE FUNCTION surface_related_nodes(
    target_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id UUID,
    title VARCHAR,
    category steep_category,
    node_type node_type,
    similarity float
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        nodes.id,
        nodes.title,
        nodes.category,
        nodes.node_type,
        (1.0 - (nodes.embedding <=> target_embedding))::float AS similarity
    FROM nodes
    WHERE nodes.embedding IS NOT NULL
      AND (1.0 - (nodes.embedding <=> target_embedding)) > match_threshold
    ORDER BY nodes.embedding <=> target_embedding ASC
    LIMIT match_count;
END;
$$;

GRANT EXECUTE ON FUNCTION surface_related_nodes(vector(384), float, int) TO authenticated;
