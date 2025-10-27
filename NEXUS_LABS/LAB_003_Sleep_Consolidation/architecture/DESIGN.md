# 🏗️ LAB_003 Architecture: Sleep Consolidation Algorithm

**Design Date:** October 27, 2025
**Status:** Design Complete, Ready for Implementation (Future Session)

---

## 🎯 Design Overview

Offline batch processing that mimics biological sleep consolidation: selectively replay important memories, strengthen breakthrough chains retroactively, and prevent catastrophic forgetting through interleaved processing.

---

## 📊 Algorithm Specification

### High-Level Pipeline

```python
def consolidate_daily_memories(date):
    """
    Nightly consolidation process (runs at 3:00 AM)

    Mimics biological sleep: selective replay, backward tracing,
    interleaved processing to prevent forgetting.
    """
    # Step 1: Fetch yesterday's episodes
    episodes = fetch_episodes_from_date(date)

    # Step 2: Identify breakthroughs
    breakthroughs = identify_breakthroughs(episodes)

    # Step 3: Trace backward chains
    chains = trace_breakthrough_chains(breakthroughs, episodes)

    # Step 4: Calculate consolidated salience
    for chain in chains:
        consolidate_chain(chain)

    # Step 5: Interleaved replay (prevent catastrophic forgetting)
    old_samples = sample_old_important_memories()
    interleaved_consolidate(chains, old_samples)

    # Step 6: Create memory traces (graph links)
    create_memory_traces(chains)

    # Step 7: Update database
    commit_consolidated_scores()

    # Step 8: Generate consolidation report
    return generate_report(breakthroughs, chains)
```

---

## 🔬 Component Breakdown

### 1. Breakthrough Detection

**Objective:** Identify top 20% most significant episodes from the day

**Algorithm:**
```python
def identify_breakthroughs(episodes, threshold_percentile=80):
    """
    Detect breakthrough episodes using multiple signals

    Based on O'Neill 2010: Reward-related memories replayed 5-10x more

    Args:
        episodes: List of episodes from past 24 hours
        threshold_percentile: Top X% considered breakthroughs

    Returns:
        List of breakthrough episodes sorted by importance
    """
    # Calculate composite breakthrough score
    for episode in episodes:
        score = 0.0

        # Signal 1: Emotional salience (LAB_001)
        score += episode.salience_score * 0.4  # 40% weight

        # Signal 2: Emotional dimensions (8D)
        breakthrough_emotions = ['joy', 'trust', 'anticipation', 'surprise']
        emotion_sum = sum(episode.emotional_8d[e] for e in breakthrough_emotions)
        score += (emotion_sum / 4) * 0.25  # 25% weight

        # Signal 3: Somatic valence (positive outcomes)
        score += max(0, episode.somatic_7d['valence']) * 0.15  # 15% weight

        # Signal 4: Importance score (pre-existing)
        score += episode.importance_score * 0.20  # 20% weight

        episode.breakthrough_score = score

    # Top 20% threshold
    threshold = np.percentile([e.breakthrough_score for e in episodes],
                               threshold_percentile)

    breakthroughs = [e for e in episodes if e.breakthrough_score >= threshold]
    breakthroughs.sort(key=lambda x: x.breakthrough_score, reverse=True)

    return breakthroughs
```

**Example Output:**
```
Date: Oct 27, 2025
Total episodes: 52
Breakthrough threshold (80th percentile): 0.72
Breakthroughs identified: 10

Top breakthrough:
  episode_id: 78d3d12c...
  content: "LAB_002 tests show 1.27x improvement!"
  breakthrough_score: 0.92
  salience: 0.92, joy: 0.85, valence: 0.80
```

---

### 2. Backward Chain Tracing

**Objective:** Find precursor episodes that led to breakthroughs

