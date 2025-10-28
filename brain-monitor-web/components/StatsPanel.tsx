'use client';

import React from 'react';
import { MemoryStats } from '@/lib/types';

interface StatsPanelProps {
  stats: MemoryStats | null;
}

export default function StatsPanel({ stats }: StatsPanelProps) {
  if (!stats) {
    return (
      <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">📊 Memory Statistics</h2>
        <p className="text-gray-400">No data available</p>
      </div>
    );
  }

  const completionPercentage =
    stats.total_episodes > 0
      ? Math.round((stats.episodes_with_embeddings / stats.total_episodes) * 100)
      : 0;

  return (
    <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-6 flex items-center gap-2">
        <span>📊</span>
        Memory Statistics
      </h2>

      <div className="space-y-4">
        {/* Total Episodes */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm text-gray-400">Total Episodes</span>
            <span className="text-2xl font-bold text-nexus-primary">
              {stats.total_episodes.toLocaleString()}
            </span>
          </div>
        </div>

        {/* With Embeddings */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">With Embeddings</span>
            <span className="text-lg font-semibold text-gray-100">
              {stats.episodes_with_embeddings.toLocaleString()}
              <span className="text-sm text-gray-400 ml-2">({completionPercentage}%)</span>
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>

        {/* Queue Status */}
        <div className="border-t border-gray-700 pt-4 mt-4">
          <div className="text-sm text-gray-400 mb-2">Embeddings Queue</div>
          <div className="grid grid-cols-2 gap-2">
            {stats.embeddings_queue.done !== undefined && (
              <div className="bg-green-500/10 border border-green-500/30 rounded px-3 py-2">
                <div className="text-xs text-green-400">Done</div>
                <div className="text-lg font-semibold text-green-300">
                  {stats.embeddings_queue.done}
                </div>
              </div>
            )}
            {(stats.embeddings_queue.pending ?? 0) > 0 && (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded px-3 py-2">
                <div className="text-xs text-yellow-400">Pending</div>
                <div className="text-lg font-semibold text-yellow-300">
                  {stats.embeddings_queue.pending}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
