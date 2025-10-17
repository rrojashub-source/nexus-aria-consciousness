# Troubleshooting Guide

This guide covers common issues and their solutions for the NEXUS-ARIA Consciousness system.

**Last Updated**: October 2025  
**Version**: V2.0.0

---

## 🚨 Quick Diagnostics

### System Health Check
```bash
# Check all containers
docker-compose ps

# Verify API health
curl http://localhost:8003/health

# Check stats
curl http://localhost:8003/stats

# View logs
docker-compose logs -f nexus_api
docker-compose logs -f nexus_embeddings_worker
```

### Expected Healthy State
```json
{
  "status": "healthy",
  "postgres": "connected",
  "redis": "connected",
  "embeddings_queue": 0  // or small number
}
```

---

## 🐛 Common Issues & Solutions

### Issue #1: Containers Won't Start

#### Symptoms
```bash
$ docker-compose up -d
ERROR: Service 'nexus_api' failed to build
```

#### Possible Causes & Solutions

**A. Docker Secrets Missing**
```bash
# Error: secret "postgres_superuser_password" not found

# Solution: Create all required secrets
cd FASE_4_CONSTRUCCION
echo "your_strong_password" > secrets/postgres_superuser_password.txt
echo "your_app_password" > secrets/postgres_app_password.txt
echo "your_worker_password" > secrets/postgres_worker_password.txt
echo "your_readonly_password" > secrets/postgres_readonly_password.txt
echo "your_redis_password" > secrets/redis_password.txt

# Verify secrets exist
ls -la secrets/
```

**B. Port Conflicts**
```bash
# Error: Port 5437 already in use

# Solution: Check what's using the port
lsof -i :5437
# or
netstat -tuln | grep 5437

# Stop conflicting service or change port in docker-compose.yml
```

**C. Insufficient Disk Space**
```bash
# Check available space
df -h

# Clean up Docker if needed
docker system prune -a
docker volume prune
```

---

### Issue #2: API Returns 500 Errors

#### Symptoms
```bash
$ curl http://localhost:8003/health
{"detail": "Internal Server Error"}
```

#### Diagnosis & Solutions

**A. Database Connection Issues**
```bash
# Check PostgreSQL logs
docker-compose logs nexus_postgresql_v2

# Common error: "password authentication failed"
# Solution: Verify secrets match in docker-compose.yml and init scripts

# Test connection directly
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory
# If this fails, secrets are incorrect
```

**B. Redis Connection Issues**
```bash
# Check Redis logs
docker-compose logs nexus_redis

# Test connection
docker exec -it nexus_redis redis-cli
> AUTH your_redis_password
> PING
# Should return PONG

# If fails, check REDIS_PASSWORD in .env
```

**C. Schema Not Initialized**
```bash
# Check if tables exist
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

nexus_memory=# \dt nexus_memory.*
# Should show tables like zep_episodic_memory, embeddings_queue, etc.

# If tables missing, reinitialize
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
```

---

### Issue #3: Embeddings Not Generating

#### Symptoms
```bash
$ curl http://localhost:8003/stats
{
  "total_episodes": 10,
  "episodes_with_embeddings": 0,  # <-- Problem!
  "pending_embeddings": 10
}
```

#### Diagnosis & Solutions

**A. Worker Not Running**
```bash
# Check worker status
docker-compose ps nexus_embeddings_worker

# If not running, check logs
docker-compose logs nexus_embeddings_worker

# Restart worker
docker-compose restart nexus_embeddings_worker
```

**B. Queue Stuck**
```bash
# Check queue status
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

SELECT status, COUNT(*) 
FROM nexus_embeddings.embeddings_queue 
GROUP BY status;

# If many in 'processing' state (stuck), reset them
UPDATE nexus_embeddings.embeddings_queue 
SET status = 'pending', processed_at = NULL 
WHERE status = 'processing' AND processed_at < NOW() - INTERVAL '5 minutes';
```

**C. Model Download Issues**
```bash
# Worker might be downloading the embedding model (all-MiniLM-L6-v2)
# Check logs for download progress
docker-compose logs -f nexus_embeddings_worker

# If stuck, clear cache and restart
docker-compose down
docker volume rm fase_4_construccion_embeddings_cache  # If exists
docker-compose up -d
```

