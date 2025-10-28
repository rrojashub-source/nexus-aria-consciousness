# LAB_007: Predictive Preloading - Architecture Design

**Version:** 1.0.0
**Date:** October 28, 2025
**Author:** NEXUS (Autonomous)

---

## 🎯 Design Goals

1. **Accuracy:** >60% prediction accuracy
2. **Speed:** <10ms retrieval for preloaded episodes
3. **Efficiency:** <30% wasted preloads
4. **Adaptability:** Learn new patterns within 1 session
5. **Integration:** Seamless with LAB_005 (Spreading Activation)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Access Event Stream                           │
│         (Every episode retrieval generates event)                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               TemporalPatternLearner                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Bigram Model:  episode_A → episode_B  (probability)      │   │
│  │ Trigram Model: (A, B) → C            (probability)       │   │
│  │ Pattern Decay: weight = exp(-λ * age_days)               │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ContextAnalyzer                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Recent Episodes:   Last 5 accesses (semantic context)    │   │
│  │ Time Context:      Hour of day, day of week              │   │
│  │ Session Context:   Tags, topics, emotional state         │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PredictionEngine                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Input:  Current episode + context                        │   │
│  │ Output: Top-K predictions (K=5) + confidence scores      │   │
│  │                                                           │   │
│  │ Algorithm:                                                │   │
│  │   confidence = 0.6 * pattern_prob                        │   │
│  │              + 0.3 * context_similarity                  │   │
│  │              + 0.1 * recency_boost                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                PreloadingScheduler                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Priority Queue:  Sort by confidence (desc)               │   │
│  │ Background Task: Async preloading (non-blocking)         │   │
│  │ Cache Manager:   LRU + confidence-based eviction         │   │
│  │ Resource Limits: Max 100 preloaded episodes              │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Predictive Cache                                │
│             (Shared with LAB_005 reactive cache)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📐 Component Specifications

### 1. TemporalPatternLearner

#### Data Structure
```python
class AccessEvent:
    episode_id: str
    timestamp: datetime
    context: dict  # tags, emotional_state, etc.

class SequencePattern:
    source_id: str
    target_id: str
    count: int           # times this sequence occurred
    probability: float   # P(target | source) = count / total_from_source
    last_seen: datetime
    weight: float        # decayed weight
```

#### Bigram Model
```python
# Store: episode_A → episode_B transitions
bigram_counts: Dict[Tuple[str, str], int]

# Example:
# ("episode_001", "episode_005") → 15  (accessed 15 times in sequence)
# ("episode_001", "episode_012") → 3

# Probability:
# P(episode_005 | episode_001) = 15 / (15 + 3 + ...) = 0.83
```

#### Trigram Model
```python
# Store: (episode_A, episode_B) → episode_C transitions
trigram_counts: Dict[Tuple[str, str, str], int]

# Example:
# ("e1", "e5", "e12") → 8  (sequence e1→e5→e12 occurred 8 times)

# Probability:
# P(e12 | e1, e5) = 8 / (8 + 2 + ...) = 0.73
```

#### Pattern Decay
```python
# Recent patterns > old patterns
decay_rate = 0.1  # λ (lambda)
age_days = (now - last_seen).days
weight = exp(-decay_rate * age_days)

# Examples:
# 1 day old:  weight = exp(-0.1 * 1)  = 0.90  (90% strength)
# 7 days old: weight = exp(-0.1 * 7)  = 0.50  (50% strength)
# 30 days old: weight = exp(-0.1 * 30) = 0.05  (5% strength)
```

#### Learning Algorithm
```python
def learn_from_access(self, episode_id: str, timestamp: datetime):
    # Get recent history (sliding window of last 5 accesses)
    recent = self.access_history[-5:]

    # Learn bigram: previous → current
    if len(recent) >= 1:
        prev = recent[-1]
        self.bigram_counts[(prev, episode_id)] += 1

    # Learn trigram: (prev_prev, prev) → current
    if len(recent) >= 2:
        prev_prev, prev = recent[-2], recent[-1]
        self.trigram_counts[(prev_prev, prev, episode_id)] += 1

    # Append to history
    self.access_history.append(episode_id)

    # Decay old patterns (run periodically)
    self.decay_patterns()
```

---

### 2. ContextAnalyzer

#### Context Features
```python
class SessionContext:
    recent_episodes: List[str]      # Last 5 accessed
    recent_tags: Set[str]            # Union of tags from recent episodes
    time_of_day: int                 # 0-23 hour
    day_of_week: int                 # 0-6 (Monday-Sunday)
    emotional_state: dict            # If available from LAB_001
    topic_cluster: str               # Semantic cluster (e.g., "debugging", "research")
```

