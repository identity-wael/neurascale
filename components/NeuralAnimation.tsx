'use client'

import { Canvas, useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

interface Neuron {
  position: THREE.Vector3
  phase: number
}

function Network() {
  const group = useRef<THREE.Group>(null!)
  const meshRefs = useRef<THREE.Mesh[]>([])

  const { neurons, lineGeometry } = useMemo(() => {
    const nodeCount = 40
    const neurons: Neuron[] = []

    for (let i = 0; i < nodeCount; i++) {
      neurons.push({
        position: new THREE.Vector3(
          (Math.random() - 0.5) * 6,
          (Math.random() - 0.5) * 6,
          (Math.random() - 0.5) * 6
        ),
        phase: Math.random() * Math.PI * 2,
      })
    }

    const linePositions = new Float32Array(nodeCount * 6)
    for (let i = 0; i < nodeCount; i++) {
      const start = neurons[i].position
      const end = neurons[Math.floor(Math.random() * nodeCount)].position
      linePositions.set(start.toArray(), i * 6)
      linePositions.set(end.toArray(), i * 6 + 3)
    }
    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3))
    return { neurons, lineGeometry: geometry }
  }, [])

  useFrame(({ clock }) => {
    if (group.current) {
      group.current.rotation.y = clock.getElapsedTime() * 0.1
    }
    meshRefs.current.forEach((mesh, idx) => {
      const neuron = neurons[idx]
      const t = clock.getElapsedTime() * 2 + neuron.phase
      const scale = 1 + 0.5 * Math.sin(t)
      mesh.scale.setScalar(scale)
      const material = mesh.material as THREE.MeshStandardMaterial
      material.emissiveIntensity = 0.5 + 0.5 * Math.sin(t)
    })
  })

  return (
    <group ref={group}>
      {neurons.map((neuron, idx) => (
        <mesh
          key={idx}
          ref={(el) => {
            if (el) meshRefs.current[idx] = el
          }}
          position={neuron.position}
        >
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial color="#1e3a8a" emissive="#06b6d4" emissiveIntensity={0.8} />
        </mesh>
      ))}
      <lineSegments geometry={lineGeometry}>
        <lineBasicMaterial color="#06b6d4" transparent opacity={0.3} />
      </lineSegments>
    </group>
  )
}

export default function NeuralAnimation() {
  return (
    <Canvas className="absolute inset-0" camera={{ position: [0, 0, 8], fov: 45 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={0.7} />
      <Network />
    </Canvas>
  )
}

