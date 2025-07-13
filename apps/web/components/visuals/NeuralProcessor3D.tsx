'use client'

import { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { 
  Environment,
  ContactShadows,
  PerspectiveCamera,
  Sparkles
} from '@react-three/drei'
import * as THREE from 'three'

function AttractorParticles() {
  const { gl, scene } = useThree()
  const [webgpuSupported, setWebgpuSupported] = useState(false)
  const meshRef = useRef<THREE.Points>(null)
  const updateComputeRef = useRef<any>(null)

  useEffect(() => {
    // Check WebGPU support
    if (!navigator.gpu) {
      console.warn('WebGPU not supported, falling back to basic particles')
      setWebgpuSupported(false)
      return
    }
    
    setWebgpuSupported(true)
    
    // Note: Full WebGPU TSL implementation would require importing three/webgpu
    // For now, creating a simplified particle system with standard Three.js
    
    const count = 10000 // Reduced for performance
    const positions = new Float32Array(count * 3)
    const velocities = new Float32Array(count * 3)
    const colors = new Float32Array(count * 3)
    
    // Initialize particles in a galaxy-like distribution
    for (let i = 0; i < count; i++) {
      const i3 = i * 3
      const radius = Math.random() * 4 + 0.5
      const angle = Math.random() * Math.PI * 2
      const height = (Math.random() - 0.5) * 0.4
      
      positions[i3] = Math.cos(angle) * radius
      positions[i3 + 1] = height
      positions[i3 + 2] = Math.sin(angle) * radius
      
      // Initial velocities for orbital motion
      const speed = 0.02 / Math.sqrt(radius)
      velocities[i3] = -Math.sin(angle) * speed
      velocities[i3 + 1] = 0
      velocities[i3 + 2] = Math.cos(angle) * speed
      
      // Color based on distance from center
      const normalizedRadius = radius / 4
      colors[i3] = 0.35 + normalizedRadius * 0.65      // Red
      colors[i3 + 1] = 0.0 + normalizedRadius * 1.0    // Green  
      colors[i3 + 2] = 1.0 - normalizedRadius * 0.35   // Blue
    }
    
    if (meshRef.current) {
      meshRef.current.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      meshRef.current.geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3))
      meshRef.current.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    }
    
  }, [gl, scene])

  useFrame((state) => {
    if (!meshRef.current) return
    
    const positions = meshRef.current.geometry.attributes.position.array as Float32Array
    const velocities = meshRef.current.geometry.attributes.velocity?.array as Float32Array
    
    if (!positions || !velocities) return
    const time = state.clock.elapsedTime
    
    // Simple gravity simulation toward multiple attractors
    const attractors = [
      { x: 0, y: 0, z: 0, mass: 5 },
      { x: Math.cos(time * 0.3) * 2, y: 0.5, z: Math.sin(time * 0.3) * 2, mass: 2 },
      { x: Math.cos(time * 0.5 + Math.PI) * 1.5, y: -0.3, z: Math.sin(time * 0.5 + Math.PI) * 1.5, mass: 1.5 }
    ]
    
    for (let i = 0; i < positions.length / 3; i++) {
      const i3 = i * 3
      
      let fx = 0, fy = 0, fz = 0
      
      // Calculate forces from all attractors
      for (const attractor of attractors) {
        const dx = attractor.x - positions[i3]
        const dy = attractor.y - positions[i3 + 1]
        const dz = attractor.z - positions[i3 + 2]
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz)
        
        if (distance > 0.1) {
          const force = attractor.mass / (distance * distance + 0.1)
          fx += (dx / distance) * force * 0.001
          fy += (dy / distance) * force * 0.001
          fz += (dz / distance) * force * 0.001
        }
      }
      
      // Update velocities
      velocities[i3] += fx
      velocities[i3 + 1] += fy
      velocities[i3 + 2] += fz
      
      // Apply damping
      velocities[i3] *= 0.999
      velocities[i3 + 1] *= 0.999
      velocities[i3 + 2] *= 0.999
      
      // Update positions
      positions[i3] += velocities[i3]
      positions[i3 + 1] += velocities[i3 + 1]
      positions[i3 + 2] += velocities[i3 + 2]
      
      // Boundary wrapping
      const bound = 8
      if (Math.abs(positions[i3]) > bound) positions[i3] = -Math.sign(positions[i3]) * bound
      if (Math.abs(positions[i3 + 1]) > bound) positions[i3 + 1] = -Math.sign(positions[i3 + 1]) * bound
      if (Math.abs(positions[i3 + 2]) > bound) positions[i3 + 2] = -Math.sign(positions[i3 + 2]) * bound
    }
    
    meshRef.current.geometry.attributes.position.needsUpdate = true
  })

  const material = new THREE.PointsMaterial({
    size: 0.02,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    transparent: true,
    opacity: 0.8
  })

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute 
          attach="attributes-position" 
          count={10000} 
          array={new Float32Array(10000 * 3)} 
          itemSize={3} 
        />
        <bufferAttribute 
          attach="attributes-velocity" 
          count={10000} 
          array={new Float32Array(10000 * 3)} 
          itemSize={3} 
        />
        <bufferAttribute 
          attach="attributes-color" 
          count={10000} 
          array={new Float32Array(10000 * 3)} 
          itemSize={3} 
        />
      </bufferGeometry>
      <primitive object={material} />
    </points>
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
        
        <AttractorParticles />
        
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