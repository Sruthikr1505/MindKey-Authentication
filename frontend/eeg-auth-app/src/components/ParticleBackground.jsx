import { useEffect, useRef, useState } from 'react'

const ParticleBackground = ({
  particleColors = ['#a855f7', '#8b5cf6'],
  particleCount = 200,
  particleSpread = 10,
  speed = 0.1,
  particleBaseSize = 100,
  moveParticlesOnHover = true,
  alphaParticles = false,
  disableRotation = false,
}) => {
  const canvasRef = useRef(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const particles = []

    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width
        this.y = Math.random() * canvas.height
        this.size = (Math.random() * particleBaseSize) / 50 + 1
        this.baseSpeedX = (Math.random() - 0.5) * speed
        this.baseSpeedY = (Math.random() - 0.5) * speed
        this.speedX = this.baseSpeedX
        this.speedY = this.baseSpeedY
        this.color = particleColors[Math.floor(Math.random() * particleColors.length)]
        this.opacity = alphaParticles ? Math.random() * 0.5 + 0.3 : 0.6
        this.rotation = 0
        this.rotationSpeed = disableRotation ? 0 : (Math.random() - 0.5) * 0.02
      }

      update(mouseX, mouseY) {
        // Mouse interaction
        if (moveParticlesOnHover) {
          const dx = mouseX - this.x
          const dy = mouseY - this.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          const maxDistance = 100

          if (distance < maxDistance) {
            const force = (maxDistance - distance) / maxDistance
            this.speedX = this.baseSpeedX - (dx / distance) * force * 2
            this.speedY = this.baseSpeedY - (dy / distance) * force * 2
          } else {
            this.speedX = this.baseSpeedX
            this.speedY = this.baseSpeedY
          }
        }

        this.x += this.speedX
        this.y += this.speedY
        this.rotation += this.rotationSpeed

        // Wrap around screen
        if (this.x > canvas.width + particleSpread) this.x = -particleSpread
        if (this.x < -particleSpread) this.x = canvas.width + particleSpread
        if (this.y > canvas.height + particleSpread) this.y = -particleSpread
        if (this.y < -particleSpread) this.y = canvas.height + particleSpread
      }

      draw() {
        ctx.save()
        ctx.translate(this.x, this.y)
        ctx.rotate(this.rotation)
        
        ctx.fillStyle = this.color
        ctx.globalAlpha = this.opacity
        ctx.beginPath()
        ctx.arc(0, 0, this.size, 0, Math.PI * 2)
        ctx.fill()
        
        ctx.restore()
      }
    }

    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle())
    }

    // Animation loop
    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      particles.forEach(particle => {
        particle.update(mousePos.x, mousePos.y)
        particle.draw()
      })

      // Draw connections
      particles.forEach((a, i) => {
        particles.slice(i + 1).forEach(b => {
          const dx = a.x - b.x
          const dy = a.y - b.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 120) {
            ctx.strokeStyle = `rgba(139, 92, 246, ${0.15 * (1 - distance / 120)})`
            ctx.lineWidth = 0.5
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.stroke()
          }
        })
      })

      requestAnimationFrame(animate)
    }

    animate()

    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('resize', handleResize)
    if (moveParticlesOnHover) {
      window.addEventListener('mousemove', handleMouseMove)
    }

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [mousePos, particleColors, particleCount, particleSpread, speed, particleBaseSize, moveParticlesOnHover, alphaParticles, disableRotation])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 1 }}
    />
  )
}

export default ParticleBackground
