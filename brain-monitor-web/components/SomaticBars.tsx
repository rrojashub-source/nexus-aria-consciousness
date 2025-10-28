'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Somatic7D } from '@/lib/types';

interface SomaticBarsProps {
  data: Somatic7D | null;
}

export default function SomaticBars({ data }: SomaticBarsProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 500;
    const height = 350;
    const margin = { top: 20, right: 80, bottom: 20, left: 150 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const dimensions = [
      { name: 'Valence', value: data.valence, range: [-1, 1] },
      { name: 'Arousal', value: data.arousal, range: [0, 1] },
      { name: 'Body State', value: data.body_state, range: [0, 1] },
      { name: 'Cognitive Load', value: data.cognitive_load, range: [0, 1] },
      { name: 'Emotional Regulation', value: data.emotional_regulation, range: [0, 1] },
      { name: 'Social Engagement', value: data.social_engagement, range: [0, 1] },
      { name: 'Temporal Awareness', value: data.temporal_awareness, range: [0, 1] },
    ];

    svg.attr('width', width).attr('height', height);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // Y scale (dimensions)
    const yScale = d3
      .scaleBand()
      .domain(dimensions.map((d) => d.name))
      .range([0, innerHeight])
      .padding(0.2);

    // X scale
    const xScale = d3.scaleLinear().domain([-1, 1]).range([0, innerWidth]);

    // Color scale
    const getColor = (value: number, isValence: boolean) => {
      if (isValence) {
        if (value > 0.3) return '#10b981'; // Green
        if (value > -0.3) return '#fbbf24'; // Yellow
        return '#ef4444'; // Red
      } else {
        if (value > 0.7) return '#10b981';
        if (value > 0.4) return '#fbbf24';
        return '#ef4444';
      }
    };

    // Draw axis
    g.append('line')
      .attr('x1', xScale(0))
      .attr('x2', xScale(0))
      .attr('y1', 0)
      .attr('y2', innerHeight)
      .attr('stroke', '#6b7280')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4,4');

    // Draw bars
    dimensions.forEach((dim) => {
      const isValence = dim.name === 'Valence';
      const barHeight = yScale.bandwidth();
      const y = yScale(dim.name)!;

      // Background bar
      g.append('rect')
        .attr('x', xScale(-1))
        .attr('y', y)
        .attr('width', innerWidth)
        .attr('height', barHeight)
        .attr('fill', '#1f2937')
        .attr('opacity', 0.3);

      // Value bar
      const barX = isValence && dim.value < 0 ? xScale(dim.value) : xScale(0);
      const barWidth = isValence
        ? Math.abs(xScale(dim.value) - xScale(0))
        : xScale(dim.value) - xScale(0);

      g.append('rect')
        .attr('x', barX)
        .attr('y', y)
        .attr('width', barWidth)
        .attr('height', barHeight)
        .attr('fill', getColor(dim.value, isValence))
        .attr('opacity', 0.7)
        .append('title')
        .text(`${dim.name}: ${dim.value.toFixed(2)}`);

      // Label
      g.append('text')
        .attr('x', -10)
        .attr('y', y + barHeight / 2)
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('fill', '#d1d5db')
        .attr('font-size', '14px')
        .text(dim.name);

      // Value label
      const valueX = isValence
        ? xScale(dim.value) + (dim.value > 0 ? 5 : -5)
        : xScale(dim.value) + 5;
      const valueAnchor = isValence && dim.value < 0 ? 'end' : 'start';

      g.append('text')
        .attr('x', valueX)
        .attr('y', y + barHeight / 2)
        .attr('text-anchor', valueAnchor)
        .attr('dominant-baseline', 'middle')
        .attr('fill', '#f3f4f6')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(isValence ? (dim.value >= 0 ? `+${dim.value.toFixed(2)}` : dim.value.toFixed(2)) : dim.value.toFixed(2));
    });

    // X axis labels
    g.append('text')
      .attr('x', xScale(-1))
      .attr('y', -5)
      .attr('text-anchor', 'start')
      .attr('fill', '#9ca3af')
      .attr('font-size', '10px')
      .text('-1.0');

    g.append('text')
      .attr('x', xScale(0))
      .attr('y', -5)
      .attr('text-anchor', 'middle')
      .attr('fill', '#9ca3af')
      .attr('font-size', '10px')
      .text('0.0');

    g.append('text')
      .attr('x', xScale(1))
      .attr('y', -5)
      .attr('text-anchor', 'end')
      .attr('fill', '#9ca3af')
      .attr('font-size', '10px')
      .text('+1.0');
  }, [data]);

  if (!data) {
    return (
      <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">🧘 Somatic State (7D)</h2>
        <div className="flex items-center justify-center h-64 text-gray-400">
          No consciousness data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
        <span>🧘</span>
        Somatic State (7D) - Damasio Model
      </h2>
      <div className="flex justify-center">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
}
