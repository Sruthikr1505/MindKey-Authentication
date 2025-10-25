# 🚀 Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Docker** (for containerized deployment)
- **Git**
- **Python Virtual Environment** (recommended)

## Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/eeg-auth-system.git
cd eeg-auth-system
```

### 2. Set Up Backend
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.api.auth_logger import AuthLogger; AuthLogger('auth_logs.db')._init_db()"
```

### 3. Set Up Frontend
```bash
cd frontend/eeg-auth-app
npm install
npm run build
cd ../..
```

### 4. Start the Application
```bash
# Start backend
uvicorn src.api.main:app --reload

# In another terminal, start frontend dev server
cd frontend/eeg-auth-app
npm run dev
```

## Docker Deployment

### 1. Build and Run with Docker Compose
```bash
docker-compose up --build -d
```

### 2. View Logs
```bash
docker-compose logs -f
```

### 3. Stop Containers
```bash
docker-compose down
```

## Cloud Deployment

### Heroku

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Deploy to Heroku:
```bash
git push heroku main
```

4. Set required configs:
```bash
heroku config:set PYTHONPATH=/app
heroku config:set MODEL_PATH=/app/models/bilstm_encoder.pth
heroku config:set PROTOTYPES_PATH=/app/data/prototypes.pkl
```

### Railway

1. Click the button below to deploy to Railway:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=your-template-id)

2. Configure environment variables as shown in the Environment Variables section.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```ini
# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./auth_logs.db
MODEL_PATH=./models/bilstm_encoder.pth
PROTOTYPES_PATH=./data/prototypes.pkl

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Error: `Address already in use`
   - Solution: Change the port or stop the process using the port
   ```bash
   # On Linux/macOS
   lsof -i :8000
   kill -9 <PID>

   # On Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Database Connection Issues**
   - Error: `sqlite3.OperationalError: unable to open database file`
   - Solution: Ensure the database directory is writable
   ```bash
   chmod 777 .  # For development only
   ```

3. **Frontend Not Connecting to Backend**
   - Error: `Connection refused`
   - Solution: Check if the backend is running and CORS is enabled
   ```bash
   # In src/api/main.py, ensure CORS is configured:
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # In production, replace with your frontend URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Missing Dependencies**
   - Error: `ModuleNotFoundError`
   - Solution: Install missing dependencies
   ```bash
   pip install -r requirements.txt
   cd frontend/eeg-auth-app && npm install
   ```

## Monitoring and Maintenance

### Viewing Logs
```bash
# Docker logs
docker-compose logs -f

# Application logs (if using file logging)
tail -f logs/app.log
```

### Database Backup
```bash
# Backup SQLite database
cp auth_logs.db auth_logs_$(date +%Y%m%d).db

# Backup to S3 (if configured)
aws s3 cp auth_logs.db s3://your-bucket/backups/auth_logs_$(date +%Y%m%d).db
```

## Security Considerations

1. **Production Deployment**
   - Use HTTPS
   - Set strong secrets
   - Enable rate limiting
   - Use a production WSGI server (e.g., Gunicorn with Uvicorn workers)

2. **Secrets Management**
   - Never commit `.env` to version control
   - Use environment variables or a secrets management service

3. **Updates**
   - Regularly update dependencies
   - Monitor for security advisories

## Support

For issues and feature requests, please open an issue on the [GitHub repository](https://github.com/yourusername/eeg-auth-system/issues).

---

**Note**: This guide assumes a basic understanding of web development and deployment. For production deployments, consult with a DevOps professional to ensure proper security and scalability measures are in place.
