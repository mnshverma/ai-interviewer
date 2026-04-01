# API Conventions — AI Interviewer

## Kilo AI Gateway API

### Base Configuration
- **Base URL**: `https://api.kilo.ai/api/gateway`
- **Chat Endpoint**: `/chat/completions`
- **Models Endpoint**: `/models`
- **Auth**: `Authorization: Bearer {API_KEY}`
- **Content-Type**: `application/json`
- **Default Model**: `kilo-auto/free`

### API Key Management
- Read from `os.getenv("VITE_KILO_API_KEY")` or `os.getenv("KILO_API_KEY")`
- Never hardcode API keys in source code
- Never log API keys to UI
- Store in `.env` file (git-ignored)

### Request Patterns
```python
import requests

KILO_API_URL = "https://api.kilo.ai/api/gateway"

def call_ai(messages, model=DEFAULT_MODEL, retries=3):
    api_key = os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.post(
        f"{KILO_API_URL}/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1200
        },
        timeout=90
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
```

### Get Free Models
```python
def get_free_models():
    try:
        res = requests.get(f"{KILO_API_URL}/models", timeout=10)
        if res.status_code == 200:
            data = res.json()
            models = []
            for m in data.get("data", []):
                model_id = m.get("id", "")
                pricing = m.get("pricing", {})
                is_free = float(pricing.get("prompt", 1)) == 0
                if is_free or "/free" in model_id.lower():
                    models.append(model_id)
            return models if models else ["kilo-auto/free"]
    except:
        pass
    return ["kilo-auto/free", "minimax/minimax-m2.5:free"]
```

### Temperature Guidelines
| Task | Temperature | Max Tokens |
|------|-------------|------------|
| Resume/JD Analysis | 0.7 | 1500 |
| Question Generation | 0.8 | 2000 |
| Answer Evaluation | 0.7 | 500 |
| Final Report | 0.7 | 2500 |

### Error Handling
- Always wrap API calls in try/except
- Handle HTTP errors (400, 401, 429, 500) with user-friendly messages
- Implement retry logic with exponential backoff
- Provide fallback models array for auto-retry
- Never expose raw error messages to users

### Common Error Codes
| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check request format |
| 401 | Unauthorized | Verify API key |
| 429 | Rate limited | Show retry message |
| 500 | Server error | Retry with backoff |

### Response Parsing
- Always check `response.status_code == 200` before parsing
- Extract content from `response.json()["choices"][0]["message"]["content"]`
- Handle empty/null choices array gracefully
- Return `None` on failure instead of raising exceptions