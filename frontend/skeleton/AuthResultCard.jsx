import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

/**
 * Authentication Result Card Component
 * Displays authentication result with score, probability, and spoof detection
 */
const AuthResultCard = ({ result, onExplain }) => {
  if (!result) return null;

  const { authenticated, score, probability, is_spoof, spoof_error, message } = result;

  const getStatusIcon = () => {
    if (is_spoof) {
      return <AlertTriangle className="w-12 h-12 text-yellow-500" />;
    }
    if (authenticated) {
      return <CheckCircle className="w-12 h-12 text-green-500" />;
    }
    return <XCircle className="w-12 h-12 text-red-500" />;
  };

  const getStatusColor = () => {
    if (is_spoof) return 'yellow';
    if (authenticated) return 'green';
    return 'red';
  };

  const statusColor = getStatusColor();

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 border-2 border-${statusColor}-200`}>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          {getStatusIcon()}
        </div>
        
        <div className="flex-1">
          <h2 className={`text-2xl font-bold text-${statusColor}-700 mb-2`}>
            {authenticated ? 'Authentication Successful' : 
             is_spoof ? 'Spoof Detected' : 
             'Authentication Failed'}
          </h2>
          
          <p className="text-gray-600 mb-4">{message}</p>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 rounded p-3">
              <p className="text-sm text-gray-500 mb-1">Similarity Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {(score * 100).toFixed(1)}%
              </p>
            </div>
            
            <div className="bg-gray-50 rounded p-3">
              <p className="text-sm text-gray-500 mb-1">Confidence</p>
              <p className="text-2xl font-bold text-gray-900">
                {(probability * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          
          {is_spoof && spoof_error !== null && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    Anomaly Detected
                  </p>
                  <p className="text-xs text-yellow-700">
                    Reconstruction error: {spoof_error.toFixed(6)}
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {onExplain && (
            <button
              onClick={onExplain}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <Info className="w-4 h-4 mr-2" />
              View Explanation
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthResultCard;
