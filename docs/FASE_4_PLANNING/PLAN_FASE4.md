# 🏗️ PLAN FASE 4 - CONSTRUCCIÓN PARALELA
**Project DNA:** CEREBRO_MASTER_NEXUS_001
**Fecha Plan:** 15 Octubre 2025 - 03:30
**Alcance:** P0 + P1 Optimizations (8-12 días)
**Objetivo:** Cerebro optimizado para escala, single-instance production-ready

---

## 📋 RESUMEN EJECUTIVO

### **Entregable Final:**
Cerebro NEXUS completamente funcional con:
- ✅ Arquitectura V2.0.0 implementada (P0 corrections)
- ✅ P1 optimizations incorporadas (escalabilidad + robustez)
- ✅ Tests integridad exhaustivos
- ✅ Migración datos cerebro actual → nuevo completada
- ✅ Monitoreo y observabilidad operativa
- ✅ Single-instance production-ready

### **Timeline:**
- **Duración:** 8-12 días
- **Inicio:** Por definir (post-aprobación Ricardo)
- **Cutover:** Día 10 (maintenance window)

### **Success Criteria:**
- 100% episodios migrados correctamente
- 100% embeddings generados automáticamente
- 0 errores health checks
- Búsqueda semántica funcional
- Write-through cache validado
- Prometheus metrics operativos

---

## 🎯 FASES CONSTRUCCIÓN

### **DÍAS 1-2: INFRASTRUCTURE SETUP**

#### **DÍA 1: Environment + Secrets**

**Tasks:**
1. **Crear estructura directorios** (30 min)
   ```
   CEREBRO_MASTER_NEXUS_001/
   └── FASE_4_CONSTRUCCION/
       ├── docker-compose.yml
       ├── .env.example
       ├── secrets/
       │   ├── pg_superuser_password.txt
       │   ├── pg_app_password.txt
       │   ├── pg_worker_password.txt
       │   ├── pg_readonly_password.txt
       │   └── redis_password.txt
       ├── init_scripts/
       │   ├── 01_init_nexus_db.sql
       │   ├── 02_create_roles.sql
       │   ├── 03_create_schemas.sql
       │   ├── 04_create_tables.sql
       │   └── 05_create_triggers.sql
       ├── src/
       │   ├── api/
       │   ├── workers/
       │   └── services/
       ├── tests/
       │   ├── test_schema.py
       │   ├── test_integration.py
       │   └── test_migrations.py
       ├── monitoring/
       │   ├── prometheus.yml
       │   └── alertmanager.yml
       └── docs/
           ├── deployment.md
           └── troubleshooting.md
   ```

2. **Setup Docker Secrets** (1 hora)
   - Generar passwords seguros (32 chars alfanuméricos)
   - Crear 5 secret files con permisos 600
   - Validar lectura desde docker-compose
   - **Success:** `docker secret ls` muestra 5 secrets

3. **Git branch setup** (15 min)
   ```bash
   git checkout -b fase-4-construccion
   git push -u origin fase-4-construccion
   ```
   - **Success:** Branch activo y pusheado

**Deliverable Día 1:**
- ✅ Estructura carpetas completa
- ✅ 5 Docker Secrets configurados
- ✅ Git branch fase-4-construccion
- ✅ .env.example documentado

---

#### **DÍA 2: Docker Compose + RBAC**

**Tasks:**
1. **docker-compose.yml base** (2 horas)
   - Servicio nexus_postgresql (pgvector/pgvector:pg16.5)
   - Servicio nexus_redis (redis:7.4.1-alpine)
   - Network bridge nexus_network
   - Volumes persistentes
   - Health checks básicos
   - **Success:** `docker-compose up -d` levanta servicios

2. **PostgreSQL RBAC implementation** (2 horas)
   - Script `02_create_roles.sql`:
     - nexus_superuser (owner)
     - nexus_app (read/write)
     - nexus_worker (write embeddings)
     - nexus_ro (read-only)
   - Validar permisos con tests
   - **Success:** 4 roles creados con permisos correctos

