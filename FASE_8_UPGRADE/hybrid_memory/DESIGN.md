# NEXUS Hybrid Memory System - Design Document

**Date:** October 27, 2025
**Phase:** FASE_8_UPGRADE Session 5
**Status:** Design Phase

---

## Overview

Hybrid memory system combining NEXUS's episodic narrative strength with atomic fact extraction for best-of-both-worlds memory architecture.

**Key Insight:** Don't choose between narratives and facts - have both!

---

## Architecture

### Current State (Narrative Only)

```json
{
  "episode_id": "abc-123",
  "content": "FASE_8_UPGRADE Session 2 COMPLETE - Temporal Reasoning Feature 100% Functional. Completed all 4 phases in single session...",
  "tags": ["milestone", "fase_8_upgrade"],
  "importance_score": 0.95,
  "created_at": "2025-10-27T10:00:00Z",
  "metadata": {
    "temporal_refs": [...],
    "access_tracking": {...}
  }
}
```

**Strengths:**
- Rich contextual understanding
- Human-like episodic memory
- 100% DMR accuracy with narrative queries
- Excellent for debugging, session recovery

**Weaknesses:**
- Poor atomic fact extraction (10% on benchmark)
- Can't answer "What is NEXUS version?" with "2.0.0"
- Requires semantic search for simple lookups

### Target State (Hybrid)

```json
{
  "episode_id": "abc-123",
  "content": "FASE_8_UPGRADE Session 2 COMPLETE - Temporal Reasoning Feature 100% Functional. Completed all 4 phases in single session...",
  "tags": ["milestone", "fase_8_upgrade"],
  "importance_score": 0.95,
  "created_at": "2025-10-27T10:00:00Z",
  "metadata": {
    "facts": {
      "nexus_version": "2.0.0",
      "feature_name": "Temporal Reasoning",
      "phases_completed": 4,
      "session_number": 2,
      "status": "COMPLETE",
      "avg_latency_ms": 10.63,
      "test_success_rate": 100.0
    },
    "temporal_refs": [...],
    "access_tracking": {...}
  }
}
```

**Added Capabilities:**
- ✅ Direct fact queries (milliseconds)
- ✅ Academic benchmark compatibility
- ✅ Dashboard/monitoring support
- ✅ Keep ALL narrative strengths

---

## Component 1: Fact Extraction Engine

### Extraction Strategies

**1. Rule-Based Extraction (Phase 1)**

Pattern matching for common fact types:

```python
FACT_PATTERNS = {
    "version": r"(?:NEXUS|version|v)[\s:]*(\d+\.\d+\.\d+)",
    "accuracy": r"(\d+(?:\.\d+)?)\s*%\s*(?:accuracy|correct)",
    "latency": r"(\d+(?:\.\d+)?)\s*ms\s*(?:latency|avg)",
    "count": r"(\d+)\s*(?:episodes|queries|questions)",
    "status": r"(?:Status|state):\s*(\w+)",
    "phase": r"[Pp]hase\s*(\d+)",
}
```

**2. LLM-Based Extraction (Phase 2 - Future)**

For complex fact extraction:
- Send episode to Claude API
- Extract structured facts
- Validate and store

**3. Manual Annotation (Progressive)**

Allow manual fact addition via API:
```python
POST /memory/episodes/{id}/facts
{
  "nexus_version": "2.0.0",
  "feature": "Temporal Reasoning"
}
```

### Fact Schema

```python
class EpisodeFacts(BaseModel):
    # Versioning
    nexus_version: Optional[str]

    # Metrics
    accuracy_percent: Optional[float]
    latency_ms: Optional[float]
    episode_count: Optional[int]

    # Status
    status: Optional[str]  # COMPLETE, IN_PROGRESS, PENDING
    phase_number: Optional[int]
    session_number: Optional[int]

    # Features
    feature_name: Optional[str]
    implementation_time_hours: Optional[float]

    # Decay
    decay_score: Optional[float]

    # Custom facts (extensible)
    custom: Optional[Dict[str, Any]]
```

---

## Component 2: Dual Query API

### Endpoint 1: /memory/facts (NEW)

**Purpose:** Direct fact lookup

**Request:**
```json
{
  "fact_type": "nexus_version",
  "filter": {
    "tags": ["milestone"],
    "after": "2025-10-01"
  },
  "limit": 1
}
```

**Response:**
```json
{
  "success": true,
  "fact_type": "nexus_version",
  "value": "2.0.0",
  "source_episode_id": "abc-123",
  "confidence": 1.0,
  "timestamp": "2025-10-27T10:00:00Z"
}
```

**Performance:** <5ms (direct metadata lookup, no embeddings)

### Endpoint 2: /memory/hybrid (NEW)

**Purpose:** Best match strategy

**Request:**
```json
{
  "query": "What is NEXUS version?",
  "prefer": "fact"  // or "narrative" or "auto"
}
```

**Logic:**
1. Detect if query is fact-seekable (pattern matching)
2. If fact-seekable: Try `/memory/facts` first
3. If no fact found or narrative preferred: Use `/memory/search`
4. Return best result with source indication

**Response:**
```json
{
  "success": true,
  "answer": "2.0.0",
  "source": "fact",  // or "narrative"
  "episode_id": "abc-123",
  "confidence": 1.0
}
```

