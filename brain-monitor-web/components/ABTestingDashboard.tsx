'use client';

import React, { useState, useEffect } from 'react';

interface ABTestMetrics {
  variant: string;
  sample_count: number;
  avg_retrieval_time_ms: number;
  p50_retrieval_time_ms: number;
  p95_retrieval_time_ms: number;
  cache_hit_rate: number;
  avg_context_coherence: number;
  avg_primed_count: number;
  total_duration_seconds: number;
}

interface ABTestComparison {
  control: ABTestMetrics;
  treatment: ABTestMetrics;
  improvements: {
    latency_reduction_percent: number;
    cache_hit_rate_increase_percent: number;
    coherence_increase_percent: number;
    avg_primed_episodes: number;
  };
  statistical_significance: {
    sample_size_adequate: boolean;
    control_samples: number;
    treatment_samples: number;
    latency_effect_size: number;
    confidence_level: string;
  };
  recommendation: string;
}

export default function ABTestingDashboard() {
  const [comparison, setComparison] = useState<ABTestComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoursBack, setHoursBack] = useState(24);

  useEffect(() => {
    fetchComparison();
    const interval = setInterval(fetchComparison, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [hoursBack]);

  const fetchComparison = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8003/ab-test/compare?hours_back=${hoursBack}`);
      const data = await response.json();

      if (data.success && data.control && data.treatment) {
        setComparison(data);
        setError(null);
      } else if (data.error) {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to fetch A/B test comparison');
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes('✅ STRONG POSITIVE')) return 'text-green-400';
    if (recommendation.includes('✅ POSITIVE')) return 'text-green-300';
    if (recommendation.includes('⚠️')) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceColor = (level: string) => {
    if (level === 'high') return 'text-green-400';
    if (level === 'medium') return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
  };

  const formatMs = (value: number) => {
    return `${value.toFixed(1)}ms`;
  };

  if (loading && !comparison) {
    return (
      <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-gray-400">Loading A/B test data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
          <span className="text-purple-400">🧪</span>
          A/B Testing Dashboard
        </h2>
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
          <p className="text-yellow-300 text-sm">
            {error}
          </p>
          <p className="text-gray-400 text-xs mt-2">
            Collect data by recording metrics for both 'control' and 'treatment' variants.
          </p>
        </div>
      </div>
    );
  }

  if (!comparison) {
    return null;
  }

  const { control, treatment, improvements, statistical_significance, recommendation } = comparison;

  return (
    <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-100 flex items-center gap-2">
          <span className="text-purple-400">🧪</span>
          A/B Testing: LAB_005 Performance
        </h2>
        <select
          value={hoursBack}
          onChange={(e) => setHoursBack(Number(e.target.value))}
          className="bg-nexus-dark border border-nexus-primary/30 rounded px-3 py-1 text-sm text-gray-300"
        >
          <option value={1}>Last 1 hour</option>
          <option value={6}>Last 6 hours</option>
          <option value={24}>Last 24 hours</option>
          <option value={72}>Last 3 days</option>
          <option value={168}>Last week</option>
        </select>
      </div>

      {/* Recommendation Banner */}
      <div className="bg-gray-800/50 border-2 border-purple-500/30 rounded-lg p-4 mb-6">
        <div className="flex items-start gap-3">
          <div className="text-3xl">📊</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-100 mb-1">Test Recommendation</h3>
            <p className={`text-lg font-mono ${getRecommendationColor(recommendation)}`}>
              {recommendation}
            </p>
            <div className="mt-2 flex items-center gap-4 text-sm">
              <span className="text-gray-400">
                Confidence: <span className={getConfidenceColor(statistical_significance.confidence_level)}>
                  {statistical_significance.confidence_level.toUpperCase()}
                </span>
              </span>
              <span className="text-gray-400">
                Samples: {statistical_significance.control_samples + statistical_significance.treatment_samples}
              </span>
              <span className="text-gray-400">
                Effect Size: {statistical_significance.latency_effect_size.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Improvements */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
          <div className="text-blue-400 text-sm mb-1">Latency Reduction</div>
          <div className="text-2xl font-bold text-white">
            {formatPercent(improvements.latency_reduction_percent)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {formatMs(control.avg_retrieval_time_ms)} → {formatMs(treatment.avg_retrieval_time_ms)}
          </div>
        </div>

        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
          <div className="text-green-400 text-sm mb-1">Cache Hit Rate</div>
          <div className="text-2xl font-bold text-white">
            {formatPercent(improvements.cache_hit_rate_increase_percent)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {(control.cache_hit_rate * 100).toFixed(1)}% → {(treatment.cache_hit_rate * 100).toFixed(1)}%
          </div>
        </div>

        <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
          <div className="text-purple-400 text-sm mb-1">Context Coherence</div>
          <div className="text-2xl font-bold text-white">
            {formatPercent(improvements.coherence_increase_percent)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {control.avg_context_coherence.toFixed(2)} → {treatment.avg_context_coherence.toFixed(2)}
          </div>
        </div>

        <div className="bg-pink-500/10 border border-pink-500/30 rounded-lg p-4">
          <div className="text-pink-400 text-sm mb-1">Primed Episodes</div>
          <div className="text-2xl font-bold text-white">
            {improvements.avg_primed_episodes.toFixed(1)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Avg per access
          </div>
        </div>
      </div>

      {/* Detailed Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Control Variant */}
        <div className="bg-gray-800/30 rounded-lg border border-gray-600/30 p-4">
          <h3 className="font-semibold text-gray-100 mb-3 flex items-center gap-2">
            <span className="text-gray-400">📊</span>
            Control (Without LAB_005)
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Samples:</span>
              <span className="text-white font-mono">{control.sample_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Latency:</span>
              <span className="text-white font-mono">{formatMs(control.avg_retrieval_time_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">P50 Latency:</span>
              <span className="text-white font-mono">{formatMs(control.p50_retrieval_time_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">P95 Latency:</span>
              <span className="text-white font-mono">{formatMs(control.p95_retrieval_time_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Cache Hit Rate:</span>
              <span className="text-white font-mono">{(control.cache_hit_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Context Coherence:</span>
              <span className="text-white font-mono">{control.avg_context_coherence.toFixed(3)}</span>
            </div>
          </div>
        </div>

        {/* Treatment Variant */}
        <div className="bg-purple-500/10 rounded-lg border border-purple-500/30 p-4">
          <h3 className="font-semibold text-gray-100 mb-3 flex items-center gap-2">
            <span className="text-purple-400">⚡</span>
            Treatment (With LAB_005)
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Samples:</span>
              <span className="text-white font-mono">{treatment.sample_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Latency:</span>
              <span className="text-green-400 font-mono">{formatMs(treatment.avg_retrieval_time_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">P50 Latency:</span>
              <span className="text-green-400 font-mono">{formatMs(treatment.p50_retrieval_time_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">P95 Latency:</span>
              <span className="text-green-400 font-mono">{formatMs(treatment.p95_retrieval_time_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Cache Hit Rate:</span>
              <span className="text-green-400 font-mono">{(treatment.cache_hit_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Context Coherence:</span>
              <span className="text-green-400 font-mono">{treatment.avg_context_coherence.toFixed(3)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Primed:</span>
              <span className="text-purple-400 font-mono">{treatment.avg_primed_count.toFixed(1)} episodes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Statistical Info */}
      <div className="mt-4 bg-gray-800/30 rounded-lg border border-gray-600/30 p-3">
        <div className="text-xs text-gray-400">
          <span className="font-semibold text-gray-300">Statistical Significance:</span>
          {' '}
          {statistical_significance.sample_size_adequate ? (
            <span className="text-green-400">✓ Sample size adequate for reliable results</span>
          ) : (
            <span className="text-yellow-400">⚠ More data needed for statistical significance</span>
          )}
        </div>
      </div>
    </div>
  );
}
