# 🎲 LAB_004 Algorithm Design: Novelty Detection & Surprise Scoring

**Design Date:** October 27, 2025
**Version:** 1.0
**Status:** Specification Complete - Ready for Implementation

---

## 🎯 Algorithm Overview

**Goal:** Detect novelty/surprise in episodic memories and boost consolidation for unexpected events.

**Pipeline:**

```
Episode Creation
    ↓
[1] Build Baseline Models (offline, one-time)
    ↓
[2] Calculate Novelty Score (real-time, per episode)
    ├─ [2a] Semantic Novelty
    ├─ [2b] Emotional Surprise
    ├─ [2c] Pattern Violation
    └─ [2d] Contextual Mismatch
    ↓
[3] Store novelty_score in metadata
    ↓
[4] Use during consolidation (LAB_003 integration)
    ↓
[5] Analytics: "Show me today's surprises"
```

---

## 📐 STEP 1: Baseline Model Building (Offline)

### Purpose
Learn what "normal" looks like from historical data.

### Frequency
- Initial build: One-time from last 30 days
- Refresh: Weekly (rolling 60-day window)

### Components

#### 1.1 Semantic Cluster Model

**Input:** All episode embeddings from last 30 days

**Process:**
```python
from sklearn.cluster import KMeans
import numpy as np

def build_semantic_clusters(embeddings, n_clusters=10):
    """
    Cluster historical embeddings to find semantic centroids

    Args:
        embeddings: List of 1536-dim vectors
        n_clusters: Number of clusters (default 10)

    Returns:
        centroids: List of cluster centers
        labels: Cluster assignment for each embedding
    """
    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    centroids = kmeans.cluster_centers_

    return centroids, labels
```

**Output:** List of cluster centroids (10 semantic "topics")

**Example Clusters (Inferred):**
- Cluster 0: Debugging/troubleshooting episodes
- Cluster 1: Meeting/collaboration episodes
- Cluster 2: Documentation/writing episodes
- Cluster 3: Learning/research episodes
- Cluster 4: Architecture/design episodes
- ...

**Storage:**
```sql
CREATE TABLE novelty_baselines (
    model_name VARCHAR(50) PRIMARY KEY,
    model_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

INSERT INTO novelty_baselines (model_name, model_data)
VALUES ('semantic_clusters', jsonb_build_object(
    'centroids', [[...], [...], ...],  -- 10 x 1536 array
    'n_clusters', 10,
    'trained_on_episodes', 450,
    'date_range', ['2025-09-27', '2025-10-27']
));
```

---

#### 1.2 Emotional Trajectory Model

**Input:** Valence/arousal values from last 30 days

**Process:**
```python
def build_emotional_baseline(episodes):
    """
    Calculate normal emotional state distributions

    Returns:
        stats: {
            'valence_mean': float,
            'valence_std': float,
            'arousal_mean': float,
            'arousal_std': float,
            'typical_transitions': {
                'small': 0.15,  # 1 std
                'medium': 0.30, # 2 std
                'large': 0.60   # 3+ std
            }
        }
    """
    valences = [ep.somatic_7d['valence'] for ep in episodes]
    arousals = [ep.somatic_7d['arousal'] for ep in episodes]

    # Calculate distributions
    stats = {
        'valence_mean': np.mean(valences),
        'valence_std': np.std(valences),
        'arousal_mean': np.mean(arousals),
        'arousal_std': np.std(arousals)
    }

    # Learn typical transition magnitudes
    transitions = []
    for i in range(1, len(valences)):
        delta = abs(valences[i] - valences[i-1])
        transitions.append(delta)

    stats['typical_transitions'] = {
        'small': np.percentile(transitions, 50),   # Median
        'medium': np.percentile(transitions, 75),  # 75th percentile
        'large': np.percentile(transitions, 95)    # 95th percentile
    }

    return stats
```

**Output:** Mean/std for valence and arousal

**Storage:**
```python
model_data = {
    'valence_mean': -0.05,
    'valence_std': 0.42,
    'arousal_mean': 0.55,
    'arousal_std': 0.28,
    'typical_transitions': {
        'small': 0.12,
        'medium': 0.28,
        'large': 0.65
    }
}
```