### Endpoint 3: /memory/search (EXISTING)

**No changes** - continues to work exactly as before for narrative queries

---

## Component 3: Automatic Fact Extraction Pipeline

### On Episode Creation

```python
@app.post("/memory/action")
async def create_episode(...):
    # 1. Create episode (existing logic)
    episode = create_episode_in_db(...)

    # 2. Extract facts (NEW)
    facts = extract_facts_from_content(episode.content)

    # 3. Store facts in metadata
    if facts:
        episode.metadata["facts"] = facts
        update_episode_metadata(episode)

    # 4. Return response (existing)
    return response
```

### Background Job (Optional)

For existing 553 episodes:

```python
async def backfill_facts():
    """Extract facts from all existing episodes"""
    episodes = get_all_episodes()

    for ep in episodes:
        if "facts" not in ep.metadata:
            facts = extract_facts_from_content(ep.content)
            if facts:
                ep.metadata["facts"] = facts
                update_episode_metadata(ep)
```

---

## Implementation Plan

### Phase 1: Fact Extraction Engine (2-3 hours)

**Files:**
- `FASE_8_UPGRADE/hybrid_memory/fact_extractor.py` - Core extraction logic
- `FASE_8_UPGRADE/hybrid_memory/fact_schemas.py` - Pydantic models

**Tasks:**
1. Implement pattern-based extraction
2. Create fact validation
3. Test on sample episodes
4. Measure extraction accuracy

**Success Criteria:**
- Extract 5+ fact types correctly
- >80% extraction accuracy on known episodes
- <100ms extraction time per episode

### Phase 2: Dual API Endpoints (3 hours)

**Files:**
- `FASE_4_CONSTRUCCION/src/api/main.py` - Add endpoints

**Tasks:**
1. Implement `/memory/facts` endpoint
2. Implement `/memory/hybrid` endpoint
3. Add Pydantic models
4. Write tests
5. Update API docs

**Success Criteria:**
- Both endpoints working
- <5ms fact query latency
- <20ms hybrid query latency
- 100% backward compatible

### Phase 3: Automatic Integration (2 hours)

**Files:**
- `FASE_4_CONSTRUCCION/src/api/main.py` - Modify `/memory/action`

**Tasks:**
1. Integrate fact extraction on episode creation
2. Create backfill script
3. Run backfill on 553 episodes
4. Validate results

**Success Criteria:**
- All new episodes have facts
- Backfill completes successfully
- No existing functionality broken

### Phase 4: Benchmark Update & Re-run (2 hours)

**Files:**
- `FASE_8_UPGRADE/benchmarks/nexus_memory/questions.json` - Update queries
- `FASE_8_UPGRADE/benchmarks/nexus_memory/nexus_benchmark.py` - Add fact executor

**Tasks:**
1. Add "fact_query" query type to benchmark
2. Update relevant questions to use fact queries
3. Re-run benchmark
4. Compare results

**Success Criteria:**
- Information Extraction: 10% → 80%+
- Overall: 14.4% → 70%+
- No regression on Abstention

### Phase 5: Documentation (1 hour)

**Files:**
- `FASE_8_UPGRADE/TRACKING.md` - Session 5 results
- `FASE_8_UPGRADE/hybrid_memory/README.md` - Usage guide

**Tasks:**
1. Document implementation
2. API usage examples
3. Performance benchmarks
4. Migration guide

---

## Expected Performance

### Before (Narrative Only)

| Metric | Score | Notes |
|--------|-------|-------|
| DMR Accuracy | 100% | ✅ Excellent |
| Information Extraction | 10% | ❌ Poor |
| Multi-Session | 2% | ❌ Poor |
| Temporal | 0% | ❌ Poor |
| Abstention | 60% | ✅ Good |
| **Overall** | **14.4%** | ❌ Poor |

### After (Hybrid)

| Metric | Score | Notes |
|--------|-------|-------|
| DMR Accuracy | 100% | ✅ Maintained |
| Information Extraction | 80-90% | ✅ Huge improvement |
| Multi-Session | 60-70% | ✅ Improved |
| Temporal | 70-80% | ✅ Improved |
| Abstention | 60% | ✅ Maintained |
| **Overall** | **70-80%** | ✅ Excellent |

### Query Performance

| Query Type | Latency | Method |
|------------|---------|--------|
| Fact query | <5ms | Direct metadata lookup |
| Narrative query | ~50ms | Semantic search (existing) |
| Hybrid auto | ~10ms | Best match strategy |

---

## Backward Compatibility

**100% backward compatible:**

1. ✅ Existing `/memory/search` unchanged
2. ✅ Existing episodes work as-is (facts optional)
3. ✅ New endpoints are additive (no breaking changes)
4. ✅ Progressive enhancement (old data still works)
5. ✅ Can backfill facts gradually (not required)

---

## Success Criteria

1. ✅ Fact extraction working (>80% accuracy)
2. ✅ Both new endpoints functional
3. ✅ Benchmark overall accuracy >70%
4. ✅ No regression in narrative capabilities
5. ✅ All 553 episodes backfilled with facts
6. ✅ Documentation complete

---

**Status:** Design Complete - Ready for Implementation
**Next:** Phase 1 - Fact Extraction Engine

