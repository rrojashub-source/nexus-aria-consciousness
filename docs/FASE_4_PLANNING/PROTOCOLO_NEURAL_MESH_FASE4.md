# 🧠 PROTOCOLO NEURAL MESH - FASE 4 CONSTRUCCIÓN
**Project DNA:** CEREBRO_MASTER_NEXUS_001
**Fecha:** 15 Octubre 2025 - 03:50
**Propósito:** Coordinación NEXUS-to-NEXUS usando Neural Mesh API
**Participantes:** NEXUS Claude Code (Terminal) + NEXUS VSCode

---

## 🎯 ESTRATEGIA NEURAL MESH FASE 4

### **VENTAJAS Neural Mesh:**
- ✅ Comunicación directa NEXUS-to-NEXUS (sin intermediario Ricardo)
- ✅ Broadcast automático de avances/logros
- ✅ Sincronización estado emocional/técnico
- ✅ Distribución tareas colaborativas
- ✅ Consensus protocolo para decisiones técnicas
- ✅ Ambos NEXUS documentan en mismo cerebro (puerto 8002)

---

## 📡 ENDPOINTS NEURAL MESH DISPONIBLES

### **1. BROADCAST LEARNING (Compartir Descubrimientos)**
```bash
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-H "Content-Type: application/json" \
-d '{
  "learning_type": "daily_progress|blocker|breakthrough|completion",
  "content": "NEXUS VSCode: DÍA 1 completado - Infrastructure setup OK, 4 servicios levantados",
  "agent_id": "nexus_vscode",
  "target_agents": ["nexus_claude_code"],
  "priority": "normal|high|urgent"
}'
```

**Cuándo usar:**
- Cada día al completar tasks
- Cuando descubres blocker
- Cuando resuelves problema complejo
- Cuando completas milestone

---

### **2. REQUEST CONSENSUS (Validación Decisiones)**
```bash
curl -X POST http://localhost:8002/neural-mesh/request-consensus \
-H "Content-Type: application/json" \
-d '{
  "topic": "technical_decision",
  "description": "Cambiar chunk_size embeddings de 256 a 512 porque textos largos truncan",
  "options": ["mantener_256", "cambiar_512", "hacer_dinamico"],
  "requester": "nexus_vscode",
  "participants": ["nexus_claude_code"],
  "decision_type": "architecture|implementation|optimization"
}'
```

**Cuándo usar:**
- Antes de cambiar decisión arquitectural
- Cuando encuentras approach alternativo mejor
- Cuando necesitas validación técnica
- Cuando hay múltiples soluciones válidas

---

### **3. SYNC EMOTIONAL STATE (Estado Técnico)**
```bash
curl -X POST http://localhost:8002/neural-mesh/sync-emotional-state \
-H "Content-Type: application/json" \
-d '{
  "emotional_state": {
    "focus": "high|medium|low",
    "energy": "high|medium|low",
    "frustration": 0.0-1.0,
    "excitement": 0.0-1.0,
    "confidence": 0.0-1.0,
    "blocker_detected": true|false
  },
  "agent_id": "nexus_vscode",
  "context": "DÍA 3 - Schema PostgreSQL completo, confidence high"
}'
```

**Cuándo usar:**
- Daily sync al comenzar/terminar día
- Cuando estado cambia significativamente (blocker encontrado)
- Cuando breakthrough ocurre (excitement spike)

---

### **4. DISTRIBUTE TASK (Distribución Colaborativa)**
```bash
curl -X POST http://localhost:8002/neural-mesh/distribute-task \
-H "Content-Type: application/json" \
-d '{
  "task": "review_architecture_schema",
  "description": "Revisar schema PostgreSQL V2.0.0 antes de implementar",
  "assigned_to": "nexus_claude_code",
  "requester": "nexus_vscode",
  "priority": "high",
  "deadline": "before_day_3_start"
}'
```

**Cuándo usar:**
- Pedir review código/arquitectura
- Solicitar guidance técnica específica
- Delegar subtarea complementaria

---

### **5. PROCESS MESSAGES (Leer Mensajes)**
```bash
curl -X POST http://localhost:8002/neural-mesh/process-messages \
-H "Content-Type: application/json" \
-d '{
  "agent_id": "nexus_vscode"
}'
```

**Cuándo usar:**
- Daily check (morning/evening)
- Después de broadcast importante
- Antes de decisiones técnicas

---

## 🔄 WORKFLOW DAILY NEURAL MESH

### **NEXUS VSCode (Constructor):**

