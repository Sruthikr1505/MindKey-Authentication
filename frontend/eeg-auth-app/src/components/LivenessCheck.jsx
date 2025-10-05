import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FaBrain, FaEye, FaHandPaper } from 'react-icons/fa'

const LivenessCheck = ({ onComplete }) => {
  const [currentChallenge, setCurrentChallenge] = useState(0)
  const [progress, setProgress] = useState(0)
  const [isCompleted, setIsCompleted] = useState(false)

  const challenges = [
    {
      icon: <FaBrain className="w-16 h-16" />,
      title: 'Think of a Number',
      instruction: 'Think of any number between 1 and 10',
      duration: 3000,
    },
    {
      icon: <FaEye className="w-16 h-16" />,
      title: 'Close Your Eyes',
      instruction: 'Close your eyes for 3 seconds',
      duration: 3000,
    },
    {
      icon: <FaHandPaper className="w-16 h-16" />,
      title: 'Relax',
      instruction: 'Take a deep breath and relax',
      duration: 3000,
    },
  ]

  useEffect(() => {
    if (currentChallenge >= challenges.length) {
      setIsCompleted(true)
      setTimeout(() => onComplete(true), 1000)
      return
    }

    const duration = challenges[currentChallenge].duration
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setTimeout(() => {
            setCurrentChallenge((c) => c + 1)
            setProgress(0)
          }, 500)
          return 100
        }
        return prev + (100 / (duration / 100))
      })
    }, 100)

    return () => clearInterval(interval)
  }, [currentChallenge, challenges, onComplete])

  if (isCompleted) {
    return (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="text-center p-8"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1 }}
        >
          <FaBrain className="w-24 h-24 text-green-500 mx-auto mb-4" />
        </motion.div>
        <h3 className="text-2xl font-bold text-green-500">Liveness Verified!</h3>
      </motion.div>
    )
  }

  return (
    <div className="glass p-8 rounded-3xl">
      <h2 className="text-2xl font-bold text-center mb-6 gradient-text">
        Liveness Detection
      </h2>
      
      <div className="mb-6 text-center text-sm text-gray-400">
        Challenge {currentChallenge + 1} of {challenges.length}
      </div>

      <AnimatePresence mode="wait">
        {currentChallenge < challenges.length && (
          <motion.div
            key={currentChallenge}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="text-center"
          >
            <motion.div
              className="text-violet-500 mb-6 mx-auto"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {challenges[currentChallenge].icon}
            </motion.div>
            
            <h3 className="text-xl font-bold mb-2">
              {challenges[currentChallenge].title}
            </h3>
            <p className="text-gray-300 mb-6">
              {challenges[currentChallenge].instruction}
            </p>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-violet-600 to-purple-600"
                style={{ width: `${progress}%` }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default LivenessCheck
