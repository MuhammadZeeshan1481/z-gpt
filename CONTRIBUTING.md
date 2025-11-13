# Contributing to Z-GPT

Thank you for your interest in contributing to Z-GPT! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/z-gpt.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Add your meaningful commit message"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and add your API tokens

# Run the backend
uvicorn backend.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Maximum line length: 100 characters

### JavaScript/React
- Use ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Use functional components with hooks
- Add PropTypes or TypeScript for type checking

## Testing

### Backend Tests
```bash
pytest backend/tests
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow the existing code style
- Write clear commit messages
- Reference related issues in PR description

## Reporting Issues

When reporting issues, please include:
- A clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information (OS, Python version, Node version)
- Error messages or logs

## Code Review Process

1. All PRs require at least one approval
2. Address all review comments
3. Keep the PR updated with the main branch
4. Squash commits before merging if requested

## Questions?

Feel free to open an issue for any questions or discussions.
