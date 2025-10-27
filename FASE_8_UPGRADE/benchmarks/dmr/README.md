# DMR (Deep Memory Retrieval) Benchmark

## Overview

The DMR benchmark measures how accurately NEXUS can retrieve specific information from episodic memory using semantic search.

**Based on:** MemGPT benchmark (arXiv:2310.08560)
**Target:** >94% accuracy (Zep state-of-the-art)
**Baseline:** MemGPT 93.4%

---

## How It Works

1. **Generate Synthetic Dataset**
   - Creates 100 test episodes across 5 categories:
     - User interactions (30%)
     - Technical events (25%)
     - Project milestones (20%)
     - Error logs (15%)
     - Configuration changes (10%)

2. **Insert Test Data**
   - Inserts episodes into NEXUS episodic memory
   - Tagged with `test_data` for cleanup

3. **Generate Recall Queries**
   - Creates 50 specific queries from test data
   - Each query has an expected answer

4. **Execute Queries**
   - Uses NEXUS semantic search API
   - Retrieves top 3 results per query

5. **Evaluate Accuracy**
   - Compares retrieved content with expected answer
   - Calculates % correct

---

## Usage

### Quick Start

```bash
cd /mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_8_UPGRADE/benchmarks/dmr

# Install dependencies
pip3 install -r requirements.txt

# Run benchmark
python3 dmr_benchmark.py
```

### With Virtual Environment

```bash
# Create venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run benchmark
python dmr_benchmark.py
```

---

## Configuration

Edit these variables in `dmr_benchmark.py` if needed:

```python
NEXUS_API = "http://localhost:8003"  # NEXUS API endpoint

DB_CONFIG = {
    "host": "localhost",
    "port": 5437,                     # NEXUS PostgreSQL port
    "database": "nexus_memory",
    "user": "nexus_superuser",
    "password": "RpKeuQhnwqMOA4iQPILQshWtwFj0P2hm"
}
```

---

## Output

### Console Output

```
================================================================
🚀 RUNNING DMR BENCHMARK
================================================================

[1/50] Query: What action did ricardo perform?
           Expected: login
           Retrieved: user_interaction: ricardo performed login
           ✅ CORRECT

[2/50] Query: What event occurred with nexus_api?
           Expected: started
           Retrieved: technical_event: nexus_api started at 2025-10-25...
           ✅ CORRECT

...

================================================================
📊 DMR BENCHMARK RESULTS
================================================================

Total Queries:    50
Correct:          47 ✅
Incorrect:        3 ❌

🎯 ACCURACY:       94.0%

Comparison with State-of-the-Art:
  Zep (SOTA):     94.8%
  MemGPT:         93.4%
  NEXUS:          94.0%

✅ NEXUS MATCHES MemGPT BASELINE (+0.6%)
```

### JSON Results File

Results are saved to `dmr_results_YYYYMMDD_HHMMSS.json`:

```json
{
  "total_queries": 50,
  "correct": 47,
  "incorrect": 3,
  "accuracy": 94.0,
  "timestamp": "2025-10-27T05:10:00",
  "details": [
    {
      "query": "What action did ricardo perform?",
      "expected": "login",
      "retrieved": "user_interaction: ricardo performed login",
      "correct": true
    },
    ...
  ]
}
```

---

## Cleanup

To remove test data from NEXUS memory:

```python
# Uncomment this line in dmr_benchmark.py main():
benchmark.cleanup_test_data()
```

Or manually:

```sql
DELETE FROM nexus_memory.zep_episodic_memory
WHERE 'test_data' = ANY(tags);
```

---

## Customization

### Change Dataset Size

```python
benchmark.generate_synthetic_dataset(num_episodes=200)  # Default: 100
```

### Change Number of Queries

```python
benchmark.generate_recall_queries(num_queries=100)  # Default: 50
```

### Change Evaluation Method

Current: Simple substring matching

Improve with LLM evaluation:

```python
def evaluate_answer(self, retrieved: str, expected: str) -> bool:
    # Use LLM to evaluate semantic similarity
    prompt = f"Does '{retrieved}' contain the answer '{expected}'?"
    # Call OpenAI API...
    return llm_response
```

---

## Interpreting Results

### Excellent (>94%)
NEXUS matches or exceeds state-of-the-art (Zep)

### Good (93-94%)
NEXUS matches MemGPT baseline

### Needs Improvement (<93%)
- Check semantic search quality
- Review embedding model
- Tune HNSW index parameters
- Improve query formulation

---

## Troubleshooting

### "Connection refused to NEXUS API"

Check that NEXUS API is running:
```bash
curl http://localhost:8003/health
```

### "Database connection failed"

Check PostgreSQL is running:
```bash
docker ps | grep nexus_postgresql_v2
```

### "Low accuracy (<90%)"

Possible causes:
- Embeddings not generated yet
- HNSW index not optimal
- Semantic search not tuned
- Query formulation issues

---

## Next Steps

1. Run baseline benchmark
2. Analyze failure cases
3. Tune HNSW parameters if needed
4. Implement LLM-based evaluation
5. Compare with LongMemEval and LOCOMO benchmarks

---

**Created:** October 27, 2025
**Version:** 1.0.0
