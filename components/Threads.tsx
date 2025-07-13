'use client'

import { Canvas, useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

export interface ThreadsProps {
  amplitude?: number
  distance?: number
  enableMouseInteraction?: boolean
  className?: string
}

function ThreadLines({ amplitude = 1, distance = 5, enableMouseInteraction = false }: ThreadsProps) {
  const group = useRef<THREE.Group>(null!)

  // Create line geometries once
  const lines = useRef<THREE.Line[]>([])

  if (lines.current.length === 0) {
    for (let i = 0; i < 50; i++) {
      const material = new THREE.LineBasicMaterial({ color: '#06b6d4', transparent: true, opacity: 0.5 })
      const points = new Float32Array([
        (Math.random() - 0.5) * distance,
        (Math.random() - 0.5) * distance,
        (Math.random() - 0.5) * distance,
        (Math.random() - 0.5) * distance,
        (Math.random() - 0.5) * distance,
        (Math.random() - 0.5) * distance,
      ])
      const geometry = new THREE.BufferGeometry()
      geometry.setAttribute('position', new THREE.BufferAttribute(points, 3))
      const line = new THREE.Line(geometry, material)
      lines.current.push(line)
    }
  }

  useFrame(({ clock, mouse }) => {
    if (!group.current) return
    const t = clock.getElapsedTime()
    group.current.rotation.y = t * 0.1 * amplitude
    if (enableMouseInteraction) {
      group.current.rotation.x = mouse.y * amplitude * 0.5
      group.current.rotation.z = mouse.x * amplitude * 0.5
    }
  })

  return <group ref={group}>{lines.current.map((line, i) => <primitive key={i} object={line} />)}</group>
}

export default function Threads({ className, ...props }: ThreadsProps) {
  return (
    <Canvas className={className} camera={{ position: [0, 0, 10], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <ThreadLines {...props} />
    </Canvas>
  )
}
