'use client'

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { 
  Float, 
  Environment,
  ContactShadows,
  PerspectiveCamera,
  Sparkles
} from '@react-three/drei'
import * as THREE from 'three'

function GPUDie() {
  const groupRef = useRef<THREE.Group>(null)
  const glowRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    // Gentle floating and rotation
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
    
    // Pulsing glow effect
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
        ref={groupRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        {/* Main GPU Die Substrate */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[8, 0.3, 6]} />
          <meshStandardMaterial 
            color="#404040"
            metalness={0.8}
            roughness={0.2}
            emissive="#0a0a0a"
            emissiveIntensity={0.1}
          />
        </mesh>

        {/* Central H100 Processing Core */}
        <mesh position={[0, 0.2, 0]}>
          <boxGeometry args={[3, 0.2, 3]} />
          <meshStandardMaterial 
            color="#000000"
            metalness={0.95}
            roughness={0.05}
            emissive="#001100"
            emissiveIntensity={0.2}
          />
        </mesh>

        {/* Glowing Green Core */}
        <mesh ref={glowRef} position={[0, 0.35, 0]}>
          <boxGeometry args={[2.5, 0.1, 2.5]} />
          <meshStandardMaterial 
            color="#00ff88"
            emissive="#00ff88"
            emissiveIntensity={hovered ? 2 : 1.5}
            metalness={0.3}
            roughness={0}
          />
        </mesh>

        {/* H100 Label */}
        <mesh position={[0, 0.3, 0]}>
          <boxGeometry args={[0.8, 0.02, 0.4]} />
          <meshStandardMaterial 
            color="#ffffff"
            emissive="#ffffff"
            emissiveIntensity={0.3}
          />
        </mesh>

        {/* GPU Cores Grid (8x8 = 64 cores) */}
        {Array.from({ length: 8 }).map((_, row) =>
          Array.from({ length: 8 }).map((_, col) => (
            <mesh 
              key={`core-${row}-${col}`}
              position={[
                (col - 3.5) * 0.3,
                0.35,
                (row - 3.5) * 0.2
              ]}
            >
              <boxGeometry args={[0.15, 0.02, 0.1]} />
              <meshStandardMaterial 
                color="#4185f4"
                emissive="#4185f4"
                emissiveIntensity={0.2 + Math.sin((row + col) * 0.5) * 0.1}
                metalness={0.5}
                roughness={0.3}
              />
            </mesh>
          ))
        )}

        {/* HBM Memory Modules (6 stacks) */}
        {Array.from({ length: 6 }).map((_, i) => (
          <mesh 
            key={`hbm-${i}`}
            position={[
              (i % 3 - 1) * 1.8,
              0.4,
              (i < 3 ? -1.5 : 1.5)
            ]}
          >
            <boxGeometry args={[0.4, 0.4, 0.4]} />
            <meshStandardMaterial 
              color="#0066ff"
              emissive="#0066ff"
              emissiveIntensity={0.3}
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
        ))}

        {/* Corner Connection Pins */}
        {[
          [-2.8, 0.1, -1.8],
          [2.8, 0.1, -1.8], 
          [-2.8, 0.1, 1.8],
          [2.8, 0.1, 1.8]
        ].map((pos, i) => (
          <mesh key={`pin-${i}`} position={pos as [number, number, number]}>
            <sphereGeometry args={[0.08, 8, 8]} />
            <meshStandardMaterial 
              color="#ffd700"
              emissive="#ffd700"
              emissiveIntensity={0.4}
              metalness={0.9}
              roughness={0.1}
            />
          </mesh>
        ))}

        {/* Circuit Traces */}
        {Array.from({ length: 20 }).map((_, i) => (
          <mesh 
            key={`trace-${i}`}
            position={[
              (Math.random() - 0.5) * 5,
              0.12,
              (Math.random() - 0.5) * 3
            ]}
            rotation={[0, Math.random() * Math.PI, 0]}
          >
            <boxGeometry args={[0.02, 0.01, 0.5]} />
            <meshStandardMaterial 
              color="#00ff88"
              emissive="#00ff88"
              emissiveIntensity={0.2}
              transparent
              opacity={0.6}
            />
          </mesh>
        ))}

        {/* NEURASCALE Branding */}
        <mesh position={[0, 0.13, -1.6]}>
          <boxGeometry args={[1.2, 0.02, 0.2]} />
          <meshStandardMaterial 
            color="#4185f4"
            emissive="#4185f4"
            emissiveIntensity={0.4}
          />
        </mesh>
      </group>
    </Float>
  )
}


export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
      <Canvas
        shadows
        gl={{ 
          antialias: true, 
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.5
        }}
      >
        <PerspectiveCamera makeDefault position={[0, 5, 10]} fov={60} />
        
        <ambientLight intensity={0.8} />
        <pointLight position={[5, 5, 5]} intensity={2} castShadow />
        <pointLight position={[-5, 5, 5]} intensity={1} />
        <pointLight position={[0, 2, 8]} intensity={1.5} color="#00ff88" />
        <directionalLight position={[0, 10, 0]} intensity={1} />
        
        {/* Debug cube to test visibility */}
        <mesh position={[3, 0, 0]}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={0.3} />
        </mesh>
        
        <group position={[0, 1, 0]} scale={[1.5, 1.5, 1.5]}>
          <GPUDie />
        </group>
        
        <ContactShadows
          position={[0, -1, 0]}
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