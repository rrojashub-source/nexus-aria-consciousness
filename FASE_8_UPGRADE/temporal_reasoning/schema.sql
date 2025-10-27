-- FASE_8_UPGRADE: Temporal Reasoning Schema Enhancement
-- Phase 1: Index + Helper Functions
-- Date: October 27, 2025

-- 1. Create GIN index on metadata for fast temporal_refs queries
CREATE INDEX IF NOT EXISTS idx_episodic_metadata_temporal
ON nexus_memory.zep_episodic_memory USING GIN (metadata jsonb_path_ops);

-- 2. Function to add temporal reference
CREATE OR REPLACE FUNCTION nexus_memory.add_temporal_ref(
    source_episode_id UUID,
    target_episode_id UUID,
    relationship_type TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE nexus_memory.zep_episodic_memory
    SET metadata = jsonb_set(
        COALESCE(metadata, '{}'::jsonb),
        ARRAY['temporal_refs', relationship_type],
        COALESCE(metadata->'temporal_refs'->relationship_type, '[]'::jsonb) || to_jsonb(target_episode_id::text),
        true
    )
    WHERE episode_id = source_episode_id;
END;
$$ LANGUAGE plpgsql;

-- 3. Function to get temporal references
CREATE OR REPLACE FUNCTION nexus_memory.get_temporal_refs(
    episode_id UUID,
    relationship_type TEXT DEFAULT NULL
) RETURNS TABLE(ref_episode_id UUID, ref_type TEXT) AS $$
BEGIN
    IF relationship_type IS NULL THEN
        -- Return all types
        RETURN QUERY
        SELECT
            (arr.value#>>'{}'::text[])::uuid as ref_episode_id,
            refs.key as ref_type
        FROM nexus_memory.zep_episodic_memory e,
             jsonb_each(e.metadata->'temporal_refs') AS refs(key, value),
             jsonb_array_elements(refs.value) AS arr(value)
        WHERE e.episode_id = get_temporal_refs.episode_id;
    ELSE
        -- Return specific type
        RETURN QUERY
        SELECT
            (value#>>'{}'::text[])::uuid as ref_episode_id,
            relationship_type as ref_type
        FROM nexus_memory.zep_episodic_memory e,
             jsonb_array_elements(e.metadata->'temporal_refs'->relationship_type) AS arr(value)
        WHERE e.episode_id = get_temporal_refs.episode_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Verification queries
SELECT 'Index created:' as status, indexname
FROM pg_indexes
WHERE tablename = 'zep_episodic_memory'
AND indexname = 'idx_episodic_metadata_temporal';

SELECT 'Functions created:' as status, proname, pronargs
FROM pg_proc
WHERE proname IN ('add_temporal_ref', 'get_temporal_refs')
AND pronamespace = 'nexus_memory'::regnamespace;
