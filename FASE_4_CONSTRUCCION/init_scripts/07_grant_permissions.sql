-- ============================================
-- NEXUS CEREBRO V2.0.0 - RBAC Permissions
-- FASE 4 - DÍA 5: Grant Permissions Fix
-- ============================================

-- ============================================
-- NEXUS_APP PERMISSIONS (API Service)
-- Full CRUD on nexus_memory tables
-- Read on memory_system tables
-- ============================================

-- nexus_memory schema
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA nexus_memory TO nexus_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA nexus_memory TO nexus_app;

-- memory_system schema (read-only for queue visibility)
GRANT SELECT ON ALL TABLES IN SCHEMA memory_system TO nexus_app;

-- consciousness schema
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA consciousness TO nexus_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA consciousness TO nexus_app;

-- ============================================
-- NEXUS_WORKER PERMISSIONS (Embeddings Worker)
-- Read/Write on episodic_memory (UPDATE embeddings)
-- Full CRUD on embeddings_queue
-- ============================================

-- nexus_memory schema (UPDATE for embeddings)
GRANT SELECT, UPDATE ON nexus_memory.zep_episodic_memory TO nexus_worker;

-- memory_system schema (FULL access to queue)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA memory_system TO nexus_worker;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA memory_system TO nexus_worker;

-- ============================================
-- NEXUS_RO PERMISSIONS (Read-Only)
-- Read-only access to all tables
-- ============================================

GRANT SELECT ON ALL TABLES IN SCHEMA nexus_memory TO nexus_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA memory_system TO nexus_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA consciousness TO nexus_ro;

-- ============================================
-- DEFAULT PRIVILEGES (for future tables)
-- ============================================

-- nexus_app
ALTER DEFAULT PRIVILEGES IN SCHEMA nexus_memory GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nexus_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA memory_system GRANT SELECT ON TABLES TO nexus_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA consciousness GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nexus_app;

-- nexus_worker
ALTER DEFAULT PRIVILEGES IN SCHEMA nexus_memory GRANT SELECT, UPDATE ON TABLES TO nexus_worker;
ALTER DEFAULT PRIVILEGES IN SCHEMA memory_system GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nexus_worker;

-- nexus_ro
ALTER DEFAULT PRIVILEGES IN SCHEMA nexus_memory GRANT SELECT ON TABLES TO nexus_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA memory_system GRANT SELECT ON TABLES TO nexus_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA consciousness GRANT SELECT ON TABLES TO nexus_ro;

-- ============================================
-- VERIFICATION
-- ============================================
\echo '✓ Permissions granted successfully'
\echo '  - nexus_app: Full CRUD on nexus_memory + consciousness'
\echo '  - nexus_worker: UPDATE on episodic_memory, Full CRUD on embeddings_queue'
\echo '  - nexus_ro: Read-only on all tables'
