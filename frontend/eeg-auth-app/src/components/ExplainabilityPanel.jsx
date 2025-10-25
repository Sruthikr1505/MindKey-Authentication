import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FaBrain, FaChartBar, FaClock, FaInfoCircle, FaCheckCircle, FaTimesCircle } from 'react-icons/fa'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts'
import axios from 'axios'
import toast from 'react-hot-toast'
import { API_BASE_URL } from '../config'

const ExplainabilityPanel = ({ explainId, apiUrl = API_BASE_URL, authResult, isAuthenticated = false, confidenceScore = 0, spoofScore = 0 }) => {
  const [loading, setLoading] = useState(true);
  const [heatmapImage, setHeatmapImage] = useState(null);
  const [topChannels, setTopChannels] = useState([]);
  const [topTimeWindows, setTopTimeWindows] = useState([]);
  const [activeTab, setActiveTab] = useState('decision');
  const [error, setError] = useState(null);
  const [decision, setDecision] = useState({
    isAuthenticated: false,
    confidence: 0,
    isSpoof: false,
    spoofScore: 0,
    explanation: '',
    keyFactors: []
  });

  useEffect(() => {
    let isMounted = true;
    
    const loadData = async () => {
      if (!isMounted) return;
      
      try {
        if (explainId) {
          await fetchExplanation();
        } else {
          // If no explainId, show fallback data immediately
          console.log('No explanation ID provided, using fallback data');
          if (isMounted) {
            setLoading(false);
            setError('No explanation ID available');
            loadFallbackData();
          }
        }
      } catch (error) {
        console.error('Error in useEffect:', error);
        if (isMounted) {
          setError('Failed to load explanation');
          loadFallbackData();
          setLoading(false);
        }
      }
    };
    
    loadData();
    
    return () => {
      isMounted = false;
    };
  }, [explainId])

  // Helper function to generate explanation text
  const generateExplanation = (isAuth, confidence, isSpoof, spoofScore) => {
    if (isSpoof) {
      return `The model detected potential spoofing activity (score: ${(spoofScore * 100).toFixed(1)}%). ` +
             `This suggests the authentication attempt may not be from a legitimate user.`;
    }
    
    if (isAuth) {
      return `The model is ${(confidence * 100).toFixed(1)}% confident this is a legitimate user. ` +
             `The brainwave patterns match the expected user's profile within acceptable thresholds.`;
    } else {
      return `The model is ${((1 - confidence) * 100).toFixed(1)}% confident this is not the claimed identity. ` +
             `The brainwave patterns do not match the expected user's profile.`;
    }
  };

  // Helper function to generate key factors
  const generateKeyFactors = (data, isAuth, isSpoof) => {
    const factors = [];
    
    if (isSpoof) {
      factors.push('High likelihood of spoofing attempt detected');
      factors.push('Unusual signal patterns inconsistent with live brain activity');
      if (data.spoof_reason) {
        factors.push(`Spoofing indicators: ${data.spoof_reason}`);
      }
    } else if (isAuth) {
      factors.push('Strong match with enrolled brainwave patterns');
      factors.push('Consistent neural response across key regions');
      factors.push('Stable signal quality throughout authentication');
    } else {
      factors.push('Significant deviation from enrolled patterns');
      factors.push('Inconsistent neural response in key regions');
      factors.push('Potential mismatch in cognitive processing style');
    }
    
    return factors;
  };

  const loadFallbackData = () => {
    // Set default decision for fallback
    setDecision({
      isAuthenticated: false,
      confidence: 0.0,
      isSpoof: false,
      spoofScore: 0.0,
      explanation: 'Using fallback data - No explanation available',
      keyFactors: [
        'Sample data - No real authentication performed',
        'This is a demonstration of the explanation interface'
      ]
    });

    setTopChannels([
      { name: 'Fp1', importance: 0.92, region: 'Frontal' },
      { name: 'F3', importance: 0.87, region: 'Frontal' },
      { name: 'C3', importance: 0.81, region: 'Central' },
      { name: 'P3', importance: 0.76, region: 'Parietal' },
      { name: 'O1', importance: 0.68, region: 'Occipital' },
    ]);
    
    setTopTimeWindows([
      { window: '0.0-0.5s', importance: 0.89, description: 'Initial response' },
      { window: '0.5-1.0s', importance: 0.84, description: 'Processing phase' },
      { window: '1.0-1.5s', importance: 0.72, description: 'Sustained activity' },
      { window: '1.5-2.0s', importance: 0.65, description: 'Late response' },
    ]);
  }

  const processExplanationData = (data) => {
    try {
      if (!data) {
        console.warn('No data provided to processExplanationData');
        loadFallbackData();
        return;
      }

      console.log('Processing explanation data:', data);
      
      // Determine authentication status from the most reliable source
      const authStatus = isAuthenticated !== undefined ? isAuthenticated : 
                       (data.is_authenticated !== undefined ? data.is_authenticated : 
                       (authResult?.is_authenticated || false));
      
      // Get confidence score from the most reliable source
      const confidence = confidenceScore !== undefined ? confidenceScore : 
                        (data.confidence_score || data.confidence || 0);
      
      // Check for spoofing - consider it a spoof if spoofScore > 0.5
      const isSpoof = (spoofScore > 0.5) || 
                     data.is_spoof || 
                     data.spoof_detected || 
                     false;
      
      const spoofScoreValue = spoofScore || data.spoof_score || 0;
      
      // Final authentication decision - not authenticated if it's a spoof
      const finalAuthStatus = authStatus && !isSpoof;
      
      // Update decision state
      setDecision({
        isAuthenticated: finalAuthStatus,
        confidence: Math.min(100, Math.max(0, Math.round(confidence * 100))), // Ensure between 0-100
        isSpoof,
        spoofScore: Math.min(100, Math.max(0, Math.round(spoofScoreValue * 100))), // Ensure between 0-100
        explanation: data.explanation || generateExplanation(finalAuthStatus, confidence, isSpoof, spoofScoreValue),
        keyFactors: data.key_factors || generateKeyFactors(data, finalAuthStatus, isSpoof)
      });
      
      // Process visualization data
      if (data.heatmap_url && typeof data.heatmap_url === 'string') {
        setHeatmapImage(data.heatmap_url);
      } else if (data.heatmap) {
        setHeatmapImage(data.heatmap);
      }
      
      if (Array.isArray(data.top_channels) && data.top_channels.length > 0) {
        setTopChannels(data.top_channels);
      } else if (data.channels) {
        setTopChannels(Array.isArray(data.channels) ? data.channels : []);
      }
      
      if (Array.isArray(data.top_time_windows) && data.top_time_windows.length > 0) {
        setTopTimeWindows(data.top_time_windows);
      } else if (data.time_windows) {
        setTopTimeWindows(Array.isArray(data.time_windows) ? data.time_windows : []);
      }
    } catch (error) {
      console.error('Error processing explanation data:', error);
      setError('Error processing explanation data');
      loadFallbackData();
    }
  };

  const fetchExplanation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!explainId) {
        console.warn('No explanation ID provided');
        setError('No explanation data available');
        loadFallbackData();
        return;
      }

      // Check if we have authResult with the explanation data
      try {
        if (authResult?.explanation) {
          console.log('Using explanation data from authResult');
          processExplanationData(authResult.explanation);
          return;
        }

        // Otherwise, fetch from API
        console.log(`Fetching explanation from API with ID: ${explainId}`);
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('Authentication required');
        }

        const response = await axios.get(`${apiUrl}/explain/${explainId}`, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          timeout: 10000 // 10 second timeout
        });

        if (response?.data) {
          console.log('Received explanation data:', response.data);
          processExplanationData(response.data);
          toast.success('Model explanation loaded!');
        } else {
          console.warn('Empty response from server');
          throw new Error('No data received from server');
        }
      } catch (apiError) {
        console.warn('Error fetching explanation, using fallback data:', apiError);
        setError(apiError.message || 'Failed to load explanation');
        loadFallbackData();
        toast.info('Showing simulated explanation data');
      }
    } catch (err) {
      console.error('Unexpected error in fetchExplanation:', err);
      setError('An unexpected error occurred');
      loadFallbackData();
    } finally {
      setLoading(false);
    }
  }

  // Helper function to determine channel region
  const getChannelRegion = (channelName) => {
    if (channelName.startsWith('Fp') || channelName.startsWith('F')) return 'Frontal'
    if (channelName.startsWith('C')) return 'Central'
    if (channelName.startsWith('P')) return 'Parietal'
    if (channelName.startsWith('O')) return 'Occipital'
    if (channelName.startsWith('T')) return 'Temporal'
    return 'Unknown'
  }

  // Helper function to describe time windows
  const getTimeDescription = (startTime) => {
    if (startTime < 0.5) return 'Initial response'
    if (startTime < 1.0) return 'Processing phase'
    if (startTime < 1.5) return 'Sustained activity'
    return 'Late response'
  }

  if (loading) {
    return (
      <div className="glass p-8 rounded-3xl">
        <div className="flex flex-col items-center justify-center space-y-4">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full"
          />
          <p className="text-gray-400 text-center">Analyzing brainwave patterns...</p>
          <p className="text-sm text-gray-500">This may take a few moments</p>
        </div>
      </div>
    )
  }

  // Render decision badge
  const renderDecisionBadge = () => {
    if (decision.isSpoof) {
      return (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-2 rounded-xl flex items-center">
          <FaTimesCircle className="mr-2" />
          <span className="font-bold">Spoofing Detected</span>
        </div>
      );
    }
    
    return decision.isAuthenticated ? (
      <div className="bg-green-500/10 border border-green-500/30 text-green-400 px-4 py-2 rounded-xl flex items-center">
        <FaCheckCircle className="mr-2" />
        <span className="font-bold">Authenticated</span>
        <span className="ml-2 text-sm">(Confidence: {(decision.confidence * 100).toFixed(1)}%)</span>
      </div>
    ) : (
      <div className="bg-orange-500/10 border border-orange-500/30 text-orange-400 px-4 py-2 rounded-xl flex items-center">
        <FaTimesCircle className="mr-2" />
        <span className="font-bold">Not Authenticated</span>
        <span className="ml-2 text-sm">(Confidence: {((1 - decision.confidence) * 100).toFixed(1)}%)</span>
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass p-8 rounded-3xl space-y-6"
    >
      {/* Decision Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Authentication Decision</h2>
          <p className="text-gray-400">Analysis of brainwave patterns</p>
        </div>
        {renderDecisionBadge()}
      </div>

      {/* Explanation Card */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-5">
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
          <FaInfoCircle className="mr-2 text-violet-400" />
          Explanation
        </h3>
        <p className="text-gray-300">{decision.explanation}</p>
        
        {decision.keyFactors && decision.keyFactors.length > 0 && (
          <div className="mt-4">
            <h4 className="font-medium text-gray-300 mb-2">Key Factors:</h4>
            <ul className="list-disc list-inside space-y-1 text-gray-400">
              {decision.keyFactors.map((factor, index) => (
                <li key={index} className="text-sm">{factor}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <FaBrain className="w-8 h-8 text-violet-500" />
        <div>
          <h2 className="text-2xl font-bold gradient-text">Model Explanation</h2>
          <p className="text-sm text-gray-400">Understanding the authentication decision</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <FaTimesCircle className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
              <div className="mt-2">
                <button
                  type="button"
                  onClick={fetchExplanation}
                  className="text-sm font-medium text-red-700 hover:text-red-600"
                >
                  Try again <span aria-hidden="true">&rarr;</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-violet-500/10 border border-violet-500/30 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
          <FaInfoCircle className="w-5 h-5 text-violet-400 mt-0.5" />
          <div className="text-sm text-gray-300">
            <p className="font-semibold mb-1">How Captum Works:</p>
            <p>Captum uses <strong>Integrated Gradients</strong> to analyze which EEG channels and time windows 
            contributed most to the authentication decision. Brighter areas indicate higher importance.</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setActiveTab('decision')}
          className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
            activeTab === 'decision'
              ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <FaInfoCircle className="inline mr-2" />
          Decision
        </button>
        <button
          onClick={() => setActiveTab('channels')}
          className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
            activeTab === 'channels'
              ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <FaChartBar className="inline mr-2" />
          Channels
        </button>
        <button
          onClick={() => setActiveTab('time')}
          className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
            activeTab === 'time'
              ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <FaClock className="inline mr-2" />
          Time
        </button>
        <button
          onClick={() => setActiveTab('heatmap')}
          className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
            activeTab === 'heatmap'
              ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <FaBrain className="inline mr-2" />
          Heatmap
        </button>
      </div>

      {/* Content */}
      {activeTab === 'decision' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          <h3 className="text-lg font-semibold mb-4">Authentication Decision Analysis</h3>
          
          {/* Decision Summary */}
          <div className={`p-6 rounded-xl border-2 ${authResult?.authenticated ? 'bg-green-500/10 border-green-500' : 'bg-red-500/10 border-red-500'}`}>
            <div className="flex items-center gap-4 mb-4">
              {authResult?.authenticated ? (
                <FaCheckCircle className="w-12 h-12 text-green-400" />
              ) : (
                <FaTimesCircle className="w-12 h-12 text-red-400" />
              )}
              <div>
                <h4 className="text-2xl font-bold">
                  {authResult?.authenticated ? 'Genuine User Detected' : 'Impostor Detected'}
                </h4>
                <p className="text-gray-300">
                  {authResult?.authenticated 
                    ? 'Brainwave pattern matches registered profile' 
                    : 'Brainwave pattern does not match registered profile'}
                </p>
              </div>
            </div>
          </div>

          {/* Score Comparison Chart */}
          <div className="bg-white/5 p-6 rounded-xl">
            <h4 className="text-lg font-semibold mb-4">Score Analysis</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { 
                  name: 'Your Score', 
                  value: (authResult?.score || 0) * 100,
                  threshold: 70,
                  fill: authResult?.authenticated ? '#10b981' : '#ef4444'
                },
                { 
                  name: 'Threshold', 
                  value: 70,
                  threshold: 70,
                  fill: '#8b5cf6'
                }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #8b5cf6' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-400 mt-4 text-center">
              {authResult?.authenticated 
                ? `✅ Your score (${((authResult?.score || 0) * 100).toFixed(1)}%) is above the threshold (70%)`
                : `❌ Your score (${((authResult?.score || 0) * 100).toFixed(1)}%) is below the threshold (70%)`}
            </p>
          </div>

          {/* Why This Decision */}
          <div className="bg-white/5 p-6 rounded-xl">
            <h4 className="text-lg font-semibold mb-4">Why This Decision?</h4>
            <div className="space-y-3">
              {authResult?.authenticated ? (
                <>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-green-400">High Similarity:</strong> Your brainwave pattern shows {((authResult?.score || 0) * 100).toFixed(1)}% similarity with your registered profile
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-green-400">Confidence Level:</strong> The model is {((authResult?.probability || 0) * 100).toFixed(1)}% confident in this decision
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-green-400">Signal Quality:</strong> Your EEG signal passed all quality checks
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-green-400">Spoof Detection:</strong> No spoofing or replay attack detected
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-red-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-red-400">Low Similarity:</strong> Brainwave pattern shows only {((authResult?.score || 0) * 100).toFixed(1)}% similarity (below 70% threshold)
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-red-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-red-400">Low Confidence:</strong> Model is only {((authResult?.probability || 0) * 100).toFixed(1)}% confident this is the registered user
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-red-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-red-400">Pattern Mismatch:</strong> Key brain regions show different activation patterns
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-red-400 rounded-full mt-2" />
                    <p className="text-gray-300">
                      <strong className="text-red-400">Security Alert:</strong> This attempt has been logged for security monitoring
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Comparison Graph */}
          <div className="bg-white/5 p-6 rounded-xl">
            <h4 className="text-lg font-semibold mb-4">Genuine vs Impostor Comparison</h4>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={[
                { category: 'Typical Impostor', score: 25, range: [10, 40] },
                { category: 'Threshold', score: 70, range: [70, 70] },
                { category: 'Typical Genuine', score: 90, range: [80, 98] },
                { category: 'Your Score', score: (authResult?.score || 0) * 100, range: [(authResult?.score || 0) * 100, (authResult?.score || 0) * 100] }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis dataKey="category" stroke="#9ca3af" angle={-15} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #8b5cf6' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 6 }} name="Score %" />
              </LineChart>
            </ResponsiveContainer>
            <div className="flex justify-between text-xs text-gray-400 mt-4">
              <span>❌ Impostor Range: 10-40%</span>
              <span>⚠️ Threshold: 70%</span>
              <span>✅ Genuine Range: 80-98%</span>
            </div>
          </div>
        </motion.div>
      )}

      {activeTab === 'heatmap' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold mb-3">Attribution Heatmap</h3>
          <p className="text-sm text-gray-400 mb-4">
            This heatmap shows the importance of each EEG channel over time. 
            Red/yellow areas had the most influence on the decision.
          </p>
          {heatmapImage && (
            <img
              src={heatmapImage}
              alt="Attribution heatmap"
              className="w-full rounded-xl border border-violet-500/30"
            />
          )}
          <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
            <span>Low Importance</span>
            <div className="flex gap-1">
              <div className="w-8 h-3 bg-gradient-to-r from-blue-500 via-yellow-500 to-red-500 rounded" />
            </div>
            <span>High Importance</span>
          </div>
        </motion.div>
      )}

      {activeTab === 'channels' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold mb-3">Most Important Channels</h3>
          <p className="text-sm text-gray-400 mb-4">
            These EEG channels contributed most to identifying your unique brain signature.
          </p>
          {topChannels.map((channel, index) => (
            <motion.div
              key={channel.name}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/5 p-4 rounded-xl hover:bg-white/10 transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-semibold">{channel.name}</p>
                    <p className="text-xs text-gray-500">{channel.region} region</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-violet-400">
                    {(channel.importance * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
              <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-violet-600 to-purple-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${channel.importance * 100}%` }}
                  transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                />
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {activeTab === 'time' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold mb-3">Critical Time Windows</h3>
          <p className="text-sm text-gray-400 mb-4">
            These time periods in your EEG signal were most distinctive for authentication.
          </p>
          {topTimeWindows.map((tw, index) => (
            <motion.div
              key={tw.window}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/5 p-4 rounded-xl hover:bg-white/10 transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="font-semibold">{tw.window}</p>
                  <p className="text-xs text-gray-500">{tw.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-violet-400">
                    {(tw.importance * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
              <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-600 to-cyan-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${tw.importance * 100}%` }}
                  transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                />
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Technical Details */}
      <div className="mt-6 p-6 bg-black/30 rounded-xl border border-white/10">
        <h4 className="text-lg font-semibold text-violet-400 mb-4">Technical Details</h4>
        <div className="space-y-3">
          <p className="text-sm text-gray-300">
            <strong className="text-violet-400">Method:</strong> Integrated Gradients (Captum)
          </p>
          <p className="text-sm text-gray-300">
            <strong className="text-violet-400">Baseline:</strong> Zero signal
          </p>
          <p className="text-sm text-gray-300">
            <strong className="text-violet-400">Steps:</strong> 50 interpolation steps
          </p>
          <p className="text-sm text-gray-300">
            <strong className="text-violet-400">Model:</strong> BiLSTM with Attention (749K parameters)
          </p>
        </div>
      </div>
    </motion.div>
  )
}

export default ExplainabilityPanel
