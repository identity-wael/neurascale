'use client'

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'

function NvidiaH100() {
  const boardRef = useRef<THREE.Group>(null)
  const fanRefs = useRef<THREE.Mesh[]>([])
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    // Gentle floating animation
    if (boardRef.current) {
      boardRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.05
      boardRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.02
    }
    
    // Spinning fans
    fanRefs.current.forEach((fan, i) => {
      if (fan) {
        fan.rotation.z = state.clock.elapsedTime * 8 + i
      }
    })
  })

  return (
    <group
      ref={boardRef as any}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      position={[0, 0, 0]}
    >
      {/* Main PCB Board */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[8, 0.15, 5]} />
        <meshStandardMaterial 
          color="#0a4f0a"
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* GPU Die/Chip */}
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[2.5, 0.1, 2.5]} />
        <meshStandardMaterial 
          color="#1a1a1a"
          metalness={0.9}
          roughness={0.1}
          emissive="#00ff00"
          emissiveIntensity={0.3}
        />
      </mesh>

      {/* HBM Memory Modules (6 stacks) */}
      {Array.from({ length: 6 }).map((_, i) => (
        <mesh 
          key={`hbm-${i}`} 
          position={[
            (i % 3 - 1) * 2.2,
            0.25,
            (i < 3 ? -2.2 : 2.2)
          ]}
        >
          <boxGeometry args={[0.6, 0.3, 0.6]} />
          <meshStandardMaterial 
            color="#2a2a2a"
            metalness={0.8}
            roughness={0.2}
            emissive="#0066ff"
            emissiveIntensity={0.2}
          />
        </mesh>
      ))}

      {/* Heat Sink Base */}
      <mesh position={[0, 0.4, 0]}>
        <boxGeometry args={[3.5, 0.2, 3.5]} />
        <meshStandardMaterial 
          color="#888888"
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      {/* Heat Sink Fins */}
      {Array.from({ length: 20 }).map((_, i) => (
        <mesh 
          key={`fin-${i}`} 
          position={[-1.6 + i * 0.16, 0.7, 0]}
        >
          <boxGeometry args={[0.1, 0.4, 3]} />
          <meshStandardMaterial 
            color="#aaaaaa"
            metalness={0.8}
            roughness={0.3}
          />
        </mesh>
      ))}

      {/* Cooling Fans */}
      {Array.from({ length: 2 }).map((_, i) => (
        <group key={`fan-group-${i}`} position={[(i - 0.5) * 2.5, 1.2, 0]}>
          {/* Fan Housing */}
          <mesh>
            <cylinderGeometry args={[0.8, 0.8, 0.2, 12]} />
            <meshStandardMaterial 
              color="#333333"
              metalness={0.7}
              roughness={0.4}
            />
          </mesh>
          
          {/* Fan Blades */}
          <mesh 
            ref={(el) => el && (fanRefs.current[i] = el)}
            position={[0, 0.05, 0]}
          >
            {Array.from({ length: 6 }).map((_, blade) => (
              <mesh 
                key={`blade-${blade}`}
                position={[
                  Math.cos(blade * Math.PI / 3) * 0.4,
                  0,
                  Math.sin(blade * Math.PI / 3) * 0.4
                ]}
                rotation={[0, blade * Math.PI / 3, 0]}
              >
                <boxGeometry args={[0.6, 0.02, 0.1]} />
                <meshStandardMaterial 
                  color="#444444"
                  metalness={0.5}
                  roughness={0.5}
                />
              </mesh>
            ))}
          </mesh>
        </group>
      ))}

      {/* Power Connectors */}
      {Array.from({ length: 2 }).map((_, i) => (
        <mesh 
          key={`power-${i}`} 
          position={[3.5, 0.3, (i - 0.5) * 1.5]}
          rotation={[0, 0, Math.PI / 2]}
        >
          <cylinderGeometry args={[0.15, 0.15, 0.5, 8]} />
          <meshStandardMaterial 
            color="#ffaa00"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      ))}

      {/* PCIe Connector */}
      <mesh position={[-3.8, 0.1, 0]}>
        <boxGeometry args={[0.3, 0.2, 4.5]} />
        <meshStandardMaterial 
          color="#ffd700"
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      {/* Status LEDs */}
      {Array.from({ length: 4 }).map((_, i) => (
        <mesh 
          key={`led-${i}`} 
          position={[2.5 + i * 0.3, 0.2, 2]}
        >
          <sphereGeometry args={[0.05, 8, 8]} />
          <meshStandardMaterial 
            color={i < 2 ? "#00ff00" : "#ff0000"}
            emissive={i < 2 ? "#00ff00" : "#ff0000"}
            emissiveIntensity={0.8}
          />
        </mesh>
      ))}

      {/* NVIDIA Logo Area */}
      <mesh position={[0, 0.31, -1.8]}>
        <boxGeometry args={[1.5, 0.02, 0.3]} />
        <meshStandardMaterial 
          color="#76b900"
          emissive="#76b900"
          emissiveIntensity={0.3}
        />
      </mesh>
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
        
        
        <NvidiaH100 />
        <CircuitLines />
      </Canvas>
    </div>
  )
}