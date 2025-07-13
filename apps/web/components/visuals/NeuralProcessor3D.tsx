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
      position={[0, 0, 0]}
    >
      
      {/* Base PCB - made larger and more visible */}
      <mesh ref={meshRef as any} position={[0, 0, 0]}>
        <boxGeometry args={[4, 0.2, 4]} />
        <meshStandardMaterial 
          color="#333333"
          metalness={0.5}
          roughness={0.5}
          emissive="#111111"
          emissiveIntensity={0.1}
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

      {/* Central processor with glow - made larger */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[3, 0.2, 3]} />
        <meshStandardMaterial 
          color="#000000"
          metalness={0.95}
          roughness={0.1}
          emissive="#001100"
          emissiveIntensity={0.2}
        />
      </mesh>

      {/* Glowing green core - made larger and brighter */}
      <mesh ref={glowRef as any} position={[0, 0.4, 0]}>
        <boxGeometry args={[2.5, 0.2, 2.5]} />
        <meshStandardMaterial 
          color="#00ff88"
          emissive="#00ff88"
          emissiveIntensity={1.5}
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
      
      {/* Neural network nodes floating around */}
      {Array.from({ length: 12 }).map((_, i) => (
        <mesh 
          key={`node-${i}`} 
          position={[
            Math.cos(i * 0.52) * 6,
            Math.sin(i * 0.3) * 2 + 1,
            Math.sin(i * 0.52) * 6
          ]}
        >
          <sphereGeometry args={[0.1, 8, 8]} />
          <meshStandardMaterial 
            color="#00aaff" 
            emissive="#00aaff" 
            emissiveIntensity={0.6}
          />
        </mesh>
      ))}
      
      {/* Data connections */}
      {Array.from({ length: 6 }).map((_, i) => (
        <mesh 
          key={`connection-${i}`} 
          position={[
            Math.cos(i * 1.05) * 3.5,
            0.8,
            Math.sin(i * 1.05) * 3.5
          ]}
          rotation={[0, i * 1.05, 0]}
        >
          <cylinderGeometry args={[0.02, 0.02, 2, 8]} />
          <meshStandardMaterial 
            color="#0088ff" 
            emissive="#0088ff" 
            emissiveIntensity={0.3}
            transparent
            opacity={0.7}
          />
        </mesh>
      ))}
    </group>
  )
}

function CircuitLines() {
  const linesRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (linesRef.current) {
      linesRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })

  return (
    <group ref={linesRef as any} position={[0, -1, 0]}>
      {/* Animated circuit rings */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[4, 6, 8, 1]} />
        <meshBasicMaterial color="#00ff88" opacity={0.4} transparent />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[6, 8, 12, 1]} />
        <meshBasicMaterial color="#0066ff" opacity={0.3} transparent />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[8, 10, 16, 1]} />
        <meshBasicMaterial color="#004488" opacity={0.2} transparent />
      </mesh>
      
      {/* Data flow particles */}
      {Array.from({ length: 20 }).map((_, i) => (
        <mesh 
          key={i} 
          position={[
            Math.cos(i * 0.314) * (4 + i * 0.3),
            0.1,
            Math.sin(i * 0.314) * (4 + i * 0.3)
          ]}
        >
          <sphereGeometry args={[0.05, 8, 8]} />
          <meshStandardMaterial 
            color="#00ffaa" 
            emissive="#00ffaa" 
            emissiveIntensity={0.8}
          />
        </mesh>
      ))}
    </group>
  )
}

export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full" style={{ minHeight: '100vh', width: '100%', zIndex: 1 }}>
      
      <Canvas
        style={{ width: '100%', height: '100%', display: 'block' }}
        camera={{ position: [0, 2, 8], fov: 60 }}
        gl={{ 
          antialias: true, 
          alpha: true,
          preserveDrawingBuffer: true
        }}
      >
        <ambientLight intensity={1} />
        <pointLight position={[5, 5, 5]} intensity={2} />
        <pointLight position={[-5, 5, 5]} intensity={1} />
        <pointLight position={[0, 0, 8]} intensity={1} color="#00ff88" />
        
        
        <ProcessorChip />
        <CircuitLines />
      </Canvas>
    </div>
  )
}