**Algorithm:**
```python
def trace_breakthrough_chains(breakthroughs, all_episodes):
    """
    Trace backward from breakthroughs to find contributing episodes

    Based on Dickinson 1996: Retrospective revaluation

    Args:
        breakthroughs: List of breakthrough episodes
        all_episodes: All episodes from the day

    Returns:
        List of chains (sequences of related episodes)
    """
    chains = []

    for breakthrough in breakthroughs:
        chain = [breakthrough]

        # Trace backward in time
        current_time = breakthrough.created_at

        # Look back up to 12 hours
        window_start = current_time - timedelta(hours=12)

        # Find related episodes
        candidates = [e for e in all_episodes
                     if window_start <= e.created_at < current_time]

        for candidate in reversed(candidates):  # Most recent first
            # Relatedness criteria
            is_related = (
                # Same session
                candidate.session_id == breakthrough.session_id
                or
                # Semantic similarity
                cosine_similarity(candidate.embedding,
                                 breakthrough.embedding) > 0.65
                or
                # Shared tags
                len(set(candidate.tags) & set(breakthrough.tags)) >= 2
                or
                # Temporal proximity + topic continuity
                (current_time - candidate.created_at).total_seconds() < 3600
                and topic_similarity(candidate, breakthrough) > 0.60
            )

            if is_related:
                chain.insert(0, candidate)  # Add to beginning
                current_time = candidate.created_at  # Update search time

        # Only keep chains with 2+ episodes
        if len(chain) >= 2:
            chains.append(chain)

    return chains
```

**Example Output:**
```
Chain 1: LAB_002 Development (6 episodes)
  [09:00] "Starting LAB_002 research"          → precursor
  [10:30] "Found McGaugh 2002 paper"           → precursor
  [12:00] "Designed decay formula"             → precursor
  [14:00] "Implemented DecayModulator"         → precursor
  [16:00] "Tests show 1.27x improvement!"      → breakthrough
  [18:00] "Documented and pushed to GitHub"    → closure

  Relatedness: Same session_id, temporal continuity, shared tags
```

---

### 3. Consolidated Salience Calculation

**Objective:** Retroactively boost precursors based on breakthrough importance

**Algorithm:**
```python
def consolidate_chain(chain):
    """
    Calculate consolidated_salience_score for each episode in chain

    Based on:
    - O'Neill 2010: 5-10x replay for rewarding experiences
    - Dickinson 1996: Retrospective revaluation

    Args:
        chain: List of episodes leading to breakthrough
    """
    breakthrough = chain[-1]  # Last episode (outcome)
    breakthrough_score = breakthrough.breakthrough_score

    for i, episode in enumerate(chain):
        # Original salience (LAB_001)
        original_salience = episode.salience_score

        # Position in chain (earlier = more boost)
        position_weight = 1.0 - (i / len(chain))  # 1.0 at start, 0.0 at end

        # Distance from breakthrough (temporal decay)
        time_diff_hours = (breakthrough.created_at - episode.created_at).total_seconds() / 3600
        temporal_decay = np.exp(-time_diff_hours / 6.0)  # Half-life 6 hours

        # Consolidation boost formula
        boost = (
            breakthrough_score *      # How important was outcome?
            position_weight *         # Earlier episodes get more boost
            temporal_decay *          # Closer in time = more boost
            0.25                      # Scale factor (max +0.25)
        )

        # Cap boost at +0.20
        boost = min(boost, 0.20)

        # Calculate consolidated salience
        consolidated_salience = min(original_salience + boost, 1.0)

        # Store both scores
        episode.salience_score = original_salience  # Preserve original
        episode.consolidated_salience_score = consolidated_salience

        # Update importance_score
        episode.importance_score *= (1.0 + boost)
```

**Example Calculation:**
```python
Chain: LAB_002 Development
Breakthrough score: 0.92

Episode 1 (09:00): "Starting LAB_002 research"
  original_salience: 0.60
  position_weight: 1.0 (first in chain)
  temporal_decay: 0.37 (7 hours before breakthrough)
  boost: 0.92 * 1.0 * 0.37 * 0.25 = 0.085
  consolidated_salience: 0.60 + 0.085 = 0.685 (+14%)

Episode 3 (12:00): "Designed decay formula"
  original_salience: 0.75
  position_weight: 0.67 (middle of chain)
  temporal_decay: 0.61 (4 hours before)
  boost: 0.92 * 0.67 * 0.61 * 0.25 = 0.094
  consolidated_salience: 0.75 + 0.094 = 0.844 (+12.5%)

Episode 5 (16:00): "Tests show 1.27x improvement!" (breakthrough)
  original_salience: 0.92
  position_weight: 0.17 (near end)
  temporal_decay: 1.0 (current)
  boost: 0.92 * 0.17 * 1.0 * 0.25 = 0.039
  consolidated_salience: 0.92 + 0.039 = 0.959 (+4%)
```

