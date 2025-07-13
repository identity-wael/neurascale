'use client'

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text, Environment, ContactShadows, MeshReflectorMaterial } from '@react-three/drei'
import * as THREE from 'three'

function GPUDie() {
  const groupRef = useRef<THREE.Group>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.05
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.02
    }
  })

  return (
    <group 
      ref={groupRef}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {/* Main GPU Package Substrate - Professional Grade */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[12, 0.8, 10]} />
        <meshPhysicalMaterial 
          color="#1a1a1a"
          metalness={0.9}
          roughness={0.1}
          clearcoat={1}
          clearcoatRoughness={0.1}
          envMapIntensity={1.5}
        />
      </mesh>

      {/* Interposer Layer */}
      <mesh position={[0, 0.41, 0]} castShadow receiveShadow>
        <boxGeometry args={[8.5, 0.2, 7]} />
        <meshPhysicalMaterial 
          color="#2d2d2d"
          metalness={0.95}
          roughness={0.05}
          transmission={0.1}
          thickness={0.5}
        />
      </mesh>

      {/* Central GPU Die with Advanced Materials */}
      <mesh position={[0, 0.65, 0]} castShadow receiveShadow>
        <boxGeometry args={[6, 0.4, 5]} />
        <meshPhysicalMaterial 
          color="#0a0a0a"
          metalness={0.98}
          roughness={0.02}
          clearcoat={1}
          clearcoatRoughness={0.01}
          reflectivity={1}
        />
      </mesh>

      {/* Advanced GPU Cores - Nanometer Precision Look */}
      {Array.from({ length: 16 }).map((_, row) =>
        Array.from({ length: 16 }).map((_, col) => {
          const x = (col - 7.5) * 0.25
          const z = (row - 7.5) * 0.2
          const distance = Math.sqrt(x * x + z * z)
          const intensity = Math.max(0.2, 1 - distance / 4)
          
          return (
            <mesh 
              key={`core-${row}-${col}`}
              position={[x, 0.85, z]}
              castShadow
            >
              <boxGeometry args={[0.15, 0.12, 0.12]} />
              <meshPhysicalMaterial 
                color={new THREE.Color().setHSL(0.6, 0.8, 0.3 + intensity * 0.4)}
                emissive={new THREE.Color().setHSL(0.6, 1, intensity * 0.3)}
                emissiveIntensity={hovered ? intensity * 2 : intensity}
                metalness={0.8}
                roughness={0.2}
                clearcoat={0.8}
                transmission={0.1}
              />
            </mesh>
          )
        })
      )}

      {/* HBM3 Memory Stacks - Ultra Realistic */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2
        const radius = 3.8
        const x = Math.cos(angle) * radius
        const z = Math.sin(angle) * radius
        
        return (
          <group key={`hbm-stack-${i}`} position={[x, 0, z]}>
            {/* HBM Stack Base */}
            <mesh position={[0, 0.6, 0]} castShadow receiveShadow>
              <boxGeometry args={[0.8, 1.2, 0.8]} />
              <meshPhysicalMaterial 
                color="#1e3a8a"
                metalness={0.95}
                roughness={0.05}
                emissive="#1e40af"
                emissiveIntensity={0.4}
                clearcoat={1}
                transmission={0.05}
              />
            </mesh>
            
            {/* Memory Layers */}
            {Array.from({ length: 12 }).map((_, layer) => (
              <mesh 
                key={`layer-${layer}`}
                position={[0, 0.1 + layer * 0.08, 0]}
                castShadow
              >
                <boxGeometry args={[0.75, 0.04, 0.75]} />
                <meshPhysicalMaterial 
                  color="#3b82f6"
                  metalness={0.9}
                  roughness={0.1}
                  emissive="#60a5fa"
                  emissiveIntensity={0.1}
                />
              </mesh>
            ))}
          </group>
        )
      })}

      {/* Precision Ball Grid Array (BGA) */}
      {Array.from({ length: 40 }).map((_, row) =>
        Array.from({ length: 32 }).map((_, col) => {
          const x = (col - 15.5) * 0.3
          const z = (row - 19.5) * 0.25
          const isInside = Math.abs(x) < 5.8 && Math.abs(z) < 4.8
          
          if (isInside) return null
          
          return (
            <mesh 
              key={`bga-${row}-${col}`}
              position={[x, -0.45, z]}
              castShadow
            >
              <sphereGeometry args={[0.04, 12, 12]} />
              <meshPhysicalMaterial 
                color="#ffd700"
                metalness={1}
                roughness={0.05}
                emissive="#ffed4e"
                emissiveIntensity={0.2}
                clearcoat={1}
              />
            </mesh>
          )
        })
      )}

      {/* Power Delivery Network Traces */}
      {Array.from({ length: 50 }).map((_, i) => {
        const angle = (i / 50) * Math.PI * 2
        const radius = 2 + Math.random() * 2
        const x = Math.cos(angle) * radius
        const z = Math.sin(angle) * radius
        
        return (
          <mesh 
            key={`trace-${i}`}
            position={[x, 0.52, z]}
            rotation={[0, angle, 0]}
          >
            <boxGeometry args={[0.02, 0.02, 1.5]} />
            <meshPhysicalMaterial 
              color="#10b981"
              emissive="#34d399"
              emissiveIntensity={0.3}
              metalness={0.8}
              roughness={0.2}
              transmission={0.1}
            />
          </mesh>
        )
      })}

      {/* Capacitor Arrays */}
      {Array.from({ length: 24 }).map((_, i) => {
        const angle = (i / 24) * Math.PI * 2
        const radius = 4.5
        const x = Math.cos(angle) * radius
        const z = Math.sin(angle) * radius
        
        return (
          <mesh 
            key={`cap-${i}`}
            position={[x, 0.3, z]}
            castShadow
          >
            <cylinderGeometry args={[0.06, 0.06, 0.4, 8]} />
            <meshPhysicalMaterial 
              color="#fbbf24"
              metalness={0.9}
              roughness={0.1}
              emissive="#f59e0b"
              emissiveIntensity={0.2}
            />
          </mesh>
        )
      })}

      {/* Thermal Pads */}
      {Array.from({ length: 4 }).map((_, i) => {
        const positions = [[-2.5, -2], [2.5, -2], [-2.5, 2], [2.5, 2]]
        const [x, z] = positions[i]
        
        return (
          <mesh 
            key={`thermal-${i}`}
            position={[x, 0.95, z]}
            castShadow
          >
            <boxGeometry args={[0.8, 0.1, 0.8]} />
            <meshPhysicalMaterial 
              color="#6b7280"
              metalness={0.7}
              roughness={0.3}
              transmission={0.3}
              thickness={0.1}
            />
          </mesh>
        )
      })}

      {/* Professional NEURASCALE Branding */}
      <group position={[0, 0.53, -3.2]}>
        <Text
          fontSize={0.4}
          font="/fonts/Inter-Bold.woff"
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.02}
        >
          <meshPhysicalMaterial 
            color="#ffffff"
            emissive="#4185f4"
            emissiveIntensity={0.3}
            metalness={0.8}
            roughness={0.2}
          />
          NEURASCALE
        </Text>
        
        {/* Logo Underline */}
        <mesh position={[0, -0.25, 0]}>
          <boxGeometry args={[2.8, 0.02, 0.02]} />
          <meshPhysicalMaterial 
            color="#4185f4"
            emissive="#4185f4"
            emissiveIntensity={0.5}
            metalness={1}
            roughness={0}
          />
        </mesh>
      </group>

      {/* Holographic Security Features */}
      <mesh position={[4.5, 0.53, 2.5]} rotation={[0, 0, Math.PI / 4]}>
        <boxGeometry args={[0.6, 0.02, 0.6]} />
        <meshPhysicalMaterial 
          color="#8b5cf6"
          emissive="#a78bfa"
          emissiveIntensity={0.4}
          metalness={0.9}
          roughness={0.1}
          transmission={0.3}
          iridescence={1}
          iridescenceIOR={1.3}
        />
      </mesh>
    </group>
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
        
        <GPUDie />
        
        {/* Professional Environment */}
        <Environment preset="studio" />
        
        {/* Reflective Ground Plane */}
        <ContactShadows 
          position={[0, -2, 0]}
          opacity={0.6}
          scale={20}
          blur={2}
          far={4}
          resolution={1024}
          color="#000000"
        />
        
        <mesh position={[0, -2.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[50, 50]} />
          <MeshReflectorMaterial
            blur={[300, 300]}
            resolution={1024}
            mixBlur={1}
            mixStrength={80}
            roughness={1}
            depthScale={1.2}
            minDepthThreshold={0.4}
            maxDepthThreshold={1.4}
            color="#101010"
            metalness={0.5}
            mirror={0.8}
          />
        </mesh>
        
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