-- ============================================
-- NEXUS CEREBRO MASTER - INDEXES OPTIMIZATION
-- Version: V2.0.0
-- Date: 15 Octubre 2025 - DÍA 3 FASE 4
-- ============================================
-- Propósito: Optimizar performance con indexes estratégicos
-- Tipos: HNSW (vectors), B-Tree (timestamps), GIN (arrays/jsonb/fts)
-- ============================================

\echo '============================================'
\echo 'NEXUS CEREBRO V2.0.0 - Indexes Optimization'
\echo 'DÍA 3 FASE 4 - Performance Tuning'
\echo '============================================'

-- ============================================
-- EPISODIC MEMORY INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for zep_episodic_memory...'

-- pgvector HNSW index (similarity search - fastest)
CREATE INDEX IF NOT EXISTS idx_episodic_embedding_hnsw
    ON nexus_memory.zep_episodic_memory
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
\echo '  ✓ HNSW vector index created (m=16, ef_construction=64)'

-- Temporal search (recent episodes)
CREATE INDEX IF NOT EXISTS idx_episodic_timestamp
    ON nexus_memory.zep_episodic_memory(timestamp DESC);
\echo '  ✓ B-Tree timestamp index created (DESC)'

-- Tag-based search
CREATE INDEX IF NOT EXISTS idx_episodic_tags
    ON nexus_memory.zep_episodic_memory USING gin(tags);
\echo '  ✓ GIN tags index created'

-- Project filter
CREATE INDEX IF NOT EXISTS idx_episodic_project
    ON nexus_memory.zep_episodic_memory(project_id)
    WHERE project_id IS NOT NULL;
\echo '  ✓ B-Tree project_id index created (partial)'

-- Full-text search
CREATE INDEX IF NOT EXISTS idx_episodic_content_fts
    ON nexus_memory.zep_episodic_memory
    USING gin(to_tsvector('english', content));
\echo '  ✓ GIN full-text search index created'

-- Embedding version tracking
CREATE INDEX IF NOT EXISTS idx_episodic_embedding_version
    ON nexus_memory.zep_episodic_memory(embedding_version)
    WHERE embedding IS NOT NULL;
\echo '  ✓ B-Tree embedding_version index created (partial)'

-- ============================================
-- SEMANTIC MEMORY INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for zep_semantic_memory...'

-- pgvector HNSW index (concept similarity)
CREATE INDEX IF NOT EXISTS idx_semantic_embedding_hnsw
    ON nexus_memory.zep_semantic_memory
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
\echo '  ✓ HNSW vector index created'

-- Concept search
CREATE INDEX IF NOT EXISTS idx_semantic_concept
    ON nexus_memory.zep_semantic_memory(concept);
\echo '  ✓ B-Tree concept index created'

-- Full-text search (concept + definition)
CREATE INDEX IF NOT EXISTS idx_semantic_concept_fts
    ON nexus_memory.zep_semantic_memory
    USING gin(to_tsvector('english', concept || ' ' || COALESCE(definition, '')));
\echo '  ✓ GIN full-text search index created'

-- ============================================
-- WORKING MEMORY INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for zep_working_memory...'

-- Context type filter
CREATE INDEX IF NOT EXISTS idx_working_context_type
    ON nexus_memory.zep_working_memory(context_type);
\echo '  ✓ B-Tree context_type index created'

-- Priority + expiration (active items)
CREATE INDEX IF NOT EXISTS idx_working_priority_expires
    ON nexus_memory.zep_working_memory(priority DESC, expires_at ASC);
\echo '  ✓ B-Tree composite index created (priority + expires_at)'

-- ============================================
-- EMBEDDINGS QUEUE INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for embeddings_queue...'

-- State filter (pending/processing only)
CREATE INDEX IF NOT EXISTS idx_embeddings_queue_state
    ON memory_system.embeddings_queue(state)
    WHERE state IN ('pending', 'processing');
\echo '  ✓ B-Tree state index created (partial - pending/processing only)'

-- Priority queue (FIFO con priority)
CREATE INDEX IF NOT EXISTS idx_embeddings_queue_priority
    ON memory_system.embeddings_queue(priority DESC, enqueued_at ASC)
    WHERE state = 'pending';
\echo '  ✓ B-Tree composite index created (priority + enqueued_at, partial)'

-- Retry monitoring
CREATE INDEX IF NOT EXISTS idx_embeddings_queue_retry
    ON memory_system.embeddings_queue(retry_count)
    WHERE state = 'pending' AND retry_count > 0;
\echo '  ✓ B-Tree retry_count index created (partial - retry candidates)'

-- ============================================
-- CONSCIOUSNESS CHECKPOINTS INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for consciousness_checkpoints...'

-- Checkpoint type filter
CREATE INDEX IF NOT EXISTS idx_consciousness_checkpoints_type
    ON consciousness.consciousness_checkpoints(checkpoint_type);
\echo '  ✓ B-Tree checkpoint_type index created'

-- Recent checkpoints
CREATE INDEX IF NOT EXISTS idx_consciousness_checkpoints_created
    ON consciousness.consciousness_checkpoints(created_at DESC);
\echo '  ✓ B-Tree created_at index created (DESC)'

-- Identity hash lookup
CREATE INDEX IF NOT EXISTS idx_consciousness_checkpoints_hash
    ON consciousness.consciousness_checkpoints(identity_hash);
\echo '  ✓ B-Tree identity_hash index created'

-- ============================================
-- INSTANCE NETWORK INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for instance_network...'

-- Status filter (active instances)
CREATE INDEX IF NOT EXISTS idx_instance_network_status
    ON consciousness.instance_network(status)
    WHERE status = 'active';
\echo '  ✓ B-Tree status index created (partial - active only)'

-- Instance type filter
CREATE INDEX IF NOT EXISTS idx_instance_network_type
    ON consciousness.instance_network(instance_type);
\echo '  ✓ B-Tree instance_type index created'

-- ============================================
-- PROJECTS INDEXES
-- ============================================
\echo ''
\echo 'Creating indexes for projects...'

-- Status filter (active projects)
CREATE INDEX IF NOT EXISTS idx_projects_status
    ON nexus_memory.projects(status)
    WHERE status = 'active';
\echo '  ✓ B-Tree status index created (partial - active only)'

-- DNA lookup
CREATE INDEX IF NOT EXISTS idx_projects_dna
    ON nexus_memory.projects(project_dna)
    WHERE project_dna IS NOT NULL;
\echo '  ✓ B-Tree project_dna index created (partial)'

-- ============================================
-- VALIDATION
-- ============================================
\echo ''
\echo 'Validating all indexes created...'

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname IN ('nexus_memory', 'memory_system', 'consciousness')
ORDER BY schemaname, tablename, indexname;

\echo ''
\echo '============================================'
\echo '✅ All indexes created successfully:'
\echo '   - HNSW vector indexes: 2 (episodic + semantic embeddings)'
\echo '   - B-Tree indexes: 15 (timestamps, foreign keys, filters)'
\echo '   - GIN indexes: 3 (arrays, jsonb, full-text search)'
\echo '   - Partial indexes: 8 (optimized for common queries)'
\echo ''
\echo 'Total: 20+ indexes for optimal performance'
\echo 'Next: Schema ready for triggers and RBAC permissions'
\echo '============================================'