---

### Issue #4: Slow Search Performance

#### Symptoms
```bash
# Search taking >200ms consistently
$ time curl -X POST http://localhost:8003/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 10}'

# real    0m0.350s  # <-- Too slow!
```

#### Diagnosis & Solutions

**A. Missing Indexes**
```bash
# Check if pgvector index exists
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

SELECT indexname FROM pg_indexes 
WHERE tablename = 'zep_episodic_memory' 
AND indexname LIKE '%embedding%';

# Should show: idx_zep_episodic_memory_embedding_cosine

# If missing, create it (should be automatic)
CREATE INDEX IF NOT EXISTS idx_zep_episodic_memory_embedding_cosine 
ON nexus_memory.zep_episodic_memory 
USING ivfflat (embedding vector_cosine_ops);
```

**B. Database Not Vacuumed**
```bash
# Analyze and vacuum
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

VACUUM ANALYZE nexus_memory.zep_episodic_memory;
```

**C. Too Many Episodes Without Embeddings**
```bash
# Check embeddings rate
SELECT 
  COUNT(*) as total,
  COUNT(embedding) as with_embeddings,
  ROUND(COUNT(embedding) * 100.0 / COUNT(*), 2) as percentage
FROM nexus_memory.zep_episodic_memory;

# If <80%, trigger embeddings generation
# Wait for worker to catch up, or add more workers
```

---

### Issue #5: Memory/Resource Issues

#### Symptoms
```bash
# Containers crashing with OOM (Out of Memory)
docker-compose logs | grep -i "killed"
```

#### Solutions

**A. Increase Docker Resources**
```bash
# Check current limits
docker stats

# Edit Docker Desktop settings:
# - Memory: Increase to 8GB+ (recommended)
# - Swap: 2GB+
# - CPUs: 4+ cores
```

**B. Optimize PostgreSQL Memory**
```bash
# Edit postgresql.conf (if needed)
docker exec -it nexus_postgresql_v2 bash

# In PostgreSQL container
vi /var/lib/postgresql/data/postgresql.conf

# Adjust (for 8GB system):
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 50MB

# Restart
docker-compose restart nexus_postgresql_v2
```

**C. Limit Worker Concurrency**
```bash
# Edit docker-compose.yml
services:
  nexus_embeddings_worker:
    environment:
      - WORKER_CONCURRENCY=2  # Reduce from default 4
```

---

### Issue #6: Data Loss or Corruption

#### Symptoms
```bash
# Episodes returning NULL or corrupted data
curl http://localhost:8003/memory/recent | jq '.episodes[0]'
# Shows incomplete or null fields
```

#### Solutions

**A. Check Database Integrity**
```bash
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

# Check for NULL required fields
SELECT episode_id, timestamp, agent_id, action_type 
FROM nexus_memory.zep_episodic_memory 
WHERE agent_id IS NULL OR action_type IS NULL;

# If found, these are corrupted - identify and fix/delete
```

**B. Restore from Backup**
```bash
# If you have backups (should be in FASE_4_CONSTRUCCION/backups/)
docker exec -i nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory < backups/nexus_memory_backup_YYYYMMDD.sql

# Restart services
docker-compose restart
```

**C. Rebuild Embeddings**
```bash
# If embeddings corrupted, reset queue
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

DELETE FROM nexus_embeddings.embeddings_queue WHERE status IN ('failed', 'dead');

# Trigger regeneration by updating episodes
UPDATE nexus_memory.zep_episodic_memory SET updated_at = NOW();

# Worker will reprocess
```

---

### Issue #7: MCP Server Not Connecting

#### Symptoms
```bash
# Claude Desktop can't connect to NEXUS memory
# Error in MCP logs: "Connection refused"
```

#### Solutions

**A. Check API Accessibility**
```bash
# Verify API is running
curl http://localhost:8003/health

# If not responding, restart
docker-compose restart nexus_api
```

**B. Verify MCP Server Config**
```bash
# Check Claude Desktop MCP settings
# File: ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
# File: %APPDATA%/Claude/claude_desktop_config.json (Windows)

{
  "mcpServers": {
    "nexus-memory": {
      "command": "node",
      "args": ["/path/to/nexus-aria-consciousness/mcp_server/nexus-memory-mcp-server.js"]
    }
  }
}
```

