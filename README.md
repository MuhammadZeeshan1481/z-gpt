# Z-GPT: AI Assistant with Chat, Image Generation, and Translation

Z-GPT is a full-stack AI assistant built using FastAPI for the backend and React for the frontend. It supports natural language conversations, image generation from prompts, and multilingual translation with automatic language detection.

## Features

- 🤖 Chatbot using Hugging Face Transformers
- 🎨 Prompt-based image generation using Stable Diffusion
- 🌐 Language detection and translation using Argos Translate
- 💬 Multilingual input/output with seamless translation handling
- 🎯 Clean React-based UI with Bootstrap styling
- 🔒 Environment-based configuration for security
- 🐳 Docker support for easy deployment

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18.x or higher
- Git

### Clone the Repository

```bash
git clone https://github.com/MuhammadZeeshan1481/z-gpt.git
cd z-gpt
```

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your configuration (especially the Hugging Face token if needed):
```bash
HUGGINGFACEHUB_API_TOKEN=your_token_here
```

### Backend Setup (FastAPI)

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn backend.main:app --reload
```

The backend API will be available at `http://localhost:8000`.
API documentation: `http://localhost:8000/docs`

### Frontend Setup (React)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Copy the frontend environment file:
```bash
cp .env.example .env
```

3. Install npm dependencies:
```bash
npm install
```

4. Start the development server:
```bash
npm start
```

The frontend will be served at `http://localhost:3000` and will interact with the backend at `http://localhost:8000`.

## Docker Deployment (Recommended)

The easiest way to run Z-GPT is using Docker Compose:

1. Ensure Docker and Docker Compose are installed
2. Copy `.env.example` to `.env` and configure your environment variables
3. Run:
```bash
docker-compose up --build
```

This will start both backend (port 8000) and frontend (port 3000) services.

## Architecture Overview

```
z-gpt/
├── backend/              # FastAPI backend
│   ├── api/             # API route handlers
│   │   ├── chat.py      # Chat endpoint
│   │   ├── image.py     # Image generation endpoint
│   │   └── translate.py # Translation endpoint
│   ├── config/          # Legacy configuration
│   ├── core/            # Core business logic
│   ├── utils/           # Utility functions
│   ├── config.py        # Centralized settings
│   └── models.py        # Pydantic models
├── frontend/            # React frontend
│   └── src/
│       ├── api/         # API client
│       ├── components/  # React components
│       └── pages/       # Page components
├── tests/               # Backend tests
└── .github/workflows/   # CI/CD pipelines
```

## Environment Variables

### Backend Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACEHUB_API_TOKEN` | Hugging Face API token | - |
| `MODEL_NAME` | LLM model name | `mistralai/Mistral-7B-Instruct-v0.1` |
| `MODEL_DEVICE` | Device to run models on | `cpu` |
| `TRANSLATION_MODEL` | Translation engine | `argos_translate` |
| `DEBUG` | Enable debug mode | `False` |
| `USE_LOCAL_MODELS` | Use locally cached models | `True` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

### Frontend Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Backend API URL | `http://localhost:8000` |

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

#### POST `/chat/`
- **Description**: Send a chat message and get an AI response
- **Request Body**:
  ```json
  {
    "message": "Hello, how are you?",
    "history": []
  }
  ```
- **Response**:
  ```json
  {
    "response": "I'm doing well, thank you!",
    "detected_lang": "en"
  }
  ```

#### POST `/image/generate`
- **Description**: Generate an image from a text prompt
- **Request Body**:
  ```json
  {
    "prompt": "A sunset over mountains",
    "guidance_scale": 8.5
  }
  ```
- **Response**:
  ```json
  {
    "image_base64": "base64_encoded_image_data..."
  }
  ```

#### POST `/translate/translate`
- **Description**: Translate text between languages
- **Request Body**:
  ```json
  {
    "text": "Hello world",
    "from": "en",
    "to": "ur"
  }
  ```
- **Response**:
  ```json
  {
    "translated_text": "ہیلو دنیا",
    "source_language": "en",
    "target_language": "ur"
  }
  ```

## Development

### Running Tests

Backend tests:
```bash
pytest tests/ -v
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Quality

Format code with Black:
```bash
black backend/ tests/
```

Lint with Ruff:
```bash
ruff check backend/ tests/
```

Setup pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Requirements

### Backend Dependencies

Runtime dependencies are in `requirements.txt`. Development dependencies are in `requirements-dev.txt`.

Major libraries:
- **FastAPI** - Modern web framework
- **Transformers** - Hugging Face transformers
- **PyTorch** - Deep learning framework
- **Diffusers** - Image generation
- **Argos Translate** - Translation engine

### Frontend Dependencies

See `frontend/package.json` for details. Key libraries:
- **React** - UI framework
- **Axios** - HTTP client
- **Bootstrap** - CSS framework
- **React Router** - Routing

## Sample Prompts

- "Who was the first prime minister of Pakistan?"
- "Generate an image of a crescent moon over a desert night in Pakistan"
- "پاکستان کا پہلا وزیراعظم کون تھا؟"
- "Tell me in French why Paris is famous"

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hugging Face for transformer models
- Stability AI for Stable Diffusion
- Argos Translate team for translation models
