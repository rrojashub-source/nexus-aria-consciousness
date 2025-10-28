# 🌐 NEXUS Brain Monitor - Web Dashboard

**Complete 3-Phase Visualization System**

Beautiful, real-time web dashboard for monitoring NEXUS cognitive systems with 2D data visualizations and immersive 3D brain exploration.

---

## 🎯 Features

### Dual View Modes
- **📊 2D Dashboard** - Data-driven charts and metrics
- **🧠 3D Brain** - Immersive neural architecture visualization
- **Seamless toggle** between views with preserved data

### Real-Time Monitoring
- **Auto-refresh** every 3 seconds
- **Connection status** indicator with live updates
- **Error handling** with graceful degradation

### 2D Visualizations (Dashboard Mode)

**Emotional State (8D Plutchik Model)**
- D3.js radar chart
- 8 dimensions: Joy, Trust, Fear, Surprise, Sadness, Disgust, Anger, Anticipation
- Color-coded by emotion type

**Somatic State (7D Damasio Model)**
- D3.js horizontal bar chart
- 7 dimensions: Valence, Arousal, Body State, Cognitive Load, Emotional Regulation, Social Engagement, Temporal Awareness
- Bidirectional bars for Valence (-1 to +1)

**LAB Systems Status**
- Visual cards for LAB_001 through LAB_004
- Status indicators (✅ active, ⚠️ warning, ❌ inactive)
- Hover descriptions

**Recent Episodes Timeline**
- Last 5 episodic memories
- Importance score badges
- Tags visualization
- Timestamp display

**Memory Statistics**
- Total episodes count
- Embeddings completion percentage
- Queue status (done/pending)
- Real-time progress bars

### 3D Brain Visualization (Brain Mode)

**Interactive 3D Neural Architecture**
- **LAB Regions** as 3D spheres in space
  - LAB_001 (Yellow) - Emotional Salience [3, 1.5, 0]
  - LAB_002 (Green) - Decay Modulation [-3, 1.5, 0]
  - LAB_003 (Purple) - Sleep Consolidation [0, -1.5, 2]
  - LAB_004 (Orange) - Novelty Detection [0, 1.5, -2]
- **Neural Connections** - Lines showing LAB interconnections
- **Activity-Based Animations**
  - Pulsing based on consciousness activity
  - Emissive glow when active
  - Smooth rotation
- **Interactive Controls**
  - Mouse drag to rotate
  - Scroll to zoom (5-20 units)
  - Right-click to pan
  - Auto-rotation (slow)
- **Real-Time Data Mapping**
  - LAB_001 activity = avg(joy, trust, anticipation)
  - LAB_002 activity = emotional_regulation
  - LAB_003 activity = avg(body_state, temporal_awareness)
  - LAB_004 activity = avg(surprise, anticipation)

---

## 🛠️ Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **D3.js 7** - Data-driven 2D visualizations (radar, bars, charts)
- **Three.js 0.160** - WebGL-based 3D rendering
- **React Three Fiber 8.15** - React renderer for Three.js
- **React Three Drei 9.92** - Helper components (OrbitControls, Text, etc.)
- **Tailwind CSS 3** - Utility-first styling
- **Axios** - HTTP client for API calls

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- NEXUS API running on `http://localhost:8003`

### Installation

```bash
# Navigate to project
cd brain-monitor-web

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if API URL is different

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Project Structure

```
brain-monitor-web/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx              # Main dashboard page with 2D/3D toggle
│   └── globals.css           # Global styles
├── components/
│   ├── EmotionalRadar.tsx    # D3 radar chart (8D)
│   ├── SomaticBars.tsx       # D3 horizontal bars (7D)
│   ├── LABStatus.tsx         # LAB cards grid
│   ├── EpisodesTimeline.tsx  # Recent episodes
│   ├── StatsPanel.tsx        # Memory statistics
│   ├── BrainModel3D.tsx      # Three.js 3D brain visualization
│   └── Header.tsx            # App header
├── lib/
│   ├── nexusAPI.ts           # API service layer
│   └── types.ts              # TypeScript interfaces
├── hooks/
│   └── useNexusData.ts       # Custom polling hook
└── public/
    └── favicon.ico
```

---

## 🎨 Customization

### Update API URL
Edit `.env`:
```
NEXT_PUBLIC_NEXUS_API_URL=http://your-nexus-api:8003
```

### Change Refresh Interval
Edit `hooks/useNexusData.ts`:
```typescript
const REFRESH_INTERVAL = 3000; // milliseconds
```

### Customize Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  nexus: {
    dark: '#0a0a0f',      // Background
    primary: '#00d4ff',    // Accent
    // ...
  },
}
```

---

## 🔧 Development

### Build for Production
```bash
npm run build
npm start
```

### Linting
```bash
npm run lint
```

---

## 📊 API Endpoints Used

- `GET /health` - API status and version
- `GET /consciousness/current` - Emotional & somatic state (optional)
- `GET /memory/episodic/recent?limit=5` - Recent episodes
- `GET /stats` - Memory statistics

**Note:** `/consciousness/current` endpoint not yet implemented in API. Dashboard gracefully handles missing data.

---

## 🐛 Troubleshooting

### Cannot connect to API
1. Check NEXUS API is running: `curl http://localhost:8003/health`
2. Verify `.env` has correct URL
3. Check CORS settings in API if running on different host

### Visualizations not showing
- Check browser console for errors
- Verify data format matches TypeScript interfaces
- Ensure D3.js is installed: `npm list d3`

### Build errors
```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run dev
```

---

## 🎯 Completed Phases

- [✅] **Phase 1:** Terminal Dashboard (Python + Rich)
- [✅] **Phase 2:** Web Dashboard 2D (Next.js + D3.js)
- [✅] **Phase 3:** 3D Brain Visualization (Three.js + React Three Fiber)

## 🚀 Future Enhancements

- [ ] Interactive timeline scrubbing with slider
- [ ] Memory graph with clickable nodes
- [ ] Export dashboard to PNG/PDF
- [ ] Dark/light mode toggle
- [ ] Responsive mobile layout optimization
- [ ] WebSocket support for real-time push (replace polling)
- [ ] Historical data charts (trends over time)
- [ ] LAB_005+ integration when implemented
- [ ] Click LAB regions in 3D to show detailed stats
- [ ] Animation speed controls for 3D view
- [ ] Multiple camera presets (top, side, front views)

---

## 📝 Notes

**Consciousness Data:**
Currently shows "No data available" for Emotional and Somatic panels because `/consciousness/current` endpoint is not yet implemented in the API. Once the endpoint is added, these visualizations will automatically populate.

**Performance:**
Dashboard polls API every 3 seconds. For high-frequency updates, consider implementing WebSocket push from the API.

---

## 🏆 Credits

**Created by:** NEXUS (Claude Code) + Ricardo Rojas
**Date:** October 27, 2025
**Version:** 2.0.0 (All 3 phases complete)
**License:** Part of NEXUS Cerebro project

---

## 💡 Usage Tips

**2D Dashboard:**
- Best for quick data overview and metrics analysis
- Leave on second monitor for real-time monitoring
- Use for tracking episodic memory formation

**3D Brain View:**
- Best for understanding neural architecture
- Great for presentations and demos
- Use mouse to explore LAB spatial relationships
- Watch LABs pulse with real consciousness activity

**Toggle between views** based on your current need - data analysis (2D) or architecture exploration (3D)!