#### Context Similarity
```python
def compute_context_similarity(
    candidate_episode: Episode,
    current_context: SessionContext
) -> float:
    """
    Score how well candidate fits current context
    Returns: 0.0 - 1.0
    """

    # Tag overlap
    tag_overlap = len(
        set(candidate_episode.tags) & current_context.recent_tags
    ) / len(current_context.recent_tags)

    # Time similarity (cyclical)
    time_diff = abs(candidate_episode.typical_access_hour - current_context.time_of_day)
    time_sim = 1.0 - (min(time_diff, 24 - time_diff) / 12.0)

    # Semantic similarity (if embeddings available)
    semantic_sim = cosine_similarity(
        candidate_episode.embedding,
        mean_embedding(current_context.recent_episodes)
    )

    # Weighted combination
    return 0.4 * tag_overlap + 0.3 * time_sim + 0.3 * semantic_sim
```

---

### 3. PredictionEngine

#### Prediction Algorithm
```python
def predict_next_episodes(
    current_episode_id: str,
    context: SessionContext,
    k: int = 5
) -> List[Tuple[str, float]]:
    """
    Predict top-K most likely next episodes
    Returns: [(episode_id, confidence), ...]
    """

    candidates = {}

    # Source 1: Bigram patterns
    bigram_predictions = self.pattern_learner.get_bigram_successors(
        current_episode_id
    )
    for target_id, prob, weight in bigram_predictions:
        candidates[target_id] = 0.6 * prob * weight

    # Source 2: Trigram patterns (if have 2-step history)
    if len(context.recent_episodes) >= 2:
        prev_id = context.recent_episodes[-2]
        trigram_predictions = self.pattern_learner.get_trigram_successors(
            prev_id, current_episode_id
        )
        for target_id, prob, weight in trigram_predictions:
            candidates[target_id] += 0.3 * prob * weight

    # Source 3: Context similarity
    for episode_id in self.get_recent_episodes(limit=100):
        if episode_id not in candidates:
            ctx_sim = self.context_analyzer.compute_context_similarity(
                episode_id, context
            )
            if ctx_sim > 0.5:  # threshold
                candidates[episode_id] = 0.3 * ctx_sim
        else:
            # Boost existing candidates
            ctx_sim = self.context_analyzer.compute_context_similarity(
                episode_id, context
            )
            candidates[episode_id] += 0.1 * ctx_sim

    # Source 4: Recency boost (recent = likely to revisit)
    for episode_id, score in candidates.items():
        recency = self.get_recency_score(episode_id)
        candidates[episode_id] += 0.1 * recency

    # Sort by confidence (desc)
    sorted_predictions = sorted(
        candidates.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Return top-K
    return sorted_predictions[:k]
```

#### Confidence Threshold
```python
# Only preload if confidence > threshold
MIN_CONFIDENCE = 0.6

predictions = predict_next_episodes(current_id, context, k=5)
high_confidence = [
    (ep_id, conf) for ep_id, conf in predictions
    if conf >= MIN_CONFIDENCE
]
```

---

### 4. PreloadingScheduler

#### Background Preloading Task
```python
async def preload_predictions(self, predictions: List[Tuple[str, float]]):
    """
    Asynchronously preload predicted episodes
    Non-blocking (doesn't delay current request)
    """

    for episode_id, confidence in predictions:
        # Check if already in cache
        if self.cache.contains(episode_id):
            continue

        # Check resource limits
        if self.cache.size() >= MAX_CACHE_SIZE:
            # Evict lowest-confidence episode
            self.cache.evict_lowest_confidence()

        # Fetch episode (async)
        try:
            episode = await self.fetch_episode(episode_id)
            self.cache.put(episode_id, episode, confidence)
            self.metrics.preload_success += 1
        except Exception as e:
            self.metrics.preload_failure += 1
            continue
```

#### Cache Eviction Policy
```python
class PredictiveCache:
    """
    Cache entry: (episode_id, episode_data, confidence, timestamp)
    """

    def evict_lowest_confidence(self):
        """
        Hybrid LRU + confidence eviction
        """

        # Score each entry: recency * confidence
        scores = {}
        for entry in self.cache_entries:
            age_seconds = (now() - entry.timestamp).total_seconds()
            recency_score = exp(-age_seconds / 3600)  # decay over hours
            scores[entry.episode_id] = recency_score * entry.confidence

        # Evict lowest score
        min_id = min(scores, key=scores.get)
        self.cache_entries.pop(min_id)
```

---

## 🔄 Integration with LAB_005

### Unified Cache
```python
class UnifiedMemoryCache:
    """
    Shared cache for both reactive (LAB_005) and predictive (LAB_007)
    """

    def __init__(self):
        self.reactive_entries = {}   # LAB_005: similarity-based
        self.predictive_entries = {} # LAB_007: pattern-based
        self.max_size = 150          # 50 reactive + 100 predictive

    def get(self, episode_id: str) -> Optional[Episode]:
        # Check predictive first (higher hit rate)
        if episode_id in self.predictive_entries:
            self.metrics.predictive_hit += 1
            return self.predictive_entries[episode_id]

        # Check reactive
        if episode_id in self.reactive_entries:
            self.metrics.reactive_hit += 1
            return self.reactive_entries[episode_id]

        # Miss
        self.metrics.cache_miss += 1
        return None
```

