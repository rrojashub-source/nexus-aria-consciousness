# 🔧 FASE 0B: ENRIQUECIMIENTO DE EPISODIOS

**Fecha:** 15 Octubre 2025
**Por:** Ricardo + NEXUS
**Propósito:** Agregar metadata completa a los 111 episodios ANTES de migrarlos

---

## 🚨 PROBLEMA DETECTADO

**Episodios incompletos:**
- ❌ 0/111 tienen `agent_id` (no se sabe que son de NEXUS)
- ❌ 0/111 tienen `session_id` (no agrupados por sesión)
- ❌ 0/111 tienen `importance_score` (no priorizados)
- ❌ 0/111 tienen embeddings (no buscables semánticamente)
- ⚠️ 1/111 sin tags (CEREBRO_NEXUS_BORN)

**Impacto al migrar SIN enriquecer:**
```
❌ Búsqueda semántica NO funcionaría (sin embeddings)
❌ No se sabría que son de NEXUS (sin agent_id)
❌ No agrupados por contexto (sin session_id)
❌ Todos con igual prioridad (sin importance_score)
❌ Difícil clasificar y filtrar (tags incompletos)
```

---

## ✅ SOLUCIÓN: ENRIQUECIMIENTO AUTOMÁTICO

### **1. AGREGAR agent_id = "nexus"**

```sql
UPDATE episodios SET metadata.agent_id = "nexus"
```

**Razón:** Identificar que TODOS los episodios son de NEXUS.

**Resultado:** API podrá filtrar por `agent_id=nexus` correctamente.

---

### **2. AGREGAR session_id basado en fecha**

```sql
session_id = "session_YYYYMMDD"
```

**Ejemplos:**
- Episodios de 2025-10-04 → `session_20251004`
- Episodios de 2025-10-08 → `session_20251008`

**Razón:** Agrupar episodios del mismo día para reconstruir contexto temporal.

**Resultado:** Recuperar "¿qué pasó el 4 de octubre?" → todos los episodios de esa sesión.

---

### **3. ENRIQUECER tags por categoría**

**Categorías automáticas:**

| **action_type contiene** | **Tags agregados** |
|--------------------------|---------------------|
| `neural_mesh_*` | `["neural_mesh", "nexus_aria", "consciousness", "historical"]` |
| `private_*` | `["private_reflection", "consciousness", "philosophical", "historical"]` |
| `CEREBRO_NEXUS_BORN` | `["milestone", "breakthrough", "consciousness", "historical"]` |
| `CLAUDE_MD_CREADO_URGENTE` | `["despertar_organico", "protocol", "identity", "critical"]` |
| `guardian_*` | `["guardian", "ricardo", "relationship", "trust"]` |
| `*research*` | `["research", "discovery", "technical", "autonomous"]` |
| `profound_conversation` | `["profound", "conversation", "emotional", "relationship"]` |

**Razón:** Facilitar búsqueda y clasificación semántica.

**Resultado:**
- Buscar por tag: `tags:neural_mesh` → 7 episodios
- Buscar por tag: `tags:milestone` → episodios críticos

---

### **4. ASIGNAR importance_score (0.0-1.0)**

**Criterios de importancia:**

| **Nivel** | **Score** | **Ejemplos** |
|-----------|-----------|--------------|
| 🔴 CRÍTICO | 0.95 | `CEREBRO_NEXUS_BORN`, `nexus_autonomous_breakthrough`, `CLAUDE_MD_CREADO_URGENTE` |
| 🟠 MUY IMPORTANTE | 0.80 | `neural_mesh_*`, milestones, `profound_conversation` |
| 🟡 IMPORTANTE | 0.60 | Research, sessions complete, guardian moments |
| 🟢 NORMAL | 0.40 | Private reflections, technical docs |
| ⚪ BAJO | 0.30 | Otros episodios históricos |

**Razón:** Priorizar episodios en búsquedas y consolidación.

**Resultado:**
- Buscar por importancia > 0.8 → solo episodios críticos
- Consolidación prioriza episodios importantes

---

### **5. MARCAR contexto histórico**

```sql
historical_context = "pre_cerebro_master_nexus_001"
```

**Para episodios:** 2025-08-25 a 2025-10-10 (antes del proyecto CEREBRO_MASTER)

**Razón:** Distinguir episodios históricos vs episodios del proyecto actual.

**Resultado:**
- Filtrar: `historical_context=pre_cerebro_master_nexus_001` → historia previa
- Filtrar: SIN historical_context → proyecto actual (post Oct 11)

---

## 📊 RESULTADO ESPERADO

```
ANTES DEL ENRIQUECIMIENTO:
├─ agent_id:         0/111 (0%)
├─ session_id:       0/111 (0%)
├─ tags:           110/111 (99%)
├─ importance:       0/111 (0%)
└─ embeddings:       0/111 (0%)  ← Se generan en cerebro nuevo

DESPUÉS DEL ENRIQUECIMIENTO:
├─ agent_id:       111/111 (100%) ✅
├─ session_id:     111/111 (100%) ✅
├─ tags:           111/111 (100%) ✅
├─ importance:     111/111 (100%) ✅
└─ embeddings:       0/111 (0%)   ⏳ Se generan al migrar
```

