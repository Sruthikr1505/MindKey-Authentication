import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

/**
 * Heatmap Display Component
 * Fetches and displays explanation heatmap from backend
 */
const HeatmapDisplay = ({ explainId, apiUrl = 'http://localhost:8000' }) => {
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!explainId) return;

    const fetchExplanation = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get(`${apiUrl}/explain/${explainId}`, {
          responseType: 'blob'
        });
        
        const url = URL.createObjectURL(response.data);
        setImageUrl(url);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching explanation:', err);
        setError('Failed to load explanation');
        setLoading(false);
      }
    };

    fetchExplanation();

    // Cleanup
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [explainId, apiUrl]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Generating explanation...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">
        Explanation Heatmap
      </h3>
      <p className="text-sm text-gray-600 mb-4">
        This heatmap shows which channels and time windows were most important for the authentication decision.
      </p>
      {imageUrl && (
        <img
          src={imageUrl}
          alt="Explanation heatmap"
          className="w-full rounded border border-gray-200"
        />
      )}
    </div>
  );
};

export default HeatmapDisplay;
