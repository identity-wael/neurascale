'use client';

import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function RotatingCube() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.5;
    }
  });

  return (
    <mesh ref={meshRef as any}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#00ff88" />
    </mesh>
  );
}

export default function SimpleTest3D() {
  return (
    <div className="absolute inset-0 w-full h-full" style={{ minHeight: '100vh', width: '100%' }}>
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-50 text-yellow-400 text-sm">
        Simple 3D Test - Rotating Cube
      </div>

      <Canvas style={{ width: '100%', height: '100%' }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <RotatingCube />
      </Canvas>
    </div>
  );
}
