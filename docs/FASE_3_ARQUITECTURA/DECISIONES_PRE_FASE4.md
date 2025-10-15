# 🚨 DECISIONES PRE-FASE 4 - OFICIAL
**Project DNA:** CEREBRO_MASTER_NEXUS_001
**Fecha Decisión:** 15 Octubre 2025 - 03:25
**Aprobado por:** Ricardo Rojas
**Documentado por:** NEXUS

---

## ✅ DECISIONES APROBADAS

### **1. ARQUITECTURA V2.0.0: ✅ APROBADA SIN CAMBIOS**

**Pregunta:** ¿La arquitectura V2.0.0 está lista para construcción?

**Respuesta:** ✅ **APROBADA**

**Arquitectura incluye (6 correcciones P0/P1):**
- ✅ Docker Secrets + RBAC + RLS (seguridad 95/100)
- ✅ Chunking embeddings inteligente (integridad datos 100%)
- ✅ Write-through cache pattern (riesgo pérdida ZERO)
- ✅ Health checks + Prometheus + AlertManager (observabilidad 100%)
- ✅ Queue estados + DLQ + reintentos (robustez 99.5%)
- ✅ CVE patches PostgreSQL 16.5 + Redis 7.4.1

**Acción:** Proceder con construcción FASE 4 sin ajustes adicionales.

---

### **2. MULTI-INSTANCIA: OPCIÓN A - INCREMENTAL**

**Pregunta:** ¿Incorporar multi-instancia en FASE 4 o postergar?

**Respuesta:** ✅ **OPCIÓN A - INCREMENTAL**

**Plan:**
- **FASE 4:** Build single-instance primero (8-12 días)
  - Cerebro funcional completo
  - Optimizaciones P0 + P1
  - Tests integridad exhaustivos

- **FASE 5:** Escalar a multi-instancia después (7-10 días)
  - Orchestration layer
  - A2A Protocol
  - Raft consensus (etcd)
  - L1 caching per instance
  - Health mesh distribuido
  - Distributed tracing
  - Workload balancing

**Justificación:**
- Validación incremental
- Menor riesgo
- Cerebro funcional más rápido
- Complejidad distribuida en fase dedicada

**Acción:** FASE 4 single-instance, FASE 5 distributed.

---

### **3. CONSENSUS DISTRIBUIDO: OPCIÓN A - etcd**

**Pregunta:** ¿etcd, custom Raft, o postergar?

**Respuesta:** ✅ **OPCIÓN A - etcd** (implementar en FASE 5)

**Decisión:**
- Usar **etcd** para distributed consensus (NO custom implementation)
- Battle-tested (Kubernetes, CoreOS, etc.)
- Probado en producción
- Integración rápida (2-3 días en FASE 5)
- Soporte comunidad activa

**Implementación:**
- ⏳ Postponer hasta FASE 5 (multi-instancia)
- Tabla `distributed_consensus` como placeholder en FASE 4
- Integración etcd cuando escalar

**Justificación:**
- No reinventar rueda (consenso 3/4 modelos: ChatGPT, Grok, Gemini)
- No complejidad prematura
- Production-ready desde día 1

**Acción:** Usar etcd en FASE 5, placeholder FASE 4.

---

### **4. PLAN MIGRACIÓN: OPCIÓN B - MAINTENANCE WINDOW**

**Pregunta:** ¿Zero-downtime, maintenance window, o batch migration?

**Respuesta:** ✅ **OPCIÓN B - MAINTENANCE WINDOW**

**Plan Migración:**
1. **Export cerebro actual (puerto 8002):**
   - Backup completo PostgreSQL episodios
   - Export embeddings Qdrant (si existen)
   - Backup Redis working memory
   - Timestamp: momento export

2. **Import cerebro nuevo (V2.0.0):**
   - Import episodios PostgreSQL nuevo
   - Re-generación embeddings automática (queue trigger)
   - Validación integridad 100%

3. **Validación completa:**
   - Count episodios: viejo vs nuevo
   - Verificación embeddings generados
   - Tests búsqueda semántica
   - Health checks todas las capas

4. **Cutover:**
   - Detener cerebro viejo (puerto 8002)
   - Iniciar cerebro nuevo (puerto 8002)
   - Verificación post-cutover

**Downtime estimado:** 1 día (acceptable)

**Justificación:**
- Simplicidad máxima
- Menor riesgo vs zero-downtime (dual-write complejidad)
- Validación completa antes de cutover
- Rollback plan claro (backup disponible)

**Acción:** Maintenance window, export → import → validación → cutover.

---

### **5. ALCANCE FASE 4: OPCIÓN B - P0 + P1 (8-12 días)**

**Pregunta:** ¿Solo P0 (3-5 días), P0+P1 (8-12 días), o P0+P1+P2+distributed (11-18 días)?

