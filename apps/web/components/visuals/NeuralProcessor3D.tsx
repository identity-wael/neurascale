'use client'

import { useRef, useEffect, useState } from 'react'

// Extend Navigator interface for WebGPU
declare global {
  interface Navigator {
    gpu?: any
  }
}

export default function NeuralProcessor3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initWebGPUGalaxy = async () => {
      try {
        if (!navigator.gpu) {
          throw new Error('WebGPU not supported')
        }

        // Dynamic import of Three.js modules
        const THREE = await import('three')
        const { FontLoader } = await import('three/addons/loaders/FontLoader.js')
        const { TextGeometry } = await import('three/addons/geometries/TextGeometry.js')

        if (!canvasRef.current) return

        // Initialize renderer (fallback to WebGL if WebGPU not available)
        const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, antialias: true })
        renderer.setPixelRatio(window.devicePixelRatio)
        renderer.setSize(window.innerWidth, window.innerHeight)
        renderer.setClearColor(0x000000)

        // Setup scene and camera
        const scene = new THREE.Scene()
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100)
        camera.position.set(3, 3, 3)

        // Galaxy parameters
        const parameters = {
          count: 100000,
          size: 0.01,
          radius: 5,
          branches: 3,
          spin: 1,
          randomness: 0.2,
          randomnessPower: 3,
          insideColor: '#ffffff',    // White center
          outsideColor: '#4185f4'    // NEURASCALE blue
        }

        // Create galaxy geometry
        const geometry = new THREE.BufferGeometry()
        const positions = new Float32Array(parameters.count * 3)
        const colors = new Float32Array(parameters.count * 3)

        const colorInside = new THREE.Color(parameters.insideColor)
        const colorOutside = new THREE.Color(parameters.outsideColor)

        for (let i = 0; i < parameters.count; i++) {
          const i3 = i * 3

          // Position
          const radius = Math.random() * parameters.radius
          const spinAngle = radius * parameters.spin
          const branchAngle = (i % parameters.branches) / parameters.branches * Math.PI * 2

          const randomX = Math.pow(Math.random(), parameters.randomnessPower) * (Math.random() < 0.5 ? 1 : -1) * parameters.randomness * radius
          const randomY = Math.pow(Math.random(), parameters.randomnessPower) * (Math.random() < 0.5 ? 1 : -1) * parameters.randomness * radius
          const randomZ = Math.pow(Math.random(), parameters.randomnessPower) * (Math.random() < 0.5 ? 1 : -1) * parameters.randomness * radius

          positions[i3] = Math.cos(branchAngle + spinAngle) * radius + randomX
          positions[i3 + 1] = randomY
          positions[i3 + 2] = Math.sin(branchAngle + spinAngle) * radius + randomZ

          // Color - white center to blue edges
          const mixedColor = colorInside.clone()
          mixedColor.lerp(colorOutside, radius / parameters.radius)

          colors[i3] = mixedColor.r
          colors[i3 + 1] = mixedColor.g
          colors[i3 + 2] = mixedColor.b
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

        // Create material
        const material = new THREE.PointsMaterial({
          size: parameters.size,
          sizeAttenuation: true,
          depthWrite: false,
          blending: THREE.AdditiveBlending,
          vertexColors: true
        })

        // Create points mesh
        const points = new THREE.Points(geometry, material)
        scene.add(points)

        // Add NEURASCALE text inside the scene with glow/outline
        const loader = new FontLoader()
        loader.load('/fonts/helvetiker_regular.typeface.json', (font) => {
          const textGeometry = new TextGeometry('NEURASCALE', {
            font: font,
            size: 0.5,
            height: 0.1,
            curveSegments: 12,
            bevelEnabled: true,
            bevelThickness: 0.02,
            bevelSize: 0.02,
            bevelOffset: 0,
            bevelSegments: 5,
          })

          textGeometry.computeBoundingBox()
          const centerOffsetX = -0.5 * (textGeometry.boundingBox!.max.x - textGeometry.boundingBox!.min.x)
          const centerOffsetY = -0.5 * (textGeometry.boundingBox!.max.y - textGeometry.boundingBox!.min.y)

          // Create bright blue text with strong glow
          const textMaterial = new THREE.MeshStandardMaterial({
            color: 0x4185f4,
            emissive: 0x6aa6ff,
            emissiveIntensity: 1.5,
            transparent: false
          })

          const textMesh = new THREE.Mesh(textGeometry, textMaterial)
          textMesh.position.x = centerOffsetX
          textMesh.position.y = centerOffsetY - 3  // Back to original position
          textMesh.position.z = 0
          scene.add(textMesh)
        })
        
        // Simple lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
        scene.add(ambientLight)
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
        directionalLight.position.set(1, 1, 1)
        scene.add(directionalLight)

        // No mouse controls - static camera position

        // Animation loop
        const animate = () => {
          // Rotate galaxy
          points.rotation.y += 0.001
          
          // Static camera looking at center
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
        console.error('WebGPU Galaxy initialization error:', err)
        setError(`WebGPU Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
      }
    }

    initWebGPUGalaxy()
  }, [])

  if (error) {
    return (
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <p className="text-red-400 mb-2">WebGPU Galaxy Error</p>
          <p className="text-sm text-gray-400">{error}</p>
          <p className="text-xs text-gray-500 mt-2">Try enabling WebGPU in your browser</p>
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