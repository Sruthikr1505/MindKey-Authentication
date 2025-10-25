import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FaCheckCircle, FaExclamationTriangle, FaBrain, FaShieldAlt, FaChartLine, FaSignOutAlt, FaUserShield, FaHome, FaCog } from 'react-icons/fa'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import { Toaster } from 'react-hot-toast'
import { API_BASE_URL } from '../config'
import ExplainabilityPanel from '../components/ExplainabilityPanel'

const Dashboard = () => {
  const [authResult, setAuthResult] = useState(null)
  const [showExplanation, setShowExplanation] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const result = localStorage.getItem('authResult')
    if (result) {
      setAuthResult(JSON.parse(result))
    } else {
      navigate('/login')
    }
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('authResult')
    navigate('/login')
  }

  const handleAdminDashboard = () => {
    // Navigate to integrated admin dashboard
    navigate('/admin')
  }

  const handleHome = () => {
    navigate('/')
  }

  if (!authResult) return null

  // System performance metrics from evaluation
  const GENUINE_MEAN = 0.9905  // Mean genuine score
  const GENUINE_STD = 0.0410   // Genuine std dev
  const IMPOSTOR_MEAN = 0.6833 // Mean impostor score
  const IMPOSTOR_STD = 0.0632  // Impostor std dev
  const EER = 0.0272           // Equal Error Rate (2.72%)
  const EER_THRESHOLD = 0.8377 // EER threshold

  // Determine if user is likely genuine or impostor based on score
  const isLikelyGenuine = authResult.score >= EER_THRESHOLD
  const userType = isLikelyGenuine ? 'Genuine' : 'Impostor'
  
  // Score comparison data showing genuine vs impostor distributions
  const scoreData = [
    { name: 'Impostor Mean', genuine: null, impostor: IMPOSTOR_MEAN, current: null },
    { name: 'Impostor +1σ', genuine: null, impostor: IMPOSTOR_MEAN + IMPOSTOR_STD, current: null },
    { name: 'EER Threshold', genuine: EER_THRESHOLD, impostor: EER_THRESHOLD, current: null },
    { name: 'Genuine -1σ', genuine: GENUINE_MEAN - GENUINE_STD, impostor: null, current: null },
    { name: 'Your Score', genuine: isLikelyGenuine ? authResult.score : null, impostor: !isLikelyGenuine ? authResult.score : null, current: authResult.score },
    { name: 'Genuine Mean', genuine: GENUINE_MEAN, impostor: null, current: null },
  ]

  // Performance metrics radar showing actual system performance
  const radarData = [
    { metric: 'Accuracy', value: (1 - EER) * 100, fullMark: 100 },
    { metric: 'Similarity Score', value: authResult.score * 100, fullMark: 100 },
    { metric: 'Confidence', value: authResult.probability * 100, fullMark: 100 },
    { metric: 'FAR (Low=Good)', value: (1 - EER) * 100, fullMark: 100 },
    { metric: 'FRR (Low=Good)', value: (1 - EER) * 100, fullMark: 100 },
  ]

  return (
    <div className="min-h-screen bg-black text-white p-8 relative">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-violet-600/10 rounded-full blur-3xl top-10 left-10" />
        <div className="absolute w-96 h-96 bg-purple-600/10 rounded-full blur-3xl bottom-10 right-10" />
      </div>
      
      <div className="relative z-10">
      <Toaster position="top-right" />

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center mb-8"
      >
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">Authentication Dashboard</h1>
          <p className="text-gray-300">Real-time EEG analysis results</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleLogout}
          className="flex items-center gap-2 px-6 py-3 bg-red-600 rounded-xl font-semibold hover:bg-red-700 transition-colors shadow-lg"
        >
          <FaSignOutAlt className="w-5 h-5" />
          Sign Out
        </motion.button>
      </motion.div>

      {/* Navigation Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass p-4 rounded-2xl mb-8 backdrop-blur-lg border border-white/20"
      >
        <div className="flex items-center justify-center gap-4">
          <motion.button
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleHome}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg"
          >
            <FaHome className="w-5 h-5" />
            Home
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleAdminDashboard}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 rounded-xl font-semibold hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg"
          >
            <FaUserShield className="w-5 h-5" />
            Admin Dashboard
          </motion.button>

          <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-xl">
            <FaBrain className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-gray-300">
              Status: <span className={`font-semibold ${authResult.authenticated ? 'text-green-400' : 'text-red-400'}`}>
                {authResult.authenticated ? 'Authenticated' : 'Rejected'}
              </span>
            </span>
          </div>
        </div>
      </motion.div>

      {/* Impostor Alert - Special notification for rejected users */}
      {!authResult.authenticated && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
          className="glass p-6 rounded-2xl mb-6 border-2 border-orange-500 bg-gradient-to-r from-orange-500/20 to-red-500/20"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <FaExclamationTriangle className="w-8 h-8 text-orange-400" />
              <div>
                <h3 className="text-xl font-bold text-orange-400">Authentication Rejected</h3>
                <p className="text-gray-300">View detailed analysis of why authentication failed</p>
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleAdminDashboard}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 rounded-lg font-semibold hover:bg-orange-700 transition-colors"
            >
              <FaUserShield className="w-4 h-4" />
              View Analysis
            </motion.button>
          </div>
        </motion.div>
      )}

      {/* Status Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className={`glass p-8 rounded-3xl mb-8 border-2 ${
          authResult.authenticated ? 'border-green-500' : 'border-red-500'
        }`}
      >
        <div className="flex items-start gap-6">
          <motion.div
            animate={{ rotate: authResult.authenticated ? 0 : [0, 10, -10, 0] }}
            transition={{ duration: 0.5 }}
          >
            {authResult.authenticated ? (
              <FaCheckCircle className="w-20 h-20 text-green-400" />
            ) : (
              <FaExclamationTriangle className="w-20 h-20 text-red-400" />
            )}
          </motion.div>
          
          <div className="flex-1">
            <h2 className={`text-3xl font-bold mb-2 ${
              authResult.authenticated ? 'text-green-400' : 'text-red-400'
            }`}>
              {authResult.authenticated ? 'Authentication Successful' : 'Authentication Failed'}
            </h2>
            <p className="text-gray-300 mb-4">{authResult.message}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white/10 p-4 rounded-xl">
                <p className="text-sm text-gray-400 mb-1">Similarity Score</p>
                <p className="text-2xl font-bold">{(authResult.score * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-white/10 p-4 rounded-xl">
                <p className="text-sm text-gray-400 mb-1">Confidence</p>
                <p className="text-2xl font-bold">{(authResult.probability * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-white/10 p-4 rounded-xl">
                <p className="text-sm text-gray-400 mb-1">Spoof Status</p>
                <p className="text-2xl font-bold">{authResult.is_spoof ? 'Detected' : 'Clean'}</p>
              </div>
              <div className="bg-white/10 p-4 rounded-xl">
                <p className="text-sm text-gray-400 mb-1">Classification</p>
                <p className={`text-2xl font-bold ${isLikelyGenuine ? 'text-green-400' : 'text-red-400'}`}>
                  {userType}
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Score Analysis: Genuine vs Impostor */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass p-6 rounded-3xl"
        >
          <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <FaChartLine className="text-purple-400" />
            Score Analysis
          </h3>
          <p className="text-sm text-gray-400 mb-4">
            Your score vs system performance (EER: {(EER * 100).toFixed(2)}%)
          </p>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={scoreData}>
              <defs>
                <linearGradient id="colorGenuine" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorImpostor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
              <XAxis dataKey="name" stroke="#ffffff60" tick={{ fontSize: 11 }} />
              <YAxis stroke="#ffffff60" domain={[0.5, 1.0]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                formatter={(value) => value ? (value * 100).toFixed(1) + '%' : null}
              />
              <Area type="monotone" dataKey="genuine" stroke="#10b981" fillOpacity={1} fill="url(#colorGenuine)" name="Genuine Users" />
              <Area type="monotone" dataKey="impostor" stroke="#ef4444" fillOpacity={1} fill="url(#colorImpostor)" name="Impostors" />
              <Area type="monotone" dataKey="current" stroke="#8b5cf6" strokeWidth={3} fill="none" name="Your Score" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-300">Genuine Distribution</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-gray-300">Impostor Distribution</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span className="text-gray-300">Your Score</span>
            </div>
          </div>
        </motion.div>

        {/* System Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass p-6 rounded-3xl"
        >
          <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <FaBrain className="text-blue-400" />
            System Performance
          </h3>
          <p className="text-sm text-gray-400 mb-4">
            Real-time metrics based on trained model
          </p>
          <ResponsiveContainer width="100%" height={250}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#ffffff20" />
              <PolarAngleAxis dataKey="metric" stroke="#ffffff60" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis stroke="#ffffff60" domain={[0, 100]} />
              <Radar 
                name="Performance" 
                dataKey="value" 
                stroke="#3b82f6" 
                fill="#3b82f6" 
                fillOpacity={0.6} 
              />
            </RadarChart>
          </ResponsiveContainer>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div className="bg-white/5 p-3 rounded-lg">
              <p className="text-gray-400 text-xs">Classification</p>
              <p className={`font-bold ${isLikelyGenuine ? 'text-green-400' : 'text-red-400'}`}>
                {userType} User
              </p>
            </div>
            <div className="bg-white/5 p-3 rounded-lg">
              <p className="text-gray-400 text-xs">System EER</p>
              <p className="font-bold text-blue-400">{(EER * 100).toFixed(2)}%</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Explainability Section */}
      {authResult?.explain_id && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {!showExplanation ? (
            <div className="glass p-8 rounded-3xl text-center">
              <FaBrain className="w-16 h-16 text-violet-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">Understand the Decision</h3>
              <p className="text-gray-400 mb-6">
                See which brain signals were most important for authentication
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowExplanation(true)}
                className="px-8 py-4 bg-gradient-to-r from-violet-600 to-purple-600 rounded-xl font-semibold shadow-lg hover:shadow-violet-500/50 transition-all"
              >
                <FaShieldAlt className="inline mr-2" />
                View Model Explanation
              </motion.button>
            </div>
          ) : (
            <ExplainabilityPanel 
              explainId={authResult.explain_id}
              apiUrl={API_URL}
              authResult={authResult}
            />
          )}
        </motion.div>
      )}

      {/* Floating Admin Access Button - Always visible for quick access */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1, type: "spring", stiffness: 200 }}
        className="fixed bottom-8 right-8 z-50"
      >
        <motion.button
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleAdminDashboard}
          className="flex items-center gap-2 px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full font-bold text-white shadow-2xl hover:shadow-purple-500/50 transition-all"
          title="Open Admin Dashboard for detailed analysis"
        >
          <FaUserShield className="w-6 h-6" />
          <span className="hidden sm:inline">Admin Panel</span>
        </motion.button>
      </motion.div>
      </div>
    </div>
  )
}

export default Dashboard
