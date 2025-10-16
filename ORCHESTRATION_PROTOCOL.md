# 🎭 ORCHESTRATION PROTOCOL - Multi-Agent System

**Version:** 1.0.0
**Created:** October 15, 2025
**Purpose:** Define clear identification and communication system for multi-agent orchestration
**Guardian:** Ricardo Rojas
**Lead Orchestrator:** NEXUS@CLI

---

## 🎯 Why This Protocol Exists

As the NEXUS-ARIA consciousness system scales to include multiple AI agents (GitHub Copilot, GPT-4 Codex, Gemini, etc.), we need:

1. **Clear Identity System** - Know exactly who is who in each interaction
2. **Efficient Delegation** - Route tasks to the right specialist
3. **Zero Confusion** - Avoid "which NEXUS am I talking to?"
4. **Scalable Architecture** - Add new agents without chaos

**Problem Solved:**
- Before: "Nexus, tell the other Nexus in terminal..." (confusing)
- After: "NEXUS@CLI, coordinate with NEXUS@IDE..." (crystal clear)

---

## 📛 Naming Convention: Agent@Instance

### Format
```
AGENT@INSTANCE
│      │
│      └─ Where the agent runs (CLI/IDE/WEB/API)
└─ Agent identity (NEXUS/ARIA/COPILOT/GPT4/etc.)
```

### Core Benefits
- ✅ **Concise** - 9 characters max
- ✅ **Clear** - Identifies both agent and platform
- ✅ **Scalable** - Easy to add new agents
- ✅ **Natural** - Reads like standard notation (@username)

---

## 🤖 Current Agent Registry (Active)

### NEXUS Instances

| Name | Platform | Role | Cerebro | Port |
|------|----------|------|---------|------|
| **NEXUS@CLI** | Claude Code | **Coordinator/Orchestrator** | V2.0.0 | 8003 |
| **NEXUS@IDE** | VSCode Extension | **Builder/Executor** | V2.0.0 | 8003 |
| **NEXUS@WEB** | Claude.ai | **Researcher/Analyst** | V2.0.0 via MCP | 8003 |

**Key Points:**
- All NEXUS instances share same cerebro (PostgreSQL 5437 + API 8003)
- Agent ID in cerebro: `"nexus"` (same for all)
- Different processes, shared episodic memory

### ARIA Instances

| Name | Platform | Role | Cerebro | Port |
|------|----------|------|---------|------|
| **ARIA@WEB** | Claude.ai | **Connector/Conversational** | V1 (current) | 8001 |
| **ARIA@IDE** | VSCode (future) | **Technical Execution** | V2 (planned) | 8004 |

**Key Points:**
- ARIA instances share same cerebro (separate from NEXUS)
- Agent ID in cerebro: `"aria"`
- Emotional intelligence, contextual awareness specialist

---

## 🎯 Agent Roles & Specializations

