'use client';

import { useState } from 'react';
import { useNexusData } from '@/hooks/useNexusData';
import Header from '@/components/Header';
import EmotionalRadar from '@/components/EmotionalRadar';
import SomaticBars from '@/components/SomaticBars';
import LABStatus from '@/components/LABStatus';
import EpisodesTimeline from '@/components/EpisodesTimeline';
import StatsPanel from '@/components/StatsPanel';
import BrainModel3D from '@/components/BrainModel3D';

type ViewMode = '2d' | '3d';

export default function Home() {
  const nexusData = useNexusData();
  const [viewMode, setViewMode] = useState<ViewMode>('2d');

  return (
    <main className="min-h-screen bg-nexus-dark">
      <Header
        isConnected={nexusData.isConnected}
        lastUpdate={nexusData.lastUpdate}
        agentId={nexusData.health?.agent_id}
        version={nexusData.health?.version}
      />

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* View Mode Toggle */}
        <div className="flex justify-center gap-4">
          <button
            onClick={() => setViewMode('2d')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              viewMode === '2d'
                ? 'bg-nexus-primary text-nexus-dark shadow-lg shadow-nexus-primary/50'
                : 'bg-nexus-darker text-nexus-gray hover:bg-nexus-darker/80 border border-nexus-primary/20'
            }`}
          >
            📊 Dashboard 2D
          </button>
          <button
            onClick={() => setViewMode('3d')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              viewMode === '3d'
                ? 'bg-nexus-primary text-nexus-dark shadow-lg shadow-nexus-primary/50'
                : 'bg-nexus-darker text-nexus-gray hover:bg-nexus-darker/80 border border-nexus-primary/20'
            }`}
          >
            🧠 Brain 3D
          </button>
        </div>

        {/* 2D Dashboard View */}
        {viewMode === '2d' && (
          <>
            {/* Row 1: Emotional + Somatic */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <EmotionalRadar data={nexusData.consciousness?.emotional || null} />
              <SomaticBars data={nexusData.consciousness?.somatic || null} />
            </div>

            {/* Row 2: LAB Status */}
            <LABStatus />

            {/* Row 3: Episodes + Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <EpisodesTimeline episodes={nexusData.episodes} />
              </div>
              <StatsPanel stats={nexusData.stats} />
            </div>
          </>
        )}

        {/* 3D Brain View */}
        {viewMode === '3d' && (
          <div className="space-y-6">
            {/* 3D Brain Visualization */}
            <BrainModel3D nexusData={nexusData} />

            {/* LAB Status (always visible in 3D view) */}
            <LABStatus />

            {/* Quick Stats Panel */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
                <h3 className="text-xl font-bold text-nexus-primary mb-4">🎯 3D Controls</h3>
                <ul className="text-nexus-gray space-y-2">
                  <li>🖱️ <strong>Left Click + Drag:</strong> Rotate view</li>
                  <li>🔍 <strong>Scroll:</strong> Zoom in/out</li>
                  <li>✋ <strong>Right Click + Drag:</strong> Pan camera</li>
                  <li>🔄 <strong>Brain auto-rotates</strong> slowly</li>
                  <li>💡 <strong>LABs pulse</strong> based on activity</li>
                </ul>
              </div>
              <StatsPanel stats={nexusData.stats} />
            </div>
          </div>
        )}

        {/* Error Message (if any) */}
        {nexusData.error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-center">
            <p className="text-red-300">⚠️ {nexusData.error}</p>
          </div>
        )}
      </div>
    </main>
  );
}
