# Z-GPT Architecture

## Overview

Z-GPT is a full-stack AI assistant application that provides chat, image generation, and translation capabilities. The system is built with a FastAPI backend and React frontend, following modern web development practices.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐              │
│  │   Chat   │  │  Image   │  │ Translation  │              │
│  │   Page   │  │   Page   │  │   (Future)   │              │
│  └──────────┘  └──────────┘  └──────────────┘              │
│         │            │                │                      │
│         └────────────┴────────────────┘                      │
│                      │                                       │
│              ┌───────▼───────┐                               │
│              │  API Service  │                               │
│              └───────────────┘                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  API Layer                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────┐          │ │
│  │  │   Chat   │  │  Image   │  │ Translation│          │ │
│  │  │ Endpoint │  │ Endpoint │  │  Endpoint  │          │ │
│  │  └──────────┘  └──────────┘  └────────────┘          │ │
│  └─────────┬─────────────┬──────────────┬─────────────────┘ │
│            │             │              │                    │
│  ┌─────────▼─────────────▼──────────────▼─────────────────┐ │
│  │                 Core Services                           │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │ │
│  │  │    LLM     │  │   Image    │  │   Translation  │   │ │
│  │  │  Handler   │  │ Generator  │  │     Tools      │   │ │
│  │  └────────────┘  └────────────┘  └────────────────┘   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Configuration                           │ │
│  │  • Environment Variables  • Model Settings               │ │
│  │  • CORS Configuration     • Rate Limiting                │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼────┐              ┌───────▼────────┐
    │ Hugging │              │    Argos       │
    │  Face   │              │  Translate     │
    │ Models  │              │   Models       │
    └─────────┘              └────────────────┘
```

## Component Details

### Frontend Layer

#### Technologies
- **React 19**: Modern UI framework with hooks
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Bootstrap 5**: UI component library
- **Tailwind CSS**: Utility-first CSS framework

#### Components
- **ChatBox**: Main chat interface with message history
- **ImageGenerator**: Image generation interface
- **API Services**: Axios-based API client services

### Backend Layer

#### Technologies
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization
- **Transformers**: Hugging Face transformers library
- **Diffusers**: Image generation models
- **Argos Translate**: Translation engine

#### API Endpoints

##### Chat API (`/chat`)
- Accepts user messages with optional conversation history
- Detects input language automatically
- Translates to English for LLM processing
- Generates response using Mistral-7B model
- Translates response back to detected language

##### Image API (`/image`)
- Generates images from text prompts
- Uses Stable Diffusion v1.5
- Returns base64-encoded PNG images
- Includes basic content filtering

##### Translation API (`/translate`)
- Direct translation between language pairs
- Supports multiple languages via Argos Translate
- Provides both legacy and modern endpoints

#### Core Services

##### LLM Handler
- Lazy loads Mistral-7B-Instruct model
- Manages conversation context (last 4 turns)
- Handles token generation and response formatting
- Implements error recovery

##### Image Generator
- Lazy loads Stable Diffusion pipeline
- Configurable inference parameters
- Memory-efficient CPU/GPU handling
- Base64 encoding for web delivery

##### Language Tools
- Language detection using XLM-RoBERTa
- Multi-language translation support
- Automatic package installation
- Fallback handling for unsupported languages

## Data Flow

### Chat Request Flow
1. User sends message through frontend
2. Frontend sends POST to `/chat/`
3. Backend detects message language
4. Backend translates to English if needed
5. LLM generates response in English
6. Backend translates response to detected language
7. Response returned to frontend
8. Frontend displays message in chat

### Image Generation Flow
1. User enters prompt in frontend
2. Frontend sends POST to `/image/generate`
3. Backend validates and filters prompt
4. Stable Diffusion generates image
5. Image converted to base64 PNG
6. Base64 image returned to frontend
7. Frontend displays image in chat

## Security Considerations

### Implemented
- CORS restrictions to allowed origins
- Input validation and sanitization
- Request size limits
- Content filtering for image prompts
- Error message sanitization
- Environment-based configuration

### Recommended Additional Security
- API authentication (JWT tokens)
- Rate limiting per user/IP
- Request throttling
- API key rotation
- Input/output content moderation
- DDoS protection
- HTTPS enforcement

## Performance Optimization

### Current
- Lazy loading of ML models
- Singleton pattern for model instances
- Request timing middleware
- Efficient base64 encoding

### Future Improvements
- Response caching (Redis)
- Model quantization
- Batch processing for multiple requests
- CDN for frontend assets
- Database for conversation persistence
- Async task queue for long-running operations

## Scalability Considerations

### Horizontal Scaling
- Stateless API design allows multiple backend instances
- Load balancer distribution
- Shared model cache (NFS or object storage)
- Message queue for asynchronous tasks

### Vertical Scaling
- GPU acceleration for models
- Increased memory for larger models
- CPU optimization for translation

## Monitoring and Observability

### Logging
- Structured logging with log levels
- Request/response logging
- Error tracking with stack traces
- Performance metrics (response time)

### Recommended Additions
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Metrics collection (Prometheus)
- Distributed tracing
- Health check endpoints

## Deployment Options

### Docker
- Multi-stage builds for optimization
- Separate containers for backend and frontend
- Docker Compose for local development
- Volume mounting for model caching

### Cloud Deployment
- **AWS**: ECS, Lambda, S3
- **GCP**: Cloud Run, Cloud Functions, GCS
- **Azure**: Container Instances, Functions, Blob Storage
- **Kubernetes**: Deployment manifests with auto-scaling

## Configuration Management

### Environment Variables
- API tokens and secrets
- Model configuration
- Server settings
- Feature flags
- Resource limits

### Configuration Files
- `.env` for local development
- `.env.example` for documentation
- Docker environment files
- Kubernetes ConfigMaps and Secrets

## Testing Strategy

### Unit Tests
- API endpoint tests
- Model handler tests
- Utility function tests
- Validation tests

### Integration Tests
- End-to-end API tests
- Translation pipeline tests
- Image generation tests
- Error handling tests

### Performance Tests
- Load testing
- Stress testing
- Response time benchmarks
- Memory usage profiling

## Future Enhancements

### Features
- User authentication and authorization
- Conversation persistence
- Multi-user chat rooms
- Voice input/output
- File upload support
- Model selection options
- Conversation export/import

### Technical
- WebSocket support for streaming
- GraphQL API option
- Microservices architecture
- Event-driven architecture
- Caching layer
- Queue system for background tasks
- Database integration (PostgreSQL/MongoDB)

## Dependencies and Licenses

### Major Dependencies
- FastAPI: MIT License
- React: MIT License
- Transformers: Apache 2.0
- Diffusers: Apache 2.0
- Argos Translate: MIT License

### Model Licenses
- Mistral-7B: Apache 2.0
- Stable Diffusion: CreativeML Open RAIL-M License
- XLM-RoBERTa: MIT License

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to the project.

## License

This project is licensed under the MIT License. See LICENSE file for details.
