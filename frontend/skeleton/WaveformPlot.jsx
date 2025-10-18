import React, { useEffect, useRef } from 'react';

/**
 * EEG Waveform Plot Component
 * Displays EEG channels using HTML5 Canvas
 */
const WaveformPlot = ({ data, fs = 128, channelsToShow = 4, width = 800, height = 400 }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Parse data if needed
    let eegData = data;
    if (typeof data === 'string') {
      eegData = JSON.parse(data);
    }
    
    const nChannels = Math.min(channelsToShow, eegData.length);
    const nSamples = eegData[0].length;
    const channelHeight = height / nChannels;
    
    // Draw each channel
    for (let ch = 0; ch < nChannels; ch++) {
      const yOffset = (ch + 0.5) * channelHeight;
      const channelData = eegData[ch];
      
      // Normalize data
      const min = Math.min(...channelData);
      const max = Math.max(...channelData);
      const range = max - min || 1;
      
      // Draw waveform
      ctx.beginPath();
      ctx.strokeStyle = `hsl(${(ch * 360) / nChannels}, 70%, 50%)`;
      ctx.lineWidth = 1;
      
      for (let i = 0; i < nSamples; i++) {
        const x = (i / nSamples) * width;
        const normalized = (channelData[i] - min) / range;
        const y = yOffset - (normalized - 0.5) * (channelHeight * 0.8);
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      
      ctx.stroke();
      
      // Draw channel label
      ctx.fillStyle = '#374151';
      ctx.font = '12px sans-serif';
      ctx.fillText(`Ch ${ch}`, 5, yOffset - channelHeight / 2 + 15);
      
      // Draw separator line
      if (ch < nChannels - 1) {
        ctx.beginPath();
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        ctx.moveTo(0, (ch + 1) * channelHeight);
        ctx.lineTo(width, (ch + 1) * channelHeight);
        ctx.stroke();
      }
    }
    
    // Draw time axis
    ctx.fillStyle = '#6b7280';
    ctx.font = '11px sans-serif';
    const duration = nSamples / fs;
    for (let t = 0; t <= duration; t += 1) {
      const x = (t / duration) * width;
      ctx.fillText(`${t}s`, x, height - 5);
    }
    
  }, [data, fs, channelsToShow, width, height]);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">EEG Waveform</h3>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="border border-gray-200 rounded"
      />
    </div>
  );
};

export default WaveformPlot;
