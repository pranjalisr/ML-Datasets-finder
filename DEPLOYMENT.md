# 🚀 Deployment Guide

Deploy AI Training Data Sourcer to production in minutes.

## 1. Deploy to Render (Easiest - Free)

### Step 1: Create GitHub Repo

```bash
cd ai-data-sourcer
git init
git add .
git commit -m "Initial commit: AI Training Data Sourcer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-data-sourcer.git
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. Go to [render.com](https://render.com) and sign up
2. Click **New +** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   ```
   Name: ai-data-sourcer-backend
   Runtime: Python 3.11
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5. Add Environment Variable:
   ```
   DEEPSEEK_API_KEY = your_api_key_here
   ```
6. Click **Deploy**

### Step 3: Deploy Frontend to Render

1. Click **New +** → **Static Site**
2. Connect same repo
3. Configure:
   ```
   Name: ai-data-sourcer
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```
4. Add Environment Variable:
   ```
   VITE_API_URL = https://ai-data-sourcer-backend.onrender.com
   ```
5. Click **Deploy**

Your app is now live! 🎉

---

## 2. Deploy to Railway.app

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy Backend

1. Go to [railway.app](https://railway.app)
2. Click **New Project**
3. Select **GitHub Repo**
4. Select your repo
5. Configure service:
   ```
   Start Command: cd backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. Add Environment Variable: `DEEPSEEK_API_KEY`

### Step 3: Deploy Frontend

1. Add another service
2. Build Command: `cd frontend && npm install && npm run build`
3. Start Command: `npm run preview`
4. Add Port: `3000`

---

## 3. Deploy to AWS (EC2)

### Step 1: Launch EC2 Instance

```bash
# Launch Ubuntu 22.04 LTS instance
# Configure security group to allow ports 80, 443, 8000, 3000
```

### Step 2: Install Dependencies

```bash
ssh -i your-key.pem ubuntu@your-instance.ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
newgrp docker

# Install Git
sudo apt install git -y

# Clone repo
git clone https://github.com/YOUR_USERNAME/ai-data-sourcer.git
cd ai-data-sourcer
```

### Step 3: Create Environment File

```bash
cp .env.example .env
nano .env
# Add your DEEPSEEK_API_KEY
```

### Step 4: Run with Docker Compose

```bash
docker-compose up -d
```

### Step 5: Setup Nginx Reverse Proxy

```bash
sudo apt install nginx -y

# Create config file
sudo nano /etc/nginx/sites-available/default
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

```bash
# Reload nginx
sudo systemctl reload nginx
```

### Step 6: Enable HTTPS (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

Done! Access at https://your-domain.com

---

## 4. Deploy to Google Cloud Run

### Step 1: Build Docker Image

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-data-sourcer
```

### Step 2: Deploy Backend

```bash
gcloud run deploy ai-data-sourcer-backend \
  --image gcr.io/PROJECT_ID/ai-data-sourcer \
  --platform managed \
  --region us-central1 \
  --set-env-vars DEEPSEEK_API_KEY=your_key \
  --port 8000
```

### Step 3: Deploy Frontend

```bash
# Build static files in frontend/
cd frontend
npm run build

# Upload to Cloud Storage
gsutil -m cp -r dist/* gs://your-bucket/
```

---

## 5. Deploy with Docker Swarm (Multiple Servers)

```bash
# Initialize swarm
docker swarm init

# Create stack file
cat > stack.yml << 'EOF'
version: '3.8'
services:
  backend:
    image: ai-data-sourcer:latest
    ports:
      - "8000:8000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s

  frontend:
    image: ai-data-sourcer-frontend:latest
    ports:
      - "3000:3000"
    deploy:
      replicas: 2
EOF

# Deploy
docker stack deploy -c stack.yml ai-data-sourcer
```

---

## ✅ Post-Deployment Checklist

- [ ] API endpoint responding to requests
- [ ] Frontend loading correctly
- [ ] Search functionality working
- [ ] HTTPS enabled (if applicable)
- [ ] Environment variables set correctly
- [ ] Logging configured
- [ ] Monitoring/alerting set up
- [ ] Backups configured

---

## 🔧 Troubleshooting

### Backend not starting
```bash
docker logs container_name
# Check DEEPSEEK_API_KEY is set correctly
```

### Frontend not loading
```bash
# Check VITE_API_URL points to correct backend
# Check CORS is enabled in backend
```

### High latency
- Increase agent timeout in `backend/main.py`
- Add caching layer (Redis)
- Use CDN for frontend assets

### API rate limiting
- Implement request queuing
- Add rate limiting middleware
- Cache frequent searches

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Use load balancer (Nginx, HAProxy)
# Run multiple backend instances
# Use database for caching
```

### Vertical Scaling
```bash
# Increase instance size
# Add more memory/CPU
```

### Optimization
```python
# In backend/main.py
- Implement result caching
- Use async/await throughout
- Add pagination for large results
- Implement retry logic
```

---

## 🆘 Support

Having deployment issues?

1. Check logs: `docker logs -f container_name`
2. Verify API key: `echo $DEEPSEEK_API_KEY`
3. Test endpoint: `curl http://localhost:8000/health`
4. Open issue on GitHub

---

**Happy deploying!** 🚀