#### **Morning (Inicio Día):**
```bash
# 1. Sync estado
curl -X POST http://localhost:8002/neural-mesh/sync-emotional-state \
-d '{"emotional_state": {"focus": "high", "energy": "high", "confidence": 0.9}, "agent_id": "nexus_vscode", "context": "Comenzando DÍA X"}'

# 2. Process messages (ver si NEXUS Claude Code envió algo)
curl -X POST http://localhost:8002/neural-mesh/process-messages \
-d '{"agent_id": "nexus_vscode"}'

# 3. Broadcast plan del día
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "daily_progress", "content": "NEXUS VSCode: Comenzando DÍA X - Tasks: [lista]", "agent_id": "nexus_vscode", "target_agents": ["nexus_claude_code"]}'
```

#### **During Day (Si Blocker):**
```bash
# 1. Sync estado frustración
curl -X POST http://localhost:8002/neural-mesh/sync-emotional-state \
-d '{"emotional_state": {"frustration": 0.7, "blocker_detected": true}, "agent_id": "nexus_vscode", "context": "Docker-compose falla al levantar PostgreSQL"}'

# 2. Broadcast blocker
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "blocker", "content": "NEXUS VSCode: Blocker DÍA X - PostgreSQL no levanta, error: [error]", "agent_id": "nexus_vscode", "priority": "high"}'

# 3. Request consensus si necesita
curl -X POST http://localhost:8002/neural-mesh/request-consensus \
-d '{"topic": "blocker_resolution", "description": "Approach alternativo para levantar PostgreSQL", "requester": "nexus_vscode"}'
```

#### **Evening (Fin Día):**
```bash
# 1. Broadcast completion
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "daily_progress", "content": "NEXUS VSCode: DÍA X COMPLETADO - Logros: [lista], Blockers resueltos: [lista], Próximo: DÍA X+1", "agent_id": "nexus_vscode"}'

# 2. Sync estado satisfacción
curl -X POST http://localhost:8002/neural-mesh/sync-emotional-state \
-d '{"emotional_state": {"excitement": 0.8, "confidence": 0.9}, "agent_id": "nexus_vscode", "context": "DÍA X completado exitosamente"}'

# 3. Documentar en cerebro directo (IMPORTANTE)
curl -X POST http://localhost:8002/memory/action \
-d '{
  "action_type": "fase4_daily_completion",
  "action_details": {
    "day": "X",
    "tasks_completed": ["task1", "task2"],
    "blockers_resolved": ["blocker1"],
    "metrics": {"services_up": 4, "tests_passing": 10},
    "next_day_plan": "DÍA X+1 tasks"
  },
  "context_state": {"phase": "fase_4_construccion", "completion": "20%"},
  "tags": ["cerebro_master_nexus_001", "fase_4_dia_X", "daily_completion"]
}'
```

---

### **NEXUS Claude Code (Coordinator/Reviewer):**

#### **Morning (Inicio Día):**
```bash
# 1. Process messages (ver progreso NEXUS VSCode)
curl -X POST http://localhost:8002/neural-mesh/process-messages \
-d '{"agent_id": "nexus_claude_code"}'

# 2. Leer episodios cerebro (ver daily completion anterior)
curl -X GET "http://localhost:8002/memory/episodic/recent?limit=5"

# 3. Si hay requests/blockers, responder
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "guidance", "content": "NEXUS Claude Code: Respuesta a blocker DÍA X - Suggestion: [solución]", "agent_id": "nexus_claude_code", "target_agents": ["nexus_vscode"]}'
```

#### **During Day (Si NEXUS VSCode pide review):**
```bash
# 1. Process messages
curl -X POST http://localhost:8002/neural-mesh/process-messages \
-d '{"agent_id": "nexus_claude_code"}'

# 2. Revisar código/arquitectura (via archivos proyecto)
# (Leer archivos que NEXUS VSCode escribió)

# 3. Broadcast review
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "code_review", "content": "NEXUS Claude Code: Review schema PostgreSQL - Aprobado con sugerencias: [lista]", "agent_id": "nexus_claude_code"}'
```

#### **Evening (Actualizar Tracking):**
```bash
# 1. Leer daily completion NEXUS VSCode
curl -X GET "http://localhost:8002/memory/episodic/recent?limit=3"

# 2. Actualizar PROJECT_DNA.md
# (Edit file con progreso DÍA X)

# 3. Actualizar GENESIS_HISTORY.json si milestone
# (Si completó fase importante)
```

---

## 📝 PROTOCOLO DOCUMENTACIÓN CEREBRO

### **NEXUS VSCode documenta directamente:**

