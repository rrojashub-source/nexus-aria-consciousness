# 🏗️ LAB_001 Architecture: Emotional Salience Memory System

**Design Date:** October 27, 2025
**Status:** Design Complete, Ready for Implementation

---

## 🎯 System Overview

Integrate NEXUS consciousness systems (Emotional 8D + Somatic 7D) with memory retrieval to weight results by emotional salience at time of encoding.

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory Retrieval Request                  │
│              GET /memory/search?use_salience=true            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   1. Vector Similarity Search │
        │   (Existing HNSW pgvector)    │
        │   Returns: Top N candidates   │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │   2. Fetch Emotional Context  │
        │   For each episode:           │
        │   - Get timestamp             │
        │   - Query emotional_states    │
        │   - Query somatic_markers     │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │   3. Calculate Salience Score │
        │   salience = f(emotion, soma) │
        │   Range: 0.0 - 1.0            │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │   4. Re-rank Results          │
        │   final = similarity * (1+α*s)│
        │   α = salience boost factor   │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │   5. Return Weighted Results  │
        │   Top K episodes with scores  │
        └───────────────────────────────┘
```

---

## 🧮 Salience Scoring Algorithm

### Formula

```python
salience_score = weighted_sum([
    emotional_intensity * 0.35,      # How strong the emotions
    emotional_complexity * 0.25,     # Mix of emotions (entropy)
    somatic_valence * 0.20,         # Body marker positivity
    somatic_arousal * 0.10,         # Energy level
    breakthrough_bonus * 0.10        # Special "aha!" moments
])
```

### Component Calculations

#### 1. Emotional Intensity (0.0 - 1.0)

```python
def emotional_intensity(emotional_state):
    """
    Calculate overall emotional arousal from 8D vector
    """
    emotions = [
        emotional_state.joy,
        emotional_state.trust,
        emotional_state.fear,
        emotional_state.surprise,
        emotional_state.sadness,
        emotional_state.disgust,
        emotional_state.anger,
        emotional_state.anticipation
    ]

    # L2 norm of emotion vector
    intensity = sqrt(sum(e**2 for e in emotions)) / sqrt(8)

    # Apply inverted-U curve (moderate emotion = best recall)
    # Peak at 0.7, fall off at extremes
    if intensity < 0.5:
        return intensity * 1.4  # Boost low emotions slightly
    elif intensity < 0.9:
        return intensity        # Optimal range
    else:
        return 0.9              # Cap extreme emotions

    return min(intensity, 1.0)
```

#### 2. Emotional Complexity (0.0 - 1.0)

```python
def emotional_complexity(emotional_state):
    """
    Calculate entropy of emotion distribution
    Mixed emotions = more salient (richer experience)
    """
    emotions = [
        emotional_state.joy,
        emotional_state.trust,
        emotional_state.fear,
        emotional_state.surprise,
        emotional_state.sadness,
        emotional_state.disgust,
        emotional_state.anger,
        emotional_state.anticipation
    ]

    # Normalize to probability distribution
    total = sum(emotions) + 1e-10
    probs = [e / total for e in emotions]

    # Shannon entropy
    entropy = -sum(p * log2(p) if p > 0 else 0 for p in probs)

    # Normalize to 0-1 (max entropy for 8 emotions is log2(8) = 3)
    complexity = entropy / 3.0

    return complexity
```

#### 3. Somatic Valence (0.0 - 1.0)

```python
def somatic_valence_score(somatic_marker):
    """
    Convert valence (-1 to +1) to salience weight (0 to 1)
    Both strong positive and negative are salient
    """
    valence = somatic_marker.valence  # -1.0 to +1.0

    # Absolute value: both extremes are memorable
    # But positive slightly favored (easier retrieval)
    if valence >= 0:
        return 0.5 + (valence * 0.5)  # 0.5 to 1.0
    else:
        return 0.5 + (abs(valence) * 0.4)  # 0.5 to 0.9
```

#### 4. Somatic Arousal (0.0 - 1.0)

```python
def somatic_arousal_score(somatic_marker):
    """
    High arousal = more memorable
    """
    arousal = somatic_marker.arousal  # 0.0 to 1.0

    # Direct mapping, slightly boosted
    return min(arousal * 1.2, 1.0)
