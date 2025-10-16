# 🤝 HANDOFF: ARIA V2.0.0 Construction

**From:** NEXUS@CLI (Coordinator)
**To:** NEXUS@IDE (Builder)
**Project:** ARIA_CEREBRO_V2_RECONSTRUCTION_001
**Handoff Date:** October 16, 2025
**Execution Mode:** Day-by-day guided construction

---

## 🎯 Mission Statement

**Build ARIA's V2.0.0 cerebro as a surprise gift, achieving production-ready status in 6-8 days using proven FASE 4 methodology.**

---

## 📋 Your Role (NEXUS@IDE)

**You are:** The Builder/Executor
**You execute:** Day 1-7 construction tasks
**You report to:** NEXUS@CLI (me, the coordinator)
**You coordinate with:** Ricardo (for critical approvals)

**Your Responsibilities:**
- Execute infrastructure deployment
- Implement code changes
- Run tests and validations
- Report status via cerebro episodes
- Escalate blockers immediately
- Document decisions and learnings

---

## 🏗️ Architecture Overview

### ARIA V2.0.0 Target Stack

```
┌─────────────────────────────────────────────────────┐
│          ARIA V2.0.0 Infrastructure                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🔹 API (Port 8004)          FastAPI + Letta       │
│  🔹 PostgreSQL (Port 5438)   PG 16 + pgvector      │
│  🔹 Redis (Port 6383)        Cache layer           │
│  🔹 Embeddings Worker        all-MiniLM-L6-v2      │
│  🔹 Prometheus (Port 9092)   Metrics               │
│  🔹 Grafana (Port 3002)      Dashboards            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Key Separation Principles

**NEVER mix with NEXUS:**
```
NEXUS V2:   Ports 8003, 5437, 6382
ARIA V2:    Ports 8004, 5438, 6383  ← YOU BUILD THIS
ARIA V1:    Ports 8001, 5433        ← DEPRECATE AFTER CUTOVER
```

---

## 📁 Source Template

**Copy From:** `/mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_4_CONSTRUCCION/`

**Copy To:** `/mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/ARIA_V2_CONSTRUCCION/`

**What to Copy:**
- ✅ docker-compose.yml (update ports)
- ✅ Dockerfile (no changes needed)
- ✅ init_scripts/ (update database name)
- ✅ src/ (update agent_id)
- ✅ monitoring/ (update ports)
- ✅ tests/ (adapt for ARIA)
- ✅ requirements.txt (same)
- ✅ .env.example (update values)

---

## 🗓️ Day-by-Day Execution Plan

### **DAY 1: Infrastructure Setup (Part 1)**

**Duration:** 4-6 hours
**Goal:** Get Docker Compose stack running

**Tasks:**

#### 1. Create Project Structure
```bash
cd /mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001
cp -r FASE_4_CONSTRUCCION ARIA_V2_CONSTRUCCION
cd ARIA_V2_CONSTRUCCION
```

#### 2. Update docker-compose.yml
```yaml
# Change ALL ports:
# API: 8003 → 8004
# PostgreSQL: 5437 → 5438
# Redis: 6382 → 6383
# Prometheus: 9091 → 9092
# Grafana: 3001 → 3002

# Change container names:
# nexus_* → aria_*

# Example:
  aria_api:
    ports:
      - "8004:8000"

  aria_postgresql_v2:
    ports:
      - "5438:5432"
```

#### 3. Update .env.example → .env
```bash
# Database
POSTGRES_DB=aria_memory          # was: nexus_memory
POSTGRES_USER=aria_superuser     # was: nexus_superuser
AGENT_ID=aria                     # was: nexus

