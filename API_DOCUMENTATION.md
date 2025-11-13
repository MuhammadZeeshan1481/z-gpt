# Z-GPT API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. Future versions will implement API key-based authentication.

## Common Response Format

### Success Response
```json
{
  "response": "string",
  "detected_lang": "string",
  "processing_time": 1.23
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## API Endpoints

### Health Check

#### GET `/`
Basic health check endpoint.

**Response (200 OK)**
```json
{
  "status": "healthy",
  "service": "Z-GPT Backend",
  "version": "1.0.0"
}
```

#### GET `/health`
Detailed health check endpoint.

**Response (200 OK)**
```json
{
  "status": "healthy",
  "service": "Z-GPT Backend",
  "version": "1.0.0",
  "timestamp": 1699876543.21
}
```

---

### Chat API

#### POST `/chat/`
Process a chat message with optional conversation history.

**Request Body**
```json
{
  "message": "Hello, how are you?",
  "history": [
    {
      "role": "user",
      "content": "Previous user message"
    },
    {
      "role": "assistant",
      "content": "Previous assistant response"
    }
  ]
}
```

**Request Parameters**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User message (1-1000 chars) |
| history | array | No | Conversation history (max 10 items) |

**Response (200 OK)**
```json
{
  "response": "I'm doing well, thank you for asking!",
  "detected_lang": "en",
  "processing_time": 2.45
}
```

**Error Responses**
- `400 Bad Request`: Invalid input (empty message, too long, etc.)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing failed

**Example cURL Request**
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of Pakistan?",
    "history": []
  }'
```

**Example Response**
```json
{
  "response": "The capital of Pakistan is Islamabad.",
  "detected_lang": "en",
  "processing_time": 1.87
}
```

**Language Support**
The chat endpoint automatically detects the input language and responds in the same language. Supported languages include:
- English (en)
- Urdu (ur)
- Spanish (es)
- French (fr)
- And many more via the language detection model

---

### Image Generation API

#### POST `/image/generate`
Generate an image from a text prompt.

**Request Body**
```json
{
  "prompt": "A crescent moon over a desert night in Pakistan"
}
```

**Request Parameters**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | Text description (3-500 chars) |

**Response (200 OK)**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "A crescent moon over a desert night in Pakistan",
  "processing_time": 45.2
}
```

**Response Fields**
| Field | Type | Description |
|-------|------|-------------|
| image_base64 | string | Base64-encoded PNG image |
| prompt | string | Original prompt used |
| processing_time | float | Time taken in seconds |

**Error Responses**
- `400 Bad Request`: Invalid prompt (too short, contains prohibited content)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Image generation failed

**Example cURL Request**
```bash
curl -X POST "http://localhost:8000/image/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains"
  }'
```

**Example Usage with Image Display**
```javascript
const response = await axios.post('/image/generate', {
  prompt: 'A beautiful sunset'
});
const imageUrl = `data:image/png;base64,${response.data.image_base64}`;
// Use imageUrl in <img> tag
```

**Content Filtering**
The API performs basic content filtering on prompts. Prohibited keywords include:
- nsfw, nude, explicit (This list can be expanded)

---

### Translation API

#### POST `/translate/`
Translate text between languages.

**Request Body**
```json
{
  "text": "Hello, how are you?",
  "from": "en",
  "to": "ur"
}
```

**Request Parameters**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Text to translate (1-1000 chars) |
| from | string | Yes | Source language code (e.g., "en") |
| to | string | Yes | Target language code (e.g., "ur") |

**Response (200 OK)**
```json
{
  "translated_text": "ہیلو، آپ کیسے ہیں؟",
  "from_lang": "en",
  "to_lang": "ur",
  "processing_time": 0.34
}
```

**Error Responses**
- `400 Bad Request`: Invalid input or unsupported language pair
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Translation failed

**Supported Language Codes**
- `en`: English
- `ur`: Urdu
- `es`: Spanish
- `fr`: French
- `ar`: Arabic
- And more (depends on installed Argos Translate packages)

**Example cURL Request**
```bash
curl -X POST "http://localhost:8000/translate/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Pakistan is beautiful",
    "from": "en",
    "to": "ur"
  }'
```

#### POST `/translate/translate` (Legacy)
Legacy endpoint for backward compatibility. Same functionality as `/translate/`.

---

## Rate Limiting

Current rate limit: 60 requests per minute (configurable via environment variable)

**Rate Limit Headers**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699876543
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Processing failed |
| 503 | Service Unavailable - Server overloaded |

---

## Response Headers

All responses include these headers:
- `X-Process-Time`: Processing time in seconds
- `Content-Type`: application/json
- `Access-Control-Allow-Origin`: CORS origin (if allowed)

---

## SDK Examples

### JavaScript/TypeScript
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Chat
async function chat(message, history = []) {
  const response = await axios.post(`${API_BASE_URL}/chat/`, {
    message,
    history
  });
  return response.data;
}

// Image Generation
async function generateImage(prompt) {
  const response = await axios.post(`${API_BASE_URL}/image/generate`, {
    prompt
  });
  return response.data.image_base64;
}

// Translation
async function translate(text, from, to) {
  const response = await axios.post(`${API_BASE_URL}/translate/`, {
    text,
    from,
    to
  });
  return response.data.translated_text;
}
```

### Python
```python
import requests

API_BASE_URL = 'http://localhost:8000'

# Chat
def chat(message, history=None):
    response = requests.post(
        f'{API_BASE_URL}/chat/',
        json={'message': message, 'history': history or []}
    )
    return response.json()

# Image Generation
def generate_image(prompt):
    response = requests.post(
        f'{API_BASE_URL}/image/generate',
        json={'prompt': prompt}
    )
    return response.json()['image_base64']

# Translation
def translate(text, from_lang, to_lang):
    response = requests.post(
        f'{API_BASE_URL}/translate/',
        json={'text': text, 'from': from_lang, 'to': to_lang}
    )
    return response.json()['translated_text']
```

### cURL
```bash
# Chat
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Image Generation
curl -X POST "http://localhost:8000/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Beautiful landscape"}'

# Translation
curl -X POST "http://localhost:8000/translate/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "from": "en", "to": "ur"}'
```

---

## Interactive API Documentation

When running in debug mode, you can access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Websocket Support (Future)

Future versions will include WebSocket support for streaming responses:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.send(JSON.stringify({message: "Hello"}));
ws.onmessage = (event) => {
  console.log('Received:', event.data);
};
```

---

## Best Practices

1. **Error Handling**: Always implement proper error handling for API calls
2. **Rate Limiting**: Respect rate limits and implement exponential backoff
3. **Timeouts**: Set appropriate timeouts (chat: 60s, image: 120s)
4. **Validation**: Validate input on client-side before sending to API
5. **Caching**: Cache responses when appropriate to reduce load
6. **Security**: Never expose API keys or tokens in client-side code

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/MuhammadZeeshan1481/z-gpt/issues
- Email: [Contact information]

---

## Changelog

### Version 1.0.0
- Initial API release
- Chat, Image Generation, and Translation endpoints
- Language detection
- Basic content filtering
- Health check endpoints