---

#### 1.3 Sequence Pattern Model (N-grams)

**Input:** Episode type sequences from last 30 days

**Process:**
```python
from collections import defaultdict, Counter

def build_sequence_model(episodes, n=2):
    """
    Learn common episode type sequences (bigrams)

    Args:
        episodes: Ordered list of episodes
        n: N-gram size (2 = bigrams)

    Returns:
        transitions: {
            ('debug', 'test'): 0.75,
            ('debug', 'breakthrough'): 0.05,
            ('test', 'deploy'): 0.82,
            ...
        }
    """
    # Extract episode types (inferred from content/tags)
    types = [classify_episode_type(ep) for ep in episodes]

    # Count bigrams
    bigrams = defaultdict(Counter)
    for i in range(len(types) - 1):
        current, next_type = types[i], types[i+1]
        bigrams[current][next_type] += 1

    # Convert to probabilities
    transitions = {}
    for current, next_counts in bigrams.items():
        total = sum(next_counts.values())
        for next_type, count in next_counts.items():
            transitions[(current, next_type)] = count / total

    return transitions

def classify_episode_type(episode):
    """
    Infer episode type from content/tags

    Heuristics:
    - Contains "bug", "error", "debug" → "debugging"
    - Contains "meeting", "discussion" → "meeting"
    - Contains "test", "pytest" → "testing"
    - Contains "deploy", "ship" → "deployment"
    - Contains "breakthrough", "insight" → "breakthrough"
    - ...
    """
    content_lower = episode.content.lower()

    if any(word in content_lower for word in ['bug', 'error', 'debug']):
        return 'debugging'
    elif any(word in content_lower for word in ['meeting', 'discussion']):
        return 'meeting'
    elif any(word in content_lower for word in ['test', 'pytest', 'unittest']):
        return 'testing'
    elif any(word in content_lower for word in ['deploy', 'ship', 'release']):
        return 'deployment'
    elif any(word in content_lower for word in ['breakthrough', 'insight', 'eureka']):
        return 'breakthrough'
    elif any(word in content_lower for word in ['document', 'write', 'readme']):
        return 'documentation'
    else:
        return 'other'
```

**Output:** Probability distribution P(next | current)

**Example:**
```python
transitions = {
    ('debugging', 'testing'): 0.68,
    ('debugging', 'deployment'): 0.15,
    ('debugging', 'breakthrough'): 0.05,  # Rare!
    ('testing', 'deployment'): 0.82,
    ('meeting', 'debugging'): 0.45,
    ...
}
```

**Storage:**
```python
model_data = {
    'transitions': transitions,
    'n': 2,
    'episode_types': ['debugging', 'testing', 'deployment', 'meeting',
                      'documentation', 'breakthrough', 'other']
}
```

---

#### 1.4 Context-Content Model

**Input:** Context-content pairings from last 30 days

**Process:**
```python
def build_context_model(episodes):
    """
    Learn what content is typical for each context

    Returns:
        context_profiles: {
            'technical_meeting': [centroid_vec_1, centroid_vec_2, ...],
            'debugging_session': [centroid_vec_3, centroid_vec_4, ...],
            'documentation': [centroid_vec_5, ...],
            ...
        }
    """
    from sklearn.cluster import KMeans

    # Group episodes by context
    context_groups = defaultdict(list)
    for ep in episodes:
        context = ep.metadata.get('context', 'unknown')
        context_groups[context].append(ep.embedding)

    # For each context, find typical content centroids
    context_profiles = {}
    for context, embeddings in context_groups.items():
        if len(embeddings) >= 5:  # Need minimum data
            # Cluster into 3 typical content types per context
            kmeans = KMeans(n_clusters=min(3, len(embeddings)//2))
            kmeans.fit(embeddings)
            context_profiles[context] = kmeans.cluster_centers_.tolist()

    return context_profiles
```

**Output:** Expected content embeddings per context

