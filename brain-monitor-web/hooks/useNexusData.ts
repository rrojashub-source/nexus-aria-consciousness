// Custom React Hook for NEXUS Data Polling

'use client';

import { useState, useEffect, useCallback } from 'react';
import { nexusAPI } from '@/lib/nexusAPI';
import { NexusData } from '@/lib/types';

const REFRESH_INTERVAL = 3000; // 3 seconds

export function useNexusData() {
  const [data, setData] = useState<NexusData>({
    health: null,
    consciousness: null,
    episodes: [],
    stats: null,
    isConnected: false,
    lastUpdate: null,
    error: null,
  });

  const fetchAllData = useCallback(async () => {
    try {
      // Fetch all data in parallel
      const [health, consciousness, episodesResponse, statsResponse] = await Promise.allSettled([
        nexusAPI.getHealth(),
        nexusAPI.getConsciousness(),
        nexusAPI.getRecentEpisodes(5),
        nexusAPI.getStats(),
      ]);

      setData({
        health: health.status === 'fulfilled' ? health.value : null,
        consciousness: consciousness.status === 'fulfilled' ? consciousness.value : null,
        episodes: episodesResponse.status === 'fulfilled' ? episodesResponse.value.episodes : [],
        stats: statsResponse.status === 'fulfilled' ? statsResponse.value.stats : null,
        isConnected: health.status === 'fulfilled',
        lastUpdate: new Date(),
        error: null,
      });
    } catch (error) {
      setData(prev => ({
        ...prev,
        isConnected: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchAllData();

    // Set up polling interval
    const intervalId = setInterval(fetchAllData, REFRESH_INTERVAL);

    // Cleanup
    return () => clearInterval(intervalId);
  }, [fetchAllData]);

  return data;
}
