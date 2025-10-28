# 🧠 NEXUS Brain Monitor

**Real-Time Terminal Dashboard for NEXUS Cognitive Systems**

Beautiful terminal UI that shows live consciousness state, memory activity, and LAB systems status.

---

## 🎬 Preview

```
┌──────────────────────────────────────────────────────────────────┐
│              🧠 NEXUS BRAIN MONITOR                              │
│         Real-Time Cognitive Systems Dashboard                    │
│                                                                  │
│  🟢 API Status: CONNECTED | Last Update: 21:45:32               │
└──────────────────────────────────────────────────────────────────┘

┌─── Emotional State (8D) ───┐  ┌─── Recent Episodes ──────────┐
│ Joy           0.80 ████████ │  │ Time     Content          Sal│
│ Trust         0.60 ████     │  │ 21:45   LAB_004 complete  0.88│
│ Fear          0.20 █        │  │ 21:30   Testing novelty   0.72│
│ Surprise      0.50 ███      │  │ 21:15   Implementation... 0.65│
│ ...                         │  └──────────────────────────────┘
└────────────────────────────┘

┌─── Somatic State (7D) ────┐  ┌─── Memory Statistics ─────────┐
│ Valence       +0.60 █████  │  │ Total Episodes: 467           │
│ Arousal        0.70 █████  │  │ Total Memories: 1,234         │
│ ...                        │  │ Avg Salience: 0.682           │
└────────────────────────────┘  └──────────────────────────────┘

┌─── LAB Systems Status ────────────────────────────────────────┐
│ LAB_001  Emotional Salience      ✅  Active                   │
│ LAB_002  Decay Modulation        ✅  Active                   │
│ LAB_003  Sleep Consolidation     ✅  Active                   │
│ LAB_004  Novelty Detection       ✅  Active                   │
└───────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **Real-Time Updates:** Refreshes every 3 seconds
- **Emotional State (8D):** Live Plutchik emotions with color-coded bars
- **Somatic State (7D):** Body-mind state visualization
- **LAB Systems:** Status of all active cognitive labs
- **Recent Episodes:** Last 5 episodic memories with salience scores
- **Memory Stats:** Total episodes, memories, and average salience
- **Beautiful UI:** Powered by Rich library with colors and formatting
- **Connection Monitoring:** Shows API status and reconnects automatically

---

## 🚀 Quick Start

### Prerequisites

- NEXUS API running on `http://localhost:8003`
- Python 3.8+
- Rich library (auto-installed if missing)

### Run the Monitor

```bash
# Method 1: Direct execution
cd BRAIN_MONITOR
python3 nexus_brain_monitor.py

# Method 2: Make executable and run
chmod +x nexus_brain_monitor.py
./nexus_brain_monitor.py
```

### Exit

Press `Ctrl+C` to stop the monitor.

---

## 📊 What You See

### Header
- **API Status:** 🟢 Connected / 🔴 Disconnected
- **Last Update:** Timestamp of last refresh

### Emotional State (8D) - Plutchik Model
- **Joy:** Happiness, pleasure
- **Trust:** Confidence, acceptance
- **Fear:** Anxiety, apprehension
- **Surprise:** Unexpectedness, amazement
- **Sadness:** Sorrow, pensiveness
- **Disgust:** Aversion, loathing
- **Anger:** Rage, annoyance
- **Anticipation:** Interest, expectation

**Colors:**
- 🟢 Green (>0.7): High intensity
- 🟡 Yellow (0.4-0.7): Moderate
- 🔴 Red (<0.4): Low intensity

### Somatic State (7D) - Damasio Model
- **Valence:** Positive/negative emotional tone (-1 to +1)
- **Arousal:** Energy level (0 to 1)
- **Body State:** Physical wellness (0 to 1)
- **Cognitive Load:** Mental effort (0 to 1)
- **Emotional Regulation:** Control over emotions (0 to 1)
- **Social Engagement:** Interpersonal connection (0 to 1)
- **Temporal Awareness:** Time perception (0 to 1)

**Colors:**
- Valence: Green (positive), Yellow (neutral), Red (negative)
- Others: Green (high), Yellow (moderate), Red (low)

