'use client'

import { Canvas, useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

function Network() {
  const group = useRef<THREE.Group>(null!)

  const { spheres, lineGeometry } = useMemo(() => {
    const nodeCount = 30
    const spheres: THREE.Vector3[] = []
    const positions: THREE.Vector3[] = []
    for (let i = 0; i < nodeCount; i++) {
      const v = new THREE.Vector3(
        (Math.random() - 0.5) * 4,
        (Math.random() - 0.5) * 4,
        (Math.random() - 0.5) * 4
      )
      spheres.push(v)
      positions.push(v)
    }

    const linePositions = new Float32Array(nodeCount * 6)
    for (let i = 0; i < nodeCount; i++) {
      const start = positions[i]
      const end = positions[Math.floor(Math.random() * nodeCount)]
      linePositions.set(start.toArray(), i * 6)
      linePositions.set(end.toArray(), i * 6 + 3)
    }
    const lineGeometry = new THREE.BufferGeometry()
    lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3))
    return { spheres, lineGeometry }
  }, [])

  useFrame(({ clock }) => {
    if (group.current) {
      group.current.rotation.y = clock.getElapsedTime() * 0.2
    }
  })

  return (
    <group ref={group}>
      {spheres.map((pos, idx) => (
        <mesh key={idx} position={pos}>
          <sphereGeometry args={[0.05, 8, 8]} />
          <meshBasicMaterial color="#06b6d4" />
        </mesh>
      ))}
      <lineSegments geometry={lineGeometry}>
        <lineBasicMaterial color="#06b6d4" transparent opacity={0.5} />
      </lineSegments>
    </group>
  )
}

export default function NeuralAnimation() {
  return (
    <Canvas className="absolute inset-0" camera={{ position: [0, 0, 5], fov: 50 }}>
      <ambientLight intensity={0.6} />
      <pointLight position={[10, 10, 10]} />
      <Network />
    </Canvas>
  )
}
