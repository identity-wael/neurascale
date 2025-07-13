'use client'

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'

function ProfessionalGPU() {
  const groupRef = useRef<THREE.Group>(null)
  const fanRefs = useRef<any[]>([])

  useFrame((state) => {
    // Gentle rotation
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
    
    // Spinning fans
    fanRefs.current.forEach((fan, i) => {
      if (fan) {
        fan.rotation.y = state.clock.elapsedTime * 6 + i * 0.5
      }
    })
  })

  return (
    <group ref={groupRef as any} position={[0, 0, 0]}>
      {/* Main GPU Shroud */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[6, 1.2, 2.5]} />
        <meshStandardMaterial 
          color="#1a1a1a"
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* GPU Backplate */}
      <mesh position={[0, -0.65, 0]}>
        <boxGeometry args={[6, 0.1, 2.5]} />
        <meshStandardMaterial 
          color="#0a0a0a"
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      {/* Triple Fan Setup */}
      {Array.from({ length: 3 }).map((_, i) => (
        <group key={`fan-${i}`} position={[(i - 1) * 1.8, 0.4, 0]}>
          {/* Fan Ring */}
          <mesh>
            <torusGeometry args={[0.6, 0.05, 8, 16]} />
            <meshStandardMaterial 
              color="#333333"
              metalness={0.7}
              roughness={0.3}
            />
          </mesh>
          
          {/* Fan Blades */}
          <group 
            ref={(el) => {
              if (el) fanRefs.current[i] = el
            }}
          >
            {Array.from({ length: 9 }).map((_, blade) => (
              <mesh 
                key={`blade-${blade}`}
                position={[
                  Math.cos(blade * Math.PI * 2 / 9) * 0.35,
                  0,
                  Math.sin(blade * Math.PI * 2 / 9) * 0.35
                ]}
                rotation={[0, blade * Math.PI * 2 / 9 + Math.PI / 2, 0]}
              >
                <boxGeometry args={[0.4, 0.02, 0.06]} />
                <meshStandardMaterial 
                  color="#2a2a2a"
                  metalness={0.6}
                  roughness={0.4}
                />
              </mesh>
            ))}
          </group>
        </group>
      ))}

      {/* RGB Light Strip */}
      <mesh position={[0, 0.1, 1.3]}>
        <boxGeometry args={[5, 0.1, 0.05]} />
        <meshStandardMaterial 
          color="#ffffff"
          emissive="#4185f4"
          emissiveIntensity={0.5}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Brand Logo */}
      <mesh position={[0, 0.2, 1.28]}>
        <boxGeometry args={[1.5, 0.3, 0.02]} />
        <meshStandardMaterial 
          color="#ffffff"
          emissive="#76b900"
          emissiveIntensity={0.4}
        />
      </mesh>

      {/* PCIe Bracket */}
      <mesh position={[-3.2, 0, 0]}>
        <boxGeometry args={[0.2, 1.2, 0.8]} />
        <meshStandardMaterial 
          color="#888888"
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      {/* Power Connectors */}
      {Array.from({ length: 2 }).map((_, i) => (
        <mesh 
          key={`power-${i}`} 
          position={[2.5, 0.3, (i - 0.5) * 0.8]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <cylinderGeometry args={[0.15, 0.15, 0.4, 8]} />
          <meshStandardMaterial 
            color="#222222"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      ))}

      {/* Heat Pipes */}
      {Array.from({ length: 4 }).map((_, i) => (
        <mesh 
          key={`pipe-${i}`} 
          position={[(i - 1.5) * 0.4, -0.1, -1]}
          rotation={[0, 0, Math.PI / 2]}
        >
          <cylinderGeometry args={[0.08, 0.08, 2, 8]} />
          <meshStandardMaterial 
            color="#copper"
            metalness={0.95}
            roughness={0.05}
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
        
        
        <ProfessionalGPU />
        <CircuitLines />
      </Canvas>
    </div>
  )
}