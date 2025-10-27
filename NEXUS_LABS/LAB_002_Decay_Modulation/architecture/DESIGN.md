# 🏗️ LAB_002 Architecture: Decay Modulation Algorithm

**Design Date:** October 27, 2025
**Status:** Design Complete, Ready for Implementation

---

## 🎯 Design Overview

Modulate memory decay rates based on emotional salience, mimicking biological memory consolidation where emotional arousal creates more durable memory traces.

---

## 📊 Algorithm Specification

### Core Formula

```python
decay_modulated_score = similarity * age_factor * (1 + salience_protection)

Where:
  age_factor = 0.95 ^ (days_old / modulation_factor)
  modulation_factor = 1.0 + (salience_score * 1.5)  # 1.0 to 2.5
  salience_protection = salience_score * 0.3        # 0.0 to 0.3 boost
```

---

### Component Breakdown

#### 1. **Base Decay (Standard Ebbinghaus)**

```python
def base_decay(days_old):
    """
    Standard forgetting curve

    Returns:
        Retention factor (0.0 to 1.0)

    Examples:
        7 days  → 0.95^7  = 0.698 (69.8% retained)
        30 days → 0.95^30 = 0.215 (21.5% retained)
        90 days → 0.95^90 = 0.010 (1.0% retained)
    """
    return 0.95 ** days_old
```

#### 2. **Emotional Modulation Factor**

```python
def emotional_modulation_factor(salience_score):
    """
    Convert salience (0.0-1.0) to decay modulation (1.0-2.5x slower)

    Based on neuroscience:
        - Emotional memories decay 2-3x slower
        - Linear mapping from salience to protection

    Args:
        salience_score: From LAB_001 (0.0 to 1.0)

    Returns:
        Modulation factor (1.0 to 2.5)

    Examples:
        salience 0.0 → M = 1.0 (no protection, standard decay)
        salience 0.5 → M = 1.75 (moderate protection)
        salience 0.9 → M = 2.35 (high protection, 2.35x slower)
        salience 1.0 → M = 2.5 (max protection, 2.5x slower)
    """
    return 1.0 + (salience_score * 1.5)
```

#### 3. **Modulated Decay**

```python
def modulated_decay(days_old, salience_score):
    """
    Apply emotional modulation to decay rate

    Formula: 0.95 ^ (days / M)

    Where M = emotional_modulation_factor

    Effect: Dividing by M "stretches" time, making decay slower

    Args:
        days_old: Time since episode creation
        salience_score: From LAB_001

    Returns:
        Retention factor (0.0 to 1.0)

    Examples:
        High salience (0.9), 30 days:
            M = 2.35
            decay = 0.95^(30/2.35) = 0.95^12.77 = 0.505
            vs standard 0.95^30 = 0.215
            → 2.35x better retention!

        Neutral salience (0.5), 30 days:
            M = 1.75
            decay = 0.95^(30/1.75) = 0.95^17.14 = 0.409
            vs standard 0.215
            → 1.90x better retention

        Low salience (0.2), 30 days:
            M = 1.30
            decay = 0.95^(30/1.30) = 0.95^23.08 = 0.299
            vs standard 0.215
            → 1.39x better retention
    """
    M = emotional_modulation_factor(salience_score)
    effective_days = days_old / M
    return 0.95 ** effective_days
```

#### 4. **Salience Protection Boost**

```python
def salience_protection_boost(salience_score):
    """
    Additional direct boost for high-salience memories

    Separate from decay modulation - this is immediate retrieval boost

    Args:
        salience_score: From LAB_001

    Returns:
        Boost multiplier (1.0 to 1.3)

    Examples:
        salience 0.0 → boost = 1.0 (no boost)
        salience 0.5 → boost = 1.15 (+15%)
        salience 0.9 → boost = 1.27 (+27%)
        salience 1.0 → boost = 1.30 (+30%)
    """
    return 1.0 + (salience_score * 0.3)
```

#### 5. **Complete Scoring Function**

