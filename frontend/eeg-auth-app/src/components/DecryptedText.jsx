import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const DecryptedText = ({ text, className = '' }) => {
  const [displayText, setDisplayText] = useState('')
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
  
  useEffect(() => {
    let iteration = 0
    const interval = setInterval(() => {
      setDisplayText(
        text
          .split('')
          .map((char, index) => {
            if (index < iteration) {
              return text[index]
            }
            if (char === ' ') return ' '
            return characters[Math.floor(Math.random() * characters.length)]
          })
          .join('')
      )
      
      if (iteration >= text.length) {
        clearInterval(interval)
      }
      
      iteration += 1 / 3
    }, 30)
    
    return () => clearInterval(interval)
  }, [text])
  
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {displayText}
    </motion.div>
  )
}

export default DecryptedText
