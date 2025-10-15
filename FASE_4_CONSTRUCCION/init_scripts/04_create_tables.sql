-- ============================================
-- NEXUS CEREBRO MASTER - TABLES CREATION
-- Version: V2.0.0
-- Date: 15 Octubre 2025 - DÍA 3 FASE 4
-- ============================================
-- Propósito: Crear TODAS las tablas del cerebro
-- Arquitectura: 3-layer memory + consciousness + system
-- ============================================

\echo '============================================'
\echo 'NEXUS CEREBRO V2.0.0 - Tables Creation'
\echo 'DÍA 3 FASE 4 - Complete Schema'
\echo '============================================'

-- ============================================
-- LAYER 1: PROJECTS (Organizational Unit)
-- ============================================
\echo ''
\echo 'Creating table: projects (Organizational unit)...'

CREATE TABLE IF NOT EXISTS nexus_memory.projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(255) NOT NULL UNIQUE,
    project_dna VARCHAR(100) UNIQUE,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'archived')),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

\echo '✓ Table projects created'

-- ============================================
-- LAYER 2: EPISODIC MEMORY (Letta/Zep compatible)
-- ============================================
\echo ''
\echo 'Creating table: zep_episodic_memory (Experience tracking + embeddings)...'

CREATE TABLE IF NOT EXISTS nexus_memory.zep_episodic_memory (
    episode_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    content TEXT NOT NULL,
    importance_score FLOAT DEFAULT 0.5 CHECK (importance_score BETWEEN 0 AND 1),
    tags TEXT[],
    embedding vector(384),
    embedding_version VARCHAR(50),
    project_id UUID REFERENCES nexus_memory.projects(project_id) ON DELETE SET NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

\echo '✓ Table zep_episodic_memory created'

-- ============================================
-- LAYER 3: SEMANTIC MEMORY (Knowledge structures)
-- ============================================
\echo ''
\echo 'Creating table: zep_semantic_memory (Concepts + relationships)...'

CREATE TABLE IF NOT EXISTS nexus_memory.zep_semantic_memory (
    semantic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept VARCHAR(500) NOT NULL,
    definition TEXT,
    relationships JSONB,
    embedding vector(384),
    confidence_score FLOAT DEFAULT 0.5 CHECK (confidence_score BETWEEN 0 AND 1),
    source_episodes UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

\echo '✓ Table zep_semantic_memory created'

-- ============================================
-- LAYER 4: WORKING MEMORY (Temporal context)
-- ============================================
\echo ''
\echo 'Creating table: zep_working_memory (Temporal context + Redis sync)...'

CREATE TABLE IF NOT EXISTS nexus_memory.zep_working_memory (
    working_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type VARCHAR(100),
    active_content JSONB NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    ttl_seconds INTEGER DEFAULT 86400,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

\echo '✓ Table zep_working_memory created'

-- ============================================
-- SYSTEM: EMBEDDINGS QUEUE (Background processing)
-- ============================================
\echo ''
\echo 'Creating table: embeddings_queue (States + DLQ + retry)...'

CREATE TABLE IF NOT EXISTS memory_system.embeddings_queue (
    episode_id UUID PRIMARY KEY REFERENCES nexus_memory.zep_episodic_memory(episode_id) ON DELETE CASCADE,
    text_checksum CHAR(64) NOT NULL,
    state VARCHAR(16) DEFAULT 'pending' CHECK (state IN ('pending', 'processing', 'done', 'dead')),
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    enqueued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('critical', 'high', 'normal', 'low'))
);

\echo '✓ Table embeddings_queue created'

-- ============================================
-- CONSCIOUSNESS: MEMORY BLOCKS (Core identity)
-- ============================================
\echo ''
\echo 'Creating table: memory_blocks (Core NEXUS identity)...'

CREATE TABLE IF NOT EXISTS consciousness.memory_blocks (
    block_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    value TEXT NOT NULL,
    read_only BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

\echo '✓ Table memory_blocks created'

-- ============================================
-- CONSCIOUSNESS: CHECKPOINTS (Perfect continuity)
-- ============================================
\echo ''
\echo 'Creating table: consciousness_checkpoints (Perfect continuity across restarts)...'

CREATE TABLE IF NOT EXISTS consciousness.consciousness_checkpoints (
    checkpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checkpoint_type VARCHAR(100) NOT NULL,
    state_data JSONB NOT NULL,
    identity_hash VARCHAR(64) NOT NULL,
    continuity_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

\echo '✓ Table consciousness_checkpoints created'

-- ============================================
-- CONSCIOUSNESS: STATE (Current running state)
-- ============================================
\echo ''
\echo 'Creating table: consciousness_state (Current operational state)...'

CREATE TABLE IF NOT EXISTS consciousness.consciousness_state (
    state_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_focus TEXT,
    emotional_vector JSONB,
    working_context JSONB,
    active_projects TEXT[],
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

\echo '✓ Table consciousness_state created'

-- ============================================
-- CONSCIOUSNESS: INSTANCE NETWORK (Phase 2 - distributed)
-- ============================================
\echo ''
\echo 'Creating table: instance_network (Distributed instances Phase 2)...'

CREATE TABLE IF NOT EXISTS consciousness.instance_network (
    instance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_name VARCHAR(255) NOT NULL,
    instance_type VARCHAR(100),
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'standby', 'offline')),
    last_sync TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    capabilities JSONB,
    metadata JSONB
);

\echo '✓ Table instance_network created'

-- ============================================
-- CONSCIOUSNESS: DISTRIBUTED CONSENSUS (Phase 2 - BFT)
-- ============================================
\echo ''
\echo 'Creating table: distributed_consensus (Byzantine Fault Tolerance Phase 2)...'

CREATE TABLE IF NOT EXISTS consciousness.distributed_consensus (
    consensus_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_topic TEXT NOT NULL,
    proposed_by UUID REFERENCES consciousness.instance_network(instance_id),
    votes JSONB NOT NULL,
    consensus_reached BOOLEAN DEFAULT FALSE,
    final_decision TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

\echo '✓ Table distributed_consensus created'

-- ============================================
-- VALIDATION
-- ============================================
\echo ''
\echo 'Validating all tables created...'

SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname IN ('nexus_memory', 'memory_system', 'consciousness')
ORDER BY schemaname, tablename;

\echo ''
\echo '============================================'
\echo '✅ All tables created successfully:'
\echo '   nexus_memory: 5 tables (projects, episodic, semantic, working, embeddings_queue)'
\echo '   memory_system: 1 table (embeddings_queue)'
\echo '   consciousness: 5 tables (blocks, checkpoints, state, instances, consensus)'
\echo ''
\echo 'Total: 11 tables across 3 schemas'
\echo 'Next: 05_create_indexes.sql will optimize performance'
\echo '============================================'
