const { execSync } = require('child_process');
const path = require('path');

console.log('Starting Vercel build process...');

// Navigate to the frontend directory
const frontendPath = path.join(__dirname, 'frontend', 'eeg-auth-app');

console.log('Installing frontend dependencies...');
try {
  execSync('npm install', { 
    cwd: frontendPath,
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'production' }
  });
  
  console.log('Building frontend...');
  execSync('npm run build', { 
    cwd: frontendPath,
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'production' }
  });
  
  console.log('Build completed successfully!');
  process.exit(0);
} catch (error) {
  console.error('Build failed:', error);
  process.exit(1);
}