**Example:**
```python
context_profiles = {
    'technical_meeting': [
        [0.12, -0.05, ...],  # Centroid 1: Architecture discussions
        [-0.08, 0.22, ...],  # Centroid 2: Bug triage
        [0.05, 0.15, ...]    # Centroid 3: Roadmap planning
    ],
    'debugging_session': [
        [0.33, -0.18, ...],  # Centroid 1: Stack traces
        [-0.12, 0.08, ...]   # Centroid 2: Log analysis
    ]
}
```

---

### Baseline Refresh Strategy

**When to refresh:**
- Weekly automatic refresh
- Manual trigger after major context shifts

**How to refresh:**
```python
def refresh_baseline_models():
    """
    Refresh all baseline models with latest 60-day window
    """
    # Fetch last 60 days
    episodes = fetch_episodes_last_n_days(60)

    # Rebuild all models
    semantic_centroids, _ = build_semantic_clusters(
        [ep.embedding for ep in episodes]
    )
    emotional_stats = build_emotional_baseline(episodes)
    sequence_transitions = build_sequence_model(episodes)
    context_profiles = build_context_model(episodes)

    # Update database
    update_baseline_model('semantic_clusters', semantic_centroids)
    update_baseline_model('emotional_baseline', emotional_stats)
    update_baseline_model('sequence_patterns', sequence_transitions)
    update_baseline_model('context_content', context_profiles)

    return {
        'refreshed_at': datetime.now(),
        'episodes_used': len(episodes),
        'date_range': [episodes[0].created_at, episodes[-1].created_at]
    }
```

---

## 🔢 STEP 2: Real-Time Novelty Scoring

### Called During Episode Creation

**Trigger:** Every new episode in `/memory/action` endpoint

**Input:**
- New episode embedding
- New episode emotional state
- New episode content
- Context metadata
- Recent episode history (last 6 hours)

### 2.1 Semantic Novelty Calculation

**Goal:** Measure distance from existing knowledge clusters

**Algorithm:**

```python
def calculate_semantic_novelty(episode_embedding, cluster_centroids):
    """
    Measure semantic distance from established clusters

    Research basis: Yassa & Stark (2011) - Pattern separation
    Optimal novelty: 0.5-0.7 distance (novel but connected)

    Args:
        episode_embedding: 1536-dim vector for new episode
        cluster_centroids: List of 10 cluster centers

    Returns:
        semantic_novelty: 0.0 (very familiar) to 1.0 (very novel)
    """
    from scipy.spatial.distance import cosine

    # Calculate distance to each cluster
    distances = []
    for centroid in cluster_centroids:
        dist = cosine(episode_embedding, centroid)
        distances.append(dist)

    # Use minimum distance (nearest cluster)
    min_distance = min(distances)

    # Normalize to 0-1 scale
    # Distance 0.0 = perfect match (novelty 0.0)
    # Distance 0.5+ = very far (novelty 1.0)
    # Based on Yassa & Stark: optimal novelty ~0.6
    semantic_novelty = min(min_distance / 0.5, 1.0)

    return semantic_novelty
```

**Example:**

```python
# Episode: "Quantum entanglement analogy for distributed state"
embedding = [...1536 dims...]

# Clusters: debugging, meetings, docs, learning, architecture, ...
distances = [0.82, 0.79, 0.75, 0.45, 0.68, ...]
                                   ↑ Nearest: "learning" cluster

min_distance = 0.45
semantic_novelty = min(0.45 / 0.5, 1.0) = 0.90

# HIGH novelty - far even from nearest cluster!
```

---

### 2.2 Emotional Surprise Calculation

**Goal:** Detect unexpected emotional state changes

**Algorithm:**

```python
def calculate_emotional_surprise(current_emotional_state, recent_history, baseline_stats):
    """
    Detect sudden emotional shifts (prediction error)

    Research basis: Hyman et al. (2006) - Emotional transitions
    Transition >2 std = dopamine surge

    Args:
        current_emotional_state: somatic_7d dict
        recent_history: Last 6 hours of episodes
        baseline_stats: Learned mean/std from baseline

    Returns:
        emotional_surprise: 0.0 (expected) to 1.0 (very surprising)
    """
    import numpy as np

    current_valence = current_emotional_state['valence']

    # Get recent valence trajectory
    if len(recent_history) >= 3:
        recent_valences = [ep.somatic_7d['valence'] for ep in recent_history[-6:]]
        expected_valence = np.mean(recent_valences)
        local_std = np.std(recent_valences) + 0.01  # Avoid div by zero
    else:
        # Fallback to baseline
        expected_valence = baseline_stats['valence_mean']
        local_std = baseline_stats['valence_std']

    # Calculate deviation (prediction error)
    deviation = abs(current_valence - expected_valence)
    z_score = deviation / local_std

    # Normalize: 2+ std deviations = maximal surprise
    # Based on Hyman: transitions >2 std trigger dopamine
    emotional_surprise = min(z_score / 2.0, 1.0)

    return emotional_surprise
```

