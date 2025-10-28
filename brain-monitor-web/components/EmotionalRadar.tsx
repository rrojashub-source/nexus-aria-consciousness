'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Emotional8D } from '@/lib/types';

interface EmotionalRadarProps {
  data: Emotional8D | null;
}

export default function EmotionalRadar({ data }: EmotionalRadarProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous render

    const width = 400;
    const height = 400;
    const radius = Math.min(width, height) / 2 - 40;
    const centerX = width / 2;
    const centerY = height / 2;

    const emotions = [
      { name: 'Joy', value: data.joy, color: '#fbbf24' },
      { name: 'Trust', value: data.trust, color: '#34d399' },
      { name: 'Fear', value: data.fear, color: '#f87171' },
      { name: 'Surprise', value: data.surprise, color: '#a78bfa' },
      { name: 'Sadness', value: data.sadness, color: '#60a5fa' },
      { name: 'Disgust', value: data.disgust, color: '#fb923c' },
      { name: 'Anger', value: data.anger, color: '#ef4444' },
      { name: 'Anticipation', value: data.anticipation, color: '#10b981' },
    ];

    const angleSlice = (Math.PI * 2) / emotions.length;

    // Create main group
    const g = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${centerX}, ${centerY})`);

    // Draw circular grid lines
    const levels = 5;
    for (let i = 1; i <= levels; i++) {
      const levelRadius = (radius / levels) * i;

      g.append('circle')
        .attr('r', levelRadius)
        .attr('fill', 'none')
        .attr('stroke', '#374151')
        .attr('stroke-width', 1)
        .attr('opacity', 0.3);

      // Add level labels
      if (i === levels) {
        g.append('text')
          .attr('x', 5)
          .attr('y', -levelRadius)
          .attr('fill', '#9ca3af')
          .attr('font-size', '10px')
          .text('1.0');
      }
    }

    // Draw axis lines
    emotions.forEach((emotion, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;

      // Axis line
      g.append('line')
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', x)
        .attr('y2', y)
        .attr('stroke', '#4b5563')
        .attr('stroke-width', 1)
        .attr('opacity', 0.5);

      // Axis labels
      const labelRadius = radius + 25;
      const labelX = Math.cos(angle) * labelRadius;
      const labelY = Math.sin(angle) * labelRadius;

      g.append('text')
        .attr('x', labelX)
        .attr('y', labelY)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('fill', emotion.color)
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(emotion.name);
    });

    // Draw data polygon
    const dataPoints = emotions.map((emotion, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const r = emotion.value * radius;
      return {
        x: Math.cos(angle) * r,
        y: Math.sin(angle) * r,
        emotion,
      };
    });

    // Create path
    const line = d3
      .line<typeof dataPoints[0]>()
      .x((d) => d.x)
      .y((d) => d.y)
      .curve(d3.curveLinearClosed);

    g.append('path')
      .datum(dataPoints)
      .attr('d', line)
      .attr('fill', '#00d4ff')
      .attr('fill-opacity', 0.2)
      .attr('stroke', '#00d4ff')
      .attr('stroke-width', 2);

    // Draw data points
    dataPoints.forEach((point) => {
      g.append('circle')
        .attr('cx', point.x)
        .attr('cy', point.y)
        .attr('r', 4)
        .attr('fill', point.emotion.color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .append('title')
        .text(`${point.emotion.name}: ${point.emotion.value.toFixed(2)}`);
    });
  }, [data]);

  if (!data) {
    return (
      <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">😊 Emotional State (8D)</h2>
        <div className="flex items-center justify-center h-64 text-gray-400">
          No consciousness data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-nexus-darker rounded-lg border border-nexus-primary/20 p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
        <span>😊</span>
        Emotional State (8D) - Plutchik Model
      </h2>
      <div className="flex justify-center">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
}
