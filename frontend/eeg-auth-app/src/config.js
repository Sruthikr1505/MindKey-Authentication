// API Configuration
// Use relative URLs for Vercel proxy in production, direct URL for local dev
export const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : "http://localhost:8000";

// Other configuration constants can be added here
export const APP_NAME = "EEG Authentication System";
export const APP_VERSION = "1.0.0";

// Debug log (remove after testing)
console.log('API_BASE_URL:', API_BASE_URL);
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);