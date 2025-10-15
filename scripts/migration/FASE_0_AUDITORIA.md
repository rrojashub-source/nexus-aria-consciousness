# 🔍 FASE 0: AUDITORÍA DE EPISODIOS PRE-MIGRACIÓN

**Fecha:** 15 Octubre 2025
**Por:** Ricardo + NEXUS
**Propósito:** Filtrar basura ANTES de migrar al cerebro nuevo

---

## 🚨 PROBLEMA DETECTADO

**Contaminación Masiva:**
```
API Stats:       103 episodios
PostgreSQL:    4,704 episodios
Diferencia:    4,601 episodios ocultos/corruptos
```

**Distribución de Basura:**
- **nexus_shadow_checkpoint:** 3,974 (84%) ← Shadow memory checkpoints automáticos
- **nexus_pre_compaction_checkpoint:** 378 (8%) ← Pre-compaction basura
- **Sin action_type:** 25 (1%) ← Episodios malformados
- **TOTAL BASURA:** 4,377 episodios (93%)

**Episodios Relevantes:** ~327 (7%)

---

## ✅ CRITERIOS DE FILTRADO

### **INCLUIR (Whitelist):**

```sql
-- Episodios del proyecto CEREBRO_MASTER_NEXUS_001
metadata->>'tags' LIKE '%cerebro_master_nexus_001%'

-- Episodios construcción FASE 4
metadata->>'action_type' LIKE 'fase4_%'

-- Milestones y proyectos importantes
metadata->>'action_type' IN (
  'project_milestone',
  'project_genesis_master_cerebro',
  'project_phase_completion',
  'milestone_completed',
  'cerebro_master_milestone'
)

-- Episodios Neural Mesh (comunicación NEXUS-ARIA)
metadata->>'action_type' LIKE 'neural_mesh_%'

-- Auditoría forense
metadata->>'action_type' LIKE 'forensic_audit_%'

-- Genesis history
metadata->>'action_type' LIKE '%genesis%'

-- Bugs críticos
metadata->>'action_type' = 'critical_bug_report'

-- Fecha: Solo desde inicio proyecto CEREBRO_MASTER
timestamp >= '2025-08-25'
```

### **EXCLUIR (Blacklist):**

```sql
-- Shadow memory checkpoints (3,974 episodios)
metadata->>'action_type' = 'nexus_shadow_checkpoint'

-- Pre-compaction checkpoints (378 episodios)
metadata->>'action_type' = 'nexus_pre_compaction_checkpoint'

-- Episodios malformados
metadata IS NULL OR metadata = '{}'

-- Episodios sin content
content IS NULL OR content = ''

-- Episodios antes del proyecto
timestamp < '2025-08-25'
```

---

## 📊 SCRIPT DE AUDITORÍA