**Result:** Early "routine" episodes now recognized as important precursors!

---

### 4. Interleaved Replay (Prevent Catastrophic Forgetting)

**Objective:** Mix recent consolidation with samples of older memories

**Algorithm:**
```python
def interleaved_consolidate(new_chains, ratio=0.3):
    """
    Interleave recent memories with samples of older important memories

    Based on bioRxiv 2025: Prevents catastrophic forgetting

    Args:
        new_chains: Today's breakthrough chains
        ratio: Proportion of old memories (0.3 = 30% old, 70% new)
    """
    # Sample older important memories (30% of batch)
    old_sample_size = int(len(new_chains) * ratio / (1 - ratio))

    # Criteria for sampling old memories:
    # 1. High consolidated_salience_score (>0.70)
    # 2. Age 7-90 days (not too recent, not too old)
    # 3. Representative of different topics/sessions

    old_memories = fetch_old_memories(
        min_consolidated_salience=0.70,
        min_age_days=7,
        max_age_days=90,
        sample_size=old_sample_size,
        diversity=True  # Ensure topic diversity
    )

    # Interleave: Random shuffle of new and old
    all_memories = list(new_chains) + list(old_memories)
    random.shuffle(all_memories)

    # Process in interleaved order
    for item in all_memories:
        if isinstance(item, list):  # New chain
            consolidate_chain(item)
        else:  # Old memory
            refresh_consolidation(item)  # Minor boost to maintain
```

**Example:**
```
Consolidation batch (13 items):
  [NEW] Chain 1: LAB_002 development (6 episodes)
  [OLD] Episode from 15 days ago: LAB_001 breakthrough
  [NEW] Chain 2: Bug fix success (3 episodes)
  [OLD] Episode from 30 days ago: FASE_4 cutover
  [NEW] Chain 3: Research discovery (4 episodes)
  [OLD] Episode from 8 days ago: Neural Mesh setup
  [OLD] Episode from 45 days ago: FASE_3 milestone
  ...

  Ratio: 70% new, 30% old (prevents forgetting older important memories)
```

---

### 5. Memory Traces (Graph Structure)

**Objective:** Create explicit links between related episodes

**Data Structure:**
```python
@dataclass
class MemoryTrace:
    """
    Directed edge in memory graph

    Represents "Episode A contributed to Episode B"
    """
    source_episode_id: str      # Precursor
    target_episode_id: str      # Outcome
    trace_type: str             # 'precursor', 'closure', 'related'
    strength: float             # 0.0 to 1.0 (how strong is connection)
    created_at: datetime        # When trace was created
    narrative_id: str           # Group ID for entire chain
```

**Algorithm:**
```python
def create_memory_traces(chains):
    """
    Create directed graph edges between chain episodes

    Enables narrative retrieval: Find any episode → Get full chain
    """
    traces = []

    for chain_id, chain in enumerate(chains):
        narrative_id = f"chain_{datetime.now().strftime('%Y%m%d')}_{chain_id}"

        for i in range(len(chain) - 1):
            source = chain[i]
            target = chain[i + 1]

            # Calculate trace strength
            time_gap_hours = (target.created_at - source.created_at).total_seconds() / 3600
            strength = 1.0 / (1.0 + time_gap_hours / 3.0)  # Decay with time gap

            # Determine trace type
            if i == 0:
                trace_type = 'initiator'
            elif i == len(chain) - 2:
                trace_type = 'conclusion'
            else:
                trace_type = 'progression'

            trace = MemoryTrace(
                source_episode_id=source.episode_id,
                target_episode_id=target.episode_id,
                trace_type=trace_type,
                strength=strength,
                created_at=datetime.now(),
                narrative_id=narrative_id
            )

            traces.append(trace)

    # Store in database
    store_memory_traces(traces)

    return traces
```

