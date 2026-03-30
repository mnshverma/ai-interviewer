# API Conventions — AI Interviewer

## OpenRouter API

### Base Configuration
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Auth**: `Authorization: Bearer {VITE_OPENROUTER_API_KEY}`
- **Content-Type**: `application/json`
- **Primary Model**: `meta-llama/llama-3.1-8b-instruct:free`

### API Key Management
- Always read from `import.meta.env.VITE_OPENROUTER_API_KEY`
- Never hardcode API keys
- Never log API keys to console
- Provide fallback UI for manual key input (InterviewSettings.jsx)

### Request Patterns
```javascript
// Standard API call pattern
const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
    'HTTP-Referer': window.location.origin,
    'X-Title': 'Manvar AI Interviewer'
  },
  body: JSON.stringify({
    model: selectedModel,
    messages: [...],
    temperature: 0.7,
    max_tokens: 1500
  })
});
```

### Temperature Guidelines
| Task | Temperature | Max Tokens |
|------|------------|------------|
| Resume Analysis | 0.7 | 1500 |
| Question Generation | 0.8 | 2000 |
| Answer Evaluation | 0.7 | 300 |
| Final Report | 0.7 | 2500 |

### Error Handling
- Always wrap API calls in try/catch
- Handle rate limiting (429) with user-friendly message
- Handle network errors with retry suggestion
- Handle malformed responses gracefully
- Provide fallback models array for auto-retry

### Free Model Fallbacks
When primary model fails, try alternatives in order:
1. `meta-llama/llama-3.1-8b-instruct:free`
2. `google/gemma-2-9b-it:free`
3. `microsoft/phi-3-medium-128k-instruct:free`

### Response Parsing
- Always check `response.ok` before parsing JSON
- Extract content from `data.choices[0].message.content`
- Handle empty/null choices array
- Strip markdown code fences from JSON responses when parsing structured data

## All API Logic Lives In
`src/utils/openRouterAPI.js` — This is the SINGLE source of truth for all LLM interactions. Never make direct API calls from components.
