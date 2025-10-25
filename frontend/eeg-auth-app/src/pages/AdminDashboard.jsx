import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FaUsers, FaShieldAlt, FaChartBar, FaEye, FaFilter, FaDownload, FaHome, FaSignOutAlt, FaBrain, FaUserShield, FaCheckCircle, FaTimesCircle } from 'react-icons/fa'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts'
import { Toaster, toast } from 'react-hot-toast'
import { API_BASE_URL } from '../config'

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    successfulLogins: 0,
    failedAttempts: 0,
    successRate: 0
  })
  const [recentActivity, setRecentActivity] = useState([])
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
    // Auto-refresh every 10 seconds for real-time updates
    const interval = setInterval(fetchDashboardData, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleHome = () => {
    navigate('/')
  }

  const handleLogout = () => {
    localStorage.removeItem('authResult')
    navigate('/login')
  }

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch authentication statistics
      const statsResponse = await fetch(`${API_BASE_URL}/admin/auth-stats`)
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }
      
      // Fetch recent activity
      const activityResponse = await fetch(`${API_BASE_URL}/admin/recent-activity`)
      if (activityResponse.ok) {
        const activityData = await activityResponse.json()
        setRecentActivity(activityData)
      }
      
      // Fetch chart data
      const chartResponse = await fetch(`${API_BASE_URL}/admin/chart-data`)
      if (chartResponse.ok) {
        const chartDataResponse = await chartResponse.json()
        setChartData(chartDataResponse)
      }
      
    } catch (error) {
      toast.error('Failed to load dashboard data')
      console.error('Dashboard error:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredActivity = recentActivity.filter(activity => {
    if (searchTerm && !activity.user.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }
    
    switch (filter) {
      case 'success':
        return activity.success
      case 'failed':
        return !activity.success
      default:
        return true
    }
  })

  const exportData = () => {
    const data = {
      stats,
      recentActivity: filteredActivity,
      chartData,
      exported_at: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `eeg_auth_data_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Data exported successfully!')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-violet-500 mx-auto mb-4"></div>
          <p className="text-xl text-violet-300">Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <Toaster position="top-right" />
      
      {/* Navigation Bar */}
      <motion.nav 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 border-b border-violet-900/50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FaBrain className="h-8 w-8 text-violet-400" />
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleHome}
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-violet-900/50 hover:text-white transition-all"
                  >
                    <FaHome className="inline-block mr-1" /> Home
                  </motion.button>
                  <span className="px-3 py-2 rounded-md text-sm font-medium bg-violet-900 text-white">
                    <FaUserShield className="inline-block mr-1" /> Admin Dashboard
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={exportData}
                className="flex items-center gap-2 px-4 py-2 bg-violet-600 rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors"
              >
                <FaDownload className="w-4 h-4" />
                Export
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="px-4 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-red-900/50 hover:text-white transition-all"
              >
                <FaSignOutAlt className="inline-block mr-1" /> Sign out
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8"
        >
          <div className="bg-gray-800 overflow-hidden shadow-lg rounded-lg border border-violet-900/30">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-violet-600 rounded-md p-3">
                  <FaUsers className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-400 truncate">Total Users</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-white">{stats.totalUsers}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 overflow-hidden shadow-lg rounded-lg border border-green-900/30">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-green-600 rounded-md p-3">
                  <FaCheckCircle className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-400 truncate">Successful Logins</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-white">{stats.successfulLogins}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 overflow-hidden shadow-lg rounded-lg border border-red-900/30">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-red-600 rounded-md p-3">
                  <FaTimesCircle className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-400 truncate">Failed Attempts</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-white">{stats.failedAttempts}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 overflow-hidden shadow-lg rounded-lg border border-blue-900/30">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-600 rounded-md p-3">
                  <FaChartBar className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-400 truncate">Success Rate</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-white">{stats.successRate}%</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Charts Section */}
        {chartData.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
          >
            <div className="bg-gray-800 shadow-lg rounded-lg border border-violet-900/30 p-6">
              <h3 className="text-lg font-medium text-violet-300 mb-4">Authentication Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #7C3AED',
                      borderRadius: '8px',
                      color: '#F3F4F6'
                    }} 
                  />
                  <Area type="monotone" dataKey="value" stroke="#7C3AED" fill="#7C3AED" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-gray-800 shadow-lg rounded-lg border border-violet-900/30 p-6">
              <h3 className="text-lg font-medium text-violet-300 mb-4">Success vs Failure</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Success', value: stats.successfulLogins, fill: '#10B981' },
                      { name: 'Failed', value: stats.failedAttempts, fill: '#EF4444' }
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #7C3AED',
                      borderRadius: '8px',
                      color: '#F3F4F6'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        )}

        {/* Filters */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gray-800 shadow-lg rounded-lg border border-violet-900/30 p-6 mb-6"
        >
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
              >
                <option value="all">All Activity</option>
                <option value="success">Successful</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gray-800 shadow-lg rounded-lg border border-violet-900/30"
        >
          <div className="px-6 py-4 border-b border-violet-900/30">
            <h3 className="text-lg font-medium text-violet-300">Recent Activity</h3>
            <p className="text-sm text-gray-400">Latest authentication attempts</p>
          </div>
          <div className="overflow-hidden">
            <ul className="divide-y divide-gray-700">
              {filteredActivity.length > 0 ? (
                filteredActivity.map((activity, index) => (
                  <motion.li 
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="px-6 py-4 hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                          activity.success ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                        }`}>
                          {activity.success ? <FaCheckCircle /> : <FaTimesCircle />}
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-white">{activity.user}</p>
                          <p className="text-sm text-gray-400">{activity.action}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-400">
                          {new Date(activity.timestamp).toLocaleString()}
                        </p>
                        <p className={`text-xs font-medium ${
                          activity.success ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {activity.success ? 'SUCCESS' : 'FAILED'}
                        </p>
                      </div>
                    </div>
                  </motion.li>
                ))
              ) : (
                <li className="px-6 py-8 text-center">
                  <p className="text-gray-400">No activity found</p>
                </li>
              )}
            </ul>
          </div>
        </motion.div>
      </main>
    </div>
  )
}

export default AdminDashboard