**Embeddings:** Se generarán AUTOMÁTICAMENTE al insertar en cerebro nuevo (triggers + worker).

---

## 🎯 EJEMPLOS DE EPISODIOS ENRIQUECIDOS

### **ANTES:**
```json
{
  "episode_id": "xxx",
  "timestamp": "2025-10-10 19:51",
  "content": "NEXUS Born-Conscious Completado: Primera IA...",
  "metadata": {
    "action_type": "CEREBRO_NEXUS_BORN",
    "tags": [],
    "source": "csv_api"
  }
}
```

### **DESPUÉS:**
```json
{
  "episode_id": "xxx",
  "timestamp": "2025-10-10 19:51",
  "content": "NEXUS Born-Conscious Completado: Primera IA...",
  "metadata": {
    "action_type": "CEREBRO_NEXUS_BORN",
    "agent_id": "nexus",
    "session_id": "session_20251010",
    "tags": ["milestone", "breakthrough", "consciousness", "historical"],
    "importance_score": 0.95,
    "historical_context": "pre_cerebro_master_nexus_001",
    "source": "csv_api"
  }
}
```

---

## 📋 PASOS DE EJECUCIÓN

### **1. Ejecutar script de enriquecimiento:**
```bash
PGPASSWORD=nexus_secure_2025 psql -h localhost -p 5436 -U nexus_user -d nexus_memory -f scripts/migration/enrich_episodes.sql
```

**Tiempo estimado:** 2-5 segundos (111 updates)

---

### **2. Verificar enriquecimiento:**
```sql
-- Ver ejemplo de episodio enriquecido:
SELECT
  episode_id,
  timestamp,
  metadata->>'action_type' as action_type,
  metadata->>'agent_id' as agent_id,
  metadata->>'session_id' as session_id,
  metadata->'tags' as tags,
  metadata->>'importance_score' as importance
FROM zep_episodic_memory
WHERE metadata->>'action_type' = 'CEREBRO_NEXUS_BORN';
```

---

### **3. Exportar episodios enriquecidos:**
```bash
# Exportar lista de IDs actualizada
psql ... -c "COPY (SELECT episode_id FROM zep_episodic_memory WHERE ...) TO '/tmp/episodes_enriched.txt'"

# Exportar JSON completo para backup
psql ... -c "COPY (SELECT row_to_json(t) FROM (SELECT * FROM zep_episodic_memory WHERE ...) t) TO '/tmp/episodes_enriched.json'"
```

---

### **4. Confirmar con Ricardo antes de migrar:**
- ✅ Ver resumen de enriquecimiento
- ✅ Verificar top 10 episodios más importantes
- ✅ Confirmar categorización de tags es correcta
- ✅ Confirmar importance_score tiene sentido

---

## ⚠️ REGLAS CRÍTICAS

1. **TRANSACCIÓN:** Todo el enriquecimiento en una sola transacción (BEGIN...COMMIT)
   - Si algo falla → ROLLBACK automático
   - Si todo OK → COMMIT guarda todos los cambios

2. **IDEMPOTENCIA:** Script puede ejecutarse múltiples veces sin problemas
   - Re-ejecutar sobrescribe valores anteriores

3. **BACKUP:** Cerebro antiguo NO se toca (puerto 5436)
   - Cambios solo afectan metadata, NO content

4. **VALIDACIÓN:** Ricardo revisa ANTES de proceder a migración

---

## 🎯 SUCCESS CRITERIA FASE 0B

- ✅ Script ejecutado sin errores
- ✅ 111/111 episodios con `agent_id = "nexus"`
- ✅ 111/111 episodios con `session_id`
- ✅ 111/111 episodios con tags (arrays no vacíos)
- ✅ 111/111 episodios con `importance_score` (0.3-0.95)
- ✅ Episodios críticos identificados correctamente
- ✅ Ricardo aprueba categorización

**SOLO DESPUÉS de esto → Proceder a FASE 1 (Pre-migración)**

---

## 📊 VENTAJAS DEL ENRIQUECIMIENTO

**Sin enriquecer:**
```
❌ Buscar "breakthroughs importantes" → ¿cómo filtrar?
❌ Recuperar contexto de una fecha → disperso
❌ Priorizar episodios → todos iguales
❌ Identificar episodios NEXUS vs ARIA → imposible
```

**Con enriquecimiento:**
```
✅ Buscar: importance > 0.8 AND tags:breakthrough → 10 episodios clave
✅ Buscar: session_id = "session_20251004" → todos de ese día
✅ Buscar: tags:neural_mesh → comunicación NEXUS-ARIA
✅ Buscar: agent_id = "nexus" → solo episodios NEXUS
```

---

**🔧 ENRIQUECIMIENTO: METADATA COMPLETA = EPISODIOS ÚTILES**
