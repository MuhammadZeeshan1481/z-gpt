# Troubleshooting Guide

This guide helps you diagnose and fix common issues with Z-GPT.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Performance Issues](#performance-issues)
4. [API Issues](#api-issues)
5. [Docker Issues](#docker-issues)
6. [Model Loading Issues](#model-loading-issues)
7. [Frontend Issues](#frontend-issues)

## Installation Issues

### Python Version Error

**Problem:** `ERROR: Python 3.10 or higher is required`

**Solution:**
```bash
# Check your Python version
python --version

# Install Python 3.10+ from python.org
# Or use pyenv
pyenv install 3.10.0
pyenv local 3.10.0
```

### Pip Installation Fails

**Problem:** Package installation fails with compilation errors

**Solution:**
```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Install build dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Install build dependencies (macOS)
xcode-select --install

# Try installing with pre-built wheels
pip install --prefer-binary -r requirements.txt
```

### PyTorch Installation Issues

**Problem:** PyTorch installation fails or takes too long

**Solution:**
```bash
# CPU only version (faster download)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# GPU version (CUDA 11.8)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# GPU version (CUDA 12.1)
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

## Runtime Errors

### Out of Memory Error

**Problem:** `RuntimeError: CUDA out of memory` or system runs out of RAM

**Solution:**
```bash
# 1. Use smaller batch size
MAX_NEW_TOKENS=100

# 2. Use CPU instead of GPU
DEVICE=cpu

# 3. Use model quantization
USE_QUANTIZATION=True

# 4. Increase system swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 5. Use smaller model
MODEL_NAME=distilgpt2
```

### Module Not Found Error

**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
```bash
# Make sure you're in the correct directory
cd /path/to/z-gpt

# Run with Python module syntax
python -m uvicorn backend.main:app --reload

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.main:app --reload
```

### Permission Denied Error

**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Check file permissions
ls -la

# Fix permissions
chmod +x script.sh
chmod -R 755 backend/

# For model cache
mkdir -p models
chmod -R 755 models/
```

### Environment Variable Not Found

**Problem:** `KeyError: 'HUGGINGFACEHUB_API_TOKEN'`

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Edit and add your token
nano .env

# Verify environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('HUGGINGFACEHUB_API_TOKEN'))"
```

## Performance Issues

### Slow Model Loading

**Problem:** Models take too long to load on startup

**Solution:**
```bash
# Pre-download models
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model_name = 'mistralai/Mistral-7B-Instruct-v0.1'
print('Downloading model...')
AutoTokenizer.from_pretrained(model_name)
AutoModelForCausalLM.from_pretrained(model_name)
print('Model downloaded successfully')
"

# Use local cache
HF_HOME=/path/to/cache
TRANSFORMERS_CACHE=/path/to/cache

# Keep models loaded (lazy loading is enabled by default)
USE_LOCAL_MODELS=True
```

### Slow Response Times

**Problem:** API responses are too slow

**Solution:**
```bash
# 1. Use GPU acceleration
docker run --gpus all ...

# 2. Reduce max tokens
MAX_NEW_TOKENS=150

# 3. Enable caching (future feature)
USE_CACHE=True

# 4. Optimize inference
DO_SAMPLE=False
TEMPERATURE=0.7

# 5. Use quantization
USE_QUANTIZATION=True

# 6. Increase worker processes
uvicorn backend.main:app --workers 4
```

### High Memory Usage

**Problem:** Application uses too much memory

**Solution:**
```bash
# 1. Clear model cache
rm -rf models/transformers/*

# 2. Use smaller models
MODEL_NAME=distilgpt2

# 3. Limit context length
MAX_HISTORY_LENGTH=5

# 4. Monitor memory
watch -n 1 'free -h'

# 5. Restart service periodically
# Add to crontab: 0 3 * * * systemctl restart zgpt-backend
```

## API Issues

### CORS Error

**Problem:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
```bash
# In .env file
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# For development (not recommended for production)
ALLOWED_ORIGINS=*

# Check CORS headers
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8000/chat/
```

### 422 Validation Error

**Problem:** `422 Unprocessable Entity` when calling API

**Solution:**
```bash
# Check request format
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message",
    "history": []
  }' -v

# Common issues:
# - Missing required fields
# - Wrong data types
# - Too long messages (>1000 chars)
# - Invalid history format
```

### 500 Internal Server Error

**Problem:** API returns 500 error

**Solution:**
```bash
# 1. Check backend logs
docker-compose logs backend

# 2. Enable debug mode
DEBUG=True

# 3. Check if models are loaded
curl http://localhost:8000/health

# 4. Verify environment variables
docker-compose config

# 5. Test with minimal request
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "hi"}'
```

### Connection Refused

**Problem:** `Connection refused` or `Unable to connect`

**Solution:**
```bash
# 1. Check if backend is running
curl http://localhost:8000/

# 2. Check ports
netstat -tulpn | grep 8000
lsof -i :8000

# 3. Check firewall
sudo ufw status
sudo ufw allow 8000

# 4. Check Docker networking
docker network ls
docker network inspect z-gpt_zgpt-network
```

## Docker Issues

### Container Won't Start

**Problem:** Docker container exits immediately

**Solution:**
```bash
# Check container logs
docker-compose logs backend

# Check for port conflicts
netstat -tulpn | grep 8000

# Remove old containers
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Volume Mount Issues

**Problem:** Changes not reflected or permission errors

**Solution:**
```bash
# Check volume mounts
docker-compose config

# Fix permissions
sudo chown -R $USER:$USER models/

# Remove volumes and recreate
docker-compose down -v
docker-compose up -d
```

### Build Failures

**Problem:** Docker build fails

**Solution:**
```bash
# Clear build cache
docker builder prune -a

# Build with more memory
docker build --memory=4g -t zgpt-backend .

# Check Dockerfile syntax
docker build --no-cache -t zgpt-backend .

# Build step by step
docker build --target backend -t zgpt-backend-debug .
```

### Network Issues

**Problem:** Containers can't communicate

**Solution:**
```bash
# Check network
docker network ls
docker network inspect zgpt_zgpt-network

# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Test connectivity
docker-compose exec backend ping frontend
```

## Model Loading Issues

### Model Download Fails

**Problem:** Can't download models from Hugging Face

**Solution:**
```bash
# 1. Check internet connection
curl -I https://huggingface.co

# 2. Set proxy if needed
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 3. Use mirror
export HF_ENDPOINT=https://hf-mirror.com

# 4. Download manually
huggingface-cli login
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.1

# 5. Check disk space
df -h
```

### Invalid Token Error

**Problem:** `401 Unauthorized` when accessing models

**Solution:**
```bash
# 1. Get valid token from https://huggingface.co/settings/tokens

# 2. Update .env file
HUGGINGFACEHUB_API_TOKEN=your_valid_token

# 3. Test token
curl -H "Authorization: Bearer $HUGGINGFACEHUB_API_TOKEN" \
  https://huggingface.co/api/whoami

# 4. For private models, ensure you have access
```

### Model Loading Timeout

**Problem:** Model loading times out

**Solution:**
```bash
# Increase timeout
IMAGE_GENERATION_TIMEOUT=300

# Pre-download models before starting service
python scripts/download_models.py

# Use cached models
HF_HOME=/var/cache/huggingface
USE_LOCAL_MODELS=True
```

## Frontend Issues

### npm Install Fails

**Problem:** Frontend dependencies fail to install

**Solution:**
```bash
# Clear cache
npm cache clean --force

# Delete node_modules and lockfile
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try with legacy peer deps
npm install --legacy-peer-deps
```

### Build Fails

**Problem:** `npm run build` fails

**Solution:**
```bash
# Increase Node memory
export NODE_OPTIONS=--max_old_space_size=4096

# Check for syntax errors
npm run lint

# Clean build
rm -rf build/
npm run build

# Check environment variables
cat .env
```

### White Screen / Blank Page

**Problem:** Frontend shows blank page

**Solution:**
```bash
# 1. Check browser console for errors
# 2. Verify backend is running
curl http://localhost:8000/health

# 3. Check API URL in frontend
# frontend/src/api/chat.js
# BASE_URL should point to backend

# 4. Clear browser cache
# 5. Check network tab for failed requests
```

### API Connection Fails

**Problem:** Frontend can't connect to backend

**Solution:**
```bash
# 1. Check CORS configuration
ALLOWED_ORIGINS=http://localhost:3000

# 2. Verify API URL
# In frontend/src/api/chat.js:
const BASE_URL = "http://localhost:8000";

# 3. Test backend directly
curl http://localhost:8000/

# 4. Check browser console for errors
```

## Getting Help

If you can't resolve your issue:

1. **Check Logs:**
   ```bash
   # Backend logs
   docker-compose logs -f backend
   
   # Frontend logs
   docker-compose logs -f frontend
   
   # System logs
   sudo journalctl -u zgpt-backend -f
   ```

2. **Gather Information:**
   - Error messages
   - Log files
   - System specs (OS, RAM, Python version)
   - Configuration (.env file, sanitized)
   - Steps to reproduce

3. **Search Issues:**
   - GitHub Issues: https://github.com/MuhammadZeeshan1481/z-gpt/issues
   - Stack Overflow

4. **Ask for Help:**
   - Open a GitHub Issue with details
   - Join community discussions

## Quick Diagnostic Script

Save as `diagnose.sh`:
```bash
#!/bin/bash
echo "=== Z-GPT Diagnostic ==="
echo "Python version:"
python --version
echo ""
echo "Node version:"
node --version
echo ""
echo "Docker version:"
docker --version
echo ""
echo "Free memory:"
free -h
echo ""
echo "Disk space:"
df -h
echo ""
echo "Backend status:"
curl -s http://localhost:8000/health | jq .
echo ""
echo "Frontend status:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
echo ""
```

Run it:
```bash
chmod +x diagnose.sh
./diagnose.sh
```
