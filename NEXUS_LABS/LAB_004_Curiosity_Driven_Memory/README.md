# 🎲 LAB_004: Curiosity-Driven Memory
## *Novelty Detection & Surprise Bonus*

**Status:** 🟡 Active - Research & Design Phase
**Start Date:** October 27, 2025
**Estimated Duration:** Research (30 min), Design (45 min), Implementation (2-3 hours)

---

## 🎯 Hypothesis

**Episodic memories that violate expectations (novelty/surprise) should be consolidated more strongly, mimicking dopaminergic signaling during unexpected events.**

**Core Insight:** The brain doesn't just remember what's important. It remembers what's SURPRISING.

---

## 🧠 Neuroscience Basis

### The Missing Dimension

**LAB_001-003 assume we know what's important:**
- LAB_001: Emotional salience (how intense?)
- LAB_002: Decay protection (how important?)
- LAB_003: Consolidation (how breakthrough?)

**But the brain has another system:** Dopamine surge when something UNEXPECTED happens.

### Dopamine & Prediction Error (Schultz et al., 1997)

**Discovery:** Dopamine neurons in VTA don't respond to reward itself, but to **prediction error**:

```
Expected reward (learned):     Dopamine = 0 (no surprise)
Unexpected reward (novel):     Dopamine = HIGH (surprise!)
Expected but didn't happen:    Dopamine = NEGATIVE (disappointment)
```

**Implication:** Surprise = biological signal to consolidate strongly

**Citation:** Schultz W, Dayan P, Montague PR. "A neural substrate of prediction and reward." *Science* 275(5306):1593-9, 1997.

### Hippocampal Novelty Detection (Lisman & Grace, 2005)

**Mechanism:**
1. Hippocampus detects novelty (compares current to stored patterns)
2. Signals VTA (ventral tegmental area)
3. VTA releases dopamine
4. Dopamine strengthens hippocampal consolidation

**Result:** Novelty bonus - new experiences consolidate faster than repeated ones

**Connection to RL:** "Exploration bonus" in reinforcement learning is biologically grounded!

**Citation:** Lisman JE, Grace AA. "The hippocampal-VTA loop: controlling the entry of information into long-term memory." *Neuron* 46(5):703-13, 2005.

### Curiosity as Intrinsic Motivation (Gottlieb et al., 2013)

**Finding:** Curious episodes are intrinsically rewarding - remembered better even without external reward.

**Brain regions:**
- Anterior cingulate cortex (ACC): Detects information gap
- Striatum: Rewards curiosity satisfaction
- Hippocampus: Encodes curious episodes more strongly

**Implication:** Novel stimuli = rewarding = stronger consolidation

**Citation:** Gottlieb J, Oudeyer PY, Lopes M, Baranes A. "Information-seeking, curiosity, and attention." *Trends Cogn Sci* 17(11):585-96, 2013.

### Temporal Context & Surprise (Hyman et al., 2012)

**Finding:** Unexpected emotional shifts trigger dopamine release.

**Example:**
- Steady frustration for 2 hours → Sudden breakthrough joy
- Dopamine surge at transition point
- Episode consolidates 3x stronger

**Citation:** Hyman SE, Malenka RC, Nestler EJ. "Neural mechanisms of addiction: the role of reward-related learning and memory." *Annu Rev Neurosci* 29:565-98, 2006.

---

## 💡 Core Idea

**Build expectation model → Detect violations → Boost consolidation**

### 4 Dimensions of Surprise

#### 1. Semantic Novelty 📚
**What:** Content distance from established clusters

**Method:**
- Calculate centroid embeddings of existing episode clusters
- Measure cosine distance of new episode to nearest centroid
- High distance = HIGH semantic novelty

**Example:**
```
Existing clusters: {debugging, meetings, documentation}
New episode: "quantum entanglement analogy for distributed systems"
Distance: 0.85 (very far from all clusters)
→ Semantic novelty: HIGH
```

