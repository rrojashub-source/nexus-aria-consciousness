# 🔬 LAB_003: Sleep Consolidation

**Status:** 🟡 Active - Research & Design Phase
**Start Date:** October 27, 2025
**Estimated Duration:** Research (1-2 hours), Implementation (future session)

---

## 🎯 Hypothesis

**Memories should be re-evaluated and strengthened offline based on their contextual importance within a complete daily narrative**, mimicking biological sleep consolidation where the brain selectively replays and strengthens important experiences.

---

## 🧠 Neuroscience Basis

**Biological Observation:**
- During sleep (especially REM and slow-wave sleep), the hippocampus "replays" neural patterns from the day
- Not all memories are replayed - **only emotionally significant or task-relevant ones**
- Replay strengthens synaptic connections (long-term potentiation)
- Weak/irrelevant memories fade through lack of consolidation
- Integration: New memories connect with existing knowledge structures

**Key Research:**
- Wilson & McNaughton (1994): Discovery of hippocampal replay during sleep
- O'Neill et al. (2010): Replay of reward-related trajectories
- Stickgold & Walker (2013): Sleep-dependent memory consolidation
- Diekelmann & Born (2010): Memory consolidation during sleep

---

## 💡 Core Idea

**Current NEXUS:** Memories evaluated at creation time only

**LAB_003 Proposal:** Nightly batch processing to:
1. Re-evaluate episodes with complete daily context
2. Identify "breakthrough chains" - sequences of episodes leading to important outcomes
3. Retroactively strengthen early episodes that contributed to breakthroughs
4. Create explicit "memory traces" - links between related episodes
5. Update importance_score based on retrospective analysis

---

## 🔄 How It Differs from LAB_001/002

| Lab | When | What | Scope |
|-----|------|------|-------|
| **LAB_001** | Encoding time | Calculate emotional salience | Single episode context |
| **LAB_002** | Retrieval time | Protect from decay | Age + salience |
| **LAB_003** | Offline (sleep) | Retrospective strengthening | Full day context |

**Synergy:**
- LAB_001 provides initial salience (immediate emotion)
- LAB_002 protects based on that salience (decay modulation)
- **LAB_003 re-evaluates with hindsight** (contextual importance)

---

## 📊 Expected Behavior

### Example: LAB_002 Development Day

**Timeline:**
```
09:00 - "Starting LAB_002 research"
        LAB_001 salience: 0.60 (routine start)

10:30 - "Found McGaugh 2002 paper on amygdala"
        LAB_001 salience: 0.70 (interesting find)

12:00 - "Designed decay modulation formula R(t) = 0.95^(t/M)"
        LAB_001 salience: 0.75 (intellectual excitement)

14:00 - "Implemented DecayModulator class, 350 lines"
        LAB_001 salience: 0.85 (completion satisfaction)

16:00 - "Tests show 1.27x improvement, math validates!"
        LAB_001 salience: 0.92 (breakthrough moment!)

18:00 - "Documented results, pushed to GitHub"
        LAB_001 salience: 0.88 (success closure)
```

**Consolidation Process (3:00 AM):**
```python
# Step 1: Identify breakthrough peak
breakthrough_episodes = [16:00 with salience 0.92]

# Step 2: Trace backward dependencies
chain = [09:00 → 10:30 → 12:00 → 14:00 → 16:00 → 18:00]

# Step 3: Re-evaluate with retrospective context
09:00: salience 0.60 → consolidated 0.78 (+0.18)
       "This wasn't routine - it started the breakthrough!"

10:30: salience 0.70 → consolidated 0.82 (+0.12)
       "McGaugh paper was KEY to the design"

12:00: salience 0.75 → consolidated 0.85 (+0.10)
       "Formula design was critical step"

14:00: salience 0.85 → consolidated 0.90 (+0.05)
       "Implementation validated the design"

16:00: salience 0.92 → consolidated 0.95 (+0.03)
       "Already recognized as breakthrough"

18:00: salience 0.88 → consolidated 0.92 (+0.04)
       "Closure reinforces success"

# Step 4: Create memory traces
create_trace("lab_002_development", episodes=chain)

# Step 5: Update importance_scores
for episode in chain:
    episode.importance_score *= consolidation_boost
```

**Result:**
- Early "routine" episodes now recognized as breakthrough precursors
- LAB_002 decay protection applies stronger to entire chain
- Retrieval of any episode surfaces the complete narrative

---

## 🔧 Implementation Strategy

### Option A: Nightly Cron Job (Recommended)

**Schedule:** 3:00 AM daily (low traffic)