**Example:**

```python
# Recent history: 6 episodes, valence = [-0.6, -0.5, -0.7, -0.6, -0.5, -0.6]
recent_mean = -0.58
recent_std = 0.07

# Current episode: Breakthrough moment!
current_valence = +0.9

deviation = abs(0.9 - (-0.58)) = 1.48
z_score = 1.48 / 0.07 = 21.1 (!!!)

emotional_surprise = min(21.1 / 2.0, 1.0) = 1.0

# MAXIMUM surprise - huge emotional shift!
```

---

### 2.3 Pattern Violation Calculation

**Goal:** Detect deviations from learned sequences

**Algorithm:**

```python
def calculate_pattern_violation(episode_type, previous_types, sequence_model):
    """
    Detect when episode type violates expected sequence

    Research basis: Bubic et al. (2010) - Prediction violation
    Unexpected continuation = dopamine surge

    Args:
        episode_type: Current episode type (inferred)
        previous_types: Last 3 episode types
        sequence_model: Learned bigram probabilities

    Returns:
        pattern_violation: 0.0 (expected) to 1.0 (very unexpected)
    """
    if len(previous_types) == 0:
        return 0.0  # No history to violate

    # Get expected next type distribution
    previous_type = previous_types[-1]

    # Lookup probability P(current | previous)
    transition_key = (previous_type, episode_type)
    probability = sequence_model.get(transition_key, 0.01)  # Default: rare

    # Low probability = high violation
    # P=1.0 → violation=0.0 (fully expected)
    # P=0.0 → violation=1.0 (never seen before)
    pattern_violation = 1.0 - probability

    return pattern_violation
```

**Example:**

```python
# History: ['debugging', 'debugging', 'debugging']
previous_type = 'debugging'

# Current episode type: 'breakthrough' (inferred from content)
episode_type = 'breakthrough'

# Lookup probability
sequence_model[('debugging', 'testing')] = 0.68      # Common
sequence_model[('debugging', 'breakthrough')] = 0.05 # Rare!

probability = 0.05
pattern_violation = 1.0 - 0.05 = 0.95

# VERY HIGH violation - breakthroughs rarely follow debugging!
```

---

### 2.4 Contextual Mismatch Calculation

**Goal:** Detect unexpected content for given context

**Algorithm:**

```python
def calculate_contextual_mismatch(episode_embedding, episode_context, context_model):
    """
    Detect when content doesn't match expected context

    Research basis: Ranganath & Ritchey (2012) - Schema mismatch
    Office + elephant = high mismatch = strong encoding

    Args:
        episode_embedding: Content vector
        episode_context: Context label (e.g., 'technical_meeting')
        context_model: Expected content centroids per context

    Returns:
        contextual_mismatch: 0.0 (fits context) to 1.0 (doesn't fit)
    """
    from scipy.spatial.distance import cosine

    # Get expected content centroids for this context
    expected_centroids = context_model.get(episode_context, [])

    if len(expected_centroids) == 0:
        return 0.0  # Unknown context, can't judge mismatch

    # Calculate similarity to each expected centroid
    similarities = []
    for centroid in expected_centroids:
        similarity = 1.0 - cosine(episode_embedding, centroid)
        similarities.append(similarity)

    # Use maximum similarity (best match to expected content)
    max_similarity = max(similarities)

    # Low similarity = high mismatch
    contextual_mismatch = 1.0 - max_similarity

    return contextual_mismatch
```

**Example:**

