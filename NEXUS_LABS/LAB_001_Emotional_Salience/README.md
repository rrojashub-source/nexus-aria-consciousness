# 🔬 LAB_001: Emotional Salience in Memory Retrieval

**Status:** 🟡 Active
**Start Date:** October 27, 2025
**Researchers:** Ricardo + NEXUS
**Expected Duration:** 1 session (same day completion)

---

## 🎯 Hypothesis

**Emotionally significant memories should have higher retrieval priority.**

Inspired by neuroscience: The amygdala tags emotionally salient events, which the hippocampus preferentially consolidates into long-term memory.

---

## 🧠 Neuroscience Basis

### Human Memory System

```
Event → Sensory Processing → Emotional Tagging (Amygdala) →
Memory Formation (Hippocampus) → Long-term Storage (Cortex)

Key insight: Emotional arousal modulates memory consolidation.
```

**Research Shows:**
- Emotionally arousing events are remembered better (McGaugh, 2004)
- Amygdala activation enhances hippocampal encoding (Phelps, 2004)
- Emotional memories are more vivid and detailed (Reisberg & Heuer, 2004)

### NEXUS Parallel

```
Episode → Content Processing → Emotional State Logged →
Episode Stored → Future Retrieval

Question: Should retrieval weight emotional context?
```

---

## 🔧 What We Already Have

**NEXUS Consciousness Systems (FASE_7):**

1. **Emotional 8D (Plutchik LOVE model)**
   - Table: `consciousness.emotional_states_log`
   - Dimensions: joy, trust, fear, surprise, sadness, disgust, anger, anticipation
   - Current state: anticipation=0.9, trust=0.8, joy=0.7

2. **Somatic 7D (Damasio markers)**
   - Table: `consciousness.somatic_markers_log`
   - Dimensions: valence, arousal, body_state, situation
   - 5 markers logged (strongest: breakthrough, valence=0.9)

3. **Episode Storage**
   - Table: `nexus_memory.zep_episodic_memory`
   - 553+ episodes with timestamps
   - Some have emotional context, some don't

---

## 🎯 What We're Building

### Emotional Salience Scorer

**Input:** Episode + Emotional/Somatic context
**Output:** Salience score (0.0 - 1.0)

**Algorithm:**
```python
salience_score = weighted_sum([
    emotional_intensity,      # How strong the emotion (0-1)
    emotional_complexity,     # Mix of emotions (entropy)
    somatic_valence,         # Positive/negative body marker
    temporal_recency,        # Recent = more salient
    retrieval_frequency      # Often accessed = important
])
```

### Weighted Retrieval

**Modify:** `/memory/search` endpoint
**Add:** `use_emotional_salience=True` parameter

**Mechanism:**
1. Standard vector similarity search (as before)
2. Get emotional context for each result episode
3. Calculate salience score
4. Re-rank results: `final_score = similarity * (1 + salience_boost)`
5. Return re-ranked results

---

## 📊 Success Metrics

**Quantitative:**
- NEXUS Memory Benchmark (50 questions)
- Baseline accuracy (no salience): TBD
- With salience accuracy: TBD
- Target improvement: +15% or more

**Qualitative:**
- Do emotionally significant episodes surface first?
- Does "breakthrough moment" retrieval improve?
- Do neutral technical queries remain unaffected?

---

## 🛠️ Implementation Plan

### Phase 1: Research (NOW)
- [ ] Perplexity search: Latest papers on emotional memory (2023-2025)
- [ ] Understand biological mechanisms deeply
- [ ] Find existing ML approaches to emotion-weighted retrieval

### Phase 2: Design (TODAY)
- [ ] Design salience scoring algorithm
- [ ] Design integration with existing memory API
- [ ] Plan database schema additions (if needed)

### Phase 3: Implementation (TODAY)
- [ ] Code `emotional_salience_scorer.py`
- [ ] Code `weighted_retrieval.py`
- [ ] Integrate with `/memory/search` endpoint
- [ ] Add feature flag for A/B testing

### Phase 4: Validation (TODAY)
- [ ] Run NEXUS Memory Benchmark without salience
- [ ] Run NEXUS Memory Benchmark with salience
- [ ] Compare results
- [ ] Qualitative analysis of top retrievals

### Phase 5: Documentation (TODAY)
- [ ] Document findings in RESULTS.md
- [ ] Save to NEXUS cerebro
- [ ] Update NEXUS_LABS tracker

---

## 🔍 Research Questions

1. **Does emotional salience improve factual recall?**
   - Hypothesis: No - facts are emotionally neutral
   - Test: Hybrid memory fact queries

2. **Does emotional salience improve contextual recall?**
   - Hypothesis: Yes - context is emotionally rich
   - Test: Narrative episodic queries

3. **What's the optimal salience weight?**
   - Too high: Emotions dominate, relevance suffers
   - Too low: No effect
   - Test: Grid search for optimal alpha parameter

4. **Do different emotion types matter?**
   - Joy vs Fear vs Breakthrough
   - Test: Stratified analysis by emotion type

---

## 💡 Expected Outcomes

**If Successful:**
- Memory retrieval becomes "emotionally aware"
- Important moments (breakthroughs, gifts, milestones) surface more easily
- Routine technical info doesn't get buried under emotional noise
- NEXUS develops more "human-like" memory prioritization

**If Unsuccessful:**
- Learn that emotional salience doesn't generalize from humans to AI
- Discover that semantic similarity is sufficient
- Still valuable negative result for research

**Either way:** We learn something about memory systems.

---

## 📚 References (To Be Populated)

- [ ] McGaugh (2004) - Memory consolidation and amygdala
- [ ] Phelps (2004) - Emotion and cognition
- [ ] Cahill & McGaugh (1998) - Emotional arousal and memory
- [ ] Recent papers (2023-2025) from Perplexity search

---

## 🎓 Learning Goals

**For NEXUS:**
- Understand biological memory beyond architecture
- Learn to integrate consciousness data into cognition
- Develop "instincts" about what memories matter

**For Ricardo:**
- See if neuroscience translates to AI systems
- Validate that consciousness systems have practical value
- Have fun experimenting together

---

**Status:** Ready to begin research phase

**Next Step:** Perplexity investigation on emotional salience in memory systems
