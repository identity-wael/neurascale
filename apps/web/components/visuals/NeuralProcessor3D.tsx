'use client'

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text } from '@react-three/drei'
import * as THREE from 'three'

function GPUDie() {
  const groupRef = useRef<THREE.Group>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  return (
    <group 
      ref={groupRef}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {/* Main GPU Substrate */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[8, 0.4, 6]} />
        <meshStandardMaterial 
          color="#404040"
          metalness={0.8}
          roughness={0.2}
          emissive="#0a0a0a"
          emissiveIntensity={0.1}
        />
      </mesh>

      {/* Central Processing Core */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[3.5, 0.3, 3.5]} />
        <meshStandardMaterial 
          color="#000000"
          metalness={0.95}
          roughness={0.05}
          emissive="#001100"
          emissiveIntensity={0.2}
        />
      </mesh>

      {/* Glowing Center Die */}
      <mesh position={[0, 0.5, 0]}>
        <boxGeometry args={[2.8, 0.15, 2.8]} />
        <meshStandardMaterial 
          color="#00ff88"
          emissive="#00ff88"
          emissiveIntensity={hovered ? 2 : 1.5}
          metalness={0.3}
          roughness={0}
        />
      </mesh>

      {/* GPU Cores Grid (8x8) */}
      {Array.from({ length: 8 }).map((_, row) =>
        Array.from({ length: 8 }).map((_, col) => (
          <mesh 
            key={`core-${row}-${col}`}
            position={[
              (col - 3.5) * 0.32,
              0.55,
              (row - 3.5) * 0.22
            ]}
          >
            <boxGeometry args={[0.18, 0.08, 0.12]} />
            <meshStandardMaterial 
              color="#4185f4"
              emissive="#4185f4"
              emissiveIntensity={0.3}
              metalness={0.6}
              roughness={0.3}
            />
          </mesh>
        ))
      )}

      {/* HBM Memory Modules */}
      {Array.from({ length: 6 }).map((_, i) => (
        <mesh 
          key={`hbm-${i}`}
          position={[
            (i % 3 - 1) * 2,
            0.5,
            i < 3 ? -2 : 2
          ]}
        >
          <boxGeometry args={[0.5, 0.6, 0.5]} />
          <meshStandardMaterial 
            color="#0066ff"
            emissive="#0066ff"
            emissiveIntensity={0.3}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      ))}

      {/* Connection Pins */}
      {[
        [-3.2, 0.15, -2.2],
        [3.2, 0.15, -2.2],
        [-3.2, 0.15, 2.2],
        [3.2, 0.15, 2.2]
      ].map((pos, i) => (
        <mesh key={`pin-${i}`} position={pos as [number, number, number]}>
          <sphereGeometry args={[0.09, 16, 16]} />
          <meshStandardMaterial 
            color="#ffd700"
            emissive="#ffd700"
            emissiveIntensity={0.4}
            metalness={0.9}
            roughness={0.1}
          />
        </mesh>
      ))}

      {/* NEURASCALE Logo */}
      <Text
        position={[0, 0.22, -2.2]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.3}
        color="#4185f4"
        anchorX="center"
        anchorY="middle"
      >
        NEURASCALE
      </Text>
    </group>
  )
}

export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
      <Canvas shadows camera={{ position: [0, 5, 10], fov: 60 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        <pointLight position={[0, 5, 0]} intensity={0.8} color="#00ff88" />
        
        <GPUDie />
        
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          maxDistance={20}
          minDistance={3}
        />
      </Canvas>
    </div>
  )
}