**Biological parallel:** Hippocampal pattern separation

#### 2. Emotional Surprise ⚡
**What:** Sudden changes in emotional state

**Method:**
- Track valence/arousal trajectory over time
- Detect jumps > 2 standard deviations
- Larger jumps = HIGHER emotional surprise

**Example:**
```
09:00-14:00: Valence = -0.6 (frustrated debugging)
14:15:       Valence = +0.9 (breakthrough!)
Jump: 1.5 (3 std deviations)
→ Emotional surprise: VERY HIGH
```

**Biological parallel:** Dopamine prediction error

#### 3. Pattern Violation 🔀
**What:** Breaks established episode sequences

**Method:**
- Learn common sequences (n-grams of episode types)
- Detect deviations from expected next episode
- Rare sequences = pattern violations

**Example:**
```
Learned pattern: debug → test → deploy (90% of time)
Actual today:    debug → BREAKTHROUGH → ship
Expected: test
Actual: BREAKTHROUGH
→ Pattern violation: HIGH
```

**Biological parallel:** Sequence prediction in prefrontal cortex

#### 4. Contextual Mismatch 🎭
**What:** Content doesn't match expected context

**Method:**
- Build context-content probability distributions
- Detect low-probability pairings
- Mismatches = contextual surprise

**Example:**
```
Context: "technical_meeting"
Expected content: {architecture, bugs, roadmap}
Actual content: "personal_philosophy_insight"
P(philosophy | meeting) = 0.05
→ Contextual mismatch: HIGH
```

**Biological parallel:** Context-dependent memory in hippocampus

---

## 🔬 Novelty Scoring Algorithm

### Composite Novelty Score

```python
novelty_score = (
    semantic_novelty * 0.30 +      # How far from existing clusters?
    emotional_surprise * 0.25 +    # Unexpected emotion change?
    pattern_violation * 0.25 +     # Violates learned sequences?
    contextual_mismatch * 0.20     # Doesn't fit expected context?
)

# Range: 0.0 (completely routine) to 1.0 (extremely novel)
```

### Semantic Novelty Calculation

```python
def calculate_semantic_novelty(episode_embedding, cluster_centroids):
    """
    Measure distance from existing knowledge clusters
    """
    # Find nearest cluster centroid
    distances = [cosine_distance(episode_embedding, centroid)
                 for centroid in cluster_centroids]
    min_distance = min(distances)

    # Normalize to 0-1 (distance 0.5+ is very novel)
    semantic_novelty = min(min_distance / 0.5, 1.0)

    return semantic_novelty
```

### Emotional Surprise Calculation

```python
def calculate_emotional_surprise(current_valence, recent_history):
    """
    Detect sudden emotional state changes
    """
    # Calculate mean/std of recent valence
    mean_valence = np.mean(recent_history)
    std_valence = np.std(recent_history)

    # Measure deviation from expectation
    deviation = abs(current_valence - mean_valence)
    z_score = deviation / (std_valence + 0.01)  # Avoid div by zero

    # Normalize: 2+ std deviations = maximal surprise
    emotional_surprise = min(z_score / 2.0, 1.0)

    return emotional_surprise
```

### Pattern Violation Calculation

```python
def calculate_pattern_violation(episode_type, previous_types, sequence_model):
    """
    Detect deviations from learned sequences
    """
    # Get expected next episode type(s)
    expected_distribution = sequence_model.predict_next(previous_types)

    # Probability of actual episode type
    actual_probability = expected_distribution.get(episode_type, 0.0)

    # Low probability = high violation
    pattern_violation = 1.0 - actual_probability

    return pattern_violation
```

### Contextual Mismatch Calculation

```python
def calculate_contextual_mismatch(episode_content, episode_context, context_model):
    """
    Detect unexpected content given context
    """
    # Get expected content distribution for this context
    expected_topics = context_model.get_topics_for_context(episode_context)

    # Compare episode content to expected topics
    content_similarity = max([
        cosine_similarity(episode_content, topic)
        for topic in expected_topics
    ])

    # Low similarity = high mismatch
    contextual_mismatch = 1.0 - content_similarity

    return contextual_mismatch
```

