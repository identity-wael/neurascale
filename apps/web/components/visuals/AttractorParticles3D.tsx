'use client'

import { useRef, useEffect, useState } from 'react'

// Extend Navigator interface for WebGPU
declare global {
  interface Navigator {
    gpu?: any
  }
}

export default function AttractorParticles3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initAttractorParticles = async () => {
      try {
        // WebGPU check removed for build compatibility

        // Dynamic import of Three.js modules
        const THREE = await import('three')

        if (!canvasRef.current) return

        // Initialize renderer (fallback to WebGL since WebGPU modules not available in build)
        const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, antialias: true })

        renderer.setPixelRatio(window.devicePixelRatio)
        renderer.setSize(window.innerWidth, window.innerHeight)
        renderer.setClearColor(0x000000)

        // Setup scene and camera
        const scene = new THREE.Scene()
        const camera = new THREE.PerspectiveCamera(25, window.innerWidth / window.innerHeight, 0.1, 100)
        camera.position.set(3, 5, 8)

        // Simple lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
        scene.add(ambientLight)
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5)
        directionalLight.position.set(4, 2, 0)
        scene.add(directionalLight)

        // Create simple particle system with galaxy colors (fallback for WebGL)
        const particleCount = 50000
        const geometry = new THREE.BufferGeometry()
        const positions = new Float32Array(particleCount * 3)
        const colors = new Float32Array(particleCount * 3)
        const velocities = new Float32Array(particleCount * 3)

        // Galaxy colors
        const colorInside = new THREE.Color('#ffffff')    // White center
        const colorOutside = new THREE.Color('#4185f4')   // NEURASCALE blue

        // Initialize particles in attractor pattern
        for (let i = 0; i < particleCount; i++) {
          const i3 = i * 3

          // Create multiple attractor points
          const attractorIndex = i % 3
          let baseX, baseY, baseZ
          
          if (attractorIndex === 0) {
            baseX = -2; baseY = 0; baseZ = 0
          } else if (attractorIndex === 1) {
            baseX = 2; baseY = 0; baseZ = -1
          } else {
            baseX = 0; baseY = 1; baseZ = 2
          }

          // Add some randomness around attractor points
          const spread = 3
          positions[i3] = baseX + (Math.random() - 0.5) * spread
          positions[i3 + 1] = baseY + (Math.random() - 0.5) * spread
          positions[i3 + 2] = baseZ + (Math.random() - 0.5) * spread

          // Initial velocities
          velocities[i3] = (Math.random() - 0.5) * 0.02
          velocities[i3 + 1] = (Math.random() - 0.5) * 0.02
          velocities[i3 + 2] = (Math.random() - 0.5) * 0.02

          // Color based on distance from center
          const distance = Math.sqrt(positions[i3] ** 2 + positions[i3 + 1] ** 2 + positions[i3 + 2] ** 2)
          const normalizedDistance = Math.min(distance / 5, 1)
          
          const mixedColor = colorInside.clone()
          mixedColor.lerp(colorOutside, normalizedDistance)

          colors[i3] = mixedColor.r
          colors[i3 + 1] = mixedColor.g
          colors[i3 + 2] = mixedColor.b
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

        // Create material
        const material = new THREE.PointsMaterial({
          size: 0.01,
          sizeAttenuation: true,
          depthWrite: false,
          blending: THREE.AdditiveBlending,
          vertexColors: true
        })

        // Create points mesh
        const points = new THREE.Points(geometry, material)
        scene.add(points)

        // Animation variables
        let time = 0
        const attractorPositions = [
          new THREE.Vector3(-2, 0, 0),
          new THREE.Vector3(2, 0, -1),
          new THREE.Vector3(0, 1, 2)
        ]

        // Animation loop
        const animate = () => {
          time += 0.01

          // Update particle positions with attractor physics
          const positionArray = geometry.attributes.position.array as Float32Array
          const colorArray = geometry.attributes.color.array as Float32Array

          for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3
            
            // Current position
            const x = positionArray[i3]
            const y = positionArray[i3 + 1] 
            const z = positionArray[i3 + 2]

            // Calculate forces from attractors
            let forceX = 0, forceY = 0, forceZ = 0

            attractorPositions.forEach((attractor, index) => {
              const dx = attractor.x - x
              const dy = attractor.y - y
              const dz = attractor.z - z
              const distance = Math.sqrt(dx * dx + dy * dy + dz * dz)
              
              if (distance > 0.1) {
                const force = 0.0001 / (distance * distance)
                forceX += dx * force
                forceY += dy * force
                forceZ += dz * force

                // Add spinning motion
                const spinForce = 0.0002
                forceX += -dy * spinForce
                forceY += dx * spinForce
              }
            })

            // Update velocities
            velocities[i3] += forceX
            velocities[i3 + 1] += forceY
            velocities[i3 + 2] += forceZ

            // Apply damping
            velocities[i3] *= 0.99
            velocities[i3 + 1] *= 0.99
            velocities[i3 + 2] *= 0.99

            // Update positions
            positionArray[i3] += velocities[i3]
            positionArray[i3 + 1] += velocities[i3 + 1]
            positionArray[i3 + 2] += velocities[i3 + 2]

            // Update colors based on speed
            const speed = Math.sqrt(velocities[i3] ** 2 + velocities[i3 + 1] ** 2 + velocities[i3 + 2] ** 2)
            const speedFactor = Math.min(speed * 100, 1)
            
            const mixedColor = colorInside.clone()
            mixedColor.lerp(colorOutside, speedFactor)

            colorArray[i3] = mixedColor.r
            colorArray[i3 + 1] = mixedColor.g
            colorArray[i3 + 2] = mixedColor.b
          }

          // Mark attributes as needing update
          geometry.attributes.position.needsUpdate = true
          geometry.attributes.color.needsUpdate = true

          // Rotate camera around the scene
          camera.position.x = Math.cos(time * 0.1) * 8
          camera.position.z = Math.sin(time * 0.1) * 8
          camera.lookAt(scene.position)

          renderer.render(scene, camera)
        }

        renderer.setAnimationLoop(animate)

        // Handle resize
        const handleResize = () => {
          camera.aspect = window.innerWidth / window.innerHeight
          camera.updateProjectionMatrix()
          renderer.setSize(window.innerWidth, window.innerHeight)
        }

        window.addEventListener('resize', handleResize)

        return () => {
          window.removeEventListener('resize', handleResize)
          renderer.dispose()
        }

      } catch (err) {
        console.error('Attractor Particles initialization error:', err)
        setError(`3D Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
      }
    }

    initAttractorParticles()
  }, [])

  if (error) {
    return (
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <p className="text-red-400 mb-2">Attractor Particles Error</p>
          <p className="text-sm text-gray-400">{error}</p>
          <p className="text-xs text-gray-500 mt-2">3D rendering not available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="absolute inset-0 w-full h-full">
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  )
}