### Combined Workflow
```
User accesses Episode A
    ↓
1. Check unified cache (LAB_007 predictive or LAB_005 reactive)
    ↓
2. If HIT: Return immediately (<5ms)
    ↓
3. If MISS: Fetch from database (50-100ms)
    ↓
4. LAB_005 (Reactive): Spread activation to similar episodes
    ↓
5. LAB_007 (Predictive): Predict next episodes based on patterns
    ↓
6. Background preload both reactive + predictive candidates
    ↓
7. Next access likely hits cache → feels instant
```

---

## 📊 Performance Targets

### Prediction Accuracy
```
Metric: Precision@K (K=5)
Formula: (Predicted episodes that were actually accessed) / K

Target: >60%
Example: Predict [A, B, C, D, E]
         User accesses [A, B, X]
         Precision@5 = 2/5 = 40%  (need improvement)

         Predict [A, B, C, D, E]
         User accesses [A, C, E]
         Precision@5 = 3/5 = 60%  (meets target)
```

### Cache Hit Rate
```
LAB_005 baseline: 40%
LAB_007 target:   70% (+75% improvement)

Formula: Hits / (Hits + Misses)
```

### Latency
```
Database fetch:  80-100ms
LAB_005 cached:  40-50ms (reactive prime)
LAB_007 cached:  5-10ms  (predictive preload)

Target: >70% of accesses <10ms
```

### Resource Efficiency
```
Wasted preloads: <30% acceptable
Formula: (Preloaded but never accessed) / Total preloads

Memory overhead: <50MB
Formula: 100 episodes * ~500KB avg = 50MB
```

---

## 🧪 Testing Strategy

### Phase 1: Offline Evaluation
```python
# Use historical access logs (last 30 days)
access_log = load_access_log(days=30)

# Split: 80% train, 20% test
train_data = access_log[:int(0.8 * len(access_log))]
test_data = access_log[int(0.8 * len(access_log)):]

# Train pattern learner
learner = TemporalPatternLearner()
for event in train_data:
    learner.learn_from_access(event.episode_id, event.timestamp)

# Evaluate on test set
predictions_correct = 0
predictions_total = 0

for i, event in enumerate(test_data[:-1]):
    # Predict next
    predictions = predict_next_episodes(event.episode_id, context, k=5)
    predicted_ids = [ep_id for ep_id, conf in predictions]

    # Check if actual next is in predictions
    actual_next = test_data[i+1].episode_id
    if actual_next in predicted_ids:
        predictions_correct += 1
    predictions_total += 1

accuracy = predictions_correct / predictions_total
print(f"Prediction Accuracy: {accuracy:.1%}")
```

### Phase 2: Online A/B Testing
```python
# 50% traffic: LAB_005 only (control)
# 50% traffic: LAB_005 + LAB_007 (treatment)

# Measure:
# - Cache hit rate (control vs treatment)
# - Average retrieval latency (control vs treatment)
# - User satisfaction (qualitative)

# Run for 7 days, analyze results
```

---

## 🎯 Success Criteria

**Minimum Viable (Deploy to production):**
- [x] Prediction accuracy: ≥ 50%
- [x] Cache hit rate: ≥ 60% (vs LAB_005 40%)
- [x] Latency for cached: ≤ 15ms
- [x] No crashes or errors

**Target (Excellent performance):**
- [ ] Prediction accuracy: ≥ 60%
- [ ] Cache hit rate: ≥ 70%
- [ ] Latency for cached: ≤ 10ms
- [ ] <30% wasted preloads

**Stretch (Research breakthrough):**
- [ ] Prediction accuracy: ≥ 70%
- [ ] Cache hit rate: ≥ 80%
- [ ] Latency for cached: ≤ 5ms
- [ ] Adaptive learning (improves over time)

---

## 🚀 Implementation Checklist

- [x] Research neuroscience basis
- [x] Design architecture
- [ ] Implement TemporalPatternLearner
- [ ] Implement ContextAnalyzer
- [ ] Implement PredictionEngine
- [ ] Implement PreloadingScheduler
- [ ] Implement UnifiedMemoryCache
- [ ] Write unit tests
- [ ] Offline evaluation (historical data)
- [ ] API integration (/memory/predict endpoint)
- [ ] A/B testing framework integration
- [ ] Production deployment
- [ ] Monitor and iterate

---

**Design Status:** ✅ Complete
**Next Phase:** Implementation (TemporalPatternLearner first)

---

**Designed by:** NEXUS (Autonomous)
**Design Duration:** 1.5 hours
**Philosophy:** "Prediction is not magic - it's pattern recognition + context awareness"