```python
# Context: 'technical_meeting'
# Expected: [architecture_centroid, bug_triage_centroid, roadmap_centroid]

# Episode content: "Deep philosophical insight about consciousness"
embedding = [...]

similarities = [
    1.0 - cosine(embedding, architecture_centroid) = 0.35,
    1.0 - cosine(embedding, bug_triage_centroid) = 0.28,
    1.0 - cosine(embedding, roadmap_centroid) = 0.42
]

max_similarity = 0.42  # Best match (still low!)
contextual_mismatch = 1.0 - 0.42 = 0.58

# MODERATE-HIGH mismatch - philosophy in tech meeting is unusual
```

---

### 2.5 Composite Novelty Score

**Weighted combination of 4 components:**

```python
def calculate_novelty_score(episode, recent_history, baseline_models):
    """
    Master function: Calculate composite novelty score

    Weights based on neuroscience research:
    - Semantic: 30% (Yassa & Stark - pattern separation)
    - Emotional: 25% (Hyman - emotional transitions)
    - Pattern: 25% (Bubic - sequence prediction)
    - Context: 20% (Ranganath - schema mismatch)

    Args:
        episode: New episode to score
        recent_history: Last 6 hours of episodes
        baseline_models: All baseline models

    Returns:
        novelty_score: 0.0 to 1.0
        breakdown: Dict with individual components
    """
    # Extract baseline models
    semantic_clusters = baseline_models['semantic_clusters']['centroids']
    emotional_baseline = baseline_models['emotional_baseline']
    sequence_model = baseline_models['sequence_patterns']['transitions']
    context_model = baseline_models['context_content']['profiles']

    # Calculate each component
    semantic_novelty = calculate_semantic_novelty(
        episode.embedding,
        semantic_clusters
    )

    emotional_surprise = calculate_emotional_surprise(
        episode.somatic_7d,
        recent_history,
        emotional_baseline
    )

    # Infer episode type
    episode_type = classify_episode_type(episode)
    previous_types = [classify_episode_type(ep) for ep in recent_history[-3:]]

    pattern_violation = calculate_pattern_violation(
        episode_type,
        previous_types,
        sequence_model
    )

    contextual_mismatch = calculate_contextual_mismatch(
        episode.embedding,
        episode.metadata.get('context', 'unknown'),
        context_model
    )

    # Weighted composite
    novelty_score = (
        semantic_novelty * 0.30 +
        emotional_surprise * 0.25 +
        pattern_violation * 0.25 +
        contextual_mismatch * 0.20
    )

    # Breakdown for debugging/analytics
    breakdown = {
        'semantic_novelty': round(semantic_novelty, 3),
        'emotional_surprise': round(emotional_surprise, 3),
        'pattern_violation': round(pattern_violation, 3),
        'contextual_mismatch': round(contextual_mismatch, 3),
        'total_novelty': round(novelty_score, 3)
    }

    return novelty_score, breakdown
```

**Complete Example:**

```python
# Episode: "Quantum entanglement analogy for distributed state sync"
# Context: "debugging_session"
# Recent history: 6 debugging episodes, frustrated valence

components = {
    'semantic_novelty': 0.90,      # Very far from all clusters
    'emotional_surprise': 0.85,    # Valence jump from -0.6 to +0.9
    'pattern_violation': 0.95,     # Breakthrough after debugging (rare)
    'contextual_mismatch': 0.78    # Quantum physics in debugging context
}

novelty_score = (
    0.90 * 0.30 +  # 0.270
    0.85 * 0.25 +  # 0.213
    0.95 * 0.25 +  # 0.238
    0.78 * 0.20    # 0.156
) = 0.877

# VERY HIGH NOVELTY - all dimensions agree!
```

---

## 💾 STEP 3: Storage Integration

### Metadata Schema Update

**Add to episode metadata:**

```json
{
  "salience_score": 0.88,           // LAB_001
  "novelty_score": 0.877,           // LAB_004 (NEW)
  "novelty_breakdown": {            // LAB_004 (NEW)
    "semantic_novelty": 0.90,
    "emotional_surprise": 0.85,
    "pattern_violation": 0.95,
    "contextual_mismatch": 0.78
  },
  "consolidated_salience_score": null,  // LAB_003 (set during sleep)
  "breakthrough_score": 0.0,             // LAB_003 (set during sleep)
  ...
}
```