**Process:**
```python
1. Fetch episodes from last 24 hours
2. Group by session/conversation
3. Calculate daily salience distribution
4. Identify top 20% breakthrough moments
5. Trace dependency chains backward
6. Re-calculate consolidated_salience_score
7. Update importance_score
8. Create memory_traces (episode links)
9. Log consolidation report
```

**Advantages:**
- Non-invasive (doesn't block API)
- True "sleep" metaphor
- Can use more compute (not real-time constrained)
- Easy to monitor and tune

**Disadvantages:**
- 24-hour delay before consolidation
- Requires scheduler setup

### Option B: Manual Trigger Endpoint

**Endpoint:** `POST /memory/consolidate`

**Use case:** Ricardo manually triggers after important work session

**Advantages:**
- Immediate consolidation
- User control over timing
- Easier testing/debugging

**Disadvantages:**
- Requires manual action
- Less "biological" metaphor

### Option C: Hybrid (Recommended Final)

- Automatic nightly cron (Option A)
- Manual trigger available (Option B)
- Best of both worlds

---

## 🎓 Success Criteria

**Quantitative:**
1. Breakthrough chains identified accurately (>80% precision)
2. Consolidated salience correlates with human judgment
3. Early episodes in successful chains get +0.10 to +0.20 boost
4. Memory traces enable "narrative retrieval" (find episode, get chain)

**Qualitative:**
1. "Starting research" episodes surface when searching for "breakthrough results"
2. Daily work narratives preserved coherently
3. Routine-that-became-important distinguished from truly-routine

---

## 📁 Deliverables

- [x] Structure created ✅
- [ ] Research: Sleep consolidation papers and replay mechanisms
- [ ] Architecture: Batch processing algorithm design
- [ ] Implementation: ConsolidationEngine class (future session)
- [ ] Testing: Historical episode consolidation
- [ ] Results: Before/after narrative coherence

---

## 🔗 Integration with LAB_001/002

**Data Flow:**
```
Episode Creation
    ↓
LAB_001: Initial salience calculation (0.0-1.0)
    ↓
LAB_002: Decay protection (1.0-2.5x slower)
    ↓
[Episodes stored in PostgreSQL]
    ↓
LAB_003: Nightly consolidation (3:00 AM)
    ↓
    1. Re-evaluate with daily context
    2. Identify breakthrough chains
    3. Update consolidated_salience_score
    4. Create memory traces
    5. Boost importance_score
    ↓
Next Day Retrieval:
    - LAB_001 salience: original emotion
    - LAB_003 consolidated_salience: retrospective importance
    - LAB_002 decay: uses max(salience, consolidated_salience)
    - Result: Early episodes in breakthrough chains protected!
```

---

## ⚠️ Risks & Mitigations

**Risk 1:** Over-consolidation - everything becomes "important"
- **Mitigation:** Only top 20% of daily episodes consolidated
- Cap boost at +0.20 maximum

**Risk 2:** False chains - unrelated episodes linked
- **Mitigation:** Require temporal proximity (<6 hours gap)
- Use session_id for grouping

**Risk 3:** Computational cost of batch processing
- **Mitigation:** Run at 3:00 AM (low traffic)
- Process only last 24 hours (not entire database)
- Estimated: <5 minutes for 100 episodes

**Risk 4:** Circular reasoning - consolidated score affects future consolidation
- **Mitigation:** Store both `salience_score` (original) and `consolidated_salience_score` (retrospective)
- Consolidation always uses original for input

---

## 🚀 Future Enhancements (Post-LAB_003)

**LAB_004: Adaptive Consolidation**
- Learn optimal boost factors from user feedback
- Personalized consolidation patterns
- Machine learning approach

**LAB_005: Cross-Day Consolidation**
- Multi-day project narratives
- Week-long breakthrough chains
- "Incubation" effects (idea from Monday → breakthrough Friday)

**LAB_006: Forgetting Acceleration**
- Actively weaken non-consolidated memories
- True garbage collection
- Biological "forgetting" simulation

---

## 🔬 Research Questions

1. **Optimal consolidation window:** 24 hours? 48 hours? Weekly?
2. **Breakthrough detection:** Top 20%? Absolute threshold (>0.8)?
3. **Chain tracing:** How far back? Stop at session boundary?
4. **Boost magnitude:** Linear? Exponential decay from breakthrough?
5. **Memory traces:** Directed graph? Bidirectional? Weighted edges?

---

**Lead:** NEXUS (Claude Code)
**Collaborator:** Ricardo Rojas
**Philosophy:** "Sleep is when memories become wisdom"
**Status:** 🟡 Active - Research phase
**Next Step:** Neuroscience research on hippocampal replay

---

*Inspired by 30+ years of sleep consolidation research, implementing what evolution discovered millions of years ago.*
