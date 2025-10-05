# MindKey - Complete Deployment Guide

## 🚀 Deploy as a Live Website (Frontend + Backend)

This guide covers deploying your MindKey authentication system as a fully responsive website.

---

## 📋 **Table of Contents**

1. [Quick Deploy (Easiest)](#quick-deploy-easiest)
2. [Frontend Deployment](#frontend-deployment)
3. [Backend Deployment](#backend-deployment)
4. [Responsive Design Check](#responsive-design-check)
5. [Custom Domain Setup](#custom-domain-setup)
6. [Production Checklist](#production-checklist)

---

## 🎯 **Quick Deploy (Easiest)**

### **Option 1: Vercel (Frontend) + Render (Backend)** ⭐ Recommended

**Total Time:** 15-20 minutes  
**Cost:** FREE  
**Difficulty:** ⭐ Easy

---

## 📱 **Frontend Deployment (Vercel)**

### **Step 1: Prepare Frontend**

```bash
cd frontend/eeg-auth-app

# Update API URL for production
# Edit src/pages/LoginPage.jsx and Dashboard.jsx
```

Create `.env.production` file:

```bash
# frontend/eeg-auth-app/.env.production
VITE_API_URL=https://your-backend.onrender.com
```

Update API URL in code:

```javascript
// src/pages/LoginPage.jsx
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### **Step 2: Build Frontend**

```bash
npm run build
```

This creates a `dist/` folder with optimized files.

### **Step 3: Deploy to Vercel**

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend/eeg-auth-app
vercel --prod
```

**Option B: Using Vercel Dashboard**

1. Go to [vercel.com](https://vercel.com)
2. Click "**Add New Project**"
3. Import from Git (push to GitHub first)
4. Configure:
   - Framework: **Vite**
   - Root Directory: `frontend/eeg-auth-app`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add Environment Variable:
   - `VITE_API_URL` = `https://your-backend.onrender.com`
6. Click "**Deploy**"

**Your frontend will be live at:** `https://mindkey.vercel.app`

---

## 🖥️ **Backend Deployment (Render)**

### **Step 1: Prepare Backend**

Create `requirements.txt` (already exists):

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
numpy==1.24.3
torch==2.1.0
captum==0.6.0
scikit-learn==1.3.2
sqlalchemy==2.0.23
bcrypt==4.1.1
```

Create `render.yaml`:

```yaml
services:
  - type: web
    name: mindkey-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd src/api && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### **Step 2: Push to GitHub**

```bash
cd /Users/sruthikr/Desktop/Thought\ Based\ Authentiction\ System\ Using\ BiLSTM/deap_bilstm_auth

# Initialize git
git init
git add .
git commit -m "Initial commit - MindKey Authentication System"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/mindkey-auth.git
git branch -M main
git push -u origin main
```

### **Step 3: Deploy to Render**

1. Go to [render.com](https://render.com)
2. Click "**New +**" → "**Web Service**"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `mindkey-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd src/api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
5. Add Environment Variables:
   - `PYTHON_VERSION` = `3.11.0`
6. Click "**Create Web Service**"

**Your backend will be live at:** `https://mindkey-api.onrender.com`

### **Step 4: Update CORS**

Edit `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mindkey.vercel.app",  # Your Vercel frontend
        "http://localhost:5173"  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📱 **Responsive Design Check**

Your frontend is already responsive! But let's verify:

### **Test Responsive Design**

```bash
# Run locally
cd frontend/eeg-auth-app
npm run dev
```

Open browser DevTools (F12) and test these breakpoints:

| Device | Width | Status |
|--------|-------|--------|
| Mobile | 375px | ✅ Responsive |
| Tablet | 768px | ✅ Responsive |
| Desktop | 1024px | ✅ Responsive |
| Large | 1440px | ✅ Responsive |

### **Responsive Features Already Implemented:**

✅ **Tailwind CSS** - Mobile-first responsive classes  
✅ **Flexbox/Grid** - Adaptive layouts  
✅ **Media Queries** - `sm:`, `md:`, `lg:`, `xl:` breakpoints  
✅ **Touch-friendly** - Large buttons, proper spacing  
✅ **Responsive Navigation** - Adapts to screen size  
✅ **Responsive Charts** - `ResponsiveContainer` in graphs  

---

## 🌐 **Alternative Deployment Options**

### **Option 2: Netlify (Frontend) + Railway (Backend)**

**Frontend (Netlify):**

```bash
cd frontend/eeg-auth-app

# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

**Backend (Railway):**

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repo
4. Railway auto-detects Python
5. Add start command: `cd src/api && uvicorn main:app --host 0.0.0.0 --port $PORT`

---

### **Option 3: AWS (Advanced)**

**Frontend (S3 + CloudFront):**

```bash
# Build
npm run build

# Upload to S3
aws s3 sync dist/ s3://mindkey-frontend

# Setup CloudFront distribution
```

**Backend (EC2 or Lambda):**

```bash
# EC2 deployment
ssh ubuntu@your-ec2-instance
git clone your-repo
cd deap_bilstm_auth
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

---

### **Option 4: Docker (Any Platform)**

Create `Dockerfile` for backend:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - PYTHON_ENV=production

  frontend:
    build: ./frontend/eeg-auth-app
    ports:
      - "80:80"
    depends_on:
      - backend
```

Deploy to:
- **DigitalOcean App Platform**
- **Google Cloud Run**
- **Azure Container Instances**

---

## 🔒 **Production Checklist**

### **Security:**

- [ ] Enable HTTPS (automatic on Vercel/Render)
- [ ] Update CORS to specific domains
- [ ] Add rate limiting
- [ ] Secure environment variables
- [ ] Enable authentication tokens
- [ ] Add API key for backend

### **Performance:**

- [ ] Enable caching
- [ ] Compress static assets
- [ ] Use CDN for frontend
- [ ] Optimize images
- [ ] Enable gzip compression

### **Monitoring:**

- [ ] Setup error tracking (Sentry)
- [ ] Add analytics (Google Analytics)
- [ ] Monitor uptime (UptimeRobot)
- [ ] Setup logging
- [ ] Add performance monitoring

### **Database:**

- [ ] Use PostgreSQL instead of SQLite
- [ ] Setup database backups
- [ ] Enable connection pooling

---

## 🎨 **Custom Domain Setup**

### **Frontend (Vercel):**

1. Go to Vercel Dashboard → Your Project
2. Settings → Domains
3. Add domain: `mindkey.yourdomain.com`
4. Update DNS:
   ```
   Type: CNAME
   Name: mindkey
   Value: cname.vercel-dns.com
   ```

### **Backend (Render):**

1. Go to Render Dashboard → Your Service
2. Settings → Custom Domain
3. Add domain: `api.yourdomain.com`
4. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

---

## 📊 **Cost Breakdown**

### **Free Tier (Recommended for Start):**

| Service | Frontend | Backend | Total |
|---------|----------|---------|-------|
| **Vercel + Render** | FREE | FREE | **$0/month** |
| Bandwidth | 100GB | Limited | - |
| Build Minutes | 6000/month | 750 hours | - |
| SSL | ✅ Free | ✅ Free | - |

### **Paid Tier (For Production):**

| Service | Frontend | Backend | Total |
|---------|----------|---------|-------|
| **Vercel Pro + Render** | $20/mo | $7/mo | **$27/month** |
| Bandwidth | Unlimited | Unlimited | - |
| Performance | ⚡ Fast | ⚡ Fast | - |
| Support | ✅ Priority | ✅ Email | - |

---

## 🚀 **Quick Deploy Commands**

### **Complete Deployment (5 minutes):**

```bash
# 1. Build Frontend
cd frontend/eeg-auth-app
npm run build

# 2. Deploy Frontend
vercel --prod

# 3. Push to GitHub
cd ../..
git add .
git commit -m "Deploy MindKey"
git push

# 4. Deploy Backend on Render (via dashboard)
# Go to render.com and connect GitHub repo

# Done! Your site is live! 🎉
```

---

## 🌍 **Your Live URLs**

After deployment, you'll have:

- **Frontend:** `https://mindkey.vercel.app`
- **Backend:** `https://mindkey-api.onrender.com`
- **API Docs:** `https://mindkey-api.onrender.com/docs`
- **Sample EEG:** `https://mindkey-api.onrender.com/samples/list`

---

## 📱 **Mobile Responsive Features**

Your app is already mobile-ready with:

✅ **Touch-friendly buttons** - Large tap targets  
✅ **Responsive navigation** - Hamburger menu on mobile  
✅ **Adaptive layouts** - Stack on mobile, grid on desktop  
✅ **Readable text** - Proper font sizes for mobile  
✅ **Optimized images** - Lazy loading  
✅ **Fast loading** - Code splitting  

---

## 🎯 **Next Steps**

1. **Deploy Backend** → Render (5 min)
2. **Deploy Frontend** → Vercel (5 min)
3. **Test Live Site** → Mobile & Desktop
4. **Add Custom Domain** → Optional
5. **Share Your Project** → Show the world! 🌟

---

## 💡 **Tips**

- Start with **free tier** to test
- Use **Render** for backend (easier than AWS)
- Use **Vercel** for frontend (automatic deployments)
- Add **custom domain** later
- Monitor with **free tools** first

---

## 🆘 **Troubleshooting**

### **Backend not loading models:**
- Ensure `models/` folder is in repo
- Check file paths in code
- Verify Python version (3.11)

### **Frontend can't connect to backend:**
- Check CORS settings
- Verify API URL in `.env.production`
- Check browser console for errors

### **Slow loading:**
- Enable caching
- Use CDN
- Optimize images
- Enable compression

---

**Your MindKey system is now ready to deploy as a live, responsive website!** 🚀✨

**Estimated deployment time: 15-20 minutes**  
**Cost: FREE (with free tiers)**