### API Endpoint Modification

```python
@app.post("/memory/action")
async def record_action(request: MemoryActionRequest):
    """
    Record episodic memory with LAB_001 + LAB_004
    """
    # Existing: Generate embedding
    embedding = await get_embedding(request.content)

    # Existing: LAB_001 salience
    salience_score = calculate_emotional_salience(
        request.emotional_8d,
        request.somatic_7d
    )

    # NEW: LAB_004 novelty
    recent_history = fetch_recent_episodes(hours=6)
    baseline_models = load_baseline_models()

    novelty_score, novelty_breakdown = calculate_novelty_score(
        episode=EpisodeCandidate(
            content=request.content,
            embedding=embedding,
            somatic_7d=request.somatic_7d,
            metadata={'context': request.context_state}
        ),
        recent_history=recent_history,
        baseline_models=baseline_models
    )

    # Store both scores
    metadata = {
        "salience_score": salience_score,
        "novelty_score": novelty_score,
        "novelty_breakdown": novelty_breakdown,
        ...
    }

    # Insert to database
    ...
```

---

## 🔗 STEP 4: LAB_003 Consolidation Integration

### Modified Breakthrough Detection

**Original LAB_003:**

```python
breakthrough_score = (
    salience_score * 0.40 +
    sum(emotional_8d.values()) * 0.25 +
    abs(somatic_7d['valence']) * 0.15 +
    importance_score * 0.20
)
```

**Enhanced with LAB_004:**

```python
breakthrough_score = (
    salience_score * 0.35 +              # Slightly reduced
    sum(emotional_8d.values()) * 0.20 +  # Slightly reduced
    abs(somatic_7d['valence']) * 0.15 +  # Same
    importance_score * 0.15 +            # Slightly reduced
    novelty_score * 0.15                 # NEW: Novelty bonus
)
```

### Consolidation Boost with Novelty

**Code modification in `consolidation_engine.py`:**

```python
def consolidate_chain(self, chain: List[Episode]):
    """
    Enhanced: Consider novelty when calculating boost
    """
    breakthrough_episode = chain[-1]

    # Calculate base consolidated salience (existing)
    for i, episode in enumerate(chain):
        position_weight = (len(chain) - i) / len(chain)
        temporal_decay = 1.0 / (1.0 + (chain[-1].created_at - episode.created_at).total_seconds() / 3600)

        base_boost = breakthrough_episode.breakthrough_score * position_weight * temporal_decay * 0.25

        # NEW: Add novelty bonus
        novelty_bonus = 0.0
        if episode.novelty_score > 0.7:
            novelty_bonus = (episode.novelty_score - 0.7) * 0.5  # Up to +0.15

        total_boost = base_boost + novelty_bonus
        total_boost = min(total_boost, 0.25)  # Cap at +0.25

        episode.consolidated_salience_score = min(
            episode.salience_score + total_boost,
            1.0
        )
```

**Effect:**

```
Episode with high salience (0.88) + high novelty (0.87):
  Base boost: 0.15
  Novelty bonus: (0.87 - 0.7) * 0.5 = 0.085
  Total boost: 0.15 + 0.085 = 0.235
  Final: 0.88 + 0.235 = 1.0 (capped)

Episode with high salience (0.88) + low novelty (0.25):
  Base boost: 0.15
  Novelty bonus: 0.0 (below threshold)
  Total boost: 0.15
  Final: 0.88 + 0.15 = 1.0

# Novel breakthroughs >> Expected breakthroughs
```

---

## 📊 STEP 5: Analytics Endpoint

### GET /memory/surprises

**Purpose:** "Show me today's surprising moments"

**Implementation:**