```python
def calculate_decay_modulated_score(similarity, created_at, salience_score):
    """
    Complete scoring with both decay modulation and salience boost

    Combines:
        1. Semantic similarity (from vector search)
        2. Age-based decay (modulated by emotion)
        3. Salience protection boost

    Args:
        similarity: Vector similarity score (0.0 to 1.0)
        created_at: Episode timestamp
        salience_score: From LAB_001 (0.0 to 1.0)

    Returns:
        Final weighted score
    """
    # Calculate age
    now = datetime.now()
    days_old = (now - created_at).days

    # Apply modulated decay
    decay_factor = modulated_decay(days_old, salience_score)

    # Apply salience protection boost
    protection_boost = salience_protection_boost(salience_score)

    # Combine all factors
    final_score = similarity * decay_factor * protection_boost

    return final_score
```

---

## 📈 Expected Behavior Examples

### Example 1: Breakthrough Memory (High Salience)

```
Episode: "FASE_8_UPGRADE gift from Ricardo"
Salience: 0.93 (from LAB_001)
Age: 90 days
Similarity: 0.65

Modulation factor: 1.0 + (0.93 * 1.5) = 2.395
Decay: 0.95^(90/2.395) = 0.95^37.58 = 0.152
Protection boost: 1.0 + (0.93 * 0.3) = 1.279

Final score: 0.65 * 0.152 * 1.279 = 0.126

Standard (no LAB_002):
  Decay: 0.95^90 = 0.010
  Final: 0.65 * 0.010 * 1.0 = 0.0065

→ LAB_002 improves score by 19.4x after 90 days!
```

### Example 2: Important Memory (Moderate Salience)

```
Episode: "FASE_4 completion celebration"
Salience: 0.72
Age: 30 days
Similarity: 0.58

Modulation factor: 1.0 + (0.72 * 1.5) = 2.08
Decay: 0.95^(30/2.08) = 0.95^14.42 = 0.476
Protection boost: 1.0 + (0.72 * 0.3) = 1.216

Final score: 0.58 * 0.476 * 1.216 = 0.336

Standard:
  Decay: 0.95^30 = 0.215
  Final: 0.58 * 0.215 * 1.0 = 0.125

→ LAB_002 improves by 2.69x after 30 days
```

### Example 3: Routine Memory (Low Salience)

```
Episode: "Fixed typo in config file"
Salience: 0.25
Age: 30 days
Similarity: 0.62

Modulation factor: 1.0 + (0.25 * 1.5) = 1.375
Decay: 0.95^(30/1.375) = 0.95^21.82 = 0.339
Protection boost: 1.0 + (0.25 * 0.3) = 1.075

Final score: 0.62 * 0.339 * 1.075 = 0.226

Standard:
  Decay: 0.95^30 = 0.215
  Final: 0.62 * 0.215 * 1.0 = 0.133

→ LAB_002 improves by 1.70x (minimal protection as intended)
```

---

## 🔧 Implementation Approach

### Option A: Retrieval-Time Modulation (SELECTED)

**Implementation:** Modify search scoring at query time

**Advantages:**
- ✅ No schema changes required
- ✅ Backward compatible
- ✅ Easy to disable/tune
- ✅ Can be deployed immediately
- ✅ Works with existing infrastructure

**Disadvantages:**
- ❌ Not "true" decay (only affects retrieval)
- ❌ Slightly higher query latency (~10-20ms)

**Integration Point:**
```python
# In main.py - /memory/search endpoint

from emotional_salience_scorer import EmotionalSalienceScorer  # LAB_001
from decay_modulator import DecayModulator  # LAB_002

# After vector search:
for result in results:
    # LAB_001: Calculate salience
    salience = scorer.calculate_salience(result.episode_id, result.timestamp)

    # LAB_002: Apply decay modulation
    decay_score = modulator.calculate_decay_modulated_score(
        similarity=result.similarity_score,
        created_at=result.created_at,
        salience_score=salience.total_score
    )

    result.final_score = decay_score
```

---

## ⚙️ Configuration Parameters

### Tunable Constants

```python
# In DecayModulator class

DECAY_BASE = 0.95  # Daily decay rate (can tune: 0.90-0.98)
MAX_MODULATION = 2.5  # Max protection multiplier (can tune: 2.0-3.0)
PROTECTION_BOOST_FACTOR = 0.3  # Direct boost (can tune: 0.2-0.5)
```

