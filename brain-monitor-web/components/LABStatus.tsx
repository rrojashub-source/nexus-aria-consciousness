'use client';

import React from 'react';
import { LABStatus as LABStatusType } from '@/lib/types';

const LABS: LABStatusType[] = [
  {
    id: 'LAB_001',
    name: 'Emotional Salience',
    status: 'active',
    description: 'Memory formation quality based on emotions',
  },
  {
    id: 'LAB_002',
    name: 'Decay Modulation',
    status: 'active',
    description: 'Intelligent memory decay protection',
  },
  {
    id: 'LAB_003',
    name: 'Sleep Consolidation',
    status: 'active',
    description: 'Offline memory strengthening',
  },
  {
    id: 'LAB_004',
    name: 'Novelty Detection',
    status: 'active',
    description: '4D surprise and curiosity bonus',
  },
];

export default function LABStatusComponent() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'border-green-500/50 bg-green-500/10';
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/10';
      case 'inactive':
        return 'border-red-500/50 bg-red-500/10';
      default:
        return 'border-gray-500/50 bg-gray-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'inactive':
        return '❌';
      default:
        return '⚪';
    }
  };

  return (
    <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
        <span className="text-green-400">🔬</span>
        LAB Systems Status
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {LABS.map((lab) => (
          <div
            key={lab.id}
            className={`rounded-lg border-2 p-4 transition-all hover:scale-105 ${getStatusColor(lab.status)}`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-sm text-gray-400">{lab.id}</span>
              <span className="text-2xl">{getStatusIcon(lab.status)}</span>
            </div>
            <h3 className="font-semibold text-gray-100 mb-1">{lab.name}</h3>
            <p className="text-xs text-gray-400">{lab.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