**Example Graph:**
```
Narrative: lab_002_20251027_0

09:00 [initiator]
  ↓ (strength: 0.91, gap: 1.5h)
10:30 [progression]
  ↓ (strength: 0.88, gap: 1.5h)
12:00 [progression]
  ↓ (strength: 0.83, gap: 2h)
14:00 [progression]
  ↓ (strength: 0.78, gap: 2h)
16:00 [progression]
  ↓ (strength: 0.86, gap: 2h)
18:00 [conclusion]

Retrieval benefit:
- Query: "LAB_002 tests"
- Matches: Episode 16:00
- Navigate graph: Return entire chain 09:00 → 18:00
- Result: Full narrative context, not just single episode
```

---

### 6. Database Schema Updates

**New Columns:**
```sql
ALTER TABLE zep_episodic_memory ADD COLUMN
    consolidated_salience_score FLOAT DEFAULT NULL;

ALTER TABLE zep_episodic_memory ADD COLUMN
    breakthrough_score FLOAT DEFAULT NULL;

ALTER TABLE zep_episodic_memory ADD COLUMN
    last_consolidated_at TIMESTAMP DEFAULT NULL;

CREATE TABLE memory_traces (
    trace_id UUID PRIMARY KEY,
    source_episode_id UUID REFERENCES zep_episodic_memory(uuid),
    target_episode_id UUID REFERENCES zep_episodic_memory(uuid),
    trace_type VARCHAR(50),
    strength FLOAT,
    narrative_id VARCHAR(100),
    created_at TIMESTAMP
);

CREATE INDEX idx_memory_traces_source ON memory_traces(source_episode_id);
CREATE INDEX idx_memory_traces_target ON memory_traces(target_episode_id);
CREATE INDEX idx_memory_traces_narrative ON memory_traces(narrative_id);
```

---

## ⚙️ Integration with LAB_001/002

### Data Flow

```
Episode Creation
    ↓
LAB_001: salience_score calculated (0.0-1.0)
    ↓
[Episode stored in PostgreSQL]
    ↓
LAB_003: Nightly consolidation (3:00 AM)
    ↓
    1. Detect breakthroughs (top 20%)
    2. Trace backward chains
    3. Calculate consolidated_salience_score
    4. Interleaved replay with old memories
    5. Create memory_traces
    ↓
Next Day Retrieval (LAB_001 + LAB_002 + LAB_003)
    ↓
    salience = max(salience_score, consolidated_salience_score)
    ↓
LAB_002: Decay modulation uses max salience
    ↓
    Result: Precursors protected retroactively!
```

### Scoring Integration

**Before LAB_003:**
```python
# LAB_002 uses only original salience
decay_result = modulator.calculate_decay_modulated_score(
    similarity=0.65,
    created_at=episode.created_at,
    salience_score=episode.salience_score  # Only LAB_001
)
```

**After LAB_003:**
```python
# Use consolidated salience if available
effective_salience = max(
    episode.salience_score,                    # LAB_001 (immediate emotion)
    episode.consolidated_salience_score or 0   # LAB_003 (retrospective importance)
)

decay_result = modulator.calculate_decay_modulated_score(
    similarity=0.65,
    created_at=episode.created_at,
    salience_score=effective_salience  # Best of both!
)
```

**Result:** Early episodes in breakthrough chains get LAB_002 decay protection even if initial salience was low!

---

## 🕐 Scheduling

### Cron Job Setup

**Schedule:** 3:00 AM daily (user sleeping, low API traffic)

**Cron Expression:**
```bash
0 3 * * * /usr/bin/python3 /app/consolidation/nightly_consolidation.py
```

