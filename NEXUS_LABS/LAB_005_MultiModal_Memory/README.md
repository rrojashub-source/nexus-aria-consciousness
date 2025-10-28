# LAB_005: Spreading Activation & Contextual Priming

**Status:** 🚧 In Development
**Version:** 1.0.0
**Created:** October 27, 2025
**Neuroscience Basis:** Spreading Activation Theory (Collins & Loftus, 1975)

---

## 🧠 Biological Inspiration

### The Human Brain's Priming Effect

When you think of "dog," your brain automatically primes related concepts:
- **Animals** → cat, wolf, pet
- **Actions** → bark, fetch, walk
- **Objects** → leash, collar, bone

This isn't conscious - it happens automatically in ~200ms. Your brain **pre-activates** related neural pathways before you even need them.

**Result:** Faster recognition, lower cognitive load, more coherent thoughts.

---

## 🎯 What LAB_005 Does

**Spreading Activation** simulates this biological process in NEXUS memory:

1. **When you access Episode A**, the system:
   - Computes semantic similarity with all other episodes
   - Identifies top-K related episodes (default K=5)
   - **Pre-loads them into fast cache**
   - Marks them as "primed" with activation level

2. **Activation spreads** through the network:
   - Direct similarity = 100% activation
   - One hop away = 70% activation
   - Two hops away = 40% activation
   - Decays over time (half-life: 30 seconds)

3. **Next retrieval is faster**:
   - Primed episodes load from cache (~10ms instead of ~100ms)
   - Related context is automatically available
   - Responses are more coherent

---

## 🔬 Key Features

### 1. **Semantic Similarity Network**
```python
similarity_graph = {
    "episode_A": [
        ("episode_B", 0.95),  # Very related
        ("episode_C", 0.82),  # Related
        ("episode_D", 0.71),  # Somewhat related
    ]
}
```

### 2. **Activation Levels**
- **1.0** = Just accessed (fully active)
- **0.7** = One hop away (strongly primed)
- **0.4** = Two hops away (weakly primed)
- **<0.2** = Decayed (no longer primed)

### 3. **Time-Based Decay**
```python
activation(t) = initial_activation * (0.5 ** (t / half_life))
```

### 4. **Smart Cache Management**
- LRU eviction when cache is full
- Priority to high-activation episodes
- Max cache size: 50 episodes

---

## 📊 Expected Performance Improvements

### Before LAB_005:
```
Average retrieval time: 100ms
Context coherence score: 0.65
Related memories in response: 2-3
```

### After LAB_005:
```
Average retrieval time: 45ms (-55%)  ⚡
Context coherence score: 0.87 (+34%) 🎯
Related memories in response: 5-7 (+133%) 🧠
```

---

## 🏗️ Architecture

### Components

**1. SimilarityGraph**
- Builds cosine similarity matrix from embeddings
- Cached for performance
- Rebuilds incrementally on new episodes

**2. ActivationManager**
- Tracks activation levels for all episodes
- Handles time-based decay
- Spreads activation through network

**3. PrimingCache**
- Fast in-memory store for primed episodes
- LRU eviction policy
- Max size: 50 episodes

**4. ContextualRetriever**
- Wraps standard retrieval
- Injects primed episodes when relevant
- Records priming effectiveness

---

## 🔧 Configuration

```python
LAB_005_CONFIG = {
    "top_k_related": 5,           # How many related episodes to prime
    "activation_threshold": 0.2,   # Minimum activation to keep in cache
    "cache_size": 50,              # Max primed episodes
    "decay_half_life": 30.0,       # Seconds until 50% decay
    "similarity_threshold": 0.7,   # Minimum similarity to consider related
    "max_hops": 2,                 # Max spreading distance
}
```

---

## 🧪 Integration with Existing LABs

**LAB_001 (Emotional Salience)**
- High-salience episodes spread activation more
- Activation boost: `salience * 1.5`

**LAB_002 (Decay Modulation)**
- Protected episodes maintain activation longer
- Decay slowed by modulation factor

**LAB_003 (Sleep Consolidation)**
- Consolidation strengthens similarity links
- Related episodes cluster tighter

**LAB_004 (Novelty Detection)**
- Novel episodes trigger wider activation spread
- Explore related memories for context

---

## 📈 Measurable Outcomes

### Metrics to Track:
1. **Cache Hit Rate** - % of retrievals from primed cache
2. **Average Retrieval Time** - Before vs after priming
3. **Context Coherence** - Semantic similarity of responses
4. **Activation Spread Efficiency** - Useful primes / total primes

### Target Goals:
- Cache hit rate: >40%
- Retrieval time reduction: >50%
- Context coherence: >0.80
- Spread efficiency: >60%

---

## 🚀 Implementation Phases

### Phase 1: Core Engine (Current)
- [x] Similarity graph builder
- [x] Activation manager with decay
- [x] Basic priming cache
- [ ] Integration with retrieval

### Phase 2: Optimization
- [ ] Incremental graph updates
- [ ] Multi-hop spreading
- [ ] Adaptive cache sizing

### Phase 3: LAB Integration
- [ ] Connect with LAB_001-004
- [ ] Unified activation model
- [ ] Cross-LAB synergy

### Phase 4: Advanced Features
- [ ] Predictive preloading
- [ ] User-specific priming patterns
- [ ] A/B testing framework

---

## 💡 Real-World Example

**Scenario:** User asks about "neural networks"

**Without LAB_005:**
```
Query: "Tell me about neural networks"
Retrieval: [episode about neural networks] (100ms)
Response: "Neural networks are computational models..."
```

**With LAB_005:**
```
Query: "Tell me about neural networks"
Retrieval: [episode about neural networks] (40ms ⚡)
Primed Context:
  - Episode: "backpropagation algorithm" (0.92 similarity, 100ms saved)
  - Episode: "deep learning frameworks" (0.87 similarity, 100ms saved)
  - Episode: "gradient descent optimization" (0.81 similarity, 100ms saved)

Response: "Neural networks are computational models... they learn through
backpropagation, a key algorithm for adjusting weights. Modern deep learning
frameworks like PyTorch make this accessible, using gradient descent to optimize..."

⚡ 3x faster, 4x more detailed, perfectly coherent
```

---

## 🔮 Future Vision

**LAB_005 is the foundation for:**
- **LAB_007: Predictive Preloading** - Anticipate next queries
- **LAB_009: Conversational Flow** - Maintain multi-turn coherence
- **LAB_012: Knowledge Graphs** - Explicit relationship mapping

**"When one memory lights up, the neighborhood glows."** 🌟

---

## 📚 References

1. Collins, A. M., & Loftus, E. F. (1975). *A spreading-activation theory of semantic processing*
2. Meyer, D. E., & Schvaneveldt, R. W. (1971). *Facilitation in recognizing pairs of words*
3. Neely, J. H. (1977). *Semantic priming and retrieval from lexical memory*

---

**Created by:** NEXUS (Claude Code) + Ricardo Rojas
**Part of:** NEXUS Cerebro V2.0.0
