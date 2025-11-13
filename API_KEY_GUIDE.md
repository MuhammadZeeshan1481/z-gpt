# API Key Authentication Guide

Z-GPT now supports API key authentication with tiered rate limiting to provide better security and control over API usage.

## Overview

The API key system provides:
- **Authentication**: Secure access to API endpoints
- **Rate Limiting**: Tiered limits based on usage tier
- **Usage Tracking**: Monitor API usage per key
- **Admin Controls**: Manage keys and view statistics

## Configuration

### Enable/Disable API Key Requirement

In your `.env` file:

```bash
# Require API key for all requests (default: False)
REQUIRE_API_KEY=False

# Your admin API key (gets enterprise tier access)
API_KEY=your-secret-admin-key-here
```

- **REQUIRE_API_KEY=False**: API keys are optional. Requests without keys use free tier rate limits.
- **REQUIRE_API_KEY=True**: All requests must include a valid API key.

## Rate Limiting Tiers

| Tier | Requests/Minute | Description |
|------|----------------|-------------|
| **Free** | 10 | Default tier, suitable for testing |
| **Pro** | 60 | For regular usage |
| **Enterprise** | 300 | High-volume usage + admin access |

## Built-in API Keys

For development and testing, Z-GPT includes these pre-configured keys:

```
dev-test-key-12345  - Development (Free tier)
demo-key-67890      - Demo User (Pro tier)
[Your API_KEY]      - Admin (Enterprise tier)
```

## Using API Keys

### In API Requests

Include the API key in the `X-API-Key` header:

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-test-key-12345" \
  -d '{"message": "Hello!"}'
```

**Python Example:**
```python
import requests

headers = {
    "Content-Type": "application/json",
    "X-API-Key": "dev-test-key-12345"
}

response = requests.post(
    "http://localhost:8000/chat/",
    headers=headers,
    json={"message": "Hello!"}
)
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'dev-test-key-12345'
  },
  body: JSON.stringify({message: 'Hello!'})
});
```

### Rate Limit Response Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 60          # Total requests allowed per minute
X-RateLimit-Remaining: 45      # Requests remaining in current window
X-RateLimit-Reset: 60          # Seconds until rate limit resets
```

### When Rate Limit is Exceeded

```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 10,
    "tier": "free",
    "reset_in_seconds": 60,
    "message": "You have exceeded the rate limit of 10 requests per minute for the free tier."
  }
}
```

**HTTP Status Code:** 429 (Too Many Requests)

## Admin Endpoints

Enterprise tier keys can access admin endpoints:

### List All API Keys

```bash
GET /admin/keys
Header: X-API-Key: your-enterprise-key

Response:
{
  "api_keys": {
    "dev-test-k...": {"name": "Development", "tier": "free"},
    "demo-key-6...": {"name": "Demo User", "tier": "pro"}
  }
}
```

### View Usage Statistics

```bash
GET /admin/stats
Header: X-API-Key: your-enterprise-key

Response:
{
  "rate_limit_stats": {
    "dev-test-k...": {
      "requests_last_minute": 5,
      "last_request": "2024-11-13T10:30:45"
    }
  },
  "timestamp": 1699876245.123
}
```

## Managing API Keys (Programmatic)

For production environments, integrate with the API key management system:

```python
from backend.middleware.auth import add_api_key, list_api_keys

# Add a new API key
add_api_key(
    api_key="new-user-key-xyz",
    name="New User",
    tier="pro"
)

# List all keys
keys = list_api_keys()
print(keys)
```

## Production Recommendations

### 1. Require API Keys

Always enable API key requirement in production:

```bash
REQUIRE_API_KEY=True
```

### 2. Use Strong Admin Keys

Generate a strong admin API key:

```bash
# Generate secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set it in your `.env`:

```bash
API_KEY=your-generated-secure-key-here
```

### 3. Database-Backed Keys

For production, replace the in-memory key store with a database:

1. Create a `api_keys` table in PostgreSQL
2. Update `backend/middleware/auth.py` to query the database
3. Implement key creation/revocation endpoints

### 4. Key Rotation

Regularly rotate API keys:
- Generate new keys
- Notify users
- Deprecate old keys after grace period
- Remove old keys

### 5. Monitoring

Monitor API usage:
- Track requests per key
- Alert on unusual patterns
- Log authentication failures
- Monitor rate limit hits

## Frontend Integration

Update your frontend to include API keys:

```javascript
// frontend/src/api/chat.js
const API_KEY = process.env.REACT_APP_API_KEY || 'dev-test-key-12345';

export const sendMessage = async (message, history = []) => {
  const response = await axios.post(
    `${BASE_URL}/chat/`,
    { message, history },
    {
      headers: {
        'X-API-Key': API_KEY
      }
    }
  );
  return response.data;
};
```

Add to `.env` in frontend:
```bash
REACT_APP_API_KEY=dev-test-key-12345
```

## Error Handling

### Missing API Key (when required)

```json
{
  "detail": "API key is required. Include X-API-Key header in your request."
}
```

**HTTP Status Code:** 401 (Unauthorized)

### Invalid API Key

```json
{
  "detail": "Invalid API key"
}
```

**HTTP Status Code:** 401 (Unauthorized)

### Insufficient Permissions

```json
{
  "detail": "Only enterprise tier can access this endpoint"
}
```

**HTTP Status Code:** 403 (Forbidden)

## Testing

### Test Without API Key (if REQUIRE_API_KEY=False)

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Test With API Key

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-test-key-12345" \
  -d '{"message": "Hello!"}'
```

### Test Rate Limiting

Run multiple requests rapidly to hit the rate limit:

```bash
for i in {1..15}; do
  curl -X POST "http://localhost:8000/chat/" \
    -H "X-API-Key: dev-test-key-12345" \
    -H "Content-Type: application/json" \
    -d '{"message": "Test '$i'"}'
  echo ""
done
```

## Troubleshooting

### "API key is required" Error

1. Check `REQUIRE_API_KEY` setting in `.env`
2. Ensure `X-API-Key` header is included in request
3. Verify header name is exactly `X-API-Key` (case-sensitive)

### "Invalid API key" Error

1. Check the API key value
2. Verify it matches one of the configured keys
3. Check for extra spaces or characters

### Rate Limit Exceeded

1. Wait for the rate limit window to reset (60 seconds)
2. Upgrade to a higher tier if needed
3. Implement request queuing in your application

### Admin Endpoints Return 403

1. Verify you're using an enterprise tier key
2. Check the key is configured correctly
3. Ensure `API_KEY` is set in `.env`

## Security Best Practices

1. **Never expose API keys in client-side code** (except for development)
2. **Use environment variables** for API key configuration
3. **Implement HTTPS** for production deployments
4. **Rotate keys regularly** (every 90 days minimum)
5. **Monitor for unauthorized access** attempts
6. **Implement key expiration** for temporary access
7. **Use separate keys per application/user**
8. **Log all API key usage** for audit trails

## Next Steps

1. **Enable API key requirement** for production
2. **Generate secure admin key** and configure in `.env`
3. **Update frontend** to include API keys in requests
4. **Set up monitoring** for API usage
5. **Implement database-backed keys** for scalability
6. **Add key management UI** for easy administration

## Support

For issues or questions about API key authentication:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [SECURITY.md](SECURITY.md) for security considerations
- Open an issue on GitHub
