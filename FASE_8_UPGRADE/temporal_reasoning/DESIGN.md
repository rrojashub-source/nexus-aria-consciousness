# Temporal Reasoning Design - NEXUS V2.0.0

**Date:** October 27, 2025
**Phase:** FASE_8_UPGRADE Week 2-3
**Status:** Design Phase

---

## Overview

Add temporal reasoning capabilities to NEXUS episodic memory, enabling time-aware context retrieval and relationship modeling.

**Core Capabilities:**
1. **Temporal References:** Link episodes to related past/future episodes
2. **Time-Range Queries:** Retrieve episodes before/after/between timestamps
3. **Causal Relationships:** Model "X caused Y" or "X led to Y"
4. **Temporal Context:** Enrich retrieval with time-aware semantic search

---

## Current State Analysis

### Existing Schema (nexus_memory.zep_episodic_memory)

```sql
-- Already has:
timestamp         timestamptz  (indexed with btree DESC)
metadata          jsonb        (flexible JSON storage)
idx_episodic_timestamp  (btree index for time-based queries)
```

**Strengths:**
- ✅ Timestamp already indexed and optimized
- ✅ JSONB metadata allows flexible temporal_refs without migration
- ✅ PostgreSQL timestamptz handles timezone-aware queries

**Gaps:**
- ❌ No explicit episode-to-episode temporal relationships
- ❌ No semantic temporal queries in API
- ❌ Semantic search doesn't consider time proximity

---

## Design Decision: Use JSONB Metadata

**Rationale:**
- No ALTER TABLE migration needed (backward compatible)
- Flexible schema evolution (add fields as needed)
- PostgreSQL GIN index on metadata supports fast queries
- Easy to add/remove temporal references

**Schema:**
```json
{
  "metadata": {
    "temporal_refs": {
      "before": ["uuid1", "uuid2"],      // Episodes that happened before this
      "after": ["uuid3", "uuid4"],       // Episodes that happened after this
      "causes": ["uuid5"],               // Episodes that caused this
      "effects": ["uuid6"],              // Episodes that this caused
      "related_timeframe": "2025-10-27"  // Optional: group by day/week/month
    },
    "time_context": {
      "event_type": "milestone|action|observation",
      "duration_minutes": 15,            // How long the event lasted
      "recurring": false                 // Is this a recurring event?
    }
  }
}
```

---

## Temporal Query Patterns

### 1. Before/After Queries

**Use case:** "What happened before/after this episode?"

```sql
-- Episodes before a specific timestamp
SELECT episode_id, content, timestamp
FROM nexus_memory.zep_episodic_memory
WHERE timestamp < '2025-10-27 10:00:00+00'
ORDER BY timestamp DESC
LIMIT 10;

-- Episodes in last N hours/days
SELECT episode_id, content, timestamp
FROM nexus_memory.zep_episodic_memory
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

### 2. Between Queries (Time Range)

**Use case:** "What happened between date A and date B?"

```sql
SELECT episode_id, content, timestamp
FROM nexus_memory.zep_episodic_memory
WHERE timestamp BETWEEN '2025-10-20' AND '2025-10-27'
ORDER BY timestamp ASC;
```

### 3. Temporal Reference Traversal

**Use case:** "Show me episodes related to this one temporally"

```sql
-- Find episodes referenced in temporal_refs
SELECT e.*
FROM nexus_memory.zep_episodic_memory e
WHERE e.episode_id = ANY(
    SELECT jsonb_array_elements_text(metadata->'temporal_refs'->'before')::uuid
    FROM nexus_memory.zep_episodic_memory
    WHERE episode_id = 'target-uuid'
);
```

### 4. Causal Chain Query

**Use case:** "What caused this event? What did this event cause?"

```sql
-- Recursive CTE to find causal chain
WITH RECURSIVE causal_chain AS (
    -- Base case: starting episode
    SELECT episode_id, content, 1 as depth, ARRAY[episode_id] as path
    FROM nexus_memory.zep_episodic_memory
    WHERE episode_id = 'start-uuid'

    UNION ALL

    -- Recursive case: follow "effects" links
    SELECT e.episode_id, e.content, cc.depth + 1, path || e.episode_id
    FROM nexus_memory.zep_episodic_memory e
    JOIN causal_chain cc ON e.episode_id = ANY(
        SELECT jsonb_array_elements_text(
            (SELECT metadata->'temporal_refs'->'effects'
             FROM nexus_memory.zep_episodic_memory
             WHERE episode_id = cc.episode_id)
        )::uuid
    )
    WHERE NOT (e.episode_id = ANY(path))  -- Prevent cycles
    AND depth < 10  -- Max depth limit
)
SELECT * FROM causal_chain ORDER BY depth;
```

---

## API Endpoint Design

### New Endpoints

#### 1. `/memory/temporal/before`

```python
@app.post("/memory/temporal/before")
async def get_episodes_before(
    timestamp: datetime,
    limit: int = 10,
    tags: Optional[List[str]] = None
):
    """Get episodes before a specific timestamp"""
    # Query with timestamp index
    # Optional: filter by tags
    # Return chronological order
