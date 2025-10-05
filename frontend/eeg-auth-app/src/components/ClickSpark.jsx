import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const ClickSpark = () => {
  const [sparks, setSparks] = useState([])

  useEffect(() => {
    const handleClick = (e) => {
      const newSpark = {
        id: Date.now(),
        x: e.clientX,
        y: e.clientY,
      }
      setSparks(prev => [...prev, newSpark])
      
      // Remove spark after animation
      setTimeout(() => {
        setSparks(prev => prev.filter(spark => spark.id !== newSpark.id))
      }, 1000)
    }

    window.addEventListener('click', handleClick)
    return () => window.removeEventListener('click', handleClick)
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 9999 }}>
      <AnimatePresence>
        {sparks.map(spark => (
          <div key={spark.id} style={{ position: 'absolute', left: spark.x, top: spark.y }}>
            {/* Brain/Neuron particles */}
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-violet-500 rounded-full"
                initial={{ 
                  x: 0, 
                  y: 0, 
                  scale: 1,
                  opacity: 1 
                }}
                animate={{
                  x: Math.cos((i * Math.PI * 2) / 8) * 50,
                  y: Math.sin((i * Math.PI * 2) / 8) * 50,
                  scale: 0,
                  opacity: 0,
                }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              />
            ))}
            
            {/* Center pulse */}
            <motion.div
              className="absolute w-4 h-4 border-2 border-violet-500 rounded-full"
              initial={{ scale: 0, opacity: 1 }}
              animate={{ scale: 3, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              style={{ transform: 'translate(-50%, -50%)' }}
            />
            
            {/* Brain wave effect */}
            <motion.div
              className="absolute"
              initial={{ scale: 0, opacity: 1 }}
              animate={{ scale: 2, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              style={{ transform: 'translate(-50%, -50%)' }}
            >
              <svg width="40" height="40" viewBox="0 0 40 40">
                <path
                  d="M20,20 Q25,15 30,20 T40,20"
                  stroke="rgba(139, 92, 246, 0.6)"
                  strokeWidth="2"
                  fill="none"
                />
                <path
                  d="M20,20 Q15,25 10,20 T0,20"
                  stroke="rgba(139, 92, 246, 0.6)"
                  strokeWidth="2"
                  fill="none"
                />
              </svg>
            </motion.div>
          </div>
        ))}
      </AnimatePresence>
    </div>
  )
}

export default ClickSpark
