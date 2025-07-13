import React, { useEffect, useRef } from 'react'

interface WavesProps {
  lineColor?: string
  backgroundColor?: string
  waveSpeedX?: number
  waveSpeedY?: number
  waveAmpX?: number
  waveAmpY?: number
  friction?: number
  tension?: number
  maxCursorMove?: number
  xGap?: number
  yGap?: number
}

export default function Waves({
  lineColor = '#fff',
  backgroundColor = 'rgba(255, 255, 255, 0.2)',
  waveSpeedX = 0.02,
  waveSpeedY = 0.01,
  waveAmpX = 40,
  waveAmpY = 20,
  friction = 0.9,
  tension = 0.01,
  maxCursorMove = 120,
  xGap = 12,
  yGap = 36,
}: WavesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const cursor = useRef({ x: 0, y: 0 })
  const offset = useRef({ x: 0, y: 0 })
  const frame = useRef<number>()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let width = canvas.clientWidth
    let height = canvas.clientHeight
    canvas.width = width
    canvas.height = height
    let time = 0

    const handleResize = () => {
      width = canvas.clientWidth
      height = canvas.clientHeight
      canvas.width = width
      canvas.height = height
    }

    const handleMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left - width / 2
      const y = e.clientY - rect.top - height / 2
      cursor.current.x = Math.max(-maxCursorMove, Math.min(maxCursorMove, x))
      cursor.current.y = Math.max(-maxCursorMove, Math.min(maxCursorMove, y))
    }

    window.addEventListener('resize', handleResize)
    window.addEventListener('mousemove', handleMove)

    const draw = () => {
      offset.current.x += (cursor.current.x - offset.current.x) * tension
      offset.current.y += (cursor.current.y - offset.current.y) * tension
      offset.current.x *= friction
      offset.current.y *= friction

      ctx.fillStyle = backgroundColor
      ctx.fillRect(0, 0, width, height)
      ctx.strokeStyle = lineColor
      ctx.lineWidth = 1

      // vertical lines
      for (let x = 0; x <= width; x += xGap) {
        ctx.beginPath()
        for (let y = 0; y <= height; y += 4) {
          const dx = Math.sin(y * waveSpeedX + time) * waveAmpX + offset.current.x
          const xpos = x + dx
          if (y === 0) ctx.moveTo(xpos, y)
          else ctx.lineTo(xpos, y)
        }
        ctx.stroke()
      }

      // horizontal lines
      for (let y = 0; y <= height; y += yGap) {
        ctx.beginPath()
        for (let x = 0; x <= width; x += 4) {
          const dy = Math.sin(x * waveSpeedY + time) * waveAmpY + offset.current.y
          const ypos = y + dy
          if (x === 0) ctx.moveTo(x, ypos)
          else ctx.lineTo(x, ypos)
        }
        ctx.stroke()
      }

      time += 0.016
      frame.current = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      if (frame.current) cancelAnimationFrame(frame.current)
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', handleMove)
    }
  }, [backgroundColor, friction, lineColor, tension, waveAmpX, waveAmpY, waveSpeedX, waveSpeedY, xGap, yGap, maxCursorMove])

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
}
