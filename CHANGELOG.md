# Changelog

All notable changes to the Z-GPT project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project improvements including security, code quality, and developer experience
- Centralized configuration management in `backend/config.py`
- Pydantic models for all API endpoints in `backend/models.py`
- Model loader utility for lazy loading in `backend/utils/model_loader.py`
- Test infrastructure with pytest and test files
- CI/CD workflows for backend, frontend, and security audits
- Docker support with `Dockerfile.backend`, `Dockerfile.frontend`, and `docker-compose.yml`
- Pre-commit hooks for code quality
- Centralized frontend API client
- Environment variable support for frontend and backend
- Comprehensive documentation updates

### Changed
- Split Python dependencies into `requirements.txt` (runtime) and `requirements-dev.txt` (dev/test)
- Updated CORS configuration to use environment variables
- Updated all API endpoints to use centralized Pydantic models
- Updated frontend API files to use new centralized client
- Improved README.md with detailed setup instructions and architecture overview

### Security
- Removed committed `.env` file from repository
- Added `.env.example` with placeholder values
- Configured environment-based CORS origins

### Fixed
- Improved error handling in API endpoints
- Better type validation with Pydantic models

## [0.1.0] - Initial Release

### Added
- FastAPI backend with chat, image generation, and translation endpoints
- React frontend with Bootstrap UI
- Hugging Face Transformers integration for chat
- Stable Diffusion integration for image generation
- Argos Translate integration for multilingual support
- Basic project structure and documentation

[Unreleased]: https://github.com/MuhammadZeeshan1481/z-gpt/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/MuhammadZeeshan1481/z-gpt/releases/tag/v0.1.0
