-- ============================================
-- NEXUS CEREBRO MASTER - TRIGGERS EMBEDDINGS
-- Version: V2.0.0
-- Date: 15 Octubre 2025 - DÍA 4 FASE 4
-- ============================================
-- Propósito: Embeddings automáticos con triggers
-- Features: INSERT + UPDATE triggers, SHA256 checksum, idempotencia
-- ============================================

\echo '============================================'
\echo 'NEXUS CEREBRO V2.0.0 - Triggers Embeddings'
\echo 'DÍA 4 FASE 4 - Automatic Embeddings Generation'
\echo '============================================'

-- ============================================
-- FUNCTION: trigger_generate_embedding()
-- ============================================
\echo ''
\echo 'Creating function: trigger_generate_embedding()...'

CREATE OR REPLACE FUNCTION memory_system.trigger_generate_embedding()
RETURNS TRIGGER AS $$
BEGIN
    -- Si embedding es NULL o versión desactualizada, enqueue
    IF NEW.embedding IS NULL OR COALESCE(NEW.embedding_version, '') <> 'miniLM-384-chunked@v2' THEN
        -- ✅ IDEMPOTENTE: ON CONFLICT DO UPDATE resetea estado
        INSERT INTO memory_system.embeddings_queue (episode_id, text_checksum, state, priority)
        VALUES (
            NEW.episode_id,
            encode(sha256(convert_to(LEFT(NEW.content, 4000), 'UTF8')), 'hex'),
            'pending',
            CASE
                WHEN NEW.importance_score >= 0.9 THEN 'critical'
                WHEN NEW.importance_score >= 0.7 THEN 'high'
                ELSE 'normal'
            END
        )
        ON CONFLICT (episode_id) DO UPDATE
            SET state = 'pending',
                retry_count = 0,
                text_checksum = EXCLUDED.text_checksum,
                priority = EXCLUDED.priority,
                enqueued_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

\echo '✓ Function trigger_generate_embedding() created'

-- ============================================
-- TRIGGER 1: auto_generate_embedding (INSERT)
-- ============================================
\echo ''
\echo 'Creating trigger: auto_generate_embedding (AFTER INSERT)...'

CREATE TRIGGER auto_generate_embedding
AFTER INSERT ON nexus_memory.zep_episodic_memory
FOR EACH ROW
EXECUTE FUNCTION memory_system.trigger_generate_embedding();

\echo '✓ Trigger auto_generate_embedding created (AFTER INSERT)'

-- ============================================
-- TRIGGER 2: auto_update_embedding (UPDATE)
-- ============================================
\echo ''
\echo 'Creating trigger: auto_update_embedding (AFTER UPDATE)...'

CREATE TRIGGER auto_update_embedding
AFTER UPDATE ON nexus_memory.zep_episodic_memory
FOR EACH ROW
WHEN (OLD.content IS DISTINCT FROM NEW.content)
EXECUTE FUNCTION memory_system.trigger_generate_embedding();

\echo '✓ Trigger auto_update_embedding created (AFTER UPDATE when content changes)'

-- ============================================
-- VALIDATION
-- ============================================
\echo ''
\echo 'Validating triggers created...'

SELECT
    trigger_schema,
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'nexus_memory'
ORDER BY trigger_name;

\echo ''
\echo '============================================'
\echo '✅ Triggers embeddings created successfully:'
\echo '   - Function: trigger_generate_embedding()'
\echo '   - Trigger 1: auto_generate_embedding (AFTER INSERT)'
\echo '   - Trigger 2: auto_update_embedding (AFTER UPDATE content)'
\echo ''
\echo 'Features:'
\echo '   ✅ SHA256 checksum (idempotencia)'
\echo '   ✅ Priority queue (critical/high/normal por importance_score)'
\echo '   ✅ ON CONFLICT DO UPDATE (no duplicados)'
\echo '   ✅ Embedding version tracking'
\echo '   ✅ Content change detection (UPDATE only if content changes)'
\echo ''
\echo 'Next: Test triggers con INSERT + UPDATE episodios'
\echo '============================================'