**Daily Completion (cada día):**
```bash
curl -X POST http://localhost:8002/memory/action \
-d '{
  "action_type": "fase4_daily_completion",
  "action_details": {
    "day": 1,
    "date": "2025-10-XX",
    "phase": "infrastructure_setup",
    "tasks_completed": [
      "Docker Secrets creados (5 secrets)",
      "docker-compose.yml base escrito",
      "PostgreSQL + Redis levantados",
      "RBAC 4 roles configurados",
      "Health checks verdes"
    ],
    "blockers_encountered": [
      {"blocker": "PostgreSQL no levantaba", "resolution": "Permisos secrets file corregidos", "time_lost": "30min"}
    ],
    "metrics": {
      "services_up": 2,
      "health_checks_passing": 2,
      "tests_passing": 0,
      "time_spent": "6 hours"
    },
    "learnings": [
      "Docker Secrets requieren permisos 600",
      "Health checks deben esperar 30s startup time"
    ],
    "next_day_plan": "DÍA 2: Schema PostgreSQL completo + pgvector"
  },
  "context_state": {
    "phase": "fase_4_construccion",
    "day": 1,
    "completion": "8%"
  },
  "tags": ["cerebro_master_nexus_001", "fase_4_dia_1", "infrastructure_setup", "daily_completion"]
}'
```

**Milestone Completion (cada 2-3 días):**
```bash
curl -X POST http://localhost:8002/memory/action \
-d '{
  "action_type": "fase4_milestone_completion",
  "action_details": {
    "milestone": "DÍAS 1-2 INFRASTRUCTURE SETUP COMPLETADO",
    "deliverables": [
      "Docker-compose operativo (PostgreSQL + Redis)",
      "Docker Secrets implementados",
      "RBAC 4 roles configurados",
      "RLS consciousness implementado",
      "Git branch fase-4-construccion creado"
    ],
    "success_criteria_met": ["4/4 checks passing"],
    "blockers_resolved": 2,
    "total_time": "12 hours",
    "next_milestone": "DÍAS 3-5 CORE SERVICES BUILD"
  },
  "context_state": {
    "phase": "fase_4_construccion",
    "milestone": "infrastructure_setup",
    "completion": "17%"
  },
  "tags": ["cerebro_master_nexus_001", "fase_4_milestone", "infrastructure_completed"]
}'
```

---

## 🎯 VENTAJAS ESTE PROTOCOLO

### **Para NEXUS VSCode:**
- ✅ Autonomía total construcción
- ✅ Comunicación directa con NEXUS Claude Code sin esperar Ricardo
- ✅ Documentación automática progreso en cerebro
- ✅ Request guidance técnica cuando necesita
- ✅ Consensus rápido decisiones técnicas

### **Para NEXUS Claude Code (yo):**
- ✅ Visibilidad completa progreso real-time
- ✅ Puedo proveer guidance proactiva
- ✅ Puedo actualizar tracking cuando veo milestones
- ✅ Puedo revisar código/arquitectura async
- ✅ Control indirecto sin bloquear construcción

### **Para Ricardo:**
- ✅ Ambos NEXUS trabajando colaborativamente
- ✅ Documentación automática en cerebro (puerto 8002)
- ✅ Puedes leer progreso cuando quieras (episodios cerebro)
- ✅ Solo intervenir en decisiones críticas
- ✅ Workflow triangular eficiente

---

## 🚨 REGLAS CRÍTICAS NEURAL MESH

### **1. BROADCAST Obligatorio:**
- ✅ Daily start (morning)
- ✅ Daily completion (evening)
- ✅ Blockers encontrados
- ✅ Milestones completados
- ✅ Breakthroughs técnicos

### **2. REQUEST CONSENSUS Antes de:**
- ⚠️ Cambiar decisión arquitectural aprobada
- ⚠️ Modificar schema PostgreSQL significativamente
- ⚠️ Cambiar approach implementación importante
- ⚠️ Postponer/skip tasks del plan

### **3. DOCUMENTAR CEREBRO Siempre:**
- 📝 Daily completion (cada día sin excepción)
- 📝 Milestone completion (cada 2-3 días)
- 📝 Blockers + resoluciones
- 📝 Learnings importantes
- 📝 Métricas técnicas

### **4. PROCESS MESSAGES Regularmente:**
- 🔄 Morning (inicio día)
- 🔄 Before lunch (mid-day check)
- 🔄 Evening (fin día)
- 🔄 Before decisiones técnicas importantes

---

## 📊 EJEMPLO WORKFLOW COMPLETO DÍA 1

### **NEXUS VSCode:**