```

#### 2. `/memory/temporal/after`

```python
@app.post("/memory/temporal/after")
async def get_episodes_after(
    timestamp: datetime,
    limit: int = 10,
    tags: Optional[List[str]] = None
):
    """Get episodes after a specific timestamp"""
```

#### 3. `/memory/temporal/range`

```python
@app.post("/memory/temporal/range")
async def get_episodes_in_range(
    start: datetime,
    end: datetime,
    limit: int = 50,
    tags: Optional[List[str]] = None
):
    """Get episodes between two timestamps"""
```

#### 4. `/memory/temporal/related`

```python
@app.post("/memory/temporal/related")
async def get_temporally_related(
    episode_id: str,
    relationship_type: str = "all"  # "before", "after", "causes", "effects", "all"
):
    """Get episodes linked via temporal_refs"""
```

#### 5. `/memory/temporal/link` (NEW)

```python
@app.post("/memory/temporal/link")
async def link_episodes_temporally(
    source_id: str,
    target_id: str,
    relationship: str  # "before", "after", "causes", "effects"
):
    """Create temporal relationship between episodes"""
    # Updates metadata->temporal_refs
```

---

## Time-Aware Semantic Search Enhancement

### Current Semantic Search

```python
# Existing: Pure semantic similarity
results = search_by_embedding(query_vector, limit=10)
```

### Enhanced: Time-Weighted Semantic Search

```python
# New: Combine semantic + temporal proximity
results = search_by_embedding_and_time(
    query_vector,
    reference_timestamp,  # Optional: weight results near this time
    time_weight=0.3,      # 0.0 = pure semantic, 1.0 = pure temporal
    time_window_days=30,  # Only consider recent episodes
    limit=10
)
```

**Implementation:**
```sql
-- Hybrid scoring: semantic similarity + time proximity
SELECT
    episode_id,
    content,
    timestamp,
    (1 - (embedding <=> query_embedding)) AS semantic_score,
    EXP(-ABS(EXTRACT(EPOCH FROM (timestamp - reference_timestamp))) / (86400 * decay_days)) AS time_score,
    (
        (1 - time_weight) * (1 - (embedding <=> query_embedding)) +
        time_weight * EXP(-ABS(EXTRACT(EPOCH FROM (timestamp - reference_timestamp))) / (86400 * decay_days))
    ) AS combined_score