---

## 🎯 Integration with LAB_001-003

### During Episode Creation (LAB_001)

**Add novelty dimension:**

```python
# Existing LAB_001
salience_score = calculate_emotional_salience(emotional_8d, somatic_7d)

# NEW: LAB_004
novelty_score = calculate_novelty(
    episode_embedding,
    emotional_trajectory,
    episode_type_history,
    context
)

# Store both
metadata = {
    "salience_score": salience_score,      # LAB_001: How intense?
    "novelty_score": novelty_score,        # LAB_004: How surprising?
    ...
}
```

**Key:** Salience and novelty are **orthogonal dimensions**:
- High salience + low novelty = Important but expected (routine success)
- Low salience + high novelty = Surprising but calm (novel insight)
- High salience + high novelty = MAXIMUM preservation (unexpected breakthrough!)
- Low salience + low novelty = Skip consolidation (routine noise)

### During Decay (LAB_002)

**Novelty slows decay:**

```python
# Existing LAB_002
M = 1.0 + (salience_score * 1.5)  # Multiplier: 1.0 to 2.5

# NEW: Add novelty bonus
novelty_bonus = novelty_score * 0.5  # Up to +0.5 to multiplier
M_enhanced = M + novelty_bonus       # Range: 1.0 to 3.0

# Decay with enhanced multiplier
R(t) = 0.95^(t / M_enhanced)
```

**Effect:** Novel episodes decay even slower than just high-salience episodes.

### During Consolidation (LAB_003)

**Surprise bonus during sleep:**

```python
# Existing LAB_003 breakthrough score
breakthrough_score = (
    salience_score * 0.40 +
    emotional_sum * 0.25 +
    abs(valence) * 0.15 +
    importance_score * 0.20
)

# NEW: Add novelty component
breakthrough_score_enhanced = (
    salience_score * 0.35 +        # Slightly reduced
    emotional_sum * 0.20 +         # Slightly reduced
    abs(valence) * 0.15 +          # Same
    importance_score * 0.15 +      # Slightly reduced
    novelty_score * 0.15           # NEW: Novelty bonus
)

# Consolidation boost considers novelty
if novelty_score > 0.7:
    consolidated_boost += 0.15  # Extra boost for surprising episodes
```

**Effect:** Surprising breakthroughs get stronger consolidation than expected ones.

---

## 📊 Expected Behavior

### Example: Debugging Day with Surprise

**Timeline:**

```
09:00 - "Starting routine debugging of authentication bug"
        Salience: 0.55 (moderate task focus)
        Novelty: 0.12 (very routine, done this 100x)
        → Standard encoding

11:30 - "Found bizarre race condition in async token refresh"
        Salience: 0.78 (high - interesting problem)
        Novelty: 0.76 (HIGH - never seen this pattern before)
        Emotional surprise: 0.82 (shift from boredom to curiosity)
        → SURPRISE DETECTED - boosted consolidation

14:00 - "Meeting about Q4 authentication roadmap"
        Salience: 0.45 (routine meeting)
        Novelty: 0.15 (expected context)
        → Standard encoding

16:45 - "Sudden insight: quantum entanglement analogy explains race condition!"
        Salience: 0.88 (high - breakthrough moment)
        Novelty: 0.91 (VERY HIGH - never connected quantum physics to auth before)
        Semantic novelty: 0.89 (far from all existing clusters)
        Contextual mismatch: 0.85 (physics in auth context?!)
        → MAXIMUM SURPRISE - maximum consolidation

18:00 - "Wrapping up, documenting solution"
        Salience: 0.62 (routine closure)
        Novelty: 0.10 (expected end-of-day)
        → Standard encoding
```

**Consolidation Report (3:00 AM):**

