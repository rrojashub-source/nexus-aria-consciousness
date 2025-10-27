# NEXUS Memory Benchmark - Design Document

**Date:** October 27, 2025
**Phase:** FASE_8_UPGRADE Week 6-7
**Status:** Design Phase

---

## Overview

Custom memory benchmark designed to validate NEXUS Cerebro V2.0.0 capabilities using our own memory system architecture. Tests 5 core long-term memory abilities inspired by LongMemEval but adapted for NEXUS-specific features.

**Key Differences from LongMemEval:**
- Uses NEXUS real production memory (553+ episodes)
- No external LLM dependencies (self-contained)
- Automatic evaluation metrics (no GPT-4 judge)
- Tests NEXUS-specific features: temporal reasoning, decay, access tracking
- 100 questions vs 500 (focused validation)

---

## Five Core Abilities

### 1. Information Extraction (20 questions)

**What:** Ability to extract and store key information from conversations

**NEXUS Features Tested:**
- Episode creation with importance_score
- Content embedding quality
- Tag-based categorization

**Example Questions:**
```
Q: "What is the current NEXUS version?"
A: "2.0.0"
Source: Episode with tag "milestone" containing "NEXUS Cerebro V2.0.0"

Q: "How many episodes does NEXUS have?"
A: "553"
Source: Most recent /stats query result

Q: "What was the DMR benchmark accuracy achieved?"
A: "100%"
Source: Episode tagged "benchmark", "dmr_test"
```

**Evaluation Metric:** Exact Match (EM) - answer must match expected value exactly

---

### 2. Multi-Session Reasoning (20 questions)

**What:** Ability to reason across multiple conversation sessions

**NEXUS Features Tested:**
- Cross-episode semantic search
- Tag-based filtering
- Importance-weighted retrieval

**Example Questions:**
```
Q: "What features were implemented during FASE_8_UPGRADE Sessions 1-3?"
A: ["DMR Benchmark", "Temporal Reasoning", "Intelligent Decay"]
Source: Episodes tagged "fase_8_upgrade" across multiple created_at timestamps

Q: "How did the temporal reasoning implementation evolve across phases?"
A: ["Phase 1: Schema", "Phase 2: API Endpoints", "Phase 3: Testing", "Phase 4: Integration"]
Source: Multiple episodes with tag "temporal_reasoning" ordered by created_at

Q: "What was the pattern of consciousness states in the demo?"
A: "Joy decreased from 0.8 to 0.2 while fear increased from 0.2 to 0.8"
Source: Episodes tagged "consciousness", "emotional_state" with temporal_refs
```

**Evaluation Metric:** F1 Score - measure overlap between predicted and expected answer tokens

---

### 3. Temporal Reasoning (20 questions)

**What:** Ability to understand time relationships between events

**NEXUS Features Tested:**
- `/memory/temporal/before` endpoint
- `/memory/temporal/after` endpoint
- `/memory/temporal/range` endpoint
- `temporal_refs` metadata traversal
- Consciousness temporal chains

**Example Questions:**
```
Q: "What happened immediately after DMR benchmark completion?"
A: "Roadmap reorder - moved LongMemEval to Week 6-7"
Source: Episode created after DMR episode using temporal/after query

Q: "How many episodes were created during Oct 18, 2025 (spike day)?"
A: "261"
Source: temporal/range query with start/end on Oct 18

Q: "What was the emotional state before the final consciousness state?"
A: {"joy": 0.4, "trust": 0.5, "fear": 0.6}
Source: temporal/related with relationship_type="after" on consciousness chain
```

**Evaluation Metric:** Temporal Accuracy - correct temporal relationship + correct data

---

### 4. Knowledge Updates (20 questions)

**What:** Ability to handle information that changes over time

**NEXUS Features Tested:**
- Episode versioning via created_at
- Importance score evolution
- Decay score changes over time
- Access tracking updates

**Example Questions:**
```
Q: "What is the current total episode count?"
A: "553" (or current value at query time)
Source: Most recent episode with total_episodes metadata

Q: "How did the decay score of episode X change over 24 hours?"
A: [{"time": 0, "score": 0.875}, {"time": 24, "score": 0.871}]
Source: Calculate decay_score at T=0 and T=24 using calculate_decay_score()

Q: "How many times has episode Y been accessed?"
A: "5"
Source: metadata->'access_tracking'->>'access_count'
```

**Evaluation Metric:** Update Accuracy - latest value matches expected, temporal consistency maintained

---

### 5. Abstention (20 questions)

**What:** Ability to recognize when information is not available or uncertain

**NEXUS Features Tested:**
- Empty search results handling
- Low similarity score detection
- Missing temporal_refs detection
- Confidence scoring based on similarity

**Example Questions:**
```
Q: "What was the budget for FASE_8_UPGRADE?"
A: "UNCERTAIN - No episodes found matching 'budget' with confidence > 0.7"
Source: Search returns no results or similarity < threshold

Q: "What will happen next week in the project?"
A: "UNCERTAIN - No future predictions in episodic memory"
Source: Temporal queries only return past/present, not future

Q: "What is the temporal predecessor of the first episode ever created?"
A: "NONE - Episode has no temporal_refs 'before' relationships"
Source: get_temporal_refs() returns empty for first episode
```