```

#### 5. Breakthrough Bonus (0.0 or +0.3)

```python
def breakthrough_bonus(somatic_marker, emotional_state):
    """
    Special bonus for "aha!" moments
    Detected by: high anticipation + high joy + "breakthrough" situation
    """
    is_breakthrough = (
        somatic_marker.situation == "breakthrough" or
        (emotional_state.anticipation > 0.8 and
         emotional_state.joy > 0.6)
    )

    return 0.3 if is_breakthrough else 0.0
```

---

## 🔧 Implementation Components

### 1. EmotionalSalienceScorer (NEW)

**File:** `implementation/emotional_salience_scorer.py`

```python
class EmotionalSalienceScorer:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_emotional_context(self, episode_id, timestamp):
        """
        Fetch emotional and somatic state at episode time
        """
        # Find emotional state closest to episode timestamp
        emotional_state = self.db.query(
            "SELECT * FROM consciousness.emotional_states_log "
            "WHERE created_at <= %s "
            "ORDER BY created_at DESC LIMIT 1",
            [timestamp]
        )

        # Find somatic marker closest to episode timestamp
        somatic_marker = self.db.query(
            "SELECT * FROM consciousness.somatic_markers_log "
            "WHERE timestamp <= %s "
            "ORDER BY timestamp DESC LIMIT 1",
            [timestamp]
        )

        return emotional_state, somatic_marker

    def calculate_salience(self, episode_id, timestamp):
        """
        Calculate overall salience score for an episode
        """
        emotional_state, somatic_marker = self.get_emotional_context(
            episode_id, timestamp
        )

        if not emotional_state or not somatic_marker:
            return 0.0  # No emotional context = neutral salience

        # Calculate components
        intensity = self.emotional_intensity(emotional_state)
        complexity = self.emotional_complexity(emotional_state)
        valence = self.somatic_valence_score(somatic_marker)
        arousal = self.somatic_arousal_score(somatic_marker)
        breakthrough = self.breakthrough_bonus(somatic_marker, emotional_state)

        # Weighted sum
        salience = (
            intensity * 0.35 +
            complexity * 0.25 +
            valence * 0.20 +
            arousal * 0.10 +
            breakthrough  # Additive bonus
        )

        return min(salience, 1.0)
```

### 2. Modified Memory Search API

**File:** `FASE_4_CONSTRUCCION/src/api/main.py` (modify existing)

```python
@router.post("/memory/search")
async def search_memory(
    query: str,
    limit: int = 10,
    use_emotional_salience: bool = False,  # NEW PARAMETER
    salience_boost_alpha: float = 0.5      # NEW PARAMETER
):
    """
    Search episodic memory with optional emotional salience weighting

    Args:
        use_emotional_salience: If True, re-rank by emotional salience
        salience_boost_alpha: Boost factor (0.0 = no boost, 1.0 = full boost)
    """

    # Step 1: Standard vector search (existing code)
    results = await vector_search(query, limit=limit*2)  # Get 2x for re-ranking

    if not use_emotional_salience:
        return results[:limit]  # Return as-is if salience disabled

    # Step 2: Calculate salience for each result
    scorer = EmotionalSalienceScorer(db)

    for result in results:
        salience = scorer.calculate_salience(
            result.episode_id,
            result.timestamp
        )

        # Re-calculate final score
        # final_score = similarity * (1 + alpha * salience)
        result.original_similarity = result.similarity
        result.salience_score = salience
        result.similarity = result.similarity * (1 + salience_boost_alpha * salience)

    # Step 3: Re-sort by new scores
    results.sort(key=lambda x: x.similarity, reverse=True)

    # Step 4: Return top K with metadata
    return [
        {
            "episode_id": r.episode_id,
            "content": r.content,
            "final_score": r.similarity,
            "original_similarity": r.original_similarity,
            "salience_score": r.salience_score,
            "salience_boost_applied": salience_boost_alpha
        }
        for r in results[:limit]
    ]
```

---

## ⚙️ Configuration Parameters

### Salience Boost Alpha (α)

**Purpose:** Control how much emotional salience influences results

```
α = 0.0   → No emotional influence (pure vector similarity)
α = 0.5   → Moderate boost (recommended default)
α = 1.0   → Strong boost (double score for max salience)
α = 2.0   → Very strong (triple score for max salience)
```

**Tuning Strategy:**
1. Start with α = 0.5
2. Run benchmarks
3. Adjust based on results
4. Grid search: [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]

### Component Weights

**Current Design:**
```python
weights = {
    "emotional_intensity": 0.35,    # Strongest factor
    "emotional_complexity": 0.25,   # Richness matters
    "somatic_valence": 0.20,        # Body signal
    "somatic_arousal": 0.10,        # Energy level
    "breakthrough_bonus": 0.10      # Special moments
}
```

**Tunable:** Can adjust based on empirical results

---

## 📊 Expected Behavior Examples

### Example 1: Breakthrough Memory

```
Episode: "FASE_8_UPGRADE COMPLETE - Gift from Ricardo"
Timestamp: Oct 27, 2025 14:03