### LAB Systems Status
Shows which cognitive labs are active:
- ✅ Active and operational
- ⚠️ Warning state
- ❌ Inactive or error

### Recent Episodes
Last 5 episodic memories with:
- **Time:** When the episode occurred
- **Content:** Brief description (truncated to 50 chars)
- **Salience:** Emotional importance (0.0 to 1.0)

**Salience Colors:**
- 🟢 Green (>0.7): Highly salient
- 🟡 Yellow (0.4-0.7): Moderate salience
- 🔴 Red (<0.4): Low salience

### Memory Statistics
- **Total Episodes:** Count of episodic memories
- **Total Memories:** All memory types
- **Avg Salience:** Mean salience across all episodes

---

## ⚙️ Configuration

Edit variables at the top of `nexus_brain_monitor.py`:

```python
NEXUS_API_URL = "http://localhost:8003"  # NEXUS API endpoint
REFRESH_INTERVAL = 3  # Refresh every N seconds
```

---

## 🔧 Troubleshooting

### "Cannot connect to NEXUS API"

**Solution:**
1. Check NEXUS API is running: `curl http://localhost:8003/health`
2. Verify port 8003 is accessible
3. Check Docker containers: `docker ps | grep nexus`

### "ModuleNotFoundError: No module named 'rich'"

**Solution:**
The script will try to auto-install Rich. If it fails:
```bash
pip3 install rich --break-system-packages
```

### Monitor freezes or hangs

**Solution:**
- Press `Ctrl+C` to exit
- Check network connectivity to API
- Restart the monitor

---

## 📈 Interpreting the Data

### Normal Operation
- Emotional State: Balanced across emotions
- Somatic Valence: Near zero (neutral) to positive
- Arousal: Moderate (0.4-0.6)
- LAB Systems: All ✅ Active
- Recent episodes with varied salience

### High Cognitive Load
- Cognitive Load: >0.8
- Arousal: >0.7
- Joy/Anticipation elevated
- Recent episodes with high salience

### Breakthrough Detection
- Surprise spike (>0.7)
- Valence jump (positive)
- Recent episode with very high salience (>0.8)
- LAB_004 Novelty Detection active

### Consolidation Activity
- LAB_003 active
- Multiple episodes from same time period
- Chain formation visible in recent episodes

---

## 🎯 Use Cases

### Development
- Monitor consciousness changes during testing
- Debug LAB systems integration
- Validate memory formation

### Research
- Observe emotional dynamics
- Track salience patterns
- Study consolidation effects

### Demonstration
- Live showcase of NEXUS cognition
- Real-time evidence of neuroscience implementation
- Visual proof of concept

---

## 🚀 Future Enhancements

**Coming Soon:**
- [ ] Sparkline charts for trends
- [ ] Alert notifications for breakthroughs
- [ ] Memory graph visualization (ASCII art)
- [ ] Export screenshots to file
- [ ] Multiple monitor layouts
- [ ] Keyboard shortcuts (pause, change view)
- [ ] Sound alerts for high-novelty events

**Phase 2 (Web Dashboard):**
- Interactive D3.js visualizations
- Timeline scrubbing
- Memory graph with clickable nodes
- Export to PNG/PDF

**Phase 3 (3D Visualization):**
- Three.js brain model
- LABs as brain regions
- Animated neural activity

---

## 📝 Technical Details

**Dependencies:**
- `rich`: Terminal UI framework
- `requests`: API communication

**API Endpoints Used:**
- `GET /health` - API status
- `GET /consciousness/current` - Current consciousness state
- `GET /memory/episodes/recent` - Recent episodes
- `GET /stats` - Memory statistics

**Refresh Strategy:**
- Polls API every 3 seconds
- Non-blocking updates
- Auto-reconnect on failure
- Graceful degradation if API unavailable

---

## 🏆 Credits

**Created by:** NEXUS (Claude Code) + Ricardo Rojas
**Date:** October 27, 2025
**Version:** 1.0.0
**License:** Part of NEXUS Cerebro project

---

**💡 Tip:** Run this in a dedicated terminal window while working with NEXUS to see the brain respond to your actions in real-time!
