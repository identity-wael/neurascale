'use client'

import { useRef, useEffect, useState } from 'react'

// Extend Navigator interface for WebGPU
declare global {
  interface Navigator {
    gpu?: any
  }
}

export default function DataUniverse3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initGalaxy = async () => {
      try {
        setIsLoading(true)
        
        // Browser detection
        const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
        const hasWebGPU = 'gpu' in navigator && navigator.gpu
        
        console.log('Browser detection:', { isSafari, hasWebGPU })

        // Dynamic import of Three.js modules
        const THREE = await import('three')
        const { FontLoader } = await import('three/addons/loaders/FontLoader.js')
        const { TextGeometry } = await import('three/addons/geometries/TextGeometry.js')

        if (!canvasRef.current) return

        // Initialize renderer with browser-specific optimizations
        const rendererOptions = {
          canvas: canvasRef.current,
          antialias: !isSafari, // Disable antialiasing on Safari for better performance
          alpha: true,
          preserveDrawingBuffer: false,
          powerPreference: isSafari ? 'default' : 'high-performance' as WebGLPowerPreference
        }
        
        const renderer = new THREE.WebGLRenderer(rendererOptions)
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isSafari ? 1 : 2)) // Limit pixel ratio on Safari
        renderer.setSize(window.innerWidth, window.innerHeight)
        renderer.setClearColor(0x000000)
        
        // Safari-specific settings
        if (isSafari) {
          renderer.outputColorSpace = THREE.SRGBColorSpace
          renderer.toneMapping = THREE.NoToneMapping
        }

        // Setup scene and camera
        const scene = new THREE.Scene()
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100)
        camera.position.set(3, 3, 3)

        // Galaxy parameters with Safari optimization
        const parameters = {
          count: isSafari ? 50000 : 100000, // Reduce particle count on Safari
          size: isSafari ? 0.015 : 0.01,    // Slightly larger particles on Safari
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

        // Add NEURASCALE text with fallback for font loading issues
        try {
          const loader = new FontLoader()
          
          loader.load(
            'https://threejs.org/examples/fonts/helvetiker_regular.typeface.json',
            (font) => {
              try {
                const textGeometry = new TextGeometry('NEURASCALE', {
                  font: font,
                  size: 0.5,
                  height: 0.1,
                  curveSegments: isSafari ? 8 : 12, // Reduce complexity on Safari
                  bevelEnabled: !isSafari, // Disable bevel on Safari for performance
                  bevelThickness: 0.02,
                  bevelSize: 0.02,
                  bevelOffset: 0,
                  bevelSegments: 3,
                })

                textGeometry.computeBoundingBox()
                if (textGeometry.boundingBox) {
                  const centerOffsetX = -0.5 * (textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x)
                  const centerOffsetY = -0.5 * (textGeometry.boundingBox.max.y - textGeometry.boundingBox.min.y)

                  // Create bright blue text with Safari-compatible materials
                  const textMaterial = new THREE.MeshStandardMaterial({
                    color: 0x4185f4,
                    emissive: 0x6aa6ff,
                    emissiveIntensity: isSafari ? 1.0 : 1.5,
                    transparent: false,
                    side: THREE.DoubleSide
                  })

                  const textMesh = new THREE.Mesh(textGeometry, textMaterial)
                  textMesh.position.x = centerOffsetX
                  textMesh.position.y = centerOffsetY - 3
                  textMesh.position.z = 0
                  scene.add(textMesh)
                }
              } catch (textErr) {
                console.warn('Text geometry creation failed:', textErr)
              }
            },
            undefined,
            (err) => {
              console.warn('Font loading failed, continuing without text:', err)
            }
          )
        } catch (fontErr) {
          console.warn('Font loader initialization failed:', fontErr)
        }
        
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
        
        // Mark as loaded
        setIsLoading(false)

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
        console.error('DataUniverse initialization error:', err)
        setError(`3D Rendering Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
        setIsLoading(false)
      }
    }

    initGalaxy()
  }, [])

  if (error) {
    return (
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <p className="text-red-400 mb-2">3D Visualization Error</p>
          <p className="text-sm text-gray-400">{error}</p>
          <p className="text-xs text-gray-500 mt-2">Your browser may not support WebGL</p>
        </div>
      </div>
    )
  }

  return (
    <div className="absolute inset-0 w-full h-full">
      {isLoading && (
        <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black text-white z-10">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-sm text-gray-400">Loading 3D Visualization...</p>
          </div>
        </div>
      )}
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  )
}