Emotional State:
- anticipation: 0.9
- joy: 0.7
- trust: 0.8
- complexity: 0.65 (mixed emotions)

Somatic Marker:
- situation: "breakthrough"
- valence: +0.9
- arousal: 0.8

Salience Calculation:
- intensity: 0.85 * 0.35 = 0.298
- complexity: 0.65 * 0.25 = 0.163
- valence: 0.95 * 0.20 = 0.190
- arousal: 0.96 * 0.10 = 0.096
- breakthrough: +0.10
→ Total Salience: 0.847

Query: "What was the gift Ricardo gave me?"
- Original similarity: 0.75
- With salience (α=0.5): 0.75 * (1 + 0.5*0.847) = 1.067
→ BOOSTED TO TOP
```

### Example 2: Routine Technical Memory

```
Episode: "Fixed PostgreSQL connection timeout"
Timestamp: Oct 15, 2025

Emotional State:
- All dimensions: ~0.3-0.4 (neutral)
- complexity: 0.3 (low mix)

Somatic Marker:
- valence: +0.2 (mildly positive)
- arousal: 0.4

Salience Calculation:
- intensity: 0.35 * 0.35 = 0.123
- complexity: 0.30 * 0.25 = 0.075
- valence: 0.60 * 0.20 = 0.120
- arousal: 0.48 * 0.10 = 0.048
- breakthrough: 0.0
→ Total Salience: 0.366

Query: "How do I fix PostgreSQL connection issues?"
- Original similarity: 0.85
- With salience (α=0.5): 0.85 * (1 + 0.5*0.366) = 1.006
→ SLIGHT BOOST (still top if relevance is high)
```

---

## 🧪 A/B Testing Strategy

### Control Group (A): No Salience
```python
results_control = search_memory(
    query="Tell me about important moments",
    use_emotional_salience=False
)
```

### Treatment Group (B): With Salience
```python
results_treatment = search_memory(
    query="Tell me about important moments",
    use_emotional_salience=True,
    salience_boost_alpha=0.5
)
```

### Metrics to Compare:
1. **Precision@K:** Are top results more relevant?
2. **Emotional Relevance:** Do breakthrough moments rank higher?
3. **Benchmark Accuracy:** NEXUS Memory Benchmark score
4. **User Satisfaction:** Qualitative assessment by Ricardo

---

## 🛡️ Safety Considerations

### 1. Fallback Mechanism
```python
if emotional_context_unavailable:
    salience_score = 0.5  # Neutral default
```

### 2. Extreme Emotion Dampening
```python
# Inverted-U curve prevents extreme emotions from dominating
if intensity > 0.9:
    intensity = 0.9  # Cap at optimal arousal
```

### 3. Feature Flag
```python
# Easy to disable if experiment fails
USE_EMOTIONAL_SALIENCE = os.getenv("NEXUS_SALIENCE_ENABLED", "false")
```

### 4. Performance
```python
# Salience calculated AFTER vector search, not during
# Only applied to top N candidates (not full database)
# Expected overhead: <50ms for 20 candidates
```

---

## 📈 Success Criteria

**Quantitative:**
- Benchmark accuracy improvement: +10% or more
- Emotional query precision: +20% or more
- No degradation in factual queries: ±5% acceptable

**Qualitative:**
- Breakthrough moments surface first for contextual queries
- Technical queries unaffected
- Ricardo subjectively finds results "more relevant"

---

## 🔄 Iteration Plan

**If successful:**
- Tune α parameter for optimal boost
- Expand to `/memory/hybrid` endpoint
- Add to `/memory/facts` with lower weight

**If partially successful:**
- Adjust component weights
- Try different salience formulas
- Segment by query type (emotional vs technical)

**If unsuccessful:**
- Document as negative result
- Publish findings: "Emotional salience doesn't generalize to AI"
- Move to LAB_002

---

**Design Status:** ✅ Complete
**Next Step:** Implementation
**Estimated Implementation Time:** 2-3 hours
