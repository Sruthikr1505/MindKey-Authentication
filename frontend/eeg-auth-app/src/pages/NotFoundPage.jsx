import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { FaBrain } from 'react-icons/fa'
import AnimatedBackground from '../components/AnimatedBackground'

const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <AnimatedBackground />
      
      <div className="relative z-10 flex items-center justify-center min-h-screen px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <FaBrain className="w-32 h-32 text-violet-500 mx-auto mb-8" />
          </motion.div>
          
          <motion.h1
            className="text-9xl font-bold gradient-text mb-4"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
          >
            404
          </motion.h1>
          
          <h2 className="text-3xl font-bold mb-4">Page Not Found</h2>
          <p className="text-gray-400 mb-8 max-w-md mx-auto">
            The page you're looking for doesn't exist in our neural network.
            Let's get you back on track.
          </p>
          
          <Link to="/">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-gradient-to-r from-violet-600 to-purple-600 rounded-xl font-semibold shadow-lg hover:shadow-violet-500/50 transition-all"
            >
              Return Home
            </motion.button>
          </Link>
        </motion.div>
      </div>
    </div>
  )
}

export default NotFoundPage