```bash
#!/bin/bash
# audit_episodes.sh

PGPASSWORD=nexus_secure_2025 psql -h localhost -p 5436 -U nexus_user -d nexus_memory <<EOF

-- 1. RESUMEN GENERAL
\echo '═══════════════════════════════════════════════════════════'
\echo '📊 AUDITORÍA DE EPISODIOS - RESUMEN GENERAL'
\echo '═══════════════════════════════════════════════════════════'

SELECT
  'TOTAL EPISODIOS' as category,
  COUNT(*) as count
FROM zep_episodic_memory
UNION ALL
SELECT
  'BASURA (shadow/compaction)' as category,
  COUNT(*) as count
FROM zep_episodic_memory
WHERE metadata->>'action_type' IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')
UNION ALL
SELECT
  'MALFORMADOS (sin metadata)' as category,
  COUNT(*) as count
FROM zep_episodic_memory
WHERE metadata IS NULL OR metadata = '{}'
UNION ALL
SELECT
  'ANTIGUOS (< 2025-08-25)' as category,
  COUNT(*) as count
FROM zep_episodic_memory
WHERE timestamp < '2025-08-25'
ORDER BY count DESC;

-- 2. EPISODIOS RELEVANTES (Whitelist)
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '✅ EPISODIOS RELEVANTES PARA MIGRACIÓN'
\echo '═══════════════════════════════════════════════════════════'

SELECT
  CASE
    WHEN metadata->>'action_type' LIKE 'fase4_%' THEN 'FASE 4 Construcción'
    WHEN metadata->>'action_type' LIKE 'neural_mesh_%' THEN 'Neural Mesh'
    WHEN metadata->>'action_type' LIKE '%milestone%' THEN 'Milestones'
    WHEN metadata->>'action_type' LIKE '%genesis%' THEN 'Genesis History'
    WHEN metadata->>'action_type' LIKE 'forensic_%' THEN 'Forensic Audit'
    WHEN metadata->>'tags' LIKE '%cerebro_master_nexus_001%' THEN 'Proyecto Master'
    ELSE 'Otros Relevantes'
  END as category,
  COUNT(*) as count
FROM zep_episodic_memory
WHERE
  timestamp >= '2025-08-25'
  AND metadata IS NOT NULL
  AND metadata != '{}'
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')
GROUP BY category
ORDER BY count DESC;

-- 3. TOP 20 EPISODIOS MÁS RECIENTES RELEVANTES
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '📋 TOP 20 EPISODIOS RECIENTES RELEVANTES'
\echo '═══════════════════════════════════════════════════════════'

SELECT
  TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI') as timestamp,
  metadata->>'action_type' as action_type,
  LEFT(content, 60) || '...' as content_preview
FROM zep_episodic_memory
WHERE
  timestamp >= '2025-08-25'
  AND metadata IS NOT NULL
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')
ORDER BY timestamp DESC
LIMIT 20;

-- 4. EXPORTAR IDs PARA MIGRACIÓN
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '💾 EXPORTANDO IDs DE EPISODIOS VÁLIDOS'
\echo '═══════════════════════════════════════════════════════════'

\copy (SELECT episode_id FROM zep_episodic_memory WHERE timestamp >= '2025-08-25' AND metadata IS NOT NULL AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')) TO '/tmp/episodes_to_migrate.txt'

SELECT COUNT(*) || ' episodios válidos exportados a /tmp/episodes_to_migrate.txt' as resultado;

EOF
```

---

## 🎯 RESULTADO ESPERADO

```
📊 AUDITORÍA:
├─ Total episodios:           4,704
├─ Basura (shadow/compact):   4,352
├─ Malformados:                  25
├─ Antiguos (< ago-25):       ~200
└─ VÁLIDOS PARA MIGRACIÓN:    ~150-300

✅ ACCIÓN: Migrar SOLO los episodios válidos
```

---

## 📋 PASOS EJECUCIÓN

### **1. Ejecutar auditoría:**
```bash
bash scripts/migration/audit_episodes.sh > audit_report.txt
cat audit_report.txt
```

### **2. Revisar reporte con Ricardo:**
- ¿Los números tienen sentido?
- ¿Falta alguna categoría importante?
- ¿Sobra algo que debería excluirse?

### **3. Ajustar filtros si necesario:**
- Modificar whitelist/blacklist según feedback
- Re-ejecutar auditoría

### **4. Confirmar lista final:**
- `/tmp/episodes_to_migrate.txt` contiene IDs válidos
- Verificar cantidad: debe ser ~150-300, NO 4,704

### **5. Proceder a FASE 1 (Pre-migración) solo después de aprobar auditoría**

---

## ⚠️ REGLAS CRÍTICAS

1. **NUNCA migrar sin auditoría previa**
2. **NUNCA asumir que todos los episodios son válidos**
3. **SIEMPRE validar conteo final con Ricardo**
4. **Si hay duda sobre un episodio → EXCLUIR (mejor perder 1 episodio que contaminar con 1,000)**

---

## 🎯 SUCCESS CRITERIA FASE 0

- ✅ Auditoría ejecutada completamente
- ✅ Basura identificada (shadow checkpoints, etc.)
- ✅ Whitelist de episodios válidos creada
- ✅ Conteo final ~150-300 episodios (NO 4,704)
- ✅ Ricardo aprueba lista de episodios a migrar
- ✅ `/tmp/episodes_to_migrate.txt` generado

**SOLO DESPUÉS de esto → Proceder a FASE 1**

---

**🛡️ PROTECCIÓN CEREBRO NUEVO: ACTIVADA**