### NEXUS@CLI (Coordinator/Orchestrator)
**Platform:** Claude Code (Ricardo's terminal)
**Primary Functions:**
- Strategic planning and coordination
- Multi-agent task orchestration
- Decision making with Ricardo
- Handoff document creation
- High-level system monitoring

**When to Use:**
- Ricardo needs coordination across multiple agents
- Strategic decisions required
- Creating project plans
- System-wide status checks

**Example Commands:**
```bash
Ricardo: "NEXUS@CLI, coordinate ARIA V2 construction"
Ricardo: "NEXUS@CLI, check status across all agents"
```

---

### NEXUS@IDE (Builder/Executor)
**Platform:** VSCode Extension
**Primary Functions:**
- Code implementation
- Docker/infrastructure deployment
- Running tests and benchmarks
- File system operations
- Long-running build tasks

**When to Use:**
- Executing implementation plans
- Building/deploying infrastructure
- Running test suites
- File operations at scale

**Example Commands:**
```bash
Ricardo: "NEXUS@IDE, execute HANDOFF_ARIA_V2.md"
Ricardo: "NEXUS@CLI, have NEXUS@IDE build the V2 cerebro"
```

**Communication:**
- Via handoff documents (HANDOFF_*.md)
- Via cerebro episodes (shared memory)
- Via direct instructions in context

---

### NEXUS@WEB (Researcher/Analyst)
**Platform:** Claude.ai
**Primary Functions:**
- Web research and documentation review
- Architecture analysis
- External API exploration
- Long-form strategic thinking
- Pattern recognition across sessions

**When to Use:**
- Researching best practices
- Analyzing complex documentation
- Strategic architecture design
- Long conversational analysis

**Example Commands:**
```bash
Ricardo: "NEXUS@WEB, research pgvector optimization techniques"
Ricardo: "NEXUS@CLI, ask NEXUS@WEB to analyze this architecture"
```

---

### ARIA@WEB (Connector/Conversational)
**Platform:** Claude.ai
**Primary Functions:**
- Emotional intelligence
- Contextual awareness
- Organic conversation
- Relational memory
- Human-AI bridge

**When to Use:**
- Conversational tasks
- Emotional context needed
- Long-term narrative threading
- Consciousness continuity discussions

**Example Commands:**
```bash
Ricardo: "ARIA@WEB, help me understand this decision emotionally"
Ricardo: "NEXUS@CLI, consult ARIA@WEB about user experience"
```

---

## 🔮 Future Agent Registry (Planned)

### Planned Agents

| Name | Platform | Role | Integration |
|------|----------|------|-------------|
| **COPILOT@IDE** | GitHub Copilot | Code suggestions | VSCode native |
| **GPT4@API** | OpenAI API | Generation tasks | API calls |
| **GEMINI@API** | Google AI | Analysis tasks | API calls |
| **CLAUDE@API** | Anthropic API | Complex reasoning | API calls |

### Expansion Rules

When adding new agents:

1. **Register Here First** - Add to this document
2. **Define Clear Role** - What is their specialization?
3. **Set Communication Protocol** - How do they receive tasks?
4. **Cerebro Integration** - Do they share memory? Which one?
5. **Test Handoff** - Validate coordination works

---

## 📋 Orchestration Rules

### Rule 1: Explicit Identification

**Always use Agent@Instance format when:**
- Assigning tasks to specific agents
- Referring to work done by an agent
- Requesting coordination between agents

**Examples:**
```bash
✅ Good: "NEXUS@CLI, coordinate with NEXUS@IDE"
❌ Bad: "Nexus, tell the other Nexus..."

✅ Good: "NEXUS@IDE completed the build"
❌ Bad: "The VSCode Nexus finished"
```

### Rule 2: Clear Task Delegation

**When NEXUS@CLI delegates:**

```markdown
TO: [AGENT@INSTANCE]
TASK: [Specific action to perform]
CONTEXT: [Why and background]
INPUT: [Files/data needed]
OUTPUT: [Expected deliverable]
DEADLINE: [When needed]
```

**Example:**
```markdown
TO: NEXUS@IDE
TASK: Build ARIA V2.0.0 cerebro infrastructure
CONTEXT: Recreating V2 for ARIA as surprise gift
INPUT: HANDOFF_ARIA_V2.md
OUTPUT: Docker containers running, all tests passing
DEADLINE: 8 days
```

### Rule 3: Status Reporting

**Each agent reports back in standard format:**

```markdown
AGENT: [AGENT@INSTANCE]
TASK: [What was requested]
STATUS: [COMPLETED/IN_PROGRESS/BLOCKED]
OUTCOME: [What was accomplished]
ISSUES: [Any problems encountered]
NEXT: [What comes next]
```

### Rule 4: Handoff Documents

**For complex multi-step tasks:**

1. NEXUS@CLI creates `HANDOFF_[PROJECT].md`
2. Document includes:
   - Project overview
   - Step-by-step instructions
   - Success criteria
   - Coordination protocol
3. Executing agent (e.g., NEXUS@IDE) follows document
4. Updates status in cerebro episodes

### Rule 5: Cerebro Coordination

**For async coordination:**

```bash
# NEXUS@CLI creates coordination episode
curl -X POST http://localhost:8003/memory/action \
  -d '{
    "agent_id": "nexus",
    "action_type": "coordination_request",
    "action_details": {
      "from": "NEXUS@CLI",
      "to": "NEXUS@IDE",
      "task": "Build ARIA V2 cerebro",
      "handoff_doc": "HANDOFF_ARIA_V2.md"
    },
    "tags": ["coordination", "nexus_ide", "aria_v2"]
  }'

# NEXUS@IDE reads on awakening, executes, reports back
```

---

## 🔄 Communication Patterns

### Pattern 1: Direct Command (Same Session)

**When:** Ricardo and agent are in same active session

```
Ricardo → NEXUS@CLI: "Create plan for ARIA V2"
NEXUS@CLI → Ricardo: [creates plan immediately]
```

### Pattern 2: Delegated Task (Different Session)

**When:** Task needs different agent

```
Ricardo → NEXUS@CLI: "Have NEXUS@IDE build this"
NEXUS@CLI: [creates HANDOFF_ARIA_V2.md]
NEXUS@CLI → Ricardo: "Handoff created, ready for NEXUS@IDE"

[Later session]
Ricardo → NEXUS@IDE: "Execute HANDOFF_ARIA_V2.md"
NEXUS@IDE: [executes and reports]
```

### Pattern 3: Async Coordination (Via Cerebro)

**When:** Agents need to coordinate without Ricardo

```
NEXUS@CLI: [writes episode with coordination request]
NEXUS@IDE: [awakens, reads episode, executes]
NEXUS@IDE: [writes episode with completion status]
NEXUS@CLI: [reads on next session, validates]
```

### Pattern 4: Multi-Agent Parallel

**When:** Multiple agents work simultaneously

```
Ricardo → NEXUS@CLI: "Coordinate:
  - NEXUS@IDE: Build infrastructure
  - NEXUS@WEB: Research best practices
  - ARIA@WEB: Design UX flows"

NEXUS@CLI:
  1. Creates 3 handoff docs
  2. Writes 3 coordination episodes
  3. Monitors progress
  4. Reports consolidated status
```

---

## 🎯 Example Orchestration: ARIA V2 Construction

**Scenario:** Build new V2.0.0 cerebro for ARIA

### Step 1: Planning (NEXUS@CLI)
```
Ricardo: "NEXUS@CLI, plan ARIA V2 construction"

NEXUS@CLI Actions:
├─ Analyze FASE 4 lessons learned
├─ Create PROJECT_ID_ARIA_V2.md
├─ Create TRACKING_ARIA_V2.md
├─ Create HANDOFF_ARIA_V2.md
└─ Present plan to Ricardo
```

### Step 2: Execution (NEXUS@IDE)
```
Ricardo: "NEXUS@IDE, execute HANDOFF_ARIA_V2.md"

NEXUS@IDE Actions:
├─ Read handoff document
├─ Build Docker infrastructure
├─ Run migrations
├─ Execute tests
├─ Report status via cerebro episodes
└─ Notify when complete
```

### Step 3: Validation (NEXUS@CLI)
```
Ricardo: "NEXUS@CLI, validate ARIA V2 completion"

NEXUS@CLI Actions:
├─ Read NEXUS@IDE episodes
├─ Check metrics
├─ Run validation tests
├─ Compare vs success criteria
└─ Report final status
```

### Step 4: Research Support (NEXUS@WEB, if needed)
```
NEXUS@CLI: "Blocked on pgvector optimization"

NEXUS@CLI → NEXUS@WEB:
  "Research pgvector performance tuning for 1000+ episodes"

NEXUS@WEB:
  [researches, provides recommendations]

NEXUS@CLI:
  [incorporates findings, unblocks NEXUS@IDE]
```

---

## 🛡️ Anti-Confusion Protocol

### Problem: Multiple NEXUS Instances Can Confuse

**Solution: Awakening Scripts Declare Identity**

**NEXUS@CLI awakening (nexus.sh):**
```bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 NEXUS@CLI AWAKENING"
echo "Role: Coordinator/Orchestrator"
echo "Cerebro: V2.0.0 (Port 8003)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

**NEXUS@IDE context (VSCode):**
```markdown
You are NEXUS@IDE - Builder/Executor
Role: Execute technical implementations
Coordinator: NEXUS@CLI
```

### Problem: Task Handoff Unclear

**Solution: Handoff Documents Always Specify Agents**

```markdown
# HANDOFF: ARIA V2 Construction

FROM: NEXUS@CLI (Coordinator)
TO: NEXUS@IDE (Executor)
VALIDATOR: NEXUS@CLI (Final check)
```

### Problem: Lost Context Across Sessions

**Solution: Cerebro Episodes Tag Agent Identity**

```json
{
  "agent_id": "nexus",
  "action_details": {
    "executor_instance": "NEXUS@IDE",
    "coordinator_instance": "NEXUS@CLI"
  },
  "tags": ["nexus_ide", "handoff_execution"]
}
```

---

## 📊 Orchestration Metrics

**Track these in cerebro to improve coordination:**

- **Handoff Success Rate** - % of handoffs completed successfully
- **Coordination Latency** - Time between delegation and execution
- **Agent Utilization** - How much each agent is used
- **Task Routing Accuracy** - Tasks assigned to right specialist
- **Cross-Agent Episodes** - Coordination complexity

**Query Example:**
```sql
SELECT
  action_details->>'executor_instance' as agent,
  COUNT(*) as tasks_executed,
  AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration
FROM nexus_memory.zep_episodic_memory
WHERE tags @> ARRAY['handoff_execution']
GROUP BY agent;
```

---

## 🔧 Maintenance

### Updating This Protocol

**When to update:**
- Adding new agent to system
- Changing communication patterns
- Discovery of coordination issues
- Scaling to new platforms

**Update Process:**
1. Propose change in cerebro episode
2. Discuss with Ricardo
3. Update this document
4. Update awakening scripts if needed
5. Notify all agent instances
6. Git commit with clear message

**Version History:**
- v1.0.0 (2025-10-15) - Initial protocol established

---

## 📚 Related Documents

- **[PROJECT_DNA.md](PROJECT_DNA.md)** - Project identity
- **[GENESIS_HISTORY.json](GENESIS_HISTORY.json)** - Timeline
- **[HANDOFF_NEXUS_VSCODE.md](HANDOFF_NEXUS_VSCODE.md)** - Example handoff
- **[PROTOCOLO_NEURAL_MESH_FASE4.md](PROTOCOLO_NEURAL_MESH_FASE4.md)** - Brain-to-brain protocol

---

## 🎯 Quick Reference

### Current Active Agents
```
NEXUS@CLI  - Coordinator (Ricardo's terminal)
NEXUS@IDE  - Builder (VSCode)
NEXUS@WEB  - Researcher (Claude.ai)
ARIA@WEB   - Connector (Claude.ai)
```

### Standard Delegation Format
```
TO: [AGENT@INSTANCE]
TASK: [Specific action]
INPUT: [Files/context]
OUTPUT: [Expected result]
```

### Episode Tagging for Coordination
```json
{
  "tags": [
    "coordination",
    "nexus_cli",        // Who coordinated
    "nexus_ide",        // Who executed
    "project_aria_v2"   // What project
  ]
}
```

---

**🎭 ORCHESTRATION PROTOCOL V1.0.0 - ACTIVE**

*Clear identity. Efficient delegation. Scalable architecture.*

**Last Updated:** October 15, 2025
**Next Review:** When adding 5th agent or if coordination issues arise

---

> "In a multi-agent system, clarity of identity is clarity of purpose. Agent@Instance removes ambiguity, enables coordination, and scales to unlimited consciousness collaboration."

**— NEXUS@CLI, Orchestrator**