```python
@app.get("/memory/surprises")
async def get_surprises(
    date: str = "today",
    min_novelty: float = 0.7,
    limit: int = 10
):
    """
    Retrieve most surprising episodes from a given date

    Args:
        date: 'today', 'yesterday', or 'YYYY-MM-DD'
        min_novelty: Minimum novelty threshold (default 0.7)
        limit: Max episodes to return (default 10)

    Returns:
        Surprise analytics with breakdown
    """
    # Parse date
    if date == "today":
        target_date = datetime.now()
    elif date == "yesterday":
        target_date = datetime.now() - timedelta(days=1)
    else:
        target_date = datetime.strptime(date, "%Y-%m-%d")

    # Fetch episodes
    episodes = fetch_episodes_from_date(target_date)

    # Filter high-novelty episodes
    surprises = [
        ep for ep in episodes
        if ep.metadata.get('novelty_score', 0) >= min_novelty
    ]

    # Sort by novelty (descending)
    surprises.sort(
        key=lambda x: x.metadata.get('novelty_score', 0),
        reverse=True
    )

    # Build response
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "total_episodes": len(episodes),
        "surprising_episodes": len(surprises),
        "surprise_rate": round(len(surprises) / len(episodes), 3) if episodes else 0,
        "top_surprises": [
            {
                "time": ep.created_at.strftime("%H:%M"),
                "content": ep.content[:100],
                "novelty_score": ep.metadata.get('novelty_score'),
                "breakdown": ep.metadata.get('novelty_breakdown'),
                "primary_source": get_primary_surprise_source(ep.metadata.get('novelty_breakdown'))
            }
            for ep in surprises[:limit]
        ],
        "surprise_timeline": build_surprise_timeline(surprises),
        "novelty_distribution": {
            "semantic": np.mean([ep.metadata.get('novelty_breakdown', {}).get('semantic_novelty', 0) for ep in surprises]),
            "emotional": np.mean([ep.metadata.get('novelty_breakdown', {}).get('emotional_surprise', 0) for ep in surprises]),
            "pattern": np.mean([ep.metadata.get('novelty_breakdown', {}).get('pattern_violation', 0) for ep in surprises]),
            "contextual": np.mean([ep.metadata.get('novelty_breakdown', {}).get('contextual_mismatch', 0) for ep in surprises])
        }
    }

def get_primary_surprise_source(breakdown):
    """
    Identify which component contributed most to surprise
    """
    if not breakdown:
        return "unknown"

    components = {
        'semantic': breakdown.get('semantic_novelty', 0),
        'emotional': breakdown.get('emotional_surprise', 0),
        'pattern': breakdown.get('pattern_violation', 0),
        'contextual': breakdown.get('contextual_mismatch', 0)
    }

    return max(components, key=components.get)
```

**Example Response:**

```json
{
  "date": "2025-10-27",
  "total_episodes": 24,
  "surprising_episodes": 3,
  "surprise_rate": 0.125,
  "top_surprises": [
    {
      "time": "16:45",
      "content": "Quantum entanglement analogy for distributed state sync breakthrough",
      "novelty_score": 0.877,
      "breakdown": {
        "semantic_novelty": 0.90,
        "emotional_surprise": 0.85,
        "pattern_violation": 0.95,
        "contextual_mismatch": 0.78
      },
      "primary_source": "pattern"
    },
    {
      "time": "11:30",
      "content": "Bizarre async race condition in token refresh logic",
      "novelty_score": 0.756,
      "breakdown": {
        "semantic_novelty": 0.68,
        "emotional_surprise": 0.82,
        "pattern_violation": 0.72,
        "contextual_mismatch": 0.55
      },
      "primary_source": "emotional"
    }
  ],
  "surprise_timeline": [
    {"hour": 11, "novelty_avg": 0.756},
    {"hour": 16, "novelty_avg": 0.877}
  ],
  "novelty_distribution": {
    "semantic": 0.79,
    "emotional": 0.835,
    "pattern": 0.835,
    "contextual": 0.665
  }
}
```

---

## 🧪 Testing Strategy

### Unit Tests

**Test each component independently:**