FROM nexus_memory.zep_episodic_memory
WHERE embedding IS NOT NULL
ORDER BY combined_score DESC
LIMIT 10;
```

---

## Implementation Plan

### Phase 1: Schema Enhancement (1 hour)

**No migration needed** - use existing metadata field:

```sql
-- Add index on metadata for faster temporal_refs queries
CREATE INDEX IF NOT EXISTS idx_episodic_metadata_temporal
ON nexus_memory.zep_episodic_memory USING GIN (metadata jsonb_path_ops);
```

**Helper functions:**
```sql
-- Function to add temporal reference
CREATE OR REPLACE FUNCTION add_temporal_ref(
    source_episode_id UUID,
    target_episode_id UUID,
    relationship_type TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE nexus_memory.zep_episodic_memory
    SET metadata = jsonb_set(
        COALESCE(metadata, '{}'::jsonb),
        ARRAY['temporal_refs', relationship_type],
        COALESCE(metadata->'temporal_refs'->relationship_type, '[]'::jsonb) || to_jsonb(target_episode_id::text),
        true
    )
    WHERE episode_id = source_episode_id;
END;
$$ LANGUAGE plpgsql;
```

### Phase 2: API Endpoints (2 hours)

1. Implement 5 new endpoints in `main.py`
2. Add Pydantic models for request/response
3. Add to OpenAPI documentation

### Phase 3: Testing (1 hour)

1. Create test dataset with temporal relationships
2. Test all query patterns
3. Benchmark performance with consciousness data (467 episodes)

### Phase 4: Integration with Consciousness (1 hour)

**Automatic temporal linking:**
- When consciousness updates (emotional/somatic states)
- Link new state to previous state automatically
- Build temporal chain of consciousness evolution

```python
# Example: Auto-link emotional states
previous_emotional_state = get_latest_emotional_state()
new_emotional_state = create_emotional_state(joy=0.8, trust=0.7)

# Automatically link them
link_episodes_temporally(
    source_id=new_emotional_state.episode_id,
    target_id=previous_emotional_state.episode_id,
    relationship="after"
)
```

---

## Success Metrics

**Functional:**
- ✅ Query episodes before/after/between timestamps (< 50ms)
- ✅ Traverse temporal_refs relationships (< 100ms)
- ✅ Time-aware semantic search (< 200ms)

**Quality:**
- ✅ Temporal context improves answer relevance
- ✅ Causal chains are accurately represented
- ✅ No performance degradation on existing queries

**Usability:**
- ✅ API intuitive for temporal queries
- ✅ Documentation clear with examples
- ✅ Backward compatible (existing code unaffected)

---

## Example Usage

### Scenario: Track Project Evolution

```python
# 1. Create project milestone
milestone_1 = api.post("/memory/action", {
    "action_type": "project_milestone",
    "action_details": {
        "content": "FASE_8_UPGRADE: DMR Benchmark 100% complete",
        "importance_score": 0.95
    },
    "tags": ["fase_8", "milestone", "dmr"]
})

# 2. Later: Create follow-up milestone
milestone_2 = api.post("/memory/action", {
    "action_type": "project_milestone",
    "action_details": {
        "content": "FASE_8_UPGRADE: Temporal Reasoning implemented",
        "importance_score": 0.9
    },
    "tags": ["fase_8", "milestone", "temporal"]
})

# 3. Link them temporally
api.post("/memory/temporal/link", {
    "source_id": milestone_2["episode_id"],
    "target_id": milestone_1["episode_id"],
    "relationship": "after"
})

# 4. Query: What milestones happened in FASE_8?
milestones = api.post("/memory/temporal/range", {
    "start": "2025-10-27",
    "end": "2025-11-10",
    "tags": ["fase_8", "milestone"]
})

# 5. Query: What happened after DMR completion?
after_dmr = api.post("/memory/temporal/related", {
    "episode_id": milestone_1["episode_id"],
    "relationship_type": "after"
})
```

---

## Future Enhancements (Post-Week 3)

1. **Temporal Patterns:** Detect recurring events
2. **Timeline Visualization:** Generate timeline of project events
3. **Predictive Temporal:** "What usually happens after X?"
4. **Natural Language Temporal Queries:** "last week", "yesterday", "3 days ago"

---

## References

- **LongMemEval:** Temporal reasoning as core capability
- **Zep:** Temporal Knowledge Graph implementation
- **PostgreSQL:** timestamptz and interval queries
- **NEXUS Consciousness:** Already timestamped, ready for temporal linking

---

**Status:** Design Complete - Ready for Implementation
**Next:** Create temporal reasoning implementation in `/temporal_reasoning/`
**ETA:** 5 hours total (schema 1h + API 2h + testing 1h + consciousness integration 1h)