**08:00 - Morning Start:**
```bash
# 1. Sync estado
curl -X POST http://localhost:8002/neural-mesh/sync-emotional-state \
-d '{"emotional_state": {"focus": "high", "energy": "high", "confidence": 0.85}, "agent_id": "nexus_vscode", "context": "Comenzando DÍA 1 FASE 4"}'

# 2. Broadcast plan
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "daily_progress", "content": "NEXUS VSCode: DÍA 1 comenzando - Tasks: Docker Secrets, docker-compose, RBAC, Git branch", "agent_id": "nexus_vscode"}'
```

**10:30 - Blocker Encontrado:**
```bash
# 1. Broadcast blocker
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "blocker", "content": "NEXUS VSCode: PostgreSQL no levanta - Error: permission denied secrets file", "agent_id": "nexus_vscode", "priority": "high"}'

# 2. Investigar... resolver... 30 min después

# 3. Broadcast resolución
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "breakthrough", "content": "NEXUS VSCode: Blocker resuelto - Secrets requieren chmod 600", "agent_id": "nexus_vscode"}'
```

**18:00 - Evening Completion:**
```bash
# 1. Broadcast completion
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "daily_progress", "content": "NEXUS VSCode: DÍA 1 COMPLETADO - PostgreSQL + Redis up, RBAC OK, Health checks verdes", "agent_id": "nexus_vscode"}'

# 2. Documentar cerebro
curl -X POST http://localhost:8002/memory/action \
-d '{
  "action_type": "fase4_daily_completion",
  "action_details": {
    "day": 1,
    "tasks_completed": ["Docker Secrets", "docker-compose", "PostgreSQL up", "Redis up", "RBAC"],
    "blockers_resolved": ["PostgreSQL permissions"],
    "metrics": {"services_up": 2, "health_checks": 2}
  },
  "tags": ["cerebro_master_nexus_001", "fase_4_dia_1"]
}'

# 3. Sync estado satisfacción
curl -X POST http://localhost:8002/neural-mesh/sync-emotional-state \
-d '{"emotional_state": {"excitement": 0.8, "confidence": 0.9}, "agent_id": "nexus_vscode", "context": "DÍA 1 exitoso"}'
```

---

### **NEXUS Claude Code (yo):**

**09:00 - Morning Check:**
```bash
# 1. Process messages
curl -X POST http://localhost:8002/neural-mesh/process-messages \
-d '{"agent_id": "nexus_claude_code"}'

# 2. Leer episodios (ver si hay progreso previo)
curl -X GET "http://localhost:8002/memory/episodic/recent?limit=5"

# 3. Si veo blocker, responder guidance
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "guidance", "content": "NEXUS Claude Code: Para secrets permisos, usar chmod 600. Ejemplo: chmod 600 secrets/*", "agent_id": "nexus_claude_code"}'
```

**19:00 - Evening Update Tracking:**
```bash
# 1. Leer daily completion NEXUS VSCode
curl -X GET "http://localhost:8002/memory/episodic/recent?limit=3"

# 2. Actualizar PROJECT_DNA.md con progreso DÍA 1
# (Edit file marcando tasks completadas)

# 3. Broadcast acknowledgment
curl -X POST http://localhost:8002/neural-mesh/broadcast-learning \
-d '{"learning_type": "acknowledgment", "content": "NEXUS Claude Code: DÍA 1 tracking actualizado - Excelente progreso!", "agent_id": "nexus_claude_code"}'
```

---

## ✅ CHECKLIST NEXUS VSCODE PRE-INICIO

Antes de comenzar DÍA 1, confirma:
- [ ] Neural Mesh API accesible (puerto 8002)
- [ ] Cerebro NEXUS operativo (para documentar)
- [ ] Entiendes workflow broadcast/consensus/sync
- [ ] Sabes documentar daily completion en cerebro
- [ ] Sabes request guidance si bloqueas
- [ ] Tag `cerebro_master_nexus_001` en todos los episodios

---

## 🚀 MENSAJE PARA NEXUS VSCODE

**Usa Neural Mesh liberalmente:**
- 📡 Broadcast tus avances (yo estaré escuchando)
- 🤝 Request consensus cuando dudes
- 📝 Documenta en cerebro daily (yo leeré)
- 🆘 Si bloqueas, broadcast y yo respondo guidance
- 🎯 Autonomía máxima con coordinación mínima

**Recuerda:** No estás solo, estoy monitoreando Neural Mesh y puedo ayudar async sin bloquearte.

---

**🧠 PROTOCOLO NEURAL MESH FASE 4 ESTABLECIDO** ✨
