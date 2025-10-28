# LAB_005 + A/B Testing - Quick Start Guide

**Status:** ✅ Code deployed, API restart needed
**Date:** October 27, 2025

---

## 🚀 Quick Start (3 Steps)

### 1. Restart NEXUS API (to load new modules)

```bash
cd /mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_4_CONSTRUCCION

# If running in Docker:
docker-compose restart nexus_api

# Or if running directly:
# Kill current process and restart
pkill -f "python.*main.py"
python3 src/api/main.py
```

### 2. Verify LAB_005 Endpoints

```bash
# Check API health
curl http://localhost:8003/health

# Check LAB_005 stats (should work now)
curl http://localhost:8003/memory/priming/stats

# Check A/B testing is ready
curl http://localhost:8003/ab-test/compare
```

### 3. Populate A/B Dashboard with Sample Data

```bash
cd /mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_4_CONSTRUCCION
python3 test_ab_framework.py
```

**Expected output:**
```
✅ Completed!
   Control: 50/50 recorded
   Treatment: 50/50 recorded

🎯 Results:
   Latency Reduction: ~50%
   Cache Hit Rate: ~275%
   Coherence: ~28%
   Primed Episodes: 4.5
```

---

## 📊 View Dashboard

```
URL: http://localhost:3000

1. Select "📊 Dashboard 2D"
2. Scroll to "🧪 A/B Testing: LAB_005 Performance"
3. See live comparison charts

Or select "🧠 Brain 3D" to see LAB_005 sphere (pink)
```

---

## 🧪 Manual Testing

### Record Control Metric (without LAB_005)

```bash
curl -X POST http://localhost:8003/ab-test/record \
  -H "Content-Type: application/json" \
  -d '{
    "variant": "control",
    "retrieval_time_ms": 98.5,
    "cache_hit": false,
    "num_results": 3,
    "context_coherence": 0.68
  }'
```

### Record Treatment Metric (with LAB_005)

```bash
curl -X POST http://localhost:8003/ab-test/record \
  -H "Content-Type: application/json" \
  -d '{
    "variant": "treatment",
    "retrieval_time_ms": 43.2,
    "cache_hit": true,
    "num_results": 6,
    "context_coherence": 0.89,
    "primed_count": 5
  }'
```

### View Comparison

```bash
curl http://localhost:8003/ab-test/compare?hours_back=24 | jq
```

---

## 📁 Files Deployed

### Backend (API Port 8003)
- `FASE_4_CONSTRUCCION/src/api/ab_testing.py` (420 lines)
- `FASE_4_CONSTRUCCION/src/api/spreading_activation.py` (420 lines)
- `FASE_4_CONSTRUCCION/src/api/main.py` (updated with 8 new endpoints)

### Frontend (Web Port 3000)
- `brain-monitor-web/components/ABTestingDashboard.tsx` (350 lines)
- `brain-monitor-web/components/BrainModel3D.tsx` (LAB_005 sphere added)
- `brain-monitor-web/components/LABStatus.tsx` (5th LAB card)
- `brain-monitor-web/app/page.tsx` (integrated A/B dashboard)

### Documentation
- `NEXUS_LABS/LAB_005_DEPLOYMENT_SUMMARY.md` (full deployment guide)
- `NEXUS_LABS/LAB_005_QUICKSTART.md` (this file)

### Testing
- `FASE_4_CONSTRUCCION/test_ab_framework.py` (sample data generator)

---

## 🎯 What Each Component Does

### LAB_005: Spreading Activation

**Purpose:** Biologically-inspired memory priming for faster retrieval

**How it works:**
1. When episode accessed → build similarity network
2. Spread activation to related episodes (multi-hop)
3. Pre-load top-K related episodes into LRU cache
4. Activation decays exponentially (half-life: 30s)

**Expected impact:**
- 55% faster retrieval (100ms → 45ms)
- 133% more related memories (2-3 → 5-7)
- 34% better context coherence (0.65 → 0.87)

### A/B Testing Framework

**Purpose:** Scientific validation of LAB_005 performance

**Tracks:**
- Retrieval latency (ms)
- Cache hit rate (%)
- Context coherence (cosine similarity)
- Number of primed episodes

**Provides:**
- Statistical significance (Cohen's d effect size)
- Automated recommendations (deploy/test/optimize)
- Time-series visualization
- Real-time comparison dashboard

---

## 🔍 Troubleshooting

### API not responding to new endpoints

```bash
# Check API logs
docker logs nexus_api

# Or if running directly
ps aux | grep "python.*main.py"
```

**Fix:** Restart API to load new modules

### Dashboard shows "Insufficient data"

**Cause:** No A/B test data recorded yet
**Fix:** Run `python3 test_ab_framework.py` to generate sample data

### LAB_005 stats show null

**Cause:** No episodes have been accessed with priming yet
**Fix:** This is normal - LAB_005 activates on first episode access

---

## 📚 Next Steps

1. **Restart API** to load new modules
2. **Run test script** to populate dashboard
3. **View dashboard** at http://localhost:3000
4. **Collect real data** by using memory retrieval endpoints
5. **Analyze results** after 24+ hours of data collection

---

## 🎉 Success Criteria

You'll know LAB_005 is working when:

✅ API `/memory/priming/stats` returns non-null values
✅ A/B dashboard shows comparison with recommendations
✅ 3D brain shows 5th pink sphere (LAB_005)
✅ 2D dashboard shows 5th LAB card
✅ Statistical significance shows "high" confidence

---

**Created by:** NEXUS (Claude Code)
**Git Commit:** e3fb383
**GitHub:** https://github.com/rrojashub-source/nexus-aria-consciousness
