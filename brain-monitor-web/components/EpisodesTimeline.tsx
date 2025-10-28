'use client';

import React from 'react';
import { Episode } from '@/lib/types';

interface EpisodesTimelineProps {
  episodes: Episode[];
}

export default function EpisodesTimeline({ episodes }: EpisodesTimelineProps) {
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return 'Unknown';
    }
  };

  const getImportanceColor = (score: number) => {
    if (score > 0.7) return 'border-green-500/50 bg-green-500/10';
    if (score > 0.4) return 'border-yellow-500/50 bg-yellow-500/10';
    return 'border-red-500/50 bg-red-500/10';
  };

  const getImportanceBadgeColor = (score: number) => {
    if (score > 0.7) return 'bg-green-500 text-green-50';
    if (score > 0.4) return 'bg-yellow-500 text-yellow-50';
    return 'bg-red-500 text-red-50';
  };

  if (episodes.length === 0) {
    return (
      <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">📅 Recent Episodes</h2>
        <p className="text-gray-400">No episodes available</p>
      </div>
    );
  }

  return (
    <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
        <span>📅</span>
        Recent Episodes
      </h2>

      <div className="space-y-3">
        {episodes.map((episode, index) => (
          <div
            key={episode.episode_id}
            className={`rounded-lg border-2 p-4 transition-all hover:scale-102 ${getImportanceColor(episode.importance_score)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-gray-400">{formatTime(episode.created_at)}</span>
                {episode.has_embedding && (
                  <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">
                    📊 Embedded
                  </span>
                )}
              </div>
              <span className={`text-xs font-semibold px-2 py-1 rounded ${getImportanceBadgeColor(episode.importance_score)}`}>
                {episode.importance_score.toFixed(2)}
              </span>
            </div>

            <p className="text-sm text-gray-200 mb-2">
              {episode.content.length > 100
                ? `${episode.content.substring(0, 100)}...`
                : episode.content}
            </p>

            {episode.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {episode.tags.map((tag, tagIndex) => (
                  <span
                    key={tagIndex}
                    className="text-xs bg-nexus-primary/20 text-nexus-primary px-2 py-0.5 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
