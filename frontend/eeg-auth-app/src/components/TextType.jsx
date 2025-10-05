import { useState, useEffect } from 'react'

const TextType = ({ 
  text = [], 
  typingSpeed = 75, 
  pauseDuration = 1500, 
  showCursor = true, 
  cursorCharacter = "|",
  className = "",
  onComplete = null
}) => {
  const [displayedText, setDisplayedText] = useState('')
  const [currentTextIndex, setCurrentTextIndex] = useState(0)
  const [currentCharIndex, setCurrentCharIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    if (text.length === 0) return

    const currentFullText = text[currentTextIndex]

    if (isPaused) {
      const pauseTimeout = setTimeout(() => {
        setIsPaused(false)
        // After showing complete word, trigger onComplete
        if (onComplete && currentTextIndex === 0) {
          onComplete()
        }
      }, pauseDuration)
      return () => clearTimeout(pauseTimeout)
    }

    if (!isDeleting && currentCharIndex < currentFullText.length) {
      // Typing forward
      const timeout = setTimeout(() => {
        setDisplayedText(currentFullText.substring(0, currentCharIndex + 1))
        setCurrentCharIndex(currentCharIndex + 1)
      }, typingSpeed)
      return () => clearTimeout(timeout)
    } else if (!isDeleting && currentCharIndex === currentFullText.length) {
      // Finished typing, pause
      setIsPaused(true)
    }
  }, [currentCharIndex, currentTextIndex, isDeleting, isPaused, text, typingSpeed, pauseDuration, onComplete])

  return (
    <div className={className}>
      {displayedText}
      {showCursor && (
        <span className="animate-pulse">{cursorCharacter}</span>
      )}
    </div>
  )
}

export default TextType
