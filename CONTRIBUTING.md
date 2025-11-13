# Contributing to Z-GPT

Thank you for your interest in contributing to Z-GPT! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/z-gpt.git
   cd z-gpt
   ```
3. **Set up the development environment** (see README.md)
4. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow existing code style and conventions
- Add comments where necessary
- Update documentation if needed

### 2. Test Your Changes

Run the test suite to ensure nothing is broken:

```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### 3. Format and Lint

Ensure code quality:

```bash
# Format with Black
black backend/ tests/

# Lint with Ruff
ruff check backend/ tests/ --fix

# Format frontend code
cd frontend
npm run format  # if configured
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add new translation feature"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference any related issues
- Screenshots for UI changes
- List of changes made

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

Example:
```python
from typing import List, Optional

def process_message(message: str, history: List[dict]) -> str:
    """
    Process a chat message.
    
    Args:
        message: User message
        history: Conversation history
        
    Returns:
        Processed response
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Use clear, descriptive variable names
- Add JSDoc comments for functions
- Follow existing component structure

Example:
```javascript
/**
 * Send a chat message to the backend
 * @param {string} message - User message
 * @param {Array} history - Chat history
 * @returns {Promise} API response
 */
export const sendMessage = async (message, history = []) => {
  // Implementation here
};
```

## Testing Guidelines

### Backend Tests

- Write tests for all new features
- Test both success and error cases
- Use pytest fixtures for common setup
- Mock external dependencies (models, APIs)

Example:
```python
def test_chat_endpoint(client, sample_chat_request):
    """Test chat endpoint returns valid response."""
    response = client.post("/chat/", json=sample_chat_request)
    assert response.status_code == 200
    assert "response" in response.json()
```

### Frontend Tests

- Test component rendering
- Test user interactions
- Test API integration
- Use React Testing Library

Example:
```javascript
test('renders chat input', () => {
  render(<ChatComponent />);
  const inputElement = screen.getByPlaceholderText(/type a message/i);
  expect(inputElement).toBeInTheDocument();
});
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation if endpoints change
- Include examples in documentation

## Pull Request Process

1. **Ensure all tests pass** in CI/CD
2. **Get code review** from maintainers
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Wait for approval** before merging

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No sensitive data (API keys, tokens) committed
- [ ] CI/CD checks passing
- [ ] Branch is up to date with main

## Reporting Bugs

When reporting bugs, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node version)
- Error messages or logs
- Screenshots if applicable

## Feature Requests

For feature requests:
- Describe the feature clearly
- Explain the use case
- Consider implementation approach
- Discuss potential impact

## Questions?

- Open an issue for questions
- Tag with `question` label
- Check existing issues first
- Be specific and provide context

## Recognition

Contributors will be:
- Listed in project acknowledgments
- Mentioned in release notes
- Appreciated and thanked!

Thank you for contributing to Z-GPT! 🚀