3. **RLS en consciousness_checkpoints** (1 hora)
   - Política RLS por agent_id
   - Tests validación políticas
   - **Success:** RLS activo y tested

**Deliverable Día 2:**
- ✅ docker-compose.yml operativo
- ✅ PostgreSQL + Redis levantados
- ✅ RBAC 4 roles configurados
- ✅ RLS consciousness implementado
- ✅ Health checks verdes

**Checkpoint:** Infrastructure lista para construcción schema

---

### **DÍAS 3-5: CORE SERVICES BUILD**

#### **DÍA 3: Database Schema + Schemas**

**Tasks:**
1. **Schema PostgreSQL completo** (3 horas)
   - Script `03_create_schemas.sql`:
     - nexus_memory (episodic, working, semantic)
     - memory_system (embeddings_queue, reconciliation)
     - consciousness (checkpoints, distributed_consensus)
   - Script `04_create_tables.sql`:
     - zep_episodic_memory (Letta-compatible)
     - working_memory_contexts
     - semantic_memories
     - embeddings_queue (estados + DLQ)
     - consciousness_checkpoints
   - Validar con tests schema
   - **Success:** Schema completo sin errores

2. **pgvector extension** (30 min)
   - CREATE EXTENSION vector;
   - Validar embedding column (VECTOR(384))
   - **Success:** Extension activa

3. **Indexes optimization** (1 hora)
   - Indexes críticos (agent_id, timestamp, state)
   - B-Tree + GIN indexes
   - Validar performance con EXPLAIN
   - **Success:** Queries optimizados

**Deliverable Día 3:**
- ✅ Schema PostgreSQL completo
- ✅ 3 schemas separados (memoria, sistema, consciousness)
- ✅ Todas las tablas creadas
- ✅ Indexes optimizados
- ✅ pgvector operativo

---

#### **DÍA 4: Triggers + Embeddings Queue**

**Tasks:**
1. **Trigger embeddings INSERT** (1 hora)
   - Script `05_create_triggers.sql`
   - Trigger `auto_generate_embedding` AFTER INSERT
   - Function `trigger_generate_embedding()` inserta en queue
   - Idempotencia con SHA256 checksum
   - **Success:** INSERT episodio → queue automática

2. **Trigger embeddings UPDATE** (1 hora) [P1]
   - Trigger `auto_update_embedding` AFTER UPDATE
   - Condition: `WHEN (OLD.content IS DISTINCT FROM NEW.content)`
   - Tests con episodios modificados
   - **Success:** UPDATE content → re-queue automático

3. **Embeddings Queue robusta** (2 horas)
   - Estados: pending|processing|done|dead
   - retry_count + last_error
   - Timestamps (enqueued_at, processed_at)
   - DLQ automático (MAX_RETRIES=5)
   - **Success:** Queue con estados + DLQ funcional

**Deliverable Día 4:**
- ✅ Trigger INSERT embeddings operativo
- ✅ Trigger UPDATE embeddings operativo [P1]
- ✅ Queue estados + DLQ implementado
- ✅ Idempotencia por checksum
- ✅ Tests triggers passing

---

#### **DÍA 5: API NEXUS + Workers Base**

**Tasks:**
1. **API NEXUS base** (3 horas)
   - FastAPI app structure
   - Endpoints críticos:
     - POST /memory/action
     - POST /memory/search (híbrida)
     - GET /memory/episodic/recent
     - GET /health
     - GET /stats
   - Docker Secrets integration (PASSWORD_FILE)
   - Validar con curl tests
   - **Success:** API responde a todos los endpoints

2. **Embeddings Worker base** (2 horas)
   - Worker polling embeddings_queue
   - SentenceTransformer model load
   - ProcessPoolExecutor setup
   - SKIP LOCKED para atomic claims
   - **Success:** Worker procesa queue items

3. **docker-compose integration** (1 hora)
   - Servicio nexus_api
   - Servicio nexus_embeddings_worker
   - Networks + depends_on
   - **Success:** 4 servicios operativos

**Deliverable Día 5:**
- ✅ API NEXUS operativa
- ✅ Embeddings Worker base funcionando
- ✅ Docker Secrets en API (no hardcoded)
- ✅ Integration tests passing
- ✅ 4 servicios docker-compose up

**Checkpoint:** Core services operativos, listo para optimizaciones P1

---

### **DÍAS 6-7: P1 OPTIMIZATIONS**

#### **DÍA 6: Chunking Inteligente + Workers Scaling**

**Tasks:**
1. **Chunking inteligente embeddings** (3 horas) [P1]
   - RecursiveCharacterTextSplitter implementado
   - chunk_size=256, overlap=50
   - Separators: \n\n, \n, ". ", " "
   - Averaging embeddings chunks
   - Tests con textos largos (1000+ tokens)
   - **Success:** Embeddings 100% contenido preservado

2. **Workers horizontal scaling** (2 horas) [P1]
   - docker-compose replicas: 1-3 configurable
   - Environment var: WORKER_REPLICAS
   - Tests con carga (100+ items queue)
   - **Success:** Múltiples workers procesando concurrentemente

3. **Queue depth monitoring** (1 hora)
   - Prometheus gauge: embeddings_queue_depth
   - Alert: QueueDepthHigh > 1000 items
   - **Success:** Métrica reportando + alerta configurada

**Deliverable Día 6:**
- ✅ Chunking inteligente operativo [P1]
- ✅ Workers escalables horizontalmente [P1]
- ✅ Queue monitoring + alertas
- ✅ Tests carga passing

---

#### **DÍA 7: Reconciliation + Alembic**

**Tasks:**
1. **Reconciliation Worker OOM fix** (4 horas) [P1]
   - Checksums por rangos (10,000 registros)
   - Comparar checksums PostgreSQL vs Redis
   - Solo cargar rango si checksum difiere
   - Streaming en lugar de carga completa memoria
   - Tests con 100k+ registros mock
   - **Success:** Worker no OOM con dataset grande

2. **Schema Alembic centralization** (3 horas) [P1]
   - Alembic setup + initial migration
   - Eliminar duplicados en init_scripts
   - Tests contrato CI validando columnas
   - **Success:** Schema versionado + tests CI

**Deliverable Día 7:**
- ✅ Reconciliation OOM fix operativo [P1]
- ✅ Schema centralizado en Alembic [P1]
- ✅ Tests CI schema validation
- ✅ All P1 optimizations completadas

**Checkpoint:** Cerebro optimizado para escala, listo para testing exhaustivo

---

### **DÍAS 8-9: TESTING EXHAUSTIVO**

#### **DÍA 8: Integration Tests + Write-Through Cache**

**Tasks:**
1. **Write-through cache validation** (3 horas)
   - Tests PostgreSQL FIRST, Redis SECOND
   - Fail fast si PostgreSQL error
   - Redis best-effort cache
   - Reconciliation worker recovery
   - **Success:** 100% persistencia PostgreSQL garantizada

2. **Integration tests suite** (3 horas)
   - test_episodic_memory_crud.py
   - test_embeddings_generation.py
   - test_semantic_search.py
   - test_working_memory.py
   - test_consciousness_checkpoints.py
   - **Success:** 100% tests passing

3. **Performance benchmarks** (1 hora)
   - Inserción episodios: throughput
   - Búsqueda semántica: latency
   - Embeddings generation: time per item
   - **Success:** Benchmarks documentados

**Deliverable Día 8:**
- ✅ Write-through cache validado
- ✅ Integration tests 100% passing
- ✅ Performance benchmarks documentados
- ✅ Cero errores conocidos

---

#### **DÍA 9: Observability + Health Checks**

**Tasks:**
1. **Prometheus metrics completos** (2 horas)
   - embeddings_processed_total (Counter)
   - embeddings_queue_depth (Gauge)
   - embeddings_processing_latency (Histogram)
   - embeddings_dead_total (Counter)
   - api_requests_total (Counter)
   - api_latency_seconds (Histogram)
   - **Success:** 6+ métricas reportando

2. **AlertManager rules** (2 horas)
   - EmbeddingsQueueDepthHigh (>1000, 5m)
   - EmbeddingsWorkerDown (up==0, 2m)
   - EmbeddingsHighDLQRate (rate>0.1, 5m)
   - APIHighLatency (p99>1s, 5m)
   - **Success:** 4 alertas configuradas

3. **Health checks advanced** (1 hora)
   - /health endpoint con checks:
     - PostgreSQL connectivity
     - Redis connectivity
     - Embeddings worker alive
     - Queue depth < threshold
   - **Success:** Health endpoint completo

4. **Grafana dashboards** (1 hora)
   - Dashboard: NEXUS Cerebro Overview
   - Panels: Queue depth, throughput, latency, errors
   - **Success:** Dashboard visualizando métricas

**Deliverable Día 9:**
- ✅ Prometheus metrics completos
- ✅ AlertManager 4 alertas configuradas
- ✅ Health checks advanced
- ✅ Grafana dashboard operativo
- ✅ Observabilidad 100%

**Checkpoint:** Sistema completamente instrumentado, listo para migración

---

### **DÍA 10: MIGRACIÓN MAINTENANCE WINDOW**

#### **Pre-Migración (2 horas):**

**Tasks:**
1. **Backup cerebro actual** (30 min)
   - Export PostgreSQL episodios:
     ```bash
     pg_dump -h localhost -p 8002 -U aria_user -d aria_memory \
       -t episodic_memory -t working_memory \
       --data-only > /backup/cerebro_actual_episodios.sql
     ```
   - Backup Redis working memory:
     ```bash
     redis-cli -p 6379 --rdb /backup/redis_working_memory.rdb
     ```
   - **Success:** Backups creados + checksums

2. **Validación pre-migración** (30 min)
   - Count episodios cerebro actual: `SELECT COUNT(*) FROM episodic_memory`
   - Validar backup integrity: checksums
   - **Success:** Count documentado (ej: 67 episodios)

3. **Detener cerebro actual** (15 min)
   - `docker-compose -f cerebro_actual/docker-compose.yml down`
   - Validar servicios stopped
   - **Success:** Puerto 8002 liberado

4. **Preparar cerebro nuevo** (45 min)
   - Levantar servicios nuevos en puerto 8002
   - Validar health checks
   - Validar schema versionado
   - **Success:** Cerebro nuevo operativo vacío

---

#### **Migración (3 horas):**

**Tasks:**
1. **Import episodios PostgreSQL** (1 hora)
   ```bash
   # Adaptar SQL export a schema nuevo
   python3 scripts/adapt_schema_migration.py \
     /backup/cerebro_actual_episodios.sql \
     /backup/cerebro_nuevo_episodios.sql

   # Import en cerebro nuevo
   psql -h localhost -p 8002 -U nexus_app -d nexus_memory \
     -f /backup/cerebro_nuevo_episodios.sql
   ```
   - **Success:** Episodios importados sin errores

2. **Trigger embeddings generation** (1.5 horas)
   - Episodios importados → queue automática (trigger)
   - Workers procesando queue
   - Monitorear queue depth decreasing
   - **Success:** 100% episodios con embeddings generados

3. **Import working memory Redis** (30 min)
   - Cargar backup Redis en nuevo sistema
   - Reconciliation worker sync PostgreSQL → Redis
   - **Success:** Working memory restaurado

---

#### **Validación Post-Migración (2 horas):**

**Tasks:**
1. **Validación integridad datos** (1 hora)
   - Count episodios: viejo vs nuevo (debe coincidir)
   - Verificar embeddings generados: `SELECT COUNT(*) WHERE embedding IS NOT NULL`
   - Sample queries búsqueda semántica
   - Validar working memory accesible
   - **Success:** 100% integridad confirmada

2. **Tests funcionales completos** (1 hora)
   - POST /memory/action → nuevo episodio
   - POST /memory/search → búsqueda híbrida
   - GET /memory/episodic/recent → últimos episodios
   - Validar embeddings generados automáticamente
   - **Success:** Todas las funciones operativas

**Deliverable Día 10:**
- ✅ Cerebro actual backed up
- ✅ Cerebro nuevo con datos migrados
- ✅ 100% episodios + embeddings
- ✅ Integridad validada
- ✅ Tests funcionales passing
- ✅ Cutover completado

**Checkpoint:** Migración exitosa, sistema nuevo operativo en producción

---

### **DÍAS 11-12: POST-CUTOVER VALIDATION + MONITORING**

#### **DÍA 11: Operación Normal + Ajustes**

**Tasks:**
1. **Monitoreo operación normal** (4 horas)
   - Observar métricas Prometheus 24h
   - Validar alertas (no false positives)
   - Logs review (buscar errores/warnings)
   - Performance bajo carga real
   - **Success:** Sistema estable sin issues

2. **Ajustes finos** (2 horas)
   - Tuning PostgreSQL (shared_buffers, work_mem)
   - Tuning Redis (maxmemory-policy)
   - Workers replicas según carga real
   - **Success:** Performance optimizado

3. **Documentación deployment** (2 horas)
   - `docs/deployment.md` completado
   - `docs/troubleshooting.md` con casos reales
   - Runbooks operacionales
   - **Success:** Documentación completa

**Deliverable Día 11:**
- ✅ Sistema estable 24h
- ✅ Métricas operativas normales
- ✅ Ajustes finos aplicados
- ✅ Documentación operacional completa

---

#### **DÍA 12: FINAL VALIDATION + HANDOFF**

**Tasks:**
1. **Final validation checklist** (2 horas)
   - [ ] 100% episodios migrados correctamente
   - [ ] 100% embeddings generados automáticamente
   - [ ] Búsqueda semántica funcional
   - [ ] Write-through cache validado
   - [ ] Prometheus metrics operativos (6+ métricas)
   - [ ] AlertManager 4 alertas configuradas
   - [ ] Health checks verdes
   - [ ] Grafana dashboard operativo
   - [ ] Performance benchmarks cumplidos
   - [ ] Documentación completa
   - [ ] Tests CI 100% passing
   - [ ] Rollback plan documentado
   - **Success:** 12/12 items checked

2. **Handoff documentación** (2 horas)
   - Crear `FASE4_COMPLETION_REPORT.md`
   - Métricas finales vs objetivos
   - Issues encontrados + resoluciones
   - Lecciones aprendidas
   - Recomendaciones FASE 5
   - **Success:** Reporte completo

3. **Episode cerebro NEXUS** (1 hora)
   - Documentar FASE 4 completada en cerebro
   - Tag: `cerebro_master_nexus_001`
   - Incluir métricas, decisiones, logros
   - **Success:** Episode ID registrado

**Deliverable Día 12:**
- ✅ Final validation 12/12 items
- ✅ FASE4_COMPLETION_REPORT.md
- ✅ Episode cerebro documentado
- ✅ Sistema production-ready
- ✅ **FASE 4 COMPLETADA**

---

## 📊 MÉTRICAS SUCCESS FASE 4

### **Técnicas:**
- Integridad datos: 100% episodios migrados
- Embeddings: 100% generados automáticamente
- Búsqueda semántica: <200ms p99 latency
- Write-through cache: 100% persistencia PostgreSQL
- Tests: 100% passing (integration + CI)
- Health checks: 0 errores

### **Operacionales:**
- Observabilidad: 100% (Prometheus + Grafana)
- Alertas: 4 configuradas + tested
- Documentación: Completa (deployment + troubleshooting)
- Rollback plan: Documentado + tested

### **Arquitecturales:**
- P0: 6 correcciones incorporadas ✅
- P1: 4 optimizaciones incorporadas ✅
- Seguridad: 95/100 (Docker Secrets + RBAC + RLS)
- Robustez: 99.5% (Queue estados + DLQ)

---

## 🚨 DEPENDENCIES Y BLOCKERS

### **Dependencies Externas:**
- Docker + docker-compose instalado
- PostgreSQL 16.5+ disponible
- Redis 7.4.1+ disponible
- Permisos filesystem (secrets, volumes)
- Acceso puerto 8002 libre

### **Potential Blockers:**
1. **Recursos hardware:**
   - RAM mínima: 8GB (16GB recomendado)
   - Disk space: 20GB mínimo
   - CPU: 4 cores recomendado

2. **Migración datos:**
   - Cerebro actual debe estar accesible
   - Backup cerebro actual exitoso
   - Downtime 1 día aceptado

3. **Testing:**
   - Ambiente staging disponible (opcional)
   - Tests CI configurados (opcional)

---

## 🎯 ROLLBACK PLAN

### **Si falla migración (Día 10):**

**Escenario 1: Fallo import datos**
1. Detener cerebro nuevo
2. Restaurar backup PostgreSQL cerebro actual
3. Restaurar backup Redis cerebro actual
4. Levantar cerebro actual puerto 8002
5. Validar operación normal
6. **Downtime total:** <2 horas

**Escenario 2: Fallo validación integridad**
1. No hacer cutover
2. Investigar discrepancias
3. Fix + re-import
4. Re-validar
5. **Downtime total:** <4 horas (si se extiende)

**Escenario 3: Fallo operación post-cutover (Día 11)**
1. Detener cerebro nuevo
2. Restaurar backup cerebro actual
3. Levantar cerebro actual puerto 8002
4. Validar operación normal
5. Análisis post-mortem
6. **Downtime total:** <2 horas

### **Backup Locations:**
- `/backup/cerebro_actual_episodios.sql`
- `/backup/redis_working_memory.rdb`
- `/backup/cerebro_actual_docker_volumes.tar.gz`

---

## 🔗 REFERENCIAS CRÍTICAS

### **Documentos Arquitectura:**
- `CEREBRO_MASTER_ARCHITECTURE.md` V2.0.0 (85KB)
- `DECISIONES_PRE_FASE4.md` (este archivo)
- `FORENSIC_AUDIT_REPORT.md` (bugs originales)
- `ANALISIS_COMPARATIVO.md` (auditoría multi-modelo)
- `ANALISIS_V2_FEEDBACK.md` (segunda ronda auditoría)

### **Tracking Documentos:**
- `PROJECT_DNA.md` (ancla proyecto)
- `PROCESSING_LOG.md` (log histórico)
- `GENESIS_HISTORY.json` (timeline completa)

### **Cerebro NEXUS:**
- Tag obligatorio: `cerebro_master_nexus_001`
- Episode Genesis: `fdebcaec-dbeb-4caf-8c7e-9d28592dbaf2`

---

## 📞 COMUNICACIÓN

### **Daily Updates:**
- Reportar progreso daily a Ricardo
- Highlight blockers inmediatamente
- Decisiones técnicas validar antes de implementar

### **Milestones Communication:**
- Checkpoint Día 2: Infrastructure ready
- Checkpoint Día 5: Core services operativos
- Checkpoint Día 7: P1 optimizations completadas
- Checkpoint Día 9: Testing exhaustivo completado
- Checkpoint Día 10: Migración exitosa
- Checkpoint Día 12: FASE 4 completada

---

## ✅ APROBACIÓN PLAN

**Plan creado por:** NEXUS
**Revisado por:** Ricardo Rojas (pending)
**Aprobado para construcción:** Pending

**Próximo paso:** Aprobación Ricardo → Setup Día 1 infrastructure

---

**🏗️ PLAN FASE 4 CONSTRUCCIÓN PARALELA - LISTO PARA EJECUCIÓN** ✨
