import { useState } from 'react'
import { motion } from 'framer-motion'
import { FaBrain } from 'react-icons/fa'
import TextType from './TextType'

const SplashScreen = ({ onComplete }) => {
  const [showLoadingBar, setShowLoadingBar] = useState(false)
  const [showInitializing, setShowInitializing] = useState(false)

  const handleTypingComplete = () => {
    // Show "Initializing..." immediately after MindKey is fully typed
    setTimeout(() => {
      setShowInitializing(true)
    }, 100)
    
    // Show loading bar after initializing message
    setTimeout(() => {
      setShowLoadingBar(true)
    }, 400)
    
    // Complete splash screen after loading bar finishes
    setTimeout(() => {
      onComplete()
    }, 2800)
  }
  
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black"
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="absolute inset-0 overflow-hidden bg-gradient-to-br from-black via-violet-950/20 to-black">
        {/* Dense Continuous Falling Code Rain Effect */}
        {[...Array(50)].map((_, i) => {
          const characters = ['0', '1', 'M', 'i', 'n', 'd', 'K', 'e', 'y', '{', '}', '<', '>', '/', '*', 'A', 'B', 'C', 'X', 'Y', 'Z']
          const xPos = (i * 2) + Math.random() * 1.5
          
          return (
            <motion.div
              key={i}
              className="absolute text-violet-400/40 font-mono text-xs"
              style={{
                left: `${xPos}%`,
                textShadow: '0 0 15px rgba(139, 92, 246, 0.6)',
              }}
              initial={{
                y: -50,
                opacity: 0,
              }}
              animate={{
                y: window.innerHeight + 50,
                opacity: [0, 0.8, 1, 0.8, 0],
              }}
              transition={{
                duration: Math.random() * 2 + 3,
                repeat: Infinity,
                delay: Math.random() * 3,
                ease: 'linear',
              }}
            >
              {Array.from({ length: 15 }, (_, j) => (
                <div key={j} className="mb-1">
                  {characters[Math.floor(Math.random() * characters.length)]}
                </div>
              ))}
            </motion.div>
          )
        })}
        
        {/* Floating particles */}
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={`particle-${i}`}
            className="absolute w-1 h-1 bg-violet-400/20 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
        
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/50 to-black/80" />
      </div>

      {/* Logo and Text */}
      <div className="relative z-10 text-center">
        <motion.div
          animate={{ scale: 1, rotate: 0 }}
        >
          <FaBrain className="w-32 h-32 mx-auto text-violet-500 mb-8" />
        </motion.div>

        <div className="mb-6">
          <TextType
            text={["MindKey"]}
            typingSpeed={75}
            pauseDuration={1500}
            showCursor={true}
            cursorCharacter="|"
            className="text-6xl font-bold gradient-text"
            onComplete={handleTypingComplete}
          />
        </div>

        {showInitializing && (
          <motion.p
            className="text-xl text-gray-300"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            Initializing Neural Authentication...
          </motion.p>
        )}

        {/* Loading Bar */}
        {showLoadingBar && (
          <motion.div
            className="w-64 h-1 bg-white/20 rounded-full mx-auto mt-8 overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <motion.div
              className="h-full bg-gradient-to-r from-violet-600 to-purple-600"
              initial={{ width: '0%' }}
              animate={{ width: '100%' }}
              transition={{ duration: 2, ease: 'easeInOut' }}
            />
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default SplashScreen
