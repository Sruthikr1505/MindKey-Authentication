# 🚀 MindKey Deployment Guide

Complete guide to deploy your Thought-Based Authentication System with both frontend and backend.

---

## 📋 **Prerequisites**

- Git repository (GitHub, GitLab, or Bitbucket)
- Trained model files in `models/` directory
- Node.js and Python installed locally for testing

---

## 🌐 **Option 1: Deploy on Render (Recommended)**

### **Why Render?**
- ✅ Free tier available
- ✅ Automatic deployments from Git
- ✅ Built-in SSL certificates
- ✅ Easy environment variable management
- ✅ Supports both Python and Node.js

### **Step 1: Prepare Your Repository**

```bash
# Initialize git if not already done
cd /Users/sruthikr/Desktop/Thought\ Based\ Authentiction\ System\ Using\ BiLSTM/deap_bilstm_auth
git init
git add .
git commit -m "Initial commit - MindKey Authentication System"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/mindkey-auth.git
git branch -M main
git push -u origin main
```

### **Step 2: Deploy Backend (FastAPI)**

1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `mindkey-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src/api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.13.0`
   - `DATABASE_URL`: `sqlite:///./auth.db`

6. Click **"Create Web Service"**

7. **Note the URL**: `https://mindkey-api.onrender.com`

### **Step 3: Update Frontend API URL**

Update the API URL in your frontend:

```javascript
// frontend/eeg-auth-app/src/pages/LoginPage.jsx
const API_URL = 'https://mindkey-api.onrender.com'

// frontend/eeg-auth-app/src/pages/Dashboard.jsx
const API_URL = 'https://mindkey-api.onrender.com'
```

### **Step 4: Deploy Frontend (React + Vite)**

#### **Option A: Render Static Site**

1. Click **"New +"** → **"Static Site"**
2. Connect your repository
3. Configure:
   - **Name**: `mindkey-frontend`
   - **Build Command**: `cd frontend/eeg-auth-app && npm install && npm run build`
   - **Publish Directory**: `frontend/eeg-auth-app/dist`

4. Click **"Create Static Site"**

#### **Option B: Vercel (Alternative)**

```bash
cd frontend/eeg-auth-app
npm install -g vercel
vercel deploy --prod
```

#### **Option C: Netlify (Alternative)**

```bash
cd frontend/eeg-auth-app
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

---

## 🐳 **Option 2: Deploy with Docker (Advanced)**

### **Step 1: Create Dockerfiles**

**Backend Dockerfile** (`Dockerfile.backend`):
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`Dockerfile.frontend`):
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY frontend/eeg-auth-app/package*.json ./
RUN npm install

COPY frontend/eeg-auth-app/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### **Step 2: Docker Compose**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./auth.db

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### **Step 3: Deploy to Cloud**

Deploy to:
- **AWS ECS** (Elastic Container Service)
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**

---

## ☁️ **Option 3: Deploy on AWS (Production)**

### **Backend on AWS Lambda + API Gateway**

```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless.yml
serverless deploy
```

### **Frontend on AWS S3 + CloudFront**

```bash
cd frontend/eeg-auth-app
npm run build

# Upload to S3
aws s3 sync dist/ s3://mindkey-frontend --acl public-read

# Create CloudFront distribution
aws cloudfront create-distribution --origin-domain-name mindkey-frontend.s3.amazonaws.com
```

---

## 🔧 **Environment Configuration**

### **Backend Environment Variables**

```bash
# .env file
DATABASE_URL=sqlite:///./auth.db
CORS_ORIGINS=https://your-frontend-url.com
SECRET_KEY=your-secret-key-here
MODEL_PATH=./models
```

### **Frontend Environment Variables**

Create `.env.production`:

```bash
VITE_API_URL=https://mindkey-api.onrender.com
VITE_APP_NAME=MindKey
```

---

## 📊 **Post-Deployment Checklist**

- [ ] Backend API is accessible
- [ ] Frontend loads correctly
- [ ] CORS is configured properly
- [ ] Model files are uploaded
- [ ] Database is initialized
- [ ] SSL certificates are active
- [ ] Environment variables are set
- [ ] Test authentication flow
- [ ] Monitor logs for errors

---

## 🔒 **Security Considerations**

1. **Enable HTTPS** - Use SSL certificates
2. **Set CORS properly** - Only allow your frontend domain
3. **Secure API keys** - Use environment variables
4. **Rate limiting** - Prevent abuse
5. **Database backups** - Regular backups
6. **Monitor logs** - Track authentication attempts

---

## 📈 **Monitoring & Maintenance**

### **Render Dashboard**
- View logs in real-time
- Monitor CPU/Memory usage
- Set up alerts

### **Error Tracking**
```bash
# Install Sentry for error tracking
pip install sentry-sdk
npm install @sentry/react
```

---

## 🚀 **Quick Deploy Commands**

### **Deploy Everything (Render)**

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy MindKey"
git push origin main

# 2. Render will auto-deploy from GitHub
# (after initial setup)
```

### **Deploy Frontend Only (Vercel)**

```bash
cd frontend/eeg-auth-app
vercel --prod
```

### **Deploy Backend Only (Render)**

```bash
# Push changes
git push origin main
# Render auto-deploys
```

---

## 🌍 **Your Deployed URLs**

After deployment, you'll have:

- **Frontend**: `https://mindkey.vercel.app`
- **Backend API**: `https://mindkey-api.onrender.com`
- **API Docs**: `https://mindkey-api.onrender.com/docs`

---

## 🆘 **Troubleshooting**

### **Backend won't start**
```bash
# Check logs
render logs --tail

# Verify requirements.txt
pip install -r requirements.txt
```

### **Frontend can't connect to API**
- Check CORS settings in backend
- Verify API_URL in frontend
- Check browser console for errors

### **Model files missing**
- Upload models to backend server
- Check file paths in code
- Verify model files in repository

---

## 📚 **Additional Resources**

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)

---

**Your MindKey Thought-Based Authentication System is now ready for the world! 🧠✨**
