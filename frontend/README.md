# Frontend for EEG Authentication

This directory contains a React + Tailwind CSS frontend skeleton for the EEG authentication system.

## Setup

### 1. Create React App with Vite

```bash
cd frontend
npm create vite@latest eeg-auth-app -- --template react
cd eeg-auth-app
```

### 2. Install Dependencies

```bash
npm install
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react
npm install axios
```

### 3. Configure Tailwind CSS

```bash
npx tailwindcss init -p
```

Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add to `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. Copy Component Skeletons

Copy the component files from `skeleton/` to `eeg-auth-app/src/components/`:

- `UploadEEG.jsx` - File upload component for EEG trials
- `WaveformPlot.jsx` - EEG waveform visualization
- `HeatmapDisplay.jsx` - Attention heatmap display
- `AuthResultCard.jsx` - Authentication result display

### 5. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## API Integration

The components use `axios` to communicate with the FastAPI backend at `http://localhost:8000`.

Make sure the backend is running before testing the frontend:

```bash
cd ..
python src/api/main.py
```

## Component Overview

### UploadEEG.jsx

Handles file upload for EEG trials (.npy files). Used for both registration and authentication.

**Props:**
- `onUpload(files)` - Callback when files are selected
- `multiple` - Allow multiple file selection (for enrollment)
- `label` - Button label text

### WaveformPlot.jsx

Displays EEG waveform data using HTML5 Canvas.

**Props:**
- `data` - EEG trial data (channels × samples)
- `fs` - Sampling frequency (default: 128 Hz)
- `channelsToShow` - Number of channels to display (default: 4)

### HeatmapDisplay.jsx

Displays attention/attribution heatmap from explainability module.

**Props:**
- `explainId` - Explanation ID from authentication response
- `apiUrl` - Backend API URL

### AuthResultCard.jsx

Displays authentication result with score, probability, and spoof detection.

**Props:**
- `result` - Authentication result object from API
- `onExplain` - Callback to show explanation

## Example App Structure

```jsx
// src/App.jsx
import { useState } from 'react'
import UploadEEG from './components/UploadEEG'
import AuthResultCard from './components/AuthResultCard'
import HeatmapDisplay from './components/HeatmapDisplay'

function App() {
  const [authResult, setAuthResult] = useState(null)
  const [showExplanation, setShowExplanation] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          EEG Authentication
        </h1>
        
        {/* Upload and auth components */}
        <UploadEEG onUpload={handleAuth} label="Authenticate" />
        
        {authResult && (
          <>
            <AuthResultCard 
              result={authResult} 
              onExplain={() => setShowExplanation(true)}
            />
            
            {showExplanation && (
              <HeatmapDisplay explainId={authResult.explain_id} />
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App
```

## Production Build

```bash
npm run build
```

The production build will be in `dist/` directory.

## Docker Deployment

The frontend can be served with nginx. See `../deployments/docker-compose.yml` for configuration.
