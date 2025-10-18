import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { FaUser, FaLock, FaBrain, FaArrowLeft, FaHome, FaEye, FaEyeSlash } from 'react-icons/fa'
import { HiUpload } from 'react-icons/hi'
import toast, { Toaster } from 'react-hot-toast'
import axios from 'axios'
import ParticleBackground from '../components/ParticleBackground'
import ClickSpark from '../components/ClickSpark'
const LoginPage = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [eegFile, setEegFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isRegisterMode, setIsRegisterMode] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [usernameError, setUsernameError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const API_URL = 'http://localhost:8000'

  // Validation functions
  const validateUsername = (value) => {
    if (value.length < 3) {
      setUsernameError('Username must be at least 3 characters')
      return false
    }
    if (value.length > 20) {
      setUsernameError('Username must be less than 20 characters')
      return false
    }
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      setUsernameError('Username can only contain letters, numbers, and underscores')
      return false
    }
    setUsernameError('')
    return true
  }

  const validatePassword = (value) => {
    if (value.length < 8) {
      setPasswordError('Password must be at least 8 characters')
      return false
    }
    if (!/(?=.*[a-z])/.test(value)) {
      setPasswordError('Password must contain at least one lowercase letter')
      return false
    }
    if (!/(?=.*[A-Z])/.test(value)) {
      setPasswordError('Password must contain at least one uppercase letter')
      return false
    }
    if (!/(?=.*\d)/.test(value)) {
      setPasswordError('Password must contain at least one number')
      return false
    }
    setPasswordError('')
    return true
  }

  const handleUsernameChange = (e) => {
    const value = e.target.value
    setUsername(value)
    if (value) validateUsername(value)
  }

  const handlePasswordChange = (e) => {
    const value = e.target.value
    setPassword(value)
    if (value) validatePassword(value)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setEegFile(e.dataTransfer.files[0])
      toast.success('EEG file uploaded!')
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setEegFile(e.target.files[0])
      toast.success('EEG file uploaded!')
    }
  }

  const handleAuth = async (e) => {
    e.preventDefault()
    
    if (!username || !password || !eegFile) {
      toast.error('Please fill in all fields and upload an EEG file')
      return
    }

    // Validate before submitting
    const isUsernameValid = validateUsername(username)
    const isPasswordValid = validatePassword(password)
    
    if (!isUsernameValid || !isPasswordValid) {
      toast.error('Please fix the validation errors')
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    try {
      if (isRegisterMode) {
        // Registration/Enrollment mode
        formData.append('enrollment_trials', eegFile)
        
        const response = await axios.post(`${API_URL}/register`, formData)
        
        if (response.data.success) {
          toast.success('Enrollment successful! You can now sign in.')
          // Switch to login mode
          setIsRegisterMode(false)
          setEegFile(null)
        } else {
          toast.error(response.data.message || 'Enrollment failed')
        }
      } else {
        // Authentication mode
        formData.append('probe_trial', eegFile)
        
        const response = await axios.post(`${API_URL}/auth/login`, formData)
        
        if (response.data.authenticated) {
          toast.success('Authentication successful!')
          localStorage.setItem('authResult', JSON.stringify(response.data))
          setTimeout(() => navigate('/dashboard'), 1000)
        } else {
          // Store failed auth result for access denied page
          localStorage.setItem('authResult', JSON.stringify(response.data))
          toast.error('Access Denied - Impostor Detected')
          setTimeout(() => navigate('/access-denied'), 1500)
        }
      }
    } catch (error) {
      console.error('Authentication error:', error)
      toast.error((isRegisterMode ? 'Enrollment' : 'Authentication') + ' failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full bg-black flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12 relative overflow-hidden transition-all duration-300" style={{ width: '100vw', minWidth: '100vw' }}>
      {/* Particle Background */}
      <ParticleBackground />
      
      {/* Click Spark Effect */}
      <ClickSpark />
      
      <Toaster position="top-right" toastOptions={{
        style: {
          background: '#1a1a1a',
          color: '#fff',
          border: '1px solid rgba(139, 92, 246, 0.3)',
        },
      }} />

      {/* Back to Home Button */}
      <Link to="/">
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          whileHover={{ scale: 1.05, x: -5 }}
          whileTap={{ scale: 0.95 }}
          className="fixed top-6 left-6 z-50 flex items-center gap-2 px-4 py-2 glass border border-violet-500/30 rounded-full font-semibold hover:bg-violet-500/20 transition-all"
        >
          <FaArrowLeft className="w-4 h-4" />
          <span className="hidden sm:inline">Back to Home</span>
          <FaHome className="w-4 h-4 sm:hidden" />
        </motion.button>
      </Link>

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute w-96 h-96 bg-violet-600/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, -50, 0],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          style={{ top: '20%', left: '10%' }}
        />
        <motion.div
          className="absolute w-96 h-96 bg-purple-600/20 rounded-full blur-3xl"
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
        transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
        className="relative z-10 w-full max-w-md mx-auto"
      >
        <div className="glass p-6 sm:p-8 rounded-3xl shadow-2xl border border-violet-500/20 transition-all duration-300 hover:border-violet-500/40">
          {/* Header */}
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="inline-block mb-4"
            >
              <FaBrain className="w-16 h-16 text-violet-500" />
            </motion.div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              {isRegisterMode ? 'Brain Enrollment' : 'Brain Authentication'}
            </h1>
            <p className="text-gray-300">
              {isRegisterMode ? 'Enroll with your unique brainwave pattern' : 'Secure login with your thoughts'}
            </p>
          </motion.div>

          {/* Form */}
          <form onSubmit={handleAuth} className="space-y-6">
            {/* Username */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <label className="block text-sm font-medium mb-2">Username</label>
              <div className="relative">
                <FaUser className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={username}
                  onChange={handleUsernameChange}
                  className={`w-full pl-12 pr-4 py-3 bg-white/10 border ${usernameError ? 'border-red-500' : 'border-white/20'} rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all`}
                  placeholder="Enter username (3-20 chars, alphanumeric)"
                  required
                />
              </div>
              {usernameError && (
                <p className="text-red-400 text-sm mt-1">{usernameError}</p>
              )}
            </motion.div>

            {/* Password */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <FaLock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={handlePasswordChange}
                  className={`w-full pl-12 pr-12 py-3 bg-white/10 border ${passwordError ? 'border-red-500' : 'border-white/20'} rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all`}
                  placeholder="Enter password (8+ chars, uppercase, lowercase, number)"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <FaEye /> : <FaEyeSlash />}
                </button>
              </div>
              {passwordError && (
                <p className="text-red-400 text-sm mt-1">{passwordError}</p>
              )}
            </motion.div>

            {/* EEG File Upload */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-sm font-medium">EEG Signal (Preprocessed Trial)</label>
                <div className="group relative">
                  <svg className="w-4 h-4 text-violet-400 cursor-help" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="invisible group-hover:visible absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl border border-violet-500/30 z-10">
                    <p className="font-semibold mb-1">Upload preprocessed DEAP trials:</p>
                    <p className="mb-1">• Genuine: Same subject (e.g., s01_trial03.npy for user enrolled with s01)</p>
                    <p>• Impostor: Different subject (e.g., s02_trial00.npy)</p>
                    <p className="mt-2 text-violet-300">Files located in: data/processed/</p>
                  </div>
                </div>
              </div>
              <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                  dragActive
                    ? 'border-purple-500 bg-purple-500/20'
                    : 'border-white/20 hover:border-white/40'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  accept=".npy"
                  onChange={handleFileChange}
                  className="hidden"
                  id="eeg-upload"
                />
                <label htmlFor="eeg-upload" className="cursor-pointer">
                  <HiUpload className="w-12 h-12 mx-auto mb-3 text-purple-400" />
                  {eegFile ? (
                    <p className="text-green-400 font-medium">{eegFile.name}</p>
                  ) : (
                    <>
                      <p className="text-gray-300 mb-1">Drop EEG file here or click to upload</p>
                      <p className="text-sm text-gray-500">.npy files only</p>
                    </>
                  )}
                </label>
              </div>
            </motion.div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl font-bold text-lg shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="inline-block w-6 h-6 border-3 border-white border-t-transparent rounded-full"
                />
              ) : (
                isRegisterMode ? 'Enroll Now' : 'Authenticate'
              )}
            </motion.button>
          </form>

          {/* Toggle Register/Login */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-6 text-center"
          >
            <p className="text-gray-400">
              {isRegisterMode ? 'Already have an account?' : "Don't have an account?"}
              {' '}
              <button
                type="button"
                onClick={() => setIsRegisterMode(!isRegisterMode)}
                className="text-violet-400 hover:text-violet-300 font-semibold transition-colors"
              >
                {isRegisterMode ? 'Sign In' : 'Enroll Now'}
              </button>
            </p>
          </motion.div>

          {/* Footer */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
            className="text-center text-xs text-gray-500 mt-4"
          >
            Powered by BiLSTM Neural Networks
          </motion.p>
        </div>
      </motion.div>
    </div>
  )
}

export default LoginPage