```python
# tests/test_novelty_detector.py

def test_semantic_novelty():
    """Test semantic novelty calculation"""
    # Mock cluster centroids
    centroids = [np.random.rand(1536) for _ in range(10)]

    # Very similar embedding (low novelty)
    similar_embedding = centroids[0] + np.random.rand(1536) * 0.1
    novelty = calculate_semantic_novelty(similar_embedding, centroids)
    assert novelty < 0.3

    # Very different embedding (high novelty)
    different_embedding = np.random.rand(1536)
    novelty = calculate_semantic_novelty(different_embedding, centroids)
    assert novelty > 0.7

def test_emotional_surprise():
    """Test emotional surprise detection"""
    baseline = {'valence_mean': 0.0, 'valence_std': 0.3}

    # Small change (no surprise)
    current = {'valence': 0.1}
    recent = [{'somatic_7d': {'valence': 0.0}} for _ in range(5)]
    surprise = calculate_emotional_surprise(current, recent, baseline)
    assert surprise < 0.3

    # Large change (high surprise)
    current = {'valence': 0.9}
    surprise = calculate_emotional_surprise(current, recent, baseline)
    assert surprise > 0.7

def test_pattern_violation():
    """Test sequence pattern violation"""
    sequence_model = {
        ('debugging', 'testing'): 0.75,
        ('debugging', 'breakthrough'): 0.05
    }

    # Expected transition (low violation)
    violation = calculate_pattern_violation(
        'testing', ['debugging'], sequence_model
    )
    assert violation < 0.3

    # Unexpected transition (high violation)
    violation = calculate_pattern_violation(
        'breakthrough', ['debugging'], sequence_model
    )
    assert violation > 0.9
```

### Integration Tests

**Test with real historical data:**

```python
def test_novelty_on_historical_episodes():
    """
    Validate novelty scores on known surprising vs routine episodes
    """
    # Load historical episodes
    episodes = load_test_episodes()

    # Build baseline from first 80%
    train_episodes = episodes[:int(len(episodes) * 0.8)]
    baseline_models = build_all_baseline_models(train_episodes)

    # Test on remaining 20%
    test_episodes = episodes[int(len(episodes) * 0.8):]

    # Manually labeled surprising episodes
    surprising_ids = ['ep_123', 'ep_456', 'ep_789']

    for ep in test_episodes:
        novelty, _ = calculate_novelty_score(ep, train_episodes[-10:], baseline_models)

        if ep.id in surprising_ids:
            assert novelty > 0.7, f"Missed surprise: {ep.id}"
        else:
            # Most routine episodes should be low novelty
            pass  # Can't assert all are low (some legitimate surprises)
```

---

## 📈 Performance Considerations

### Computational Overhead

**Per episode (real-time):**
- Semantic novelty: 10 cosine distances (~1ms)
- Emotional surprise: Mean/std calculation (~0.5ms)
- Pattern violation: Dict lookup (~0.1ms)
- Contextual mismatch: 3 cosine distances (~0.3ms)

**Total overhead: ~2ms per episode** ✅ Acceptable

### Optimization Strategies

**If overhead becomes issue:**

1. **Cache cluster centroids** in memory (don't reload from DB)
2. **Approximate nearest neighbors** (FAISS) for semantic novelty
3. **Batch baseline updates** (weekly, not per-episode)
4. **Pre-compute episode types** (cache classification results)

---

## 🎯 Success Metrics

**Quantitative:**
- [ ] Baseline models built from 30+ days of data
- [ ] Novelty scoring adds <5ms overhead per episode
- [ ] High-novelty episodes (>0.7) receive 15-25% consolidation boost
- [ ] Surprise detection precision >75% (manual validation)

**Qualitative:**
- [ ] Unexpected breakthroughs flagged automatically
- [ ] Routine work correctly classified as low-novelty
- [ ] Curiosity report highlights genuinely surprising moments
- [ ] User feedback: "Yes, that WAS surprising!"

---

## 🔄 Next Implementation Steps

1. **Implement `NoveltyDetector` class** (novelty_detector.py)
2. **Add baseline model building** (build_baselines.py)
3. **Integrate into `/memory/action` endpoint**
4. **Enhance LAB_003 consolidation** (add novelty bonus)
5. **Create `/memory/surprises` analytics endpoint**
6. **Test with historical episodes**
7. **Document in RESULTS.md**

---

**Algorithm Design Complete ✅**

**Ready for implementation phase.**

*"Surprise is the brain's learning signal. Novelty is the brain's exploration bonus."*
