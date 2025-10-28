'use client';

import React from 'react';

interface HeaderProps {
  isConnected: boolean;
  lastUpdate: Date | null;
  agentId?: string;
  version?: string;
}

export default function Header({ isConnected, lastUpdate, agentId, version }: HeaderProps) {
  const getTimeSinceUpdate = () => {
    if (!lastUpdate) return 'Never';
    const seconds = Math.floor((Date.now() - lastUpdate.getTime()) / 1000);
    if (seconds < 5) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    return `${Math.floor(seconds / 60)}m ago`;
  };

  return (
    <header className="bg-nexus-darker border-b border-nexus-primary/20 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-nexus-primary flex items-center gap-2">
            <span className="text-3xl">🧠</span>
            NEXUS Brain Monitor
          </h1>
          <span className="text-sm text-gray-400">Web Dashboard</span>
        </div>

        <div className="flex items-center gap-6">
          {/* Connection Status */}
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-300">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Agent Info */}
          {agentId && (
            <div className="text-sm text-gray-400">
              <span className="font-semibold text-gray-300">{agentId}</span>
              {version && <span className="ml-2">v{version}</span>}
            </div>
          )}

          {/* Last Update */}
          <div className="text-sm text-gray-400">
            Last update: <span className="text-gray-300">{getTimeSinceUpdate()}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