```json
{
  "breakthroughs": [
    {
      "time": "16:45",
      "content": "quantum entanglement analogy for race condition",
      "salience": 0.88,
      "novelty": 0.91,
      "surprise_bonus": +0.25,
      "final_boost": +0.45,
      "reason": "Extreme semantic novelty + contextual mismatch"
    },
    {
      "time": "11:30",
      "content": "bizarre async race condition",
      "salience": 0.78,
      "novelty": 0.76,
      "surprise_bonus": +0.15,
      "final_boost": +0.30,
      "reason": "High novelty + emotional surprise"
    }
  ],
  "routine_episodes": 3,
  "novel_episodes": 2,
  "surprise_threshold": 0.7
}
```

**Retrieval 30 Days Later:**

- 16:45 quantum insight: **95% recall** (salience + novelty + surprise bonus)
- 11:30 race condition: **88% recall** (novelty protected)
- 09:00 routine start: **40% recall** (low novelty, decayed)
- 14:00 meeting: **35% recall** (expected, decayed)

**Outcome:** Surprising discoveries preserved much longer than routine work, even if routine work was also important.

---

## 🔧 Implementation Strategy

### Phase 1: Baseline Model Building (Offline)

**Goal:** Learn what "normal" looks like

**Process:**
```python
1. Fetch last 30 days of episodes
2. Calculate cluster centroids (semantic baseline)
3. Build emotional trajectory model (valence/arousal norms)
4. Learn common sequences (episode type n-grams)
5. Map context-content probabilities
6. Store baseline models in database
```

**Deliverable:** `baseline_models` table with serialized models

### Phase 2: Real-Time Novelty Scoring (During Encoding)

**Goal:** Score each new episode for novelty

**Integration Point:** Episode creation endpoint

```python
@app.post("/memory/action")
async def record_action(request):
    # Existing LAB_001
    salience_score = calculate_salience(...)

    # NEW: LAB_004
    novelty_detector = NoveltyDetector(baseline_models)
    novelty_score = novelty_detector.calculate_novelty(
        episode_content=request.content,
        episode_embedding=embedding,
        episode_context=request.context,
        emotional_state=emotional_8d,
        recent_history=fetch_recent_episodes(hours=6)
    )

    # Store both
    metadata["salience_score"] = salience_score
    metadata["novelty_score"] = novelty_score
```

**Deliverable:** `novelty_score` added to episode metadata

### Phase 3: Consolidation Integration (Sleep Processing)

**Goal:** Use novelty during LAB_003 consolidation

**Integration Point:** ConsolidationEngine

```python
class ConsolidationEngine:
    def identify_breakthroughs(self, episodes):
        for ep in episodes:
            # Existing breakthrough score
            base_score = self._calculate_base_breakthrough(ep)

            # NEW: Add novelty bonus
            novelty_bonus = ep.novelty_score * 0.15

            ep.breakthrough_score = base_score + novelty_bonus
```

**Deliverable:** Surprise bonus in consolidation algorithm

### Phase 4: Curiosity Report (New Endpoint)

**Goal:** "Show me today's surprises"

**New Endpoint:**

```python
@app.get("/memory/surprises")
async def get_surprises(date: str = "today", min_novelty: float = 0.7):
    """
    Retrieve most surprising episodes from a given date

    Returns:
    - Top 5 most novel episodes
    - Breakdown of surprise sources (semantic, emotional, pattern, context)
    - Surprise timeline (when did surprises cluster?)
    """
    episodes = fetch_episodes_from_date(date)
    surprises = [ep for ep in episodes if ep.novelty_score >= min_novelty]
    surprises.sort(key=lambda x: x.novelty_score, reverse=True)

    return {
        "date": date,
        "total_episodes": len(episodes),
        "surprising_episodes": len(surprises),
        "top_surprises": surprises[:5],
        "surprise_breakdown": calculate_surprise_breakdown(surprises)
    }
```

**Deliverable:** Curiosity analytics endpoint

---

## 🎓 Success Criteria

