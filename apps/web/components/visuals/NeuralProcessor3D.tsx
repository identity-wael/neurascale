'use client'

import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text } from '@react-three/drei'
import * as THREE from 'three'

function Galaxy() {
  const pointsRef = useRef<THREE.Points>(null)
  const particleCount = 15000

  // Create galaxy particles
  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)
  const sizes = new Float32Array(particleCount)

  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3
    
    // Create spiral galaxy shape
    const radius = Math.random() * 8
    const spinAngle = radius * 0.5
    const branchAngle = (i % 3) * ((Math.PI * 2) / 3)
    
    const randomX = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3
    const randomY = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3
    const randomZ = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3

    positions[i3] = Math.cos(branchAngle + spinAngle) * radius + randomX
    positions[i3 + 1] = randomY
    positions[i3 + 2] = Math.sin(branchAngle + spinAngle) * radius + randomZ

    // Color transition: white at center to blue at edges
    const distanceFromCenter = Math.sqrt(
      positions[i3] * positions[i3] + 
      positions[i3 + 2] * positions[i3 + 2]
    )
    const colorMix = Math.min(distanceFromCenter / 8, 1)
    
    // White (1,1,1) to Blue (#4185f4 = 0.255, 0.522, 0.957)
    colors[i3] = 1 - colorMix * (1 - 0.255)     // Red
    colors[i3 + 1] = 1 - colorMix * (1 - 0.522) // Green
    colors[i3 + 2] = 1 - colorMix * (1 - 0.957) // Blue

    // Size based on distance (smaller particles further out)
    sizes[i] = Math.random() * 6 + 2 - colorMix * 3
  }

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.05
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute 
          attach="attributes-position" 
          count={particleCount} 
          array={positions} 
          itemSize={3} 
        />
        <bufferAttribute 
          attach="attributes-color" 
          count={particleCount} 
          array={colors} 
          itemSize={3} 
        />
        <bufferAttribute 
          attach="attributes-size" 
          count={particleCount} 
          array={sizes} 
          itemSize={1} 
        />
      </bufferGeometry>
      <pointsMaterial 
        size={1}
        sizeAttenuation={true}
        vertexColors={true}
        blending={THREE.AdditiveBlending}
        transparent={true}
        opacity={0.8}
      />
    </points>
  )
}

export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
      <Canvas 
        shadows 
        camera={{ position: [0, 8, 15], fov: 60 }}
        gl={{ 
          antialias: true,
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2
        }}
      >
        {/* Enhanced Lighting for Visibility */}
        <ambientLight intensity={0.6} />
        <directionalLight 
          position={[10, 10, 5]} 
          intensity={3} 
          castShadow 
          shadow-mapSize={[2048, 2048]}
          shadow-camera-far={50}
          shadow-camera-left={-20}
          shadow-camera-right={20}
          shadow-camera-top={20}
          shadow-camera-bottom={-20}
        />
        <pointLight position={[-5, 8, 5]} intensity={1.5} color="#4185f4" />
        <pointLight position={[5, 8, -5]} intensity={1.2} color="#ffffff" />
        <pointLight position={[0, 10, 0]} intensity={2} color="#ffffff" />
        <spotLight 
          position={[0, 20, 0]} 
          intensity={2} 
          angle={0.4} 
          penumbra={0.3}
          castShadow
          color="#ffffff"
        />
        
        <Galaxy />
        
        {/* NEURASCALE Logo */}
        <Text
          position={[0, -3, 0]}
          fontSize={1.2}
          color="#4185f4"
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.02}
        >
          <meshStandardMaterial 
            color="#4185f4"
            emissive="#4185f4"
            emissiveIntensity={0.3}
          />
          NEURASCALE
        </Text>
        
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          maxDistance={30}
          minDistance={8}
          maxPolarAngle={Math.PI / 1.5}
          target={[0, 0, 0]}
          enableDamping={true}
          dampingFactor={0.05}
        />
      </Canvas>
    </div>
  )
}