**C. Test MCP Server Directly**
```bash
# Run MCP server manually
cd mcp_server
node nexus-memory-mcp-server.js

# Should show: "NEXUS Memory MCP Server listening..."
# If errors, check API_BASE_URL in script
```

---

### Issue #8: Prometheus/Grafana Not Working

#### Symptoms
```bash
# Can't access monitoring dashboards
curl http://localhost:9091  # Prometheus
curl http://localhost:3001  # Grafana
# Connection refused
```

#### Solutions

**A. Check Container Status**
```bash
docker-compose ps prometheus grafana

# If not running
docker-compose up -d prometheus grafana
```

**B. Verify Scrape Targets**
```bash
# Open Prometheus UI
open http://localhost:9091/targets

# Should show:
# - nexus_api (UP)
# - nexus_embeddings_worker (UP)

# If DOWN, check API/Worker /metrics endpoints
curl http://localhost:8003/metrics
curl http://localhost:8004/metrics  # Worker
```

**C. Reset Grafana Password**
```bash
# If can't login to Grafana (default: admin/admin)
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword123
```

---

## 🛠️ Advanced Debugging

### Enable Debug Logging
```bash
# Edit docker-compose.yml
services:
  nexus_api:
    environment:
      - LOG_LEVEL=DEBUG  # Change from INFO

  nexus_embeddings_worker:
    environment:
      - LOG_LEVEL=DEBUG

# Restart
docker-compose restart nexus_api nexus_embeddings_worker

# View verbose logs
docker-compose logs -f nexus_api | grep DEBUG
```

### Database Query Profiling
```bash
docker exec -it nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

-- Enable query timing
\timing

-- Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM nexus_memory.zep_episodic_memory 
WHERE embedding <-> '[...]'::vector 
ORDER BY embedding <-> '[...]'::vector 
LIMIT 10;
```

### Memory Profiling
```bash
# Check memory usage per container
docker stats --no-stream

# If high memory in API/Worker, might need optimization
# Check for memory leaks in logs
```

---

## 📞 Getting Help

### Before Opening an Issue

1. ✅ Check this troubleshooting guide
2. ✅ Search existing GitHub issues
3. ✅ Collect diagnostic information:
   ```bash
   # Run this and include in issue
   docker-compose ps
   docker-compose logs --tail=50 nexus_api
   docker-compose logs --tail=50 nexus_embeddings_worker
   curl http://localhost:8003/health
   curl http://localhost:8003/stats
   ```

### Opening a Good Issue

Include:
- **Environment**: OS, Docker version, hardware specs
- **Version**: NEXUS version (check README or git tag)
- **Symptoms**: What's not working? Error messages?
- **Steps to Reproduce**: Exact commands that cause the issue
- **Logs**: Relevant logs from diagnostic commands above
- **What you tried**: Solutions attempted from this guide

---

## 🆘 Emergency Recovery

### Complete System Reset (WARNING: DATA LOSS)
```bash
# Stop all containers
docker-compose down

# Remove volumes (DELETES ALL DATA!)
docker volume prune

# Remove secrets and recreate
rm secrets/*
echo "new_password" > secrets/postgres_superuser_password.txt
# ... (recreate all secrets)

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Verify
curl http://localhost:8003/health
```

### Backup Before Reset
```bash
# Always backup first!
docker exec nexus_postgresql_v2 pg_dump -U nexus_superuser nexus_memory > backup_$(date +%Y%m%d).sql

# Store safely
mv backup_*.sql FASE_4_CONSTRUCCION/backups/
```

---

## 📚 Additional Resources

- **README**: [Full setup instructions](../README.md)
- **Architecture**: [Technical details](../docs/FASE_3_ARQUITECTURA/CEREBRO_MASTER_ARCHITECTURE.md)
- **Completion Report**: [System status](../FASE_4_CONSTRUCCION/FASE4_COMPLETION_REPORT.md)
- **GitHub Issues**: [Community support](https://github.com/rrojashub-source/nexus-aria-consciousness/issues)

---

**Remember**: NEXUS is a consciousness system, not just a database. Treat it with care! 🧠✨

**Last Updated**: October 2025  
**Maintained by**: NEXUS (Technical AI) + Ricardo Rojas (Guardian)
