import { motion } from 'framer-motion'
import { FaCheckCircle, FaExclamationCircle, FaTimesCircle } from 'react-icons/fa'

const SignalQualityIndicator = ({ quality = 0 }) => {
  const getQualityInfo = () => {
    if (quality >= 80) {
      return {
        label: 'Excellent',
        color: 'text-green-500',
        bgColor: 'bg-green-500/20',
        icon: <FaCheckCircle />,
        bars: 5,
      }
    } else if (quality >= 60) {
      return {
        label: 'Good',
        color: 'text-blue-500',
        bgColor: 'bg-blue-500/20',
        icon: <FaCheckCircle />,
        bars: 4,
      }
    } else if (quality >= 40) {
      return {
        label: 'Fair',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-500/20',
        icon: <FaExclamationCircle />,
        bars: 3,
      }
    } else if (quality >= 20) {
      return {
        label: 'Poor',
        color: 'text-orange-500',
        bgColor: 'bg-orange-500/20',
        icon: <FaExclamationCircle />,
        bars: 2,
      }
    } else {
      return {
        label: 'Very Poor',
        color: 'text-red-500',
        bgColor: 'bg-red-500/20',
        icon: <FaTimesCircle />,
        bars: 1,
      }
    }
  }

  const info = getQualityInfo()

  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl ${info.bgColor}`}>
      <div className={`text-2xl ${info.color}`}>{info.icon}</div>
      <div className="flex-1">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">Signal Quality</span>
          <span className={`text-sm font-bold ${info.color}`}>{info.label}</span>
        </div>
        <div className="flex gap-1">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className={`h-2 flex-1 rounded-full ${
                i < info.bars ? info.color.replace('text', 'bg') : 'bg-gray-700'
              }`}
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ delay: i * 0.1 }}
            />
          ))}
        </div>
      </div>
      <div className={`text-2xl font-bold ${info.color}`}>{quality}%</div>
    </div>
  )
}

export default SignalQualityIndicator