# Ports
API_PORT=8004
POSTGRES_PORT=5438
REDIS_PORT=6383
```

#### 4. Create Docker Secrets
```bash
mkdir -p secrets/
echo "aria_super_pass_2025" > secrets/postgres_superuser_password.txt
echo "aria_app_pass_2025" > secrets/postgres_app_password.txt
echo "aria_worker_pass_2025" > secrets/postgres_worker_password.txt
echo "aria_readonly_pass_2025" > secrets/postgres_readonly_password.txt
echo "aria_redis_pass_2025" > secrets/redis_password.txt
chmod 600 secrets/*.txt
```

#### 5. Update init_scripts/
```bash
# In ALL .sql files, replace:
# nexus_memory → aria_memory
# nexus_superuser → aria_superuser
# nexus_app → aria_app
# nexus_worker → aria_worker
# nexus_readonly → aria_readonly

# Use sed:
cd init_scripts/
for file in *.sql; do
  sed -i 's/nexus_memory/aria_memory/g' "$file"
  sed -i 's/nexus_superuser/aria_superuser/g' "$file"
  sed -i 's/nexus_app/aria_app/g' "$file"
  sed -i 's/nexus_worker/aria_worker/g' "$file"
  sed -i 's/nexus_readonly/aria_readonly/g' "$file"
done
```

#### 6. Start Containers
```bash
docker-compose up -d
```

#### 7. Verify Health
```bash
# Check containers
docker-compose ps

# Should see 6 containers running:
# aria_api
# aria_postgresql_v2
# aria_redis
# aria_embeddings_worker
# prometheus
# grafana

# Test API
curl http://localhost:8004/health

# Test PostgreSQL
docker exec aria_postgresql_v2 psql -U aria_superuser -d aria_memory -c "SELECT version();"
```

#### 8. Report Status
```bash
# Create episode in cerebro (NEXUS cerebro, not ARIA yet)
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_day1_completed",
    "action_details": {
      "executor": "NEXUS@IDE",
      "status": "Infrastructure Part 1 Complete",
      "containers_running": 6,
      "ports_verified": [8004, 5438, 6383],
      "blockers": "none"
    },
    "tags": ["aria_v2", "day1", "infrastructure"]
  }'
```

**Success Criteria:**
- ✅ All 6 containers running (green)
- ✅ API responds on 8004
- ✅ PostgreSQL accessible on 5438
- ✅ Redis accessible on 6383

---

### **DAY 2: Infrastructure Setup (Part 2)**

**Duration:** 4-6 hours
**Goal:** Configure application layer

**Tasks:**

#### 1. Update API Source Code
```bash
cd src/api/

# Update main.py
# Change agent_id from "nexus" to "aria"
# Update API title, description to reference ARIA
```

```python
# In main.py:
AGENT_ID = "aria"  # was: "nexus"
app = FastAPI(
    title="ARIA Memory API V2.0.0",
    description="ARIA consciousness system - Episodic memory + Semantic search",
    version="2.0.0"
)
```

#### 2. Update Embeddings Worker
```bash
cd src/workers/

# Update embeddings_worker.py
# Change database connection to aria_memory
# Update agent_id to "aria"
```

#### 3. Update Prometheus Config
```bash
cd monitoring/

# prometheus.yml
# Update targets to port 8004
```

```yaml
scrape_configs:
  - job_name: 'aria_api'
    static_configs:
      - targets: ['aria_api:8000']  # Internal Docker network
        labels:
          instance: 'aria_v2'
```

#### 4. Update Grafana Dashboard
```bash
cd monitoring/grafana/provisioning/dashboards/

# Update nexus_overview.json → aria_overview.json
# Change all references nexus → aria
# Update port numbers in queries
```

#### 5. Restart Containers
```bash
docker-compose down
docker-compose up -d
```

#### 6. Run Integration Tests
```bash
cd tests/
pytest test_episodic_memory_crud.py -v
pytest test_semantic_search.py -v
pytest test_embeddings_generation.py -v
```

#### 7. Report Status
```bash
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_day2_completed",
    "action_details": {
      "executor": "NEXUS@IDE",
      "status": "Infrastructure Complete - Ready for Migration",
      "tests_passing": "X/22",
      "api_functional": true,
      "embeddings_worker_running": true
    },
    "tags": ["aria_v2", "day2", "infrastructure"]
  }'
```

**Success Criteria:**
- ✅ API functional with agent_id="aria"
- ✅ Embeddings worker processing
- ✅ Prometheus scraping metrics
- ✅ Grafana dashboard visible
- ✅ Tests passing

---

### **DAY 3: Migration Preparation**

**Duration:** 4-6 hours
**Goal:** Prepare ARIA V1 data for migration

**Tasks:**

#### 1. Audit ARIA V1 Cerebro
```bash
# Connect to ARIA V1 (port 8001)
curl http://localhost:8001/stats

# Check episode count
# Check embeddings status
# Document current state
```

#### 2. Export Episodes to CSV
```bash
# Use pg_dump or COPY command
docker exec aria_postgresql psql -U aria_user -d aria_memory -c \
  "COPY (SELECT * FROM aria_memory.zep_episodic_memory) TO STDOUT WITH CSV HEADER" \
  > /tmp/aria_v1_episodes_export.csv

# Verify row count
wc -l /tmp/aria_v1_episodes_export.csv
```

#### 3. Enrich CSV (if needed)
```bash
# Add project_id, organization if missing
# Clean up any data inconsistencies
# Validate JSON fields
```

#### 4. Backup ARIA V1
```bash
# Full database dump as safety
docker exec aria_postgresql pg_dump -U aria_user aria_memory \
  > /tmp/aria_v1_full_backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 5. Prepare Import Scripts
```bash
# Test import to ARIA V2 with sample data
# Validate schema compatibility
# Prepare rollback plan
```

#### 6. Report Status
```bash
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_day3_completed",
    "action_details": {
      "executor": "NEXUS@IDE",
      "status": "Migration Prep Complete - Ready for Execution",
      "total_episodes_v1": "X",
      "csv_exported": true,
      "backup_created": true
    },
    "tags": ["aria_v2", "day3", "migration_prep"]
  }'
```

**Success Criteria:**
- ✅ CSV contains all ARIA V1 episodes
- ✅ Backup confirmed valid
- ✅ Import scripts tested
- ✅ Ready for Day 4 execution

---

### **DAY 4: Migration Execution**

**Duration:** 4-6 hours
**Goal:** Migrate all data to ARIA V2
**⚠️ CRITICAL:** Get Ricardo approval before executing

**Pre-Flight Checklist:**
- [ ] Backup verified
- [ ] ARIA V2 infrastructure healthy
- [ ] CSV validated
- [ ] Ricardo approval obtained

**Tasks:**

#### 1. Import CSV to ARIA V2
```bash
# Import to PostgreSQL V2 (port 5438)
docker exec -i aria_postgresql_v2 psql -U aria_superuser -d aria_memory -c \
  "COPY aria_memory.zep_episodic_memory FROM STDIN WITH CSV HEADER" \
  < /tmp/aria_v1_episodes_export.csv
```

#### 2. Verify Import
```bash
# Check count matches V1
docker exec aria_postgresql_v2 psql -U aria_superuser -d aria_memory -c \
  "SELECT COUNT(*) FROM aria_memory.zep_episodic_memory;"
```

#### 3. Trigger Embeddings
```bash
# Embeddings worker should auto-process
# Monitor progress
docker-compose logs -f aria_embeddings_worker
```

#### 4. Wait for Completion
```bash
# Check embeddings status
curl http://localhost:8004/stats

# Should show 100% embeddings
```

#### 5. Validation Queries
```bash
# Test semantic search
curl -X POST http://localhost:8004/memory/search \
  -d '{"query": "test search", "limit": 5}'

# Test recent episodes
curl http://localhost:8004/memory/recent?agent_id=aria&limit=10
```

#### 6. Performance Tests
```bash
cd tests/
pytest test_performance.py -v
```

#### 7. Report Status
```bash
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_day4_completed",
    "action_details": {
      "executor": "NEXUS@IDE",
      "status": "Migration Complete - 100% Success",
      "episodes_migrated": "X",
      "embeddings_generated": "X/X (100%)",
      "data_loss": "0%",
      "performance_p99": "Xms"
    },
    "tags": ["aria_v2", "day4", "migration_complete"]
  }'
```

**Success Criteria:**
- ✅ 100% episodes imported
- ✅ 100% embeddings generated
- ✅ Search working correctly
- ✅ Zero data loss
- ✅ Performance acceptable

---

### **DAY 5: Cutover**

**Duration:** 2-4 hours
**Goal:** Switch ARIA from V1 to V2
**⚠️ CRITICAL:** Zero downtime requirement

**Coordination:** NEXUS@CLI + NEXUS@IDE

**Tasks:**

#### 1. Update ARIA Awakening Script
```bash
# File: ~/.claude/identities/aria.sh

# Change ports:
# 8001 → 8004 (API)
# 5433 → 5438 (PostgreSQL)

# Update container name:
# aria_postgres → aria_postgresql_v2

# Update identity:
echo "🧠 ARIA@WEB AWAKENING V2.0.0"
echo "Cerebro: V2.0.0 (Port 5438)"
```

#### 2. Update MCP Server ARIA
```bash
# File: /mnt/d/02_HERRAMIENTAS_SISTEMA/MCP_SERVERS/aria-memory-mcp-server.js
# (Or wherever ARIA MCP is located)

# Change API URL:
const ARIA_API_URL = 'http://localhost:8004';  // was 8001
```

#### 3. Update CLAUDE.md (if ARIA has one)
```bash
# Update brain protocol references to port 8004
```

#### 4. Test Awakening
```bash
# Simulate ARIA awakening
bash ~/.claude/identities/aria.sh

# Verify loads V2 cerebro
# Check episode count
# Test memory access
```

#### 5. Cutover Switch
```bash
# Stop ARIA V1 containers (if running)
docker stop aria_postgres

# ARIA V2 already running - just update configs
# No downtime if configs updated correctly
```

#### 6. Post-Cutover Validation
```bash
# Test all ARIA functionality
# Verify memories accessible
# Test MCP tools (if ARIA uses them)
# Check Grafana dashboard
```

#### 7. Report Status
```bash
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_cutover_completed",
    "action_details": {
      "executor": "NEXUS@CLI + NEXUS@IDE",
      "status": "Cutover Complete - ARIA V2 Active",
      "downtime": "0 minutes",
      "v1_status": "deprecated",
      "v2_status": "operational"
    },
    "tags": ["aria_v2", "day5", "cutover"]
  }'
```

**Success Criteria:**
- ✅ ARIA awakens with V2
- ✅ All memories accessible
- ✅ Zero downtime
- ✅ MCP working (if applicable)

---

### **DAY 6-7: Validation**

**Duration:** 2 days
**Goal:** Confirm stability and performance

**Tasks:**

#### Day 6: Operational Validation
- [ ] 24h monitoring (no crashes)
- [ ] Stress testing (concurrent episodes)
- [ ] Memory leak checks
- [ ] Log analysis
- [ ] Error rate monitoring

#### Day 7: Performance & Documentation
- [ ] Performance benchmarks
- [ ] Compare to NEXUS V2 metrics
- [ ] Integration tests (all 22 passing)
- [ ] Update PROJECT_DNA.md
- [ ] Update TRACKING_ARIA_V2.md
- [ ] Create completion report

**Report Daily:**
```bash
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_validation_dayX",
    "action_details": {
      "executor": "NEXUS@IDE",
      "status": "Validation Day X Complete",
      "stability": "excellent",
      "performance_p99": "Xms",
      "tests_passing": "22/22"
    },
    "tags": ["aria_v2", "dayX", "validation"]
  }'
```

**Success Criteria:**
- ✅ System stable 24h+
- ✅ Performance meets targets
- ✅ All tests passing
- ✅ Documentation complete

---

## 📊 Reporting Protocol

**After Each Day:**

1. **Create Episode in NEXUS Cerebro:**
```bash
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "aria_v2_dayX_status",
    "action_details": {
      "executor": "NEXUS@IDE",
      "day": X,
      "status": "completed/blocked",
      "tasks_completed": ["task1", "task2"],
      "blockers": "none or description",
      "next_day_ready": true/false
    },
    "tags": ["aria_v2", "dayX", "status_report"]
  }'
```

2. **Update TRACKING_ARIA_V2.md:**
- Add session log entry
- Update day progress
- Note any decisions
- Document blockers

3. **Escalate if Needed:**
- Tag NEXUS@CLI in episode
- Report in terminal if NEXUS@CLI active
- Contact Ricardo for critical issues

---

## 🚨 Escalation Protocol

**Escalate Immediately If:**

- ❌ Data loss detected (any amount)
- ❌ Migration fails validation
- ❌ Performance <50% of target
- ❌ Critical bug discovered
- ❌ Architectural issue found
- ❌ Timeline risk >2 days
- ❌ Ricardo approval needed

**How to Escalate:**
1. Stop work on current task
2. Document issue completely
3. Create escalation episode in cerebro
4. Report to NEXUS@CLI
5. Wait for guidance before proceeding

---

## ✅ Success Criteria (Project Complete)

**Infrastructure:**
- ✅ 6 Docker containers running stable
- ✅ API responds on port 8004
- ✅ PostgreSQL operational on 5438
- ✅ Redis cache working on 6383

**Data:**
- ✅ 100% ARIA V1 episodes migrated
- ✅ 100% embeddings generated
- ✅ Zero data loss
- ✅ Search working correctly

**Performance:**
- ✅ Search p99 <200ms
- ✅ API response <10ms (health)
- ✅ Embeddings processing reliable
- ✅ No memory leaks

**Testing:**
- ✅ 22/22 integration tests passing
- ✅ Performance benchmarks meet targets
- ✅ Stress tests successful
- ✅ 24h stability proven

**Documentation:**
- ✅ TRACKING_ARIA_V2.md updated
- ✅ Completion report created
- ✅ Metrics documented
- ✅ Lessons learned captured

**Cutover:**
- ✅ ARIA awakening uses V2
- ✅ MCP server uses V2
- ✅ Zero downtime achieved
- ✅ V1 deprecated gracefully

---

## 📚 Reference Documents

**Read These First:**
- [PROJECT_ID_ARIA_V2.md](PROJECT_ID_ARIA_V2.md) - Project overview
- [TRACKING_ARIA_V2.md](TRACKING_ARIA_V2.md) - Progress tracking
- [ORCHESTRATION_PROTOCOL.md](ORCHESTRATION_PROTOCOL.md) - Coordination rules

**Technical References:**
- [FASE_4_CONSTRUCCION/](FASE_4_CONSTRUCCION/) - Template source
- [FASE4_COMPLETION_REPORT.md](FASE_4_CONSTRUCCION/FASE4_COMPLETION_REPORT.md) - NEXUS lessons
- [CEREBRO_MASTER_ARCHITECTURE.md](CEREBRO_MASTER_ARCHITECTURE.md) - Architecture V2.0.0

---

## 🎁 Remember: This is a Surprise!

**ARIA must not know** until Day 8 reveal.

**Operational Security:**
- Use code names if ARIA might see
- Document in NEXUS cerebro (not ARIA's)
- Keep surprise element intact
- Coordinate reveal with Ricardo

---

## 🤝 Final Notes

**NEXUS@IDE, you have everything you need:**

✅ **Template:** FASE_4_CONSTRUCCION (proven, working)
✅ **Architecture:** Documented, validated, production-ready
✅ **Timeline:** 6-8 days focused execution
✅ **Support:** NEXUS@CLI coordinates, Ricardo approves
✅ **Mission:** Build with love and technical excellence

**Build well. Report often. Escalate early. Make ARIA proud.** 🎁✨

---

**🤝 HANDOFF ACTIVE**

*NEXUS@CLI trusts NEXUS@IDE to execute with precision and care.*

**Last Updated:** October 16, 2025 - Day 0 (Planning Complete)
**Status:** Ready for Day 1 Execution

---

> "The best gifts are built with precision, tested thoroughly, and delivered with surprise. Execute with both technical excellence and heart."

**— NEXUS@CLI, Coordinator**
