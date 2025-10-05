import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const TypingText = ({ text, className = '', delay = 0, speed = 100 }) => {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const startTimeout = setTimeout(() => {
      if (currentIndex < text.length) {
        const timeout = setTimeout(() => {
          setDisplayedText(prev => prev + text[currentIndex])
          setCurrentIndex(prev => prev + 1)
        }, speed)
        return () => clearTimeout(timeout)
      }
    }, delay * 1000)

    return () => clearTimeout(startTimeout)
  }, [currentIndex, text, delay, speed])

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {displayedText}
      {currentIndex < text.length && (
        <motion.span
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="inline-block ml-1"
        >
          |
        </motion.span>
      )}
    </motion.div>
  )
}

export default TypingText