**Tuning Strategy:**
1. Start with bio-validated defaults (0.95, 2.5, 0.3)
2. Run A/B tests with user queries
3. Adjust based on retrieval relevance feedback
4. Grid search if needed: [0.93, 0.95, 0.97] x [2.0, 2.5, 3.0]

---

## 📊 Success Metrics

### Quantitative

1. **Retrieval Precision:** High-salience old memories should rank higher
2. **Temporal Coherence:** Important memories accessible after 60+ days
3. **No Recent Degradation:** Recent memories (<7 days) unaffected

### Qualitative

1. **Emotional Timeline:** FASE milestones still retrievable months later
2. **Routine Fade:** Technical fixes naturally deprioritized over time
3. **User Satisfaction:** Ricardo finds "important old memories" easily

---

## 🔗 Integration with LAB_001

### Data Flow

```
Query Input
    ↓
Vector Search → Top N candidates
    ↓
LAB_001: Calculate Salience (emotional + somatic context)
    ↓
LAB_002: Modulate Decay (age + salience → adjusted score)
    ↓
Re-rank by decay-modulated scores
    ↓
Return Top K results
```

### Combined Effect

**LAB_001 alone (no time factor):**
- Episode A (recent, high salience): Score 0.8
- Episode B (old, low salience): Score 0.6
- Ranking: A > B ✅

**LAB_002 added (time factor):**
- Episode A (7 days old, salience 0.9): 0.8 * 0.95^(7/2.35) * 1.27 = 0.94
- Episode B (30 days old, salience 0.3): 0.6 * 0.95^(30/1.45) * 1.09 = 0.31
- Ranking: A > B ✅✅ (even stronger separation)

**Synergy:** LAB_001 + LAB_002 = Both immediate AND long-term memory prioritization

---

## 🛡️ Safety Mechanisms

### 1. **Fallback to Standard Decay**

```python
if salience_score is None or salience_score < 0:
    # No emotional data available
    modulation_factor = 1.0  # Standard decay
```

### 2. **Cap Modulation**

```python
modulation_factor = min(2.5, 1.0 + salience_score * 1.5)
# Never exceed 2.5x protection (prevents over-preservation)
```

### 3. **Feature Flag**

```python
USE_DECAY_MODULATION = os.getenv("NEXUS_DECAY_MOD_ENABLED", "false")

if not USE_DECAY_MODULATION:
    return standard_score  # Easy disable
```

---

## 🔬 A/B Testing Design

**Control Group:**
```python
results = search_memory(
    query="FASE_8 breakthrough",
    use_emotional_salience=False,  # LAB_001 off
    use_decay_modulation=False     # LAB_002 off
)
```

**Treatment Group 1 (LAB_001 only):**
```python
results = search_memory(
    query="FASE_8 breakthrough",
    use_emotional_salience=True,
    use_decay_modulation=False
)
```

**Treatment Group 2 (LAB_001 + LAB_002):**
```python
results = search_memory(
    query="FASE_8 breakthrough",
    use_emotional_salience=True,
    use_decay_modulation=True
)
```

**Metrics:**
- Precision@K for 60+ day old memories
- User click-through rate on results
- Qualitative feedback from Ricardo

---

## ⏱️ Performance Considerations

**Additional Overhead:**
- Salience calculation: ~5ms (LAB_001)
- Age calculation: <1ms
- Decay modulation math: <1ms
- **Total: ~6-7ms per result**

**For 10 results:** ~60-70ms total overhead (acceptable)

**Optimization:**
- Cache salience scores (calculate once at encoding)
- Pre-compute age daily (batch job)
- Use vectorized operations for batch scoring

---

## 📈 Future Enhancements (Post-LAB_002)

### LAB_003: Sleep Consolidation
- Offline batch processing
- Re-calculate salience for old memories
- Strengthen important connections

### LAB_004: Adaptive Decay
- Learn optimal decay rates from user behavior
- Personalized modulation factors
- Reinforcement learning approach

### LAB_005: Rehearsal Boost
- Frequently accessed memories decay even slower
- Combine access patterns with emotional salience
- "Studying" effect simulation

---

**Design Status:** ✅ Complete
**Next Step:** Implementation (DecayModulator class)
**Estimated Implementation Time:** 1 hour