**Quantitative:**
1. Baseline models trained on 30+ days of data
2. Novelty scoring adds <10ms overhead to episode creation
3. High-novelty episodes (>0.7) show 20-30% stronger consolidation
4. Surprise detection precision >75% (manual validation)

**Qualitative:**
1. Unexpected breakthroughs automatically flagged
2. "Quantum entanglement" type insights preserved strongly
3. Routine work correctly classified as low-novelty
4. Curiosity report highlights genuinely surprising moments

---

## 📁 Deliverables

- [ ] Structure created ✅
- [ ] Research: Dopamine prediction error & novelty papers
- [ ] Architecture: Novelty scoring algorithm spec
- [ ] Implementation: NoveltyDetector class
- [ ] Integration: Add novelty_score to episode metadata
- [ ] Enhancement: LAB_003 surprise bonus
- [ ] Endpoint: GET /memory/surprises
- [ ] Testing: Historical episode validation
- [ ] Results: RESULTS.md with surprise analytics

---

## 🔗 Synergy with Existing LABs

| Lab | Function | LAB_004 Enhancement |
|-----|----------|-------------------|
| **LAB_001** | Emotional salience | + Novelty dimension (orthogonal) |
| **LAB_002** | Decay protection | Novel episodes decay slower (+0.5 multiplier) |
| **LAB_003** | Consolidation | Surprise bonus (+0.15 to +0.25 boost) |

**Combined Effect:**

```
High salience + High novelty = MAXIMUM preservation
├─ LAB_001: Strong initial encoding
├─ LAB_002: Slowest decay (M up to 3.0)
├─ LAB_003: Strongest consolidation boost
└─ LAB_004: Surprise flagging + analytics
```

---

## ⚠️ Risks & Mitigations

**Risk 1:** Over-flagging novelty (everything seems new)
- **Mitigation:** Adaptive threshold - learn from 30 days, not 3 days
- Update baseline models weekly

**Risk 2:** Expensive computations (cluster distance, sequence prediction)
- **Mitigation:** Cache cluster centroids, use approximate nearest neighbors
- Novelty scoring should add <10ms overhead

**Risk 3:** False positives (random noise flagged as novel)
- **Mitigation:** Require novelty on multiple dimensions (semantic + emotional)
- Single-dimension spikes don't trigger bonus

**Risk 4:** Stale baseline models (world changes, old normal no longer relevant)
- **Mitigation:** Rolling window - baseline uses last 30-60 days, not all-time
- Automatic model refresh weekly

---

## 🚀 Future Enhancements (Post-LAB_004)

**LAB_005:** Pattern Learning
- Explicit sequence models (LSTMs, transformers)
- "Predict next episode" accuracy tracking
- Anomaly detection when predictions fail

**LAB_006:** Active Curiosity
- NEXUS asks clarifying questions when novelty detected
- "This seems unusual - tell me more?"
- Interactive surprise exploration

**LAB_007:** Cross-Domain Analogies
- Detect when insights from Domain A applied to Domain B
- "Quantum physics → distributed systems" connections
- Semantic bridge detection

---

## 🔬 Research Questions

1. **Optimal novelty threshold:** 0.7? 0.8? Dynamic based on daily distribution?
2. **Component weights:** Is 30% semantic, 25% emotional, 25% pattern, 20% context optimal?
3. **Baseline window:** 30 days? 60 days? Adaptive?
4. **Surprise bonus magnitude:** +0.15? +0.25? Linear or exponential with novelty?
5. **Update frequency:** Refresh baselines daily? Weekly? Monthly?

---

**Lead:** NEXUS (Claude Code)
**Collaborator:** Ricardo Rojas
**Philosophy:** *"The brain doesn't just remember what's important. It remembers what's SURPRISING."*
**Status:** 🟡 Active - Research phase
**Next Step:** Neuroscience research on dopamine prediction error & novelty detection

---

*Inspired by 30+ years of dopamine research, implementing what evolution discovered: Surprise = Learn.*
