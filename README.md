# Z-GPT: AI Assistant with Chat, Image Generation, and Translation

[![CI/CD](https://github.com/MuhammadZeeshan1481/z-gpt/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/MuhammadZeeshan1481/z-gpt/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Z-GPT is a full-stack AI assistant built using FastAPI for the backend and React for the frontend. It supports natural language conversations, image generation from prompts, and multilingual translation with automatic language detection.

## ✨ Features

- 💬 **Smart Chatbot** - Powered by Mistral-7B-Instruct with conversation context
- 🎨 **Image Generation** - Create images from text using Stable Diffusion v1.5
- 🌍 **Multi-language Support** - Automatic language detection and translation
- 🔒 **Secure** - Input validation, error handling, and CORS protection
- 🐳 **Docker Ready** - Easy deployment with Docker and Docker Compose
- 📚 **Well Documented** - Comprehensive API and architecture documentation
- ⚡ **Production Ready** - Logging, monitoring, and health checks included

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Usage](#api-usage)
- [Development](#development)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/MuhammadZeeshan1481/z-gpt.git
cd z-gpt

# Configure environment
cp .env.example .env
# Edit .env and add your Hugging Face API token

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- 8GB+ RAM (for AI models)
- Hugging Face API token (for image generation)

### Backend Setup

1. **Clone and navigate**
```bash
git clone https://github.com/MuhammadZeeshan1481/z-gpt.git
cd z-gpt
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your configuration
```

5. **Run the backend**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend**
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

## ⚙️ Configuration

Create a `.env` file based on `.env.example`:

```bash
# Required
HUGGINGFACEHUB_API_TOKEN=your_token_here

# Optional - Model Settings
MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
USE_LOCAL_MODELS=False

# Optional - Server Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000

# Optional - Security
RATE_LIMIT_PER_MINUTE=60
SECRET_KEY=your-secret-key
```

See `.env.example` for all available options.

## 🔌 API Usage

### Chat Endpoint

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of Pakistan?",
    "history": []
  }'
```

### Image Generation

```bash
curl -X POST "http://localhost:8000/image/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains"
  }'
```

### Translation

```bash
curl -X POST "http://localhost:8000/translate/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "from": "en",
    "to": "ur"
  }'
```

For complete API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 💻 Development

### Running Tests

```bash
# Backend tests (when available)
pytest backend/tests

# Frontend tests
cd frontend && npm test
```

### Code Quality

```bash
# Python linting
flake8 backend
black backend

# Type checking
mypy backend

# Frontend linting
cd frontend && npm run lint
```

### Project Structure

```
z-gpt/
├── backend/           # FastAPI backend
│   ├── api/          # API endpoints
│   ├── core/         # Core services (LLM, etc.)
│   ├── config/       # Configuration
│   └── utils/        # Utility functions
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── api/         # API client
│   └── public/
├── .github/          # CI/CD workflows
├── models/           # Model cache (created at runtime)
└── docs/            # Documentation
```

## 🚢 Deployment

### Docker Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

Quick start:
```bash
docker-compose up -d
```

### Cloud Platforms

- **AWS**: ECS, Lambda, or EC2
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **Kubernetes**: See deployment manifests in docs

For detailed cloud deployment guides, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Architecture](ARCHITECTURE.md) - System design and architecture
- [Deployment Guide](DEPLOYMENT.md) - Deployment instructions
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [Security](SECURITY.md) - Security best practices

## 🎯 Sample Prompts

**Chat:**
- "Who was the first prime minister of Pakistan?"
- "Explain quantum computing in simple terms"
- "پاکستان کا پہلا وزیراعظم کون تھا؟" (Urdu)
- "Parlez-moi de Paris" (French)

**Image Generation:**
- "Generate an image of a crescent moon over a desert night"
- "A cyberpunk city at night with neon lights"
- "Abstract art with vibrant colors"

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- Transformers - Hugging Face transformers
- Diffusers - Stable Diffusion models
- Argos Translate - Translation engine
- PyTorch - Deep learning framework

**Frontend:**
- React 19 - UI framework
- React Router - Client-side routing
- Axios - HTTP client
- Bootstrap 5 - UI components

**DevOps:**
- Docker & Docker Compose
- GitHub Actions - CI/CD
- Nginx - Reverse proxy

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🔒 Security

For security concerns, please see [SECURITY.md](SECURITY.md) and report vulnerabilities responsibly.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Hugging Face for amazing ML models
- FastAPI for the excellent web framework
- React team for the frontend framework
- All contributors and supporters

## 📧 Contact

- GitHub Issues: [Report bugs or request features](https://github.com/MuhammadZeeshan1481/z-gpt/issues)
- GitHub Discussions: [Ask questions or share ideas](https://github.com/MuhammadZeeshan1481/z-gpt/discussions)

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!
