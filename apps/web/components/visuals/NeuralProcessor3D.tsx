'use client'

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'

function ProcessorChip() {
  const meshRef = useRef<THREE.Mesh>(null)
  const glowRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.2
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.1
    }
    if (glowRef.current && glowRef.current.material) {
      const material = glowRef.current.material as THREE.MeshStandardMaterial
      material.emissiveIntensity = 0.5 + Math.sin(state.clock.elapsedTime * 2) * 0.3
    }
  })

  return (
    <group
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {/* Base PCB */}
      <mesh ref={meshRef as any} castShadow receiveShadow>
        <boxGeometry args={[4, 0.15, 4]} />
        <meshStandardMaterial 
          color="#0a0a0a"
          metalness={0.9}
          roughness={0.2}
        />
      </mesh>

      {/* PCB Surface Details */}
      <mesh position={[0, 0.08, 0]}>
        <planeGeometry args={[3.8, 3.8]} />
        <meshStandardMaterial 
          color="#111111"
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* Central processor with glow */}
      <mesh position={[0, 0.15, 0]}>
        <boxGeometry args={[1.5, 0.1, 1.5]} />
        <meshStandardMaterial 
          color="#000000"
          metalness={0.95}
          roughness={0.1}
        />
      </mesh>

      {/* Glowing green core */}
      <mesh ref={glowRef as any} position={[0, 0.2, 0]}>
        <boxGeometry args={[1.2, 0.05, 1.2]} />
        <meshStandardMaterial 
          color="#00ff88"
          emissive="#00ff88"
          emissiveIntensity={hovered ? 1 : 0.5}
          metalness={0.5}
          roughness={0}
        />
      </mesh>

      {/* Core details */}
      <mesh position={[0, 0.25, 0]}>
        <boxGeometry args={[0.8, 0.02, 0.8]} />
        <meshStandardMaterial 
          color="#00ff88"
          emissive="#00ff88"
          emissiveIntensity={0.8}
        />
      </mesh>

      {/* Connection pins - simplified */}
      {Array.from({ length: 8 }).map((_, i) => (
        <mesh key={`pin-${i}`} position={[2.1, -0.05, -1.2 + i * 0.3]}>
          <boxGeometry args={[0.2, 0.05, 0.08]} />
          <meshStandardMaterial color="#ffd700" metalness={0.8} roughness={0.2} />
        </mesh>
      ))}
    </group>
  )
}

function CircuitLines() {
  return (
    <group position={[0, -2, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[3, 8, 6, 1]} />
        <meshBasicMaterial color="#003366" opacity={0.3} transparent />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[5, 6, 6, 1]} />
        <meshBasicMaterial color="#003366" opacity={0.2} transparent />
      </mesh>
    </group>
  )
}

export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full" style={{ minHeight: '100vh', width: '100%' }}>
      {/* Debug indicator */}
      <div className="absolute top-4 left-4 z-50 text-green-400 text-xs">Neural Processor Loading...</div>
      
      <Canvas
        shadows
        style={{ width: '100%', height: '100%' }}
        gl={{ 
          antialias: true, 
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.5
        }}
      >
        <PerspectiveCamera makeDefault position={[5, 4, 5]} fov={45} />
        
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={0.5} castShadow />
        <pointLight position={[-10, 10, -10]} intensity={0.3} />
        <pointLight position={[0, 5, 0]} intensity={0.5} color="#00ff88" />
        
        <ProcessorChip />
        <CircuitLines />
      </Canvas>
    </div>
  )
}