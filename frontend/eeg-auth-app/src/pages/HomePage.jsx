import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import { FaBrain, FaLock, FaChartLine, FaShieldAlt, FaBolt, FaUpload, FaCheckCircle } from 'react-icons/fa'
import DecryptedText from '../components/DecryptedText'
import SplashScreen from '../components/SplashScreen'
import ScrollReveal from '../components/ScrollReveal'
import ParticleBackground from '../components/ParticleBackground'
import ClickSpark from '../components/ClickSpark'

const HomePage = () => {
  const [showSplash, setShowSplash] = useState(true)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const features = [
    {
      icon: <FaBrain className="w-12 h-12" />,
      title: 'Brain Signal Authentication',
      description: 'Unique EEG patterns from your brain waves provide unbreakable biometric security'
    },
    {
      icon: <FaLock className="w-12 h-12" />,
      title: 'BiLSTM Deep Learning',
      description: 'Advanced neural networks with attention mechanism for 95%+ accuracy'
    },
    {
      icon: <FaChartLine className="w-12 h-12" />,
      title: 'Real-time Analysis',
      description: 'Instant authentication in under 50ms with live EEG signal processing'
    },
    {
      icon: <FaShieldAlt className="w-12 h-12" />,
      title: 'Spoof Detection',
      description: 'AI-powered anomaly detection prevents replay and presentation attacks'
    }
  ]

  useEffect(() => {
    document.documentElement.style.scrollBehavior = 'smooth'
    return () => {
      document.documentElement.style.scrollBehavior = 'auto'
    }
  }, [])

  return (
    <>
      <AnimatePresence>
        {showSplash && <SplashScreen onComplete={() => setShowSplash(false)} />}
      </AnimatePresence>

      {!showSplash && (
        <div className="min-h-screen w-full text-white relative overflow-x-hidden"
          style={{ cursor: 'default', width: '100vw', minWidth: '100vw' }}
        >
          {/* Particle Background */}
          <ParticleBackground />

          {/* Click Spark Effect */}
          <ClickSpark />

          {/* New Gradient Mesh Background */}
          <div className="fixed inset-0 bg-black" style={{ zIndex: 0 }}>
            <div className="absolute inset-0 bg-gradient-to-br from-violet-900/20 via-black to-purple-900/20" />
            <div className="absolute inset-0">
              {/* Animated Grid */}
              <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.03)_1px,transparent_1px)] bg-[size:100px_100px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

              {/* Floating Orbs */}
              <motion.div
                className="absolute top-20 left-20 w-72 h-72 bg-violet-600/10 rounded-full blur-3xl"
                animate={{
                  x: [0, 100, 0],
                  y: [0, -50, 0],
                }}
                transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
              />
              <motion.div
                className="absolute bottom-20 right-20 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl"
                animate={{
                  x: [0, -80, 0],
                  y: [0, 80, 0],
                }}
                transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
              />
            </div>
          </div>

          {/* Fixed Navigation */}
          <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
              scrolled ? 'bg-black/80 backdrop-blur-xl border-b border-white/10' : 'bg-transparent'
            }`}
          >
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FaBrain className="w-8 h-8 text-violet-500" />
                <span className="text-2xl font-bold gradient-text">MindKey</span>
              </div>

              {/* Smooth scroll navigation links */}
              <div className="hidden md:flex gap-8 items-center text-white font-semibold text-lg">
                <a href="#about" className="hover:text-violet-400 transition-colors cursor-pointer">About</a>
                <a href="#features" className="hover:text-violet-400 transition-colors cursor-pointer">Features</a>
                <a href="#how-it-works" className="hover:text-violet-400 transition-colors cursor-pointer">How It Works</a>
                <a href="#contact" className="hover:text-violet-400 transition-colors cursor-pointer">Contact</a>
              </div>

              <Link to="/login">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-2 bg-gradient-to-r from-violet-600 to-purple-600 rounded-full font-semibold ml-6"
                >
                  Sign In
                </motion.button>
              </Link>
            </div>
          </motion.nav>

          {/* Hero Section / About */}
          <section id="about" className="relative min-h-screen flex items-center justify-center px-6 pt-20">
            <div className="relative z-10 text-center max-w-6xl mx-auto">

              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="mb-8"
              >
                <DecryptedText
                  text="MindKey"
                  className="text-7xl md:text-9xl font-black mb-6 gradient-text tracking-tight"
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.8 }}
              >
                <DecryptedText
                  text="Unlock With Your Thoughts"
                  className="text-4xl md:text-6xl font-bold mb-6 text-white tracking-tight"
                />
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6, duration: 0.8 }}
                className="text-lg md:text-xl text-white/80 mb-12 max-w-3xl mx-auto leading-relaxed"
              >
                Next-generation biometric authentication powered by your unique brain signals
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9, duration: 0.8 }}
                className="flex justify-center mb-16"
              >
                <Link to="/login">
                  <motion.button
                    whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(139, 92, 246, 0.5)" }}
                    whileTap={{ scale: 0.95 }}
                    className="px-12 py-4 bg-gradient-to-r from-violet-600 to-purple-600 rounded-full font-bold text-lg shadow-xl"
                  >
                    Get Started →
                  </motion.button>
                </Link>
              </motion.div>

              {/* Scroll Indicator */}
              <motion.div
                className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <div className="w-6 h-10 border-2 border-violet-500/50 rounded-full p-1">
                  <motion.div
                    className="w-1.5 h-3 bg-violet-500 rounded-full mx-auto"
                    animate={{ y: [0, 12, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                </div>
              </motion.div>
            </div>
          </section>

          {/* Features Section */}
          <section id="features" className="py-20 px-6">
            <div className="overflow-hidden">
              <ScrollReveal>
                <h2 className="text-5xl md:text-6xl font-black text-white text-center mb-4 tracking-tight">
                  Revolutionary Technology
                </h2>
                <p className="text-center text-white/70 mb-16 text-lg">
                  Powered by cutting-edge AI and neuroscience
                </p>
              </ScrollReveal>
            </div>

            <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature, index) => (
                <ScrollReveal key={index}>
                  <motion.div
                    whileHover={{ y: -10, scale: 1.02 }}
                    className="glass p-6 rounded-2xl hover:bg-white/20 transition-all h-full flex flex-col border border-white/10"
                  >
                    <motion.div
                      className="text-violet-400 mb-4"
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.5 }}
                    >
                      {feature.icon}
                    </motion.div>
                    <h3 className="text-xl font-bold mb-3 text-white">{feature.title}</h3>
                    <p className="text-sm text-white/70 leading-relaxed">{feature.description}</p>
                  </motion.div>
                </ScrollReveal>
              ))}
            </div>
          </section>

          {/* Stats Section - Always Visible */}
          <section className="relative py-32 px-6">
            <div className="max-w-7xl mx-auto">
              <div className="overflow-hidden">
                <ScrollReveal>
                  <h2 className="text-5xl md:text-6xl font-black text-white text-center mb-4 tracking-tight">
                    Performance Metrics
                  </h2>
                  <p className="text-center text-white/70 mb-16 text-lg">
                    Industry-leading accuracy and speed
                  </p>
                </ScrollReveal>
              </div>

              <div className="grid md:grid-cols-3 gap-8">
                <ScrollReveal>
                  <motion.div
                    whileHover={{ y: -10, boxShadow: "0 20px 40px rgba(139, 92, 246, 0.3)" }}
                    className="glass p-8 rounded-2xl text-center border border-violet-500/20"
                  >
                    <div className="w-16 h-16 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <FaChartLine className="w-8 h-8" />
                    </div>
                    <h3 className="text-5xl font-bold gradient-text mb-2">95%+</h3>
                    <p className="text-lg text-gray-300 font-semibold">Accuracy Rate</p>
                    <p className="text-sm text-gray-500 mt-2">Best-in-class authentication</p>
                  </motion.div>
                </ScrollReveal>

                <ScrollReveal>
                  <motion.div
                    whileHover={{ y: -10, boxShadow: "0 20px 40px rgba(139, 92, 246, 0.3)" }}
                    className="glass p-8 rounded-2xl text-center border border-violet-500/20"
                  >
                    <div className="w-16 h-16 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <FaBolt className="w-8 h-8" />
                    </div>
                    <h3 className="text-5xl font-bold gradient-text mb-2">&lt;50ms</h3>
                    <p className="text-lg text-gray-300 font-semibold">Authentication Time</p>
                    <p className="text-sm text-gray-500 mt-2">Lightning-fast verification</p>
                  </motion.div>
                </ScrollReveal>

                <ScrollReveal>
                  <motion.div
                    whileHover={{ y: -10, boxShadow: "0 20px 40px rgba(139, 92, 246, 0.3)" }}
                    className="glass p-8 rounded-2xl text-center border border-violet-500/20"
                  >
                    <div className="w-16 h-16 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <FaShieldAlt className="w-8 h-8" />
                    </div>
                    <h3 className="text-5xl font-bold gradient-text mb-2">3-8%</h3>
                    <p className="text-lg text-gray-300 font-semibold">Equal Error Rate</p>
                    <p className="text-sm text-gray-500 mt-2">Minimal false positives</p>
                  </motion.div>
                </ScrollReveal>
              </div>
            </div>
          </section>

          {/* How It Works Section */}
          <section id="how-it-works" className="relative py-32 px-6">
            <div className="max-w-7xl mx-auto">
              <div className="overflow-hidden">
                <ScrollReveal>
                  <h2 className="text-5xl md:text-6xl font-black text-white text-center mb-4 tracking-tight">
                    How It Works
                  </h2>
                  <p className="text-center text-white/70 mb-16 text-lg">
                    Three simple steps to secure authentication
                  </p>
                </ScrollReveal>
              </div>

              <div className="grid md:grid-cols-3 gap-8 relative">
                {/* Connecting Lines */}
                <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-600/0 via-violet-600/50 to-violet-600/0 transform -translate-y-1/2" style={{ zIndex: 0 }} />

                {/* Step 1: Register */}
                <ScrollReveal delay={0.1}>
                  <motion.div
                    whileHover={{ y: -10, scale: 1.02 }}
                    className="relative glass p-8 rounded-2xl border border-violet-500/20 hover:border-violet-500/40 transition-all"
                    style={{ zIndex: 1 }}
                  >
                    <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                      <div className="w-12 h-12 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center text-xl font-bold shadow-lg">
                        1
                      </div>
                    </div>

                    <div className="mt-8 text-center">
                      <motion.div
                        className="w-20 h-20 bg-violet-600/20 rounded-full flex items-center justify-center mx-auto mb-6"
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.5 }}
                      >
                        <FaUpload className="w-10 h-10 text-violet-400" />
                      </motion.div>

                      <h3 className="text-2xl font-bold text-white mb-4">Register Your Brain</h3>
                      <p className="text-white/70 leading-relaxed">
                        Upload your EEG data to create your unique brain fingerprint
                      </p>
                    </div>
                  </motion.div>
                </ScrollReveal>

                {/* Step 2: Process */}
                <ScrollReveal delay={0.2}>
                  <motion.div
                    whileHover={{ y: -10, scale: 1.02 }}
                    className="relative glass p-8 rounded-2xl border border-violet-500/20 hover:border-violet-500/40 transition-all"
                    style={{ zIndex: 1 }}
                  >
                    <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                      <div className="w-12 h-12 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center text-xl font-bold shadow-lg">
                        2
                      </div>
                    </div>

                    <div className="mt-8 text-center">
                      <motion.div
                        className="w-20 h-20 bg-violet-600/20 rounded-full flex items-center justify-center mx-auto mb-6"
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.5 }}
                      >
                        <FaBrain className="w-10 h-10 text-violet-400" />
                      </motion.div>

                      <h3 className="text-2xl font-bold text-white mb-4">AI Processing</h3>
                      <p className="text-white/70 leading-relaxed">
                        Deep learning analyzes your brainwave patterns with 98% accuracy
                      </p>
                    </div>
                  </motion.div>
                </ScrollReveal>

                {/* Step 3: Authenticate */}
                <ScrollReveal delay={0.3}>
                  <motion.div
                    whileHover={{ y: -10, scale: 1.02 }}
                    className="relative glass p-8 rounded-2xl border border-violet-500/20 hover:border-violet-500/40 transition-all"
                    style={{ zIndex: 1 }}
                  >
                    <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                      <div className="w-12 h-12 bg-gradient-to-br from-violet-600 to-purple-600 rounded-full flex items-center justify-center text-xl font-bold shadow-lg">
                        3
                      </div>
                    </div>

                    <div className="mt-8 text-center">
                      <motion.div
                        className="w-20 h-20 bg-violet-600/20 rounded-full flex items-center justify-center mx-auto mb-6"
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.5 }}
                      >
                        <FaCheckCircle className="w-10 h-10 text-violet-400" />
                      </motion.div>

                      <h3 className="text-2xl font-bold text-white mb-4">Instant Verification</h3>
                      <p className="text-white/70 leading-relaxed">
                        Get authenticated in under 50ms with advanced spoof detection
                      </p>
                    </div>
                  </motion.div>
                </ScrollReveal>
              </div>
            </div>
          </section>

          {/* CTA Section - Always Visible */}
          <section className="relative py-32 px-6">
            <div className="max-w-4xl mx-auto text-center">
              <motion.h2
                initial={{ opacity: 1 }}
                className="text-5xl md:text-6xl font-black text-white mb-6 tracking-tight"
              >
                Ready to Experience the Future?
              </motion.h2>
              <motion.p
                initial={{ opacity: 1 }}
                className="text-lg md:text-xl text-white/70 mb-12 leading-relaxed"
              >
                Join the next generation of secure authentication
              </motion.p>
              <div className="flex flex-col items-center gap-4">
                <Link to="/login" className="w-full sm:w-auto">
                  <motion.button
                    whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(139, 92, 246, 0.5)" }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full sm:w-auto px-12 py-5 bg-gradient-to-r from-violet-600 to-purple-600 rounded-full font-bold text-xl shadow-2xl transition-all"
                  >
                    Start Authenticate →
                  </motion.button>
                </Link>
              </div>
            </div>
          </section>

          {/* Footer */}
          <footer id="contact" className="relative py-8 px-6 border-t border-white/10">
            <div className="max-w-7xl mx-auto">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <FaBrain className="w-6 h-6 text-violet-500" />
                  <span className="text-lg font-bold gradient-text">MindKey</span>
                </div>
                <p className="text-white/60 text-sm">
                  © 2025 MindKey. All rights reserved.
                </p>
                <div className="flex gap-6 text-sm text-white/60">
                  <a href="https://github.com/Sruthikr1505" target="_blank" rel="noopener noreferrer" className="hover:text-violet-500 transition-colors">GitHub</a>
                  <a href="#" className="hover:text-violet-500 transition-colors">Privacy</a>
                  <a href="#" className="hover:text-violet-500 transition-colors">Terms</a>
                  <a href="#" className="hover:text-violet-500 transition-colors">Contact</a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      )}
    </>
  )
}

export default HomePage


