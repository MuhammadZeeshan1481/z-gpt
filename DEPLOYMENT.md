# Deployment Guide for Z-GPT

This guide covers various deployment options for the Z-GPT application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Considerations](#production-considerations)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- Git
- Python 3.10+ (for local/traditional deployment)
- Node.js 18+ (for frontend)
- Docker and Docker Compose (for containerized deployment)
- 8GB+ RAM (for running AI models)
- 20GB+ disk space (for models)

### Optional
- NVIDIA GPU with CUDA support (for faster inference)
- Redis (for caching)
- Nginx (as reverse proxy)

## Local Development

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/MuhammadZeeshan1481/z-gpt.git
cd z-gpt
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Hugging Face token
nano .env
```

5. **Run the backend**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Docker Deployment

### Quick Start with Docker Compose

1. **Clone and configure**
```bash
git clone https://github.com/MuhammadZeeshan1481/z-gpt.git
cd z-gpt
cp .env.example .env
# Edit .env with your configuration
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Check logs**
```bash
docker-compose logs -f
```

4. **Stop services**
```bash
docker-compose down
```

### Individual Container Deployment

#### Backend Container
```bash
# Build
docker build -t zgpt-backend -f Dockerfile .

# Run
docker run -d \
  --name zgpt-backend \
  -p 8000:8000 \
  -e HUGGINGFACEHUB_API_TOKEN=your_token \
  -v $(pwd)/models:/app/models \
  zgpt-backend
```

#### Frontend Container
```bash
# Build
docker build -t zgpt-frontend -f Dockerfile.frontend .

# Run
docker run -d \
  --name zgpt-frontend \
  -p 3000:80 \
  zgpt-frontend
```

### Docker with GPU Support

```yaml
# docker-compose.gpu.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create ECR repositories**
```bash
aws ecr create-repository --repository-name zgpt-backend
aws ecr create-repository --repository-name zgpt-frontend
```

2. **Build and push images**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -t zgpt-backend .
docker tag zgpt-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/zgpt-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/zgpt-backend:latest

# Build and push frontend
docker build -t zgpt-frontend -f Dockerfile.frontend .
docker tag zgpt-frontend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/zgpt-frontend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/zgpt-frontend:latest
```

3. **Create ECS task definition** (use AWS Console or CLI)

4. **Deploy to ECS**
```bash
aws ecs update-service --cluster zgpt-cluster --service zgpt-backend --force-new-deployment
```

#### Using AWS Lambda (for API only)

```bash
# Install additional dependencies
pip install mangum

# Create Lambda deployment package
zip -r function.zip backend/ -x "*.pyc" "*.pyo" "__pycache__/*"

# Deploy
aws lambda create-function \
  --function-name zgpt-api \
  --runtime python3.10 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler backend.main.handler \
  --zip-file fileb://function.zip \
  --memory-size 2048 \
  --timeout 60
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push to GCR**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/zgpt-backend
gcloud builds submit --tag gcr.io/PROJECT_ID/zgpt-frontend -f Dockerfile.frontend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy zgpt-backend \
  --image gcr.io/PROJECT_ID/zgpt-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --set-env-vars HUGGINGFACEHUB_API_TOKEN=your_token

gcloud run deploy zgpt-frontend \
  --image gcr.io/PROJECT_ID/zgpt-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Microsoft Azure

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name zgpt-rg --location eastus

# Deploy backend
az container create \
  --resource-group zgpt-rg \
  --name zgpt-backend \
  --image YOUR_REGISTRY/zgpt-backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables HUGGINGFACEHUB_API_TOKEN=your_token

# Deploy frontend
az container create \
  --resource-group zgpt-rg \
  --name zgpt-frontend \
  --image YOUR_REGISTRY/zgpt-frontend:latest \
  --cpu 1 \
  --memory 1 \
  --ports 80
```

### Kubernetes Deployment

1. **Create namespace**
```bash
kubectl create namespace zgpt
```

2. **Create secrets**
```bash
kubectl create secret generic zgpt-secrets \
  --from-literal=hf-token=your_token \
  --namespace zgpt
```

3. **Apply deployments**

Create `k8s/backend-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zgpt-backend
  namespace: zgpt
spec:
  replicas: 2
  selector:
    matchLabels:
      app: zgpt-backend
  template:
    metadata:
      labels:
        app: zgpt-backend
    spec:
      containers:
      - name: backend
        image: your-registry/zgpt-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: HUGGINGFACEHUB_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: zgpt-secrets
              key: hf-token
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: zgpt-backend-service
  namespace: zgpt
spec:
  selector:
    app: zgpt-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

## Production Considerations

### Environment Configuration

**Critical Settings:**
```bash
# Security
SECRET_KEY=<generate-strong-secret>
ALLOWED_ORIGINS=https://yourdomain.com
DEBUG=False

# Performance
USE_LOCAL_MODELS=True
HF_HOME=/var/models
TRANSFORMERS_CACHE=/var/models/transformers

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
```

### Reverse Proxy Setup (Nginx)

Create `/etc/nginx/sites-available/zgpt`:
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/zgpt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/TLS Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
sudo certbot renew --dry-run  # Test renewal
```

### Systemd Service (for non-Docker deployment)

Create `/etc/systemd/system/zgpt-backend.service`:
```ini
[Unit]
Description=Z-GPT Backend
After=network.target

[Service]
Type=simple
User=zgpt
WorkingDirectory=/opt/zgpt
Environment="PATH=/opt/zgpt/venv/bin"
ExecStart=/opt/zgpt/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zgpt-backend
sudo systemctl start zgpt-backend
sudo systemctl status zgpt-backend
```

### Monitoring

#### Prometheus + Grafana

Add to `requirements.txt`:
```
prometheus-client
prometheus-fastapi-instrumentator
```

Instrument FastAPI:
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

#### Health Checks

```bash
# Check backend health
curl https://yourdomain.com/health

# Check with monitoring tool
while true; do
    curl -s https://yourdomain.com/health | jq '.status'
    sleep 60
done
```

### Backup Strategy

```bash
# Backup models
tar -czf models-backup-$(date +%Y%m%d).tar.gz models/

# Backup configuration
cp .env .env.backup-$(date +%Y%m%d)

# Backup to S3
aws s3 cp models-backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

### Scaling Considerations

1. **Horizontal Scaling**
   - Use load balancer (AWS ALB, GCP Load Balancer)
   - Share model cache via NFS or object storage
   - Stateless API design allows multiple replicas

2. **Vertical Scaling**
   - Increase memory for larger models
   - Add GPU for faster inference
   - Increase CPU for better throughput

3. **Caching**
   - Implement Redis for response caching
   - Cache language detection results
   - Cache translation results

## Troubleshooting

### Common Issues

#### Out of Memory
```bash
# Solution 1: Increase container memory
docker run --memory="8g" ...

# Solution 2: Use smaller models
MODEL_NAME=distilgpt2

# Solution 3: Enable model quantization
USE_QUANTIZATION=True
```

#### Slow Model Loading
```bash
# Pre-download models
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.1')"

# Use model cache
HF_HOME=/path/to/cache
```

#### CORS Issues
```bash
# Check CORS configuration
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Verify in logs
curl -H "Origin: http://localhost:3000" http://localhost:8000/
```

#### Image Generation Timeout
```bash
# Increase timeout
IMAGE_GENERATION_TIMEOUT=300

# Use GPU
docker run --gpus all ...
```

### Logs

```bash
# Docker Compose logs
docker-compose logs -f backend

# Individual container
docker logs -f zgpt-backend

# Kubernetes
kubectl logs -f deployment/zgpt-backend -n zgpt

# Systemd service
sudo journalctl -u zgpt-backend -f
```

### Performance Tuning

```bash
# Enable model optimization
USE_LOCAL_MODELS=True

# Reduce max tokens
MAX_NEW_TOKENS=150

# Adjust batch size
BATCH_SIZE=1

# Use CPU efficiently
OMP_NUM_THREADS=4
```

## Maintenance

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Deploy with zero downtime
docker-compose up -d --no-deps --build backend
```

### Update Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node packages
cd frontend && npm update
```

### Monitor Resources

```bash
# Docker stats
docker stats

# System resources
htop

# Disk usage
df -h
du -sh models/
```

## Support

For deployment issues:
- GitHub Issues: https://github.com/MuhammadZeeshan1481/z-gpt/issues
- Documentation: See README.md and ARCHITECTURE.md
- Community: [Your community channel]
