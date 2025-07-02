'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export default function NeuralAnimation() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    const container = containerRef.current

    let scene: THREE.Scene
    let camera: THREE.PerspectiveCamera
    let renderer: THREE.WebGLRenderer
    let controls: OrbitControls
    const neurons: THREE.Mesh[][] = []
    const connections: THREE.Line[] = []

    const config = {
      layers: [16, 32, 16, 4],
      neuronRadius: 0.8,
      neuronColor: 0x00ffff,
      activeNeuronColor: 0xffffff,
      connectionColor: 0x00ffff,
      activeConnectionColor: 0xffa500,
      layerSpacing: 30,
      neuronSpacing: 6,
      pulseSpeed: 0.05,
      pulseDecay: 0.98,
      activationThreshold: 0.8,
      connectionPulseIntensity: 0.5,
    }

    function init() {
      scene = new THREE.Scene()
      scene.background = new THREE.Color(0x0a0a0a)

      const width = container.clientWidth
      const height = container.clientHeight

      camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      camera.position.set(
        0,
        0,
        (config.layerSpacing * config.layers.length) / 2 + 50
      )

      renderer = new THREE.WebGLRenderer({ antialias: true })
      renderer.setSize(width, height)
      container.appendChild(renderer.domElement)

      controls = new OrbitControls(camera, renderer.domElement)
      controls.enableDamping = true
      controls.dampingFactor = 0.05
      controls.screenSpacePanning = false
      controls.minDistance = 50
      controls.maxDistance = 300

      createNeuralNetwork()

      const ambientLight = new THREE.AmbientLight(0x404040)
      scene.add(ambientLight)
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5)
      directionalLight.position.set(1, 1, 1).normalize()
      scene.add(directionalLight)

      window.addEventListener('resize', onWindowResize)
      animate()
    }

    function createNeuralNetwork() {
      const neuronGeometry = new THREE.SphereGeometry(
        config.neuronRadius,
        16,
        16
      )
      const baseNeuronMaterial = new THREE.MeshBasicMaterial({
        color: config.neuronColor,
        transparent: true,
        opacity: 0.7,
      })

      for (let i = 0; i < config.layers.length; i++) {
        const layerNeurons: THREE.Mesh[] = []
        const numNeuronsInLayer = config.layers[i]
        const layerOffsetZ =
          i * config.layerSpacing -
          ((config.layers.length - 1) * config.layerSpacing) / 2

        for (let j = 0; j < numNeuronsInLayer; j++) {
          const x = (j - (numNeuronsInLayer - 1) / 2) * config.neuronSpacing
          const y = 0
          const z = layerOffsetZ

          const neuron = new THREE.Mesh(neuronGeometry, baseNeuronMaterial.clone())
          neuron.position.set(x, y, z)
          ;(neuron as any).userData = {
            layerIndex: i,
            neuronIndex: j,
            activation: 0,
            baseColor: new THREE.Color(config.neuronColor),
          }
          scene.add(neuron)
          layerNeurons.push(neuron)
        }
        neurons.push(layerNeurons)
      }

      for (let i = 0; i < neurons.length - 1; i++) {
        const currentLayer = neurons[i]
        const nextLayer = neurons[i + 1]

        for (const fromNeuron of currentLayer) {
          for (const toNeuron of nextLayer) {
            const material = new THREE.LineBasicMaterial({
              color: config.connectionColor,
              transparent: true,
              opacity: 0.3,
              linewidth: 1,
            })
            const points = [fromNeuron.position, toNeuron.position]
            const geometry = new THREE.BufferGeometry().setFromPoints(points)
            const connection = new THREE.Line(geometry, material)
            ;(connection as any).userData = {
              fromNeuron,
              toNeuron,
              activation: 0,
              baseColor: new THREE.Color(config.connectionColor),
            }
            scene.add(connection)
            connections.push(connection)
          }
        }
      }
    }

    function animate() {
      controls.update()

      for (let i = 0; i < neurons.length; i++) {
        for (let j = 0; j < neurons[i].length; j++) {
          const neuron: any = neurons[i][j]
          neuron.userData.activation *= config.pulseDecay

          if (i === 0) {
            if (Math.random() < 0.005) {
              neuron.userData.activation = 1
            }
          } else {
            let sumPrevActivation = 0
            connections.forEach(conn => {
              const data: any = conn.userData
              if (
                data.toNeuron === neuron &&
                (data.fromNeuron as any).userData.activation > 0.1
              ) {
                sumPrevActivation += (data.fromNeuron as any).userData.activation
              }
            })
            if (
              sumPrevActivation > config.activationThreshold &&
              Math.random() < 0.1
            ) {
              neuron.userData.activation = Math.min(
                1,
                sumPrevActivation * 0.5
              )
            }
          }

          const activeColor = new THREE.Color(config.activeNeuronColor)
          const currentColor = neuron.userData.baseColor
            .clone()
            .lerp(activeColor, neuron.userData.activation)
          ;(neuron.material as THREE.MeshBasicMaterial).color.copy(currentColor)
          ;(neuron.material as THREE.MeshBasicMaterial).opacity =
            0.7 + neuron.userData.activation * 0.3
          neuron.scale.setScalar(1 + neuron.userData.activation * 0.5)
        }
      }

      connections.forEach(connection => {
        const data: any = connection.userData
        const fromNeuron: any = data.fromNeuron
        const toNeuron: any = data.toNeuron

        if (
          fromNeuron.userData.activation > 0.1 &&
          toNeuron.userData.activation > 0.1
        ) {
          data.activation = Math.min(
            1,
            fromNeuron.userData.activation * config.connectionPulseIntensity
          )
        } else {
          data.activation *= config.pulseDecay
        }

        const activeColor = new THREE.Color(config.activeConnectionColor)
        const currentColor = data.baseColor
          .clone()
          .lerp(activeColor, data.activation)
        ;(connection.material as THREE.LineBasicMaterial).color.copy(currentColor)
        ;(connection.material as THREE.LineBasicMaterial).opacity =
          0.3 + data.activation * 0.7
      })

      renderer.render(scene, camera)
      requestAnimationFrame(animate)
    }

    function onWindowResize() {
      const width = container.clientWidth
      const height = container.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }

    init()

    return () => {
      window.removeEventListener('resize', onWindowResize)
      container.innerHTML = ''
    }
  }, [])

  return <div ref={containerRef} className="w-full h-[60vh]" />
}

