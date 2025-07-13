'use client'

import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { 
  PerspectiveCamera,
  Environment,
  Float,
  MeshReflectorMaterial
} from '@react-three/drei'
import * as THREE from 'three'

function ServerRack({ position, delay = 0 }: { position: [number, number, number], delay?: number }) {
  const groupRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + delay) * 0.05
    }
  })

  return (
    <Float speed={1} rotationIntensity={0.01} floatIntensity={0.1}>
      <group ref={groupRef} position={position}>
        {/* Rack frame */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[2, 4, 0.8]} />
          <meshStandardMaterial 
            color="#0a0a0a"
            metalness={0.9}
            roughness={0.3}
          />
        </mesh>

        {/* Server units */}
        {Array.from({ length: 8 }).map((_, i) => (
          <group key={i} position={[0, -1.7 + i * 0.45, 0.05]}>
            {/* Server chassis */}
            <mesh castShadow>
              <boxGeometry args={[1.8, 0.4, 0.7]} />
              <meshStandardMaterial 
                color="#1a1a1a"
                metalness={0.8}
                roughness={0.4}
              />
            </mesh>
            
            {/* Front panel */}
            <mesh position={[0, 0, 0.36]}>
              <boxGeometry args={[1.7, 0.35, 0.02]} />
              <meshStandardMaterial 
                color="#2a2a2a"
                metalness={0.7}
                roughness={0.5}
              />
            </mesh>

            {/* LED indicators */}
            <mesh position={[-0.7, 0, 0.37]}>
              <boxGeometry args={[0.05, 0.05, 0.01]} />
              <meshStandardMaterial 
                color="#00ff00"
                emissive="#00ff00"
                emissiveIntensity={Math.random() > 0.5 ? 1 : 0.3}
              />
            </mesh>
            <mesh position={[-0.6, 0, 0.37]}>
              <boxGeometry args={[0.05, 0.05, 0.01]} />
              <meshStandardMaterial 
                color="#0099ff"
                emissive="#0099ff"
                emissiveIntensity={Math.random() > 0.5 ? 1 : 0.3}
              />
            </mesh>

            {/* Drive bays */}
            {Array.from({ length: 4 }).map((_, j) => (
              <mesh key={j} position={[0.2 + j * 0.3, 0, 0.37]}>
                <boxGeometry args={[0.25, 0.25, 0.02]} />
                <meshStandardMaterial 
                  color="#151515"
                  metalness={0.9}
                  roughness={0.2}
                />
              </mesh>
            ))}
          </group>
        ))}
      </group>
    </Float>
  )
}

function DataCenter() {
  const positions: [number, number, number][] = [
    [-4, 0, -2],
    [-2, 0, -2],
    [0, 0, -2],
    [2, 0, -2],
    [4, 0, -2],
    [-4, 0, 0],
    [-2, 0, 0],
    [0, 0, 0],
    [2, 0, 0],
    [4, 0, 0],
    [-4, 0, 2],
    [-2, 0, 2],
    [0, 0, 2],
    [2, 0, 2],
    [4, 0, 2],
  ]

  return (
    <>
      {positions.map((pos, i) => (
        <ServerRack key={i} position={pos} delay={i * 0.1} />
      ))}
    </>
  )
}

export default function ServerRacks3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
      <Canvas
        shadows
        gl={{ 
          antialias: true, 
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
        }}
      >
        <PerspectiveCamera 
          makeDefault 
          position={[8, 5, 8]} 
          fov={50}
        />
        
        <fog attach="fog" args={['#000000', 5, 20]} />
        
        <ambientLight intensity={0.1} />
        <pointLight position={[10, 10, 10]} intensity={0.3} castShadow />
        <pointLight position={[-10, 10, -10]} intensity={0.2} />
        <spotLight
          position={[0, 10, 0]}
          angle={0.5}
          penumbra={1}
          intensity={0.5}
          castShadow
          shadow-mapSize={[2048, 2048]}
        />
        
        <DataCenter />
        
        {/* Floor with reflection */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]} receiveShadow>
          <planeGeometry args={[20, 20]} />
          <MeshReflectorMaterial
            blur={[300, 100]}
            resolution={2048}
            mixBlur={1}
            mixStrength={80}
            roughness={1}
            depthScale={1.2}
            minDepthThreshold={0.4}
            maxDepthThreshold={1.4}
            color="#101010"
            metalness={0.5}
          />
        </mesh>
        
        <Environment preset="night" />
      </Canvas>
    </div>
  )
}