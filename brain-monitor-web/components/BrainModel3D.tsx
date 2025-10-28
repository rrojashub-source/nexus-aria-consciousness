'use client';

import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { NexusData } from '@/lib/types';

interface BrainModel3DProps {
  nexusData: NexusData;
}

export default function BrainModel3D({ nexusData }: BrainModel3DProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const labMeshesRef = useRef<{ [key: string]: THREE.Mesh }>({});
  const animationIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / 800,
      0.1,
      1000
    );
    camera.position.z = 12;
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(containerRef.current.clientWidth, 800);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0xffffff, 1);
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x00d4ff, 0.5);
    pointLight2.position.set(-10, -10, -10);
    scene.add(pointLight2);

    // Central brain structure (wireframe sphere)
    const brainGeometry = new THREE.SphereGeometry(2, 64, 64);
    const brainMaterial = new THREE.MeshBasicMaterial({
      color: 0x1e293b,
      wireframe: true,
      transparent: true,
      opacity: 0.1,
    });
    const brainMesh = new THREE.Mesh(brainGeometry, brainMaterial);
    scene.add(brainMesh);

    // LAB regions configuration
    const labsConfig = [
      { id: 'LAB_001', position: [3, 1.5, 0], color: 0xfbbf24, name: 'Emotional Salience' },
      { id: 'LAB_002', position: [-3, 1.5, 0], color: 0x34d399, name: 'Decay Modulation' },
      { id: 'LAB_003', position: [0, -1.5, 2], color: 0xa78bfa, name: 'Sleep Consolidation' },
      { id: 'LAB_004', position: [0, 1.5, -2], color: 0xf97316, name: 'Novelty Detection' },
    ];

    // Create LAB spheres
    labsConfig.forEach((lab) => {
      const geometry = new THREE.SphereGeometry(0.8, 32, 32);
      const material = new THREE.MeshStandardMaterial({
        color: lab.color,
        emissive: lab.color,
        emissiveIntensity: 0.3,
        transparent: true,
        opacity: 0.7,
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(lab.position[0], lab.position[1], lab.position[2]);
      scene.add(mesh);
      labMeshesRef.current[lab.id] = mesh;

      // Outer glow
      const glowGeometry = new THREE.SphereGeometry(1.0, 32, 32);
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: lab.color,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide,
      });
      const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
      glowMesh.position.set(lab.position[0], lab.position[1], lab.position[2]);
      scene.add(glowMesh);

      // Label (using sprite instead of text for simplicity)
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = 256;
      canvas.height = 64;
      if (context) {
        context.fillStyle = '#ffffff';
        context.font = 'Bold 32px Arial';
        context.textAlign = 'center';
        context.fillText(lab.id, 128, 40);
      }
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.position.set(lab.position[0], lab.position[1] + 1.2, lab.position[2]);
      sprite.scale.set(2, 0.5, 1);
      scene.add(sprite);
    });

    // Neural connections
    const connections = [
      { from: [3, 1.5, 0], to: [-3, 1.5, 0] },
      { from: [3, 1.5, 0], to: [0, -1.5, 2] },
      { from: [3, 1.5, 0], to: [0, 1.5, -2] },
      { from: [0, -1.5, 2], to: [0, 1.5, -2] },
    ];

    connections.forEach((conn) => {
      const points = [
        new THREE.Vector3(conn.from[0], conn.from[1], conn.from[2]),
        new THREE.Vector3(conn.to[0], conn.to[1], conn.to[2]),
      ];
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const material = new THREE.LineBasicMaterial({
        color: 0x00d4ff,
        transparent: true,
        opacity: 0.2,
      });
      const line = new THREE.Line(geometry, material);
      scene.add(line);
    });

    // Background stars
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.1 });
    const starsVertices = [];
    for (let i = 0; i < 200; i++) {
      const x = (Math.random() - 0.5) * 50;
      const y = (Math.random() - 0.5) * 50;
      const z = (Math.random() - 0.5) * 50;
      starsVertices.push(x, y, z);
    }
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const stars = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(stars);

    // Mouse controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let rotation = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;
      rotation.y += deltaX * 0.005;
      rotation.x += deltaY * 0.005;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      camera.position.z += e.deltaY * 0.01;
      camera.position.z = Math.max(5, Math.min(20, camera.position.z));
    };

    renderer.domElement.addEventListener('mousedown', onMouseDown);
    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('mouseup', onMouseUp);
    renderer.domElement.addEventListener('wheel', onWheel);

    // Animation loop
    let time = 0;
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      time += 0.01;

      // Rotate brain group
      brainMesh.rotation.y = rotation.y + time * 0.1;
      brainMesh.rotation.x = rotation.x;

      // Animate LABs
      Object.values(labMeshesRef.current).forEach((mesh) => {
        const pulse = Math.sin(time * 2) * 0.1;
        mesh.scale.setScalar(1 + pulse * 0.3);
        mesh.rotation.y += 0.002;
      });

      renderer.render(scene, camera);
    };
    animate();

    // Cleanup
    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      renderer.domElement.removeEventListener('mousedown', onMouseDown);
      renderer.domElement.removeEventListener('mousemove', onMouseMove);
      renderer.domElement.removeEventListener('mouseup', onMouseUp);
      renderer.domElement.removeEventListener('wheel', onWheel);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Update LAB activities based on nexusData
  useEffect(() => {
    if (!nexusData.consciousness) return;

    const emotional = nexusData.consciousness.emotional;
    const somatic = nexusData.consciousness.somatic;

    const activities = {
      LAB_001: emotional
        ? (emotional.joy + emotional.trust + emotional.anticipation) / 3
        : 0.5,
      LAB_002: somatic ? somatic.emotional_regulation : 0.5,
      LAB_003: somatic ? (somatic.body_state + somatic.temporal_awareness) / 2 : 0.5,
      LAB_004: emotional ? (emotional.surprise + emotional.anticipation) / 2 : 0.5,
    };

    Object.entries(activities).forEach(([labId, activity]) => {
      const mesh = labMeshesRef.current[labId];
      if (mesh && mesh.material instanceof THREE.MeshStandardMaterial) {
        mesh.material.emissiveIntensity = activity * 0.5;
      }
    });
  }, [nexusData.consciousness]);

  return (
    <div className="w-full h-[800px] bg-nexus-darker rounded-lg border border-nexus-primary/20 overflow-hidden">
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
}
