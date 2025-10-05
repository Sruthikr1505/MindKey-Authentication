import { motion } from 'framer-motion'

const LoadingSkeleton = ({ className = '' }) => {
  return (
    <motion.div
      className={`bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 rounded-lg ${className}`}
      animate={{
        backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'linear',
      }}
      style={{
        backgroundSize: '200% 100%',
      }}
    />
  )
}

export const CardSkeleton = () => (
  <div className="glass p-6 rounded-3xl space-y-4">
    <LoadingSkeleton className="h-8 w-3/4" />
    <LoadingSkeleton className="h-4 w-full" />
    <LoadingSkeleton className="h-4 w-5/6" />
    <LoadingSkeleton className="h-32 w-full" />
  </div>
)

export const DashboardSkeleton = () => (
  <div className="space-y-6">
    <LoadingSkeleton className="h-12 w-64" />
    <div className="grid md:grid-cols-2 gap-6">
      <CardSkeleton />
      <CardSkeleton />
    </div>
    <LoadingSkeleton className="h-96 w-full" />
  </div>
)

export default LoadingSkeleton