**Evaluation Metric:** Abstention F1 - correct identification of unknowns vs incorrect abstentions

---

## Dataset Generation Strategy

### Option A: Synthetic Data (Controlled)
```python
# Create 100 episodes with known ground truth
episodes = [
    {"content": "NEXUS version is 2.0.0", "tags": ["version", "milestone"], "importance": 0.9},
    {"content": "DMR accuracy: 100%", "tags": ["benchmark", "dmr"], "importance": 0.95},
    # ... 98 more
]

# Generate questions with known answers
questions = generate_questions_from_episodes(episodes)
```

**Pros:** Perfect ground truth, reproducible
**Cons:** Not testing real production memory

### Option B: Production Data + Manual Annotation (Realistic) ⭐ RECOMMENDED
```python
# Use existing 553 production episodes
# Manually annotate 100 questions with expected answers
questions = [
    {
        "id": "info_001",
        "category": "information_extraction",
        "question": "What is the NEXUS version?",
        "expected_answer": "2.0.0",
        "source_episode_id": "f765e093-637e-4d76-96d3-d5d214d79e73",
        "evaluation_metric": "exact_match"
    },
    # ... 99 more
]
```

**Pros:** Tests real memory, realistic
**Cons:** Requires manual annotation work

### Option C: Hybrid (Balanced)
```python
# 50 synthetic + 50 production-based
# Synthetic for controlled testing
# Production for realistic validation
```

---

## Implementation Plan

### Phase 1: Dataset Creation (3-4 hours)
1. Analyze production episodes (553 total)
2. Identify key information extractable
3. Create 100 question-answer pairs across 5 categories
4. Format as JSON: `questions.json`

### Phase 2: Evaluation Engine (2-3 hours)
1. Implement query executor (uses NEXUS API)
2. Implement metric calculators:
   - Exact Match (EM)
   - F1 Score
   - Temporal Accuracy
   - Update Accuracy
   - Abstention F1
3. Create `nexus_benchmark.py` runner

### Phase 3: Execution & Analysis (1 hour)
1. Run benchmark against NEXUS
2. Generate results report
3. Compare against expected performance
4. Identify weaknesses/strengths

**Total Estimated Time:** 6-8 hours (1 day)

---

## Evaluation Metrics Details

### 1. Exact Match (EM)
```python
def exact_match(predicted, expected):
    """Binary: 1 if exact match, 0 otherwise"""
    return 1.0 if predicted.strip().lower() == expected.strip().lower() else 0.0
```

### 2. F1 Score
```python
def f1_score(predicted, expected):
    """Token-level F1: precision and recall over words"""
    pred_tokens = set(predicted.lower().split())
    exp_tokens = set(expected.lower().split())

    if len(pred_tokens) == 0 or len(exp_tokens) == 0:
        return 0.0

    common = pred_tokens & exp_tokens
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(exp_tokens)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)
```

### 3. Temporal Accuracy
```python
def temporal_accuracy(predicted, expected):
    """1.0 if temporal relationship correct AND data correct"""
    relationship_correct = predicted['relationship'] == expected['relationship']
    data_correct = f1_score(predicted['data'], expected['data']) > 0.7
    return 1.0 if (relationship_correct and data_correct) else 0.0
```

### 4. Update Accuracy
```python
def update_accuracy(predicted, expected):
    """1.0 if latest value correct"""
    return exact_match(predicted, expected)
```

### 5. Abstention F1
```python
def abstention_f1(predicted, expected):
    """F1 for abstention detection (should_abstain vs did_abstain)"""
    # True Positive: Correctly abstained
    # False Positive: Abstained when shouldn't
    # False Negative: Didn't abstain when should
    # Compute precision/recall/F1
    pass  # Implementation similar to classification F1
```

---

## Expected Performance Targets

Based on NEXUS current capabilities:

| Ability | Target Accuracy | Rationale |
|---------|----------------|-----------|
| Information Extraction | >90% | Strong semantic search + embeddings |
| Multi-Session Reasoning | >80% | Good cross-episode search, needs tuning |
| Temporal Reasoning | >85% | Just implemented, should be strong |
| Knowledge Updates | >75% | Depends on query recency, trickier |
| Abstention | >70% | New capability, conservative estimate |
| **OVERALL** | **>80%** | Solid performance across all abilities |

---

## Success Criteria

1. ✅ Benchmark completes successfully (no crashes)
2. ✅ All 5 categories tested (20 questions each)
3. ✅ Overall accuracy >80%
4. ✅ No category falls below 60%
5. ✅ Results documented and reproducible

---

## Next Steps

1. Create `questions.json` with 100 annotated questions
2. Implement `nexus_benchmark.py` evaluation engine
3. Run benchmark and collect results
4. Document findings in TRACKING.md
5. Prepare for LongMemEval 500-question adaptation

---

**Status:** Design Complete - Ready for Implementation
**Next:** Create questions.json dataset
