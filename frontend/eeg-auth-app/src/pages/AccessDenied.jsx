import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FaExclamationTriangle, FaShieldAlt, FaChartLine } from 'react-icons/fa'
import ParticleBackground from '../components/ParticleBackground'
import ClickSpark from '../components/ClickSpark'

const AccessDenied = () => {
  const navigate = useNavigate()

  const handleViewDetails = () => {
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 relative overflow-hidden">
      {/* Particle Background */}
      <ParticleBackground />
      
      {/* Click Spark Effect */}
      <ClickSpark />

      {/* Animated Background */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 bg-red-600/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, -50, 0],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          style={{ top: '20%', left: '10%' }}
        />
        <motion.div
          className="absolute w-96 h-96 bg-orange-600/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -50, 0],
            y: [0, 50, 0],
          }}
          transition={{ duration: 12, repeat: Infinity }}
          style={{ bottom: '20%', right: '10%' }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-2xl mx-auto text-center"
      >
        <div className="glass p-12 rounded-3xl shadow-2xl border border-red-500/30">
          {/* Warning Icon */}
          <motion.div
            animate={{ 
              rotate: [0, -10, 10, -10, 10, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
            className="inline-block mb-6"
          >
            <FaExclamationTriangle className="w-24 h-24 text-red-500 mx-auto" />
          </motion.div>

          {/* Fuzzy/Glitch 404 Text */}
          <motion.div
            className="mb-6"
            animate={{
              textShadow: [
                '0 0 10px rgba(239, 68, 68, 0.8)',
                '0 0 20px rgba(239, 68, 68, 0.6)',
                '0 0 10px rgba(239, 68, 68, 0.8)',
              ]
            }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <h1 className="text-8xl font-black text-red-500 mb-2 tracking-wider">
              <motion.span
                animate={{
                  x: [-2, 2, -2, 2, 0],
                  opacity: [1, 0.8, 1, 0.8, 1]
                }}
                transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 1 }}
              >
                4
              </motion.span>
              <motion.span
                animate={{
                  y: [-2, 2, -2, 2, 0],
                  opacity: [1, 0.9, 1, 0.9, 1]
                }}
                transition={{ duration: 0.4, repeat: Infinity, repeatDelay: 1.2 }}
              >
                0
              </motion.span>
              <motion.span
                animate={{
                  x: [2, -2, 2, -2, 0],
                  opacity: [1, 0.8, 1, 0.8, 1]
                }}
                transition={{ duration: 0.35, repeat: Infinity, repeatDelay: 1.1 }}
              >
                4
              </motion.span>
            </h1>
          </motion.div>

          {/* Access Denied Text */}
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-bold text-white mb-4"
          >
            Access Denied
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-xl text-red-400 mb-6"
          >
            Authentication Failed
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-gray-300 mb-8 leading-relaxed"
          >
            Your brainwave pattern does not match our records. This could be due to:
          </motion.p>

          {/* Reasons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
            className="grid gap-4 mb-8 text-left"
          >
            {[
              { icon: FaShieldAlt, text: 'Impostor detection triggered' },
              { icon: FaChartLine, text: 'Low similarity score with registered pattern' },
              { icon: FaExclamationTriangle, text: 'Signal quality issues' },
            ].map((reason, index) => (
              <motion.div
                key={index}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 1 + index * 0.1 }}
                className="flex items-center gap-3 p-4 bg-white/5 rounded-xl border border-red-500/20"
              >
                <reason.icon className="w-5 h-5 text-red-400" />
                <span className="text-gray-300">{reason.text}</span>
              </motion.div>
            ))}
          </motion.div>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(239, 68, 68, 0.5)" }}
              whileTap={{ scale: 0.95 }}
              onClick={handleViewDetails}
              className="px-8 py-4 bg-gradient-to-r from-red-600 to-orange-600 rounded-xl font-bold text-lg shadow-xl"
            >
              View Details & Analysis
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/login')}
              className="px-8 py-4 border-2 border-red-500/50 rounded-xl font-bold text-lg hover:bg-red-500/10 transition-colors"
            >
              Try Again
            </motion.button>
          </div>

          {/* Footer Message */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="text-sm text-gray-500 mt-8"
          >
            For security reasons, this attempt has been logged
          </motion.p>
        </div>
      </motion.div>
    </div>
  )
}

export default AccessDenied