**Script:**
```python
#!/usr/bin/env python3
"""
nightly_consolidation.py

Runs LAB_003 sleep consolidation process
"""

import sys
from datetime import datetime, timedelta
from consolidation_engine import ConsolidationEngine

def main():
    """Execute nightly consolidation"""
    yesterday = datetime.now() - timedelta(days=1)

    print(f"[{datetime.now()}] Starting consolidation for {yesterday.date()}")

    engine = ConsolidationEngine(
        db_host='nexus_postgresql',
        db_port=5432,
        db_name='nexus_memory'
    )

    try:
        report = engine.consolidate_daily_memories(yesterday)

        print(f"[{datetime.now()}] Consolidation complete")
        print(f"  Breakthroughs: {report['breakthrough_count']}")
        print(f"  Chains: {report['chain_count']}")
        print(f"  Episodes boosted: {report['boosted_count']}")
        print(f"  Memory traces: {report['trace_count']}")

        # Store report
        engine.store_consolidation_report(report)

        return 0

    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Monitoring:**
```bash
# Log consolidation reports
tail -f /var/log/nexus/consolidation.log

# Check last consolidation
curl http://localhost:8003/memory/consolidation/last_report
```

---

## 📊 Success Metrics

### Quantitative

1. **Breakthrough Detection Precision:** >80% of detected breakthroughs judged important by user
2. **Chain Completeness:** >90% of breakthrough precursors included in chains
3. **Consolidated Boost Range:** Average +0.10 to +0.15 for precursors
4. **Processing Time:** <10 minutes for 100 episodes
5. **Memory Trace Accuracy:** >85% of traces enable correct narrative retrieval

### Qualitative

1. **Narrative Coherence:** Querying any episode returns full project context
2. **Routine-to-Important Recognition:** "Started research" episodes surface when needed
3. **No False Consolidation:** Unrelated episodes not incorrectly linked
4. **Temporal Logic:** Chains follow natural chronological narrative

---

## ⚡ Performance Considerations

**Computational Cost:**

| Operation | Time per Episode | Time for 100 Episodes |
|-----------|-----------------|---------------------|
| Fetch episodes | <1ms | <100ms |
| Breakthrough detection | 5ms | 500ms |
| Chain tracing | 10ms | 1s |
| Consolidated salience calc | 2ms | 200ms |
| Interleaved replay | 3ms | 300ms |
| Memory traces | 5ms | 500ms |
| Database updates | 10ms | 1s |
| **Total** | **~35ms** | **~3.5 minutes** |

**Optimization:**
- Batch database queries (not one-by-one)
- Cache embeddings (no re-computation)
- Parallel chain tracing (independent chains)
- Use database indexes for trace lookups

**Estimated:** 5-10 minutes for typical daily workload (50-150 episodes)

---

## 🛡️ Safety Mechanisms

### 1. Consolidation Bounds
```python
# Never boost beyond 1.0
consolidated_salience = min(original + boost, 1.0)

# Never boost more than +0.20
boost = min(calculated_boost, 0.20)

# Require minimum original salience (no boosting garbage)
if original_salience < 0.30:
    boost = 0  # Don't consolidate very low salience episodes
```

### 2. Chain Validation
```python
# Max chain length (prevent runaway tracing)
MAX_CHAIN_LENGTH = 15

# Max time window (don't connect distant episodes)
MAX_CHAIN_HOURS = 12

# Min relatedness threshold
MIN_SIMILARITY = 0.60
```

### 3. Interleaved Ratio
```python
# Ensure old memories don't dominate
MIN_NEW_RATIO = 0.60  # At least 60% new memories
MAX_OLD_RATIO = 0.40  # At most 40% old memories
```

### 4. Rollback on Failure
```python
# Database transaction
with db.transaction():
    try:
        consolidate_all()
        commit()
    except Exception as e:
        rollback()
        log_error(e)
        send_alert()
```

---

## 🔮 Future Enhancements

**LAB_003.1: Adaptive Consolidation**
- Learn optimal boost factors from user feedback
- Personalized breakthrough detection thresholds

**LAB_003.2: Multi-Day Consolidation**
- Weekly consolidation (consolidate the consolidations)
- Project-level narratives (spans weeks)

**LAB_003.3: Forgetting Acceleration**
- Actively weaken non-consolidated memories
- Faster decay for low-salience, non-consolidated episodes

---

**Design Status:** ✅ Complete
**Next Step:** Implementation (ConsolidationEngine class) - Future Session
**Estimated Implementation Time:** 3-4 hours

---

*"Memory is not about preserving everything. It's about preserving what matters." - Inspired by biological sleep consolidation*
