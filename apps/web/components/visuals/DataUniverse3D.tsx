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
        const isChrome = /chrome/i.test(navigator.userAgent) && !isSafari
        const hasWebGPU = 'gpu' in navigator && navigator.gpu
        
        console.log('Browser detection:', { isSafari, isChrome, hasWebGPU, userAgent: navigator.userAgent })

        // Dynamic import of Three.js modules
        const THREE = await import('three')
        const { FontLoader } = await import('three/addons/loaders/FontLoader.js')
        const { TextGeometry } = await import('three/addons/geometries/TextGeometry.js')

        if (!canvasRef.current) return

        // Initialize renderer: Force WebGPU for Chrome, WebGL for Safari
        let renderer: any
        
        if (isChrome && hasWebGPU) {
          try {
            console.log('Attempting WebGPU initialization for Chrome...')
            
            // Test WebGPU availability first
            const adapter = await navigator.gpu.requestAdapter()
            if (!adapter) {
              throw new Error('No WebGPU adapter available')
            }
            
            const device = await adapter.requestDevice()
            if (!device) {
              throw new Error('WebGPU device creation failed')
            }
            
            // Import and initialize WebGPU renderer
            const WebGPURenderer = await import('three/examples/jsm/renderers/webgpu/WebGPURenderer.js')
            renderer = new WebGPURenderer.WebGPURenderer({
              canvas: canvasRef.current,
              antialias: true
            })
            
            await renderer.init()
            console.log('✅ Successfully using WebGPU renderer')
            
          } catch (webgpuError) {
            console.log('❌ WebGPU failed, falling back to WebGL:', webgpuError)
            // Fallback to high-performance WebGL for Chrome
            const rendererOptions = {
              canvas: canvasRef.current,
              antialias: true,
              alpha: true,
              preserveDrawingBuffer: false,
              powerPreference: 'high-performance' as WebGLPowerPreference
            }
            renderer = new THREE.WebGLRenderer(rendererOptions)
            console.log('🔄 Using WebGL renderer (Chrome fallback)')
          }
        } else {
          // Use WebGL for Safari and non-Chrome browsers
          const rendererOptions = {
            canvas: canvasRef.current,
            antialias: !isSafari,
            alpha: true,
            preserveDrawingBuffer: false,
            powerPreference: isSafari ? 'default' : 'high-performance' as WebGLPowerPreference
          }
          renderer = new THREE.WebGLRenderer(rendererOptions)
          console.log('🌐 Using WebGL renderer (Safari/other browsers)')
        }
        
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isSafari ? 1 : 2))
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

        // Galaxy parameters: Full quality for Chrome, optimized for Safari
        const parameters = {
          count: isSafari ? 50000 : (isChrome ? 150000 : 100000), // Max particles for Chrome
          size: isSafari ? 0.015 : 0.01,
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

        // Skip 3D text on Safari to avoid positioning issues
        if (!isSafari) {
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
                    curveSegments: 12,
                    bevelEnabled: true,
                    bevelThickness: 0.02,
                    bevelSize: 0.02,
                    bevelOffset: 0,
                    bevelSegments: 3,
                  })

                  textGeometry.computeBoundingBox()
                  if (textGeometry.boundingBox) {
                    const centerOffsetX = -0.5 * (textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x)
                    const centerOffsetY = -0.5 * (textGeometry.boundingBox.max.y - textGeometry.boundingBox.min.y)

                    const textMaterial = new THREE.MeshStandardMaterial({
                      color: 0x4185f4,
                      emissive: 0x6aa6ff,
                      emissiveIntensity: 1.5,
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