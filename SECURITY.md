# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Z-GPT, please report it responsibly:

1. **DO NOT** open a public issue
2. Send an email to the maintainers with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to resolve the issue.

## Security Best Practices

### For Developers

#### Environment Variables
- **NEVER** commit `.env` files to version control
- Always use `.env.example` as a template
- Rotate API keys and secrets regularly
- Use strong, unique secrets in production

#### API Security
- Implement API authentication (JWT, OAuth2)
- Use rate limiting to prevent abuse
- Validate and sanitize all user inputs
- Implement request size limits
- Use HTTPS in production

#### Model Security
- Keep Hugging Face tokens secure
- Implement content filtering for prompts
- Monitor model usage for abuse
- Set resource limits for model inference

#### CORS Configuration
```python
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### For Deployment

#### Docker Security
```bash
# Don't run containers as root
USER nonroot

# Limit resources
docker run --memory="2g" --cpus="2" zgpt-backend

# Use secrets management
docker secret create hf_token hf_token.txt
```

#### Environment Security
```bash
# Use strong secret keys
SECRET_KEY=$(openssl rand -hex 32)

# Restrict CORS origins
ALLOWED_ORIGINS=https://yourdomain.com

# Enable rate limiting
RATE_LIMIT_PER_MINUTE=30

# Use HTTPS only
HTTPS_ONLY=true
```

#### Network Security
- Use reverse proxy (Nginx, Traefik)
- Enable HTTPS with valid SSL certificates
- Configure firewall rules
- Use private networks for backend services
- Implement DDoS protection

### Input Validation

#### Current Implementation
- Maximum message length: 1000 characters
- Maximum history length: 10 messages
- Maximum prompt length: 500 characters
- Content filtering for prohibited keywords

#### Additional Recommendations
- Implement more sophisticated content filtering
- Add SQL injection prevention
- Sanitize HTML/JavaScript in inputs
- Validate file uploads (future feature)
- Implement CSRF protection

### Data Privacy

#### Current State
- No user data persistence
- No conversation logging (except temporary logs)
- No user tracking

#### Recommendations for Future
- Implement GDPR compliance if storing user data
- Add data retention policies
- Provide data export functionality
- Implement data deletion on request
- Add privacy policy

### Model Security

#### Content Filtering
Current implementation includes basic keyword filtering:
```python
prohibited_keywords = ['nsfw', 'nude', 'explicit']
```

#### Recommendations
- Implement ML-based content filtering
- Add profanity detection
- Monitor for prompt injection attacks
- Implement output filtering
- Add abuse detection and reporting

### Dependency Security

#### Current Practices
- Regular dependency updates
- Security scanning in CI/CD pipeline
- Using official package sources

#### Recommendations
```bash
# Check for vulnerabilities
pip install safety
safety check

# Audit npm packages
npm audit

# Update dependencies regularly
pip install --upgrade -r requirements.txt
npm update
```

### Logging Security

#### Best Practices
- Don't log sensitive data (tokens, passwords)
- Implement log rotation
- Secure log storage
- Monitor logs for suspicious activity
- Use structured logging

#### Current Implementation
```python
# Good - Logs without sensitive data
logger.info(f"Processing chat message: {request.message[:50]}...")

# Bad - Don't do this
# logger.info(f"API token: {HUGGINGFACEHUB_API_TOKEN}")
```

### Database Security (Future)

When implementing database:
- Use parameterized queries
- Implement proper access control
- Encrypt sensitive data at rest
- Use connection pooling
- Regular backups with encryption
- Implement audit logging

### API Authentication (Recommended)

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    # Verify token (JWT, API key, etc.)
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return token

@app.post("/chat/", dependencies=[Depends(verify_token)])
async def chat(request: ChatRequest):
    # Protected endpoint
    pass
```

### Rate Limiting Implementation

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat/")
@limiter.limit("5/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # Rate-limited endpoint
    pass
```

### Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Force HTTPS in production
if not DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Monitoring and Alerts

#### Recommendations
- Monitor for unusual API usage patterns
- Alert on repeated failures
- Track error rates
- Monitor resource usage
- Implement intrusion detection

#### Example Monitoring
```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

## Security Checklist for Production

- [ ] Change all default secrets and API keys
- [ ] Configure CORS with specific allowed origins
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Implement API authentication
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure firewall rules
- [ ] Implement backup strategy
- [ ] Set up log rotation and retention
- [ ] Enable security headers
- [ ] Run security scans (OWASP ZAP, etc.)
- [ ] Review and update dependencies
- [ ] Document security procedures
- [ ] Train team on security practices
- [ ] Set up incident response plan

## Known Security Limitations

1. **No Authentication**: API is currently open to anyone
2. **Basic Content Filtering**: Simple keyword-based filtering
3. **No Rate Limiting**: Can be abused with excessive requests
4. **Model Access**: Unrestricted access to AI models
5. **No Encryption**: Data not encrypted in transit (development)

## Planned Security Enhancements

1. JWT-based authentication
2. Advanced content filtering with ML
3. Request rate limiting per user/IP
4. API key management
5. Audit logging
6. Security scanning automation
7. Penetration testing
8. Bug bounty program

## Compliance

Currently, Z-GPT does not store user data, so GDPR and other data protection regulations don't apply. If you plan to store user data:

- Review GDPR requirements
- Implement data protection measures
- Add privacy policy
- Implement consent mechanisms
- Enable data export/deletion

## Contact

For security concerns, contact: [Your Security Contact]

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Python Security Best Practices](https://snyk.io/blog/python-security-best-practices-cheat-sheet/)
