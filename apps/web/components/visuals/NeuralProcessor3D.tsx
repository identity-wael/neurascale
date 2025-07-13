'use client'

import { useRef, useEffect, useState } from 'react'
import dynamic from 'next/dynamic'

function BabylonGPUDie() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<any>(null)
  const engineRef = useRef<any>(null)
  const [isClient, setIsClient] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    if (!isClient || !canvasRef.current) return

    let engine: any = null
    let scene: any = null

    const initBabylon = async () => {
      try {
        // Dynamically import Babylon.js modules
        const BABYLON = await import('@babylonjs/core')
        
        // Create Babylon.js engine and scene
        engine = new BABYLON.Engine(canvasRef.current, true, { preserveDrawingBuffer: true, stencil: true })
        scene = new BABYLON.Scene(engine)
        
        engineRef.current = engine
        sceneRef.current = scene

        // Set background color to black
        scene.clearColor = new BABYLON.Color3(0, 0, 0)

        // Create camera
        const camera = new BABYLON.ArcRotateCamera('camera', -Math.PI / 2, Math.PI / 2.5, 10, BABYLON.Vector3.Zero(), scene)
        camera.attachControls(canvasRef.current, true)
        camera.setTarget(BABYLON.Vector3.Zero())

        // Lighting setup
        const ambientLight = new BABYLON.HemisphericLight('ambientLight', new BABYLON.Vector3(0, 1, 0), scene)
        ambientLight.intensity = 0.4

        const directionalLight = new BABYLON.DirectionalLight('directionalLight', new BABYLON.Vector3(-1, -1, -1), scene)
        directionalLight.intensity = 1.2
        directionalLight.diffuse = new BABYLON.Color3(1, 1, 1)

        // Create GPU die components
        createGPUDie(scene, BABYLON)

        // Render loop
        engine.runRenderLoop(() => {
          scene.render()
        })

        // Handle resize
        const handleResize = () => {
          engine.resize()
        }
        window.addEventListener('resize', handleResize)

      } catch (err) {
        console.error('Babylon.js initialization error:', err)
        setError('Failed to initialize 3D graphics. Your browser may not support WebGL.')
      }
    }

    initBabylon()

    return () => {
      if (engine) {
        engine.dispose()
      }
    }
  }, [isClient])

  const createGPUDie = (scene: any, BABYLON: any) => {
    // Main GPU substrate
    const substrate = BABYLON.MeshBuilder.CreateBox('substrate', { width: 8, height: 0.4, depth: 6 }, scene)
    substrate.position.y = 0
    
    const substrateMaterial = new BABYLON.PBRMaterial('substrateMaterial', scene)
    substrateMaterial.baseColor = new BABYLON.Color3(0.25, 0.25, 0.25)
    substrateMaterial.metallic = 0.8
    substrateMaterial.roughness = 0.2
    substrateMaterial.emissiveColor = new BABYLON.Color3(0.05, 0.05, 0.05)
    substrate.material = substrateMaterial

    // Central processing core
    const core = BABYLON.MeshBuilder.CreateBox('core', { width: 3.5, height: 0.3, depth: 3.5 }, scene)
    core.position.y = 0.35
    
    const coreMaterial = new BABYLON.PBRMaterial('coreMaterial', scene)
    coreMaterial.baseColor = new BABYLON.Color3(0, 0, 0)
    coreMaterial.metallic = 0.95
    coreMaterial.roughness = 0.05
    coreMaterial.emissiveColor = new BABYLON.Color3(0, 0.1, 0)
    core.material = coreMaterial

    // Glowing center die
    const glowCore = BABYLON.MeshBuilder.CreateBox('glowCore', { width: 2.8, height: 0.15, depth: 2.8 }, scene)
    glowCore.position.y = 0.5
    
    const glowMaterial = new BABYLON.PBRMaterial('glowMaterial', scene)
    glowMaterial.baseColor = new BABYLON.Color3(0, 1, 0.53)
    glowMaterial.emissiveColor = new BABYLON.Color3(0, 0.8, 0.42)
    glowMaterial.metallic = 0.3
    glowMaterial.roughness = 0
    glowCore.material = glowMaterial

    // GPU cores grid (8x8)
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const gpuCore = BABYLON.MeshBuilder.CreateBox(`core-${row}-${col}`, { width: 0.18, height: 0.08, depth: 0.12 }, scene)
        gpuCore.position.x = (col - 3.5) * 0.32
        gpuCore.position.y = 0.55
        gpuCore.position.z = (row - 3.5) * 0.22
        
        const gpuCoreMaterial = new BABYLON.PBRMaterial(`coreMateria-${row}-${col}`, scene)
        gpuCoreMaterial.baseColor = new BABYLON.Color3(0.25, 0.52, 0.96)
        gpuCoreMaterial.emissiveColor = new BABYLON.Color3(0.1, 0.25, 0.48)
        gpuCoreMaterial.metallic = 0.6
        gpuCoreMaterial.roughness = 0.3
        gpuCore.material = gpuCoreMaterial
      }
    }

    // HBM Memory modules
    for (let i = 0; i < 6; i++) {
      const hbm = BABYLON.MeshBuilder.CreateBox(`hbm-${i}`, { width: 0.5, height: 0.6, depth: 0.5 }, scene)
      hbm.position.x = (i % 3 - 1) * 2
      hbm.position.y = 0.5
      hbm.position.z = i < 3 ? -2 : 2
      
      const hbmMaterial = new BABYLON.PBRMaterial(`hbmMaterial-${i}`, scene)
      hbmMaterial.baseColor = new BABYLON.Color3(0, 0.4, 1)
      hbmMaterial.emissiveColor = new BABYLON.Color3(0, 0.2, 0.5)
      hbmMaterial.metallic = 0.8
      hbmMaterial.roughness = 0.2
      hbm.material = hbmMaterial
    }

    // Connection pins
    const pinPositions = [
      [-3.2, 0.15, -2.2],
      [3.2, 0.15, -2.2],
      [-3.2, 0.15, 2.2],
      [3.2, 0.15, 2.2]
    ]

    pinPositions.forEach((pos, i) => {
      const pin = BABYLON.MeshBuilder.CreateSphere(`pin-${i}`, { diameter: 0.18 }, scene)
      pin.position.x = pos[0]
      pin.position.y = pos[1]
      pin.position.z = pos[2]
      
      const pinMaterial = new BABYLON.PBRMaterial(`pinMaterial-${i}`, scene)
      pinMaterial.baseColor = new BABYLON.Color3(1, 0.84, 0)
      pinMaterial.emissiveColor = new BABYLON.Color3(0.5, 0.42, 0)
      pinMaterial.metallic = 0.9
      pinMaterial.roughness = 0.1
      pin.material = pinMaterial
    })

    // NEURASCALE logo
    createNeurascaleLogo(scene, BABYLON)
  }

  const createNeurascaleLogo = (scene: any, BABYLON: any) => {
    // Create dynamic texture for text
    const textTexture = new BABYLON.DynamicTexture('textTexture', { width: 512, height: 128 }, scene)
    textTexture.hasAlpha = true
    
    // Create text on texture
    const font = 'bold 40px Arial'
    textTexture.drawText('NEURASCALE', null, null, font, '#4185f4', 'transparent', true)
    
    // Create plane for logo
    const logoPlane = BABYLON.MeshBuilder.CreatePlane('logoPlane', { width: 2.5, height: 0.6 }, scene)
    logoPlane.position.y = 0.22
    logoPlane.position.z = -2.2
    logoPlane.rotation.x = Math.PI / 2
    
    const logoMaterial = new BABYLON.StandardMaterial('logoMaterial', scene)
    logoMaterial.diffuseTexture = textTexture
    logoMaterial.emissiveTexture = textTexture
    logoMaterial.emissiveColor = new BABYLON.Color3(0.25, 0.52, 0.96)
    logoMaterial.opacityTexture = textTexture
    logoPlane.material = logoMaterial
  }

  if (error) {
    return (
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <p className="text-red-400 mb-2">3D Graphics Error</p>
          <p className="text-sm text-gray-400">{error}</p>
        </div>
      </div>
    )
  }

  if (!isClient) {
    return (
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <p className="text-blue-400">Loading 3D Engine...</p>
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

export default function NeuralProcessor3D() {
  return <BabylonGPUDie />
}