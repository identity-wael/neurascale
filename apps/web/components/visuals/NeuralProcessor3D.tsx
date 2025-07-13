'use client'

import { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame, useLoader, MeshProps } from '@react-three/fiber'
import { 
  Float, 
  Environment,
  ContactShadows,
  PerspectiveCamera,
  MeshReflectorMaterial,
  useTexture,
  Sparkles
} from '@react-three/drei'
import * as THREE from 'three'

function ProcessorChip() {
  const meshRef = useRef<THREE.Mesh>(null)
  const glowRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.2
    }
    if (glowRef.current && glowRef.current.material) {
      const material = glowRef.current.material as THREE.MeshStandardMaterial
      material.emissiveIntensity = 0.5 + Math.sin(state.clock.elapsedTime * 2) * 0.3
    }
  })

  return (
    <Float
      speed={1.5}
      rotationIntensity={0.2}
      floatIntensity={0.3}
      floatingRange={[-0.1, 0.1]}
    >
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

        {/* Outer chip package */}
        {[-1.5, -0.5, 0.5, 1.5].map((x) => 
          [-1.5, -0.5, 0.5, 1.5].map((z) => (
            <mesh key={`${x}-${z}`} position={[x, 0.1, z]}>
              <boxGeometry args={[0.7, 0.05, 0.7]} />
              <meshStandardMaterial 
                color="#1a1a1a"
                metalness={0.8}
                roughness={0.3}
              />
            </mesh>
          ))
        )}

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

        {/* Connection pins - sides */}
        {Array.from({ length: 12 }).map((_, i) => (
          <group key={`pins-${i}`}>
            <mesh position={[2.1, -0.05, -1.8 + i * 0.3]}>
              <boxGeometry args={[0.2, 0.05, 0.08]} />
              <meshStandardMaterial color="#gold" metalness={0.8} roughness={0.2} />
            </mesh>
            <mesh position={[-2.1, -0.05, -1.8 + i * 0.3]}>
              <boxGeometry args={[0.2, 0.05, 0.08]} />
              <meshStandardMaterial color="#gold" metalness={0.8} roughness={0.2} />
            </mesh>
          </group>
        ))}

        {/* Capacitors */}
        {[
          [-1.5, 0.15, 0],
          [1.5, 0.15, 0],
          [0, 0.15, -1.5],
          [0, 0.15, 1.5],
        ].map((pos, i) => (
          <mesh key={`cap-${i}`} position={pos as [number, number, number]}>
            <cylinderGeometry args={[0.1, 0.1, 0.1]} />
            <meshStandardMaterial color="#333333" metalness={0.7} />
          </mesh>
        ))}
      </group>
    </Float>
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
        
        <ContactShadows
          position={[0, -2, 0]}
          opacity={0.4}
          scale={10}
          blur={2}
          far={4}
        />
        
        <Sparkles
          count={50}
          scale={10}
          size={2}
          speed={0.4}
          opacity={0.3}
          color="#00ff88"
        />
        
        <Environment preset="night" />
      </Canvas>
    </div>
  )
}