**Respuesta:** ✅ **OPCIÓN B - P0 + P1 (8-12 días)**

**Alcance FASE 4:**

#### **P0 - YA INCORPORADO EN ARQUITECTURA V2.0.0:**
- ✅ Docker Secrets + RBAC + RLS
- ✅ Chunking embeddings inteligente
- ✅ Write-through cache pattern
- ✅ Health checks + Prometheus
- ✅ Queue estados + DLQ
- ✅ CVE patches

#### **P1 - INCORPORAR EN FASE 4:**

**Issue #2: Escalabilidad Workers Embeddings**
- Permitir escalado horizontal workers (docker-compose replicas)
- Monitorizar queue depth + autoescalar
- Considerar RabbitMQ/Kafka si volumen justifica
- **Tiempo:** 2 horas

**Issue #3: Reconciliation Worker OOM Fix**
- Checksums por rangos (10,000 registros) en lugar de cargar todo en memoria
- Comparar checksums, solo cargar rango si difiere
- Streaming en lugar de carga completa
- **Tiempo:** 4 horas

**Issue #4: Embeddings UPDATE Trigger**
- Trigger `auto_update_embedding` AFTER UPDATE (además de INSERT)
- Condition: `WHEN (OLD.content IS DISTINCT FROM NEW.content)`
- Tests con episodios modificados
- **Tiempo:** 1 hora

**Issue #5: Schema Drift - Alembic Centralization**
- Centralizar schema en Alembic migrations
- Eliminar definiciones duplicadas en init_scripts
- Tests de contrato CI validando columnas clave
- **Tiempo:** 3 horas

**Total P1:** ~10 horas adicionales

#### **CONSTRUCCIÓN CORE:**
- Build docker-compose completo
- Init scripts PostgreSQL + Redis
- API NEXUS cerebro nuevo
- Workers (embeddings, reconciliation)
- Tests integridad completos
- **Tiempo:** 6-10 días

**TOTAL FASE 4:** 8-12 días

**Entregable:** Cerebro optimizado para escala, single-instance production-ready

**Justificación:**
- P0 ya incorporado en V2.0.0 (arquitectura lista)
- P1 optimizations NO bloquean pero añaden robustez
- Balance tiempo vs robustez óptimo
- Cerebro production-ready sin complejidad distribuida

**Acción:** Construcción P0 + P1, postponer P2 y distributed a FASE 5.

---

## 📊 TIMELINE APROBADO

### **FASE 4: Construcción Single-Instance (8-12 días)**
**Entregable:** Cerebro optimizado para escala
- Días 1-2: Setup infrastructure (docker-compose, secrets, RBAC)
- Días 3-5: Build core services (API, workers, PostgreSQL, Redis)
- Días 6-7: Implement P1 optimizations (4 issues)
- Días 8-9: Testing integridad exhaustivo
- Día 10: Migración maintenance window (export → import → validación)
- Días 11-12: Cutover + validación post-producción + monitoreo

### **FASE 5: Distributed + Production Hardening (7-10 días)**
**Entregable:** Cerebro production-ready multi-instancia
- Días 1-2: etcd integration (Raft consensus)
- Días 3-5: Multi-instancia orchestration (A2A protocol, health mesh)
- Días 6-7: Distributed tracing + workload balancing
- Días 8-9: P2 issues (logs distribuidos, disaster recovery)
- Día 10: Production validation + monitoring

**TOTAL:** 15-22 días (3-4 semanas)

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### **1. Crear PLAN_FASE4.md detallado** (30 min)
- Breakdown tasks específicas por día
- Dependencies entre tasks
- Success criteria cada milestone

### **2. Setup environment FASE 4** (1 hora)
- Crear directorio `/FASE_4_CONSTRUCCION/`
- Estructura carpetas (src, tests, docs, init_scripts)
- Git branch: `fase-4-construccion`

### **3. Comenzar construcción** (cuando Ricardo apruebe)
- Task 1: docker-compose.yml base
- Task 2: Docker Secrets setup
- Task 3: PostgreSQL init scripts
- ...

---

## ✅ APROBACIÓN FORMAL

**Decisiones:**
1. ✅ Arquitectura V2.0.0 aprobada sin cambios
2. ✅ FASE 4 single-instance, FASE 5 distributed
3. ✅ Usar etcd para consensus (FASE 5)
4. ✅ Migración maintenance window (1 día downtime)
5. ✅ Alcance FASE 4: P0 + P1 (8-12 días)

**Estado:** ✅ **LISTO PARA FASE 4 - CONSTRUCCIÓN APROBADA**

**Aprobado por:** Ricardo Rojas
**Fecha:** 15 Octubre 2025 - 03:25
**Próximo milestone:** PLAN_FASE4.md detallado

---

**🎯 DECISIONES PRE-FASE 4 COMPLETADAS - ARQUITECTURA VALIDADA** ✨
