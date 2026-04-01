# Error Handling — AI Interviewer

## Principle: Graceful Degradation
The app should **never crash or show raw errors** to the user. Every failure should result in a meaningful message and a way to recover.

## Error Handling Patterns

### 1. API Calls (Kilo)
```python
def call_ai(messages, model=DEFAULT_MODEL, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=90)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                if attempt == retries - 1:
                    st.error(f"API Error ({response.status_code}): Unable to process request")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retry
            else:
                st.error("Connection error: Unable to reach server")
    return None
```

### 2. File Operations (PDF)
```python
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        if not text.strip():
            st.error("Could not extract text from this PDF")
            return ""
        return text
    except Exception as e:
        st.error("Error reading PDF. Please try a different file.")
        return ""
```

### 3. Streamlit Components
- `st.camera_input()` - Handle permission denial gracefully
- `st.audio_input()` - Show message if mic not available
- Use `st.error()`, `st.warning()`, `st.success()` for user feedback

## Degradation Strategy

| Feature Failed | Fallback |
|---------------|----------|
| Camera | Show message, continue without video |
| Microphone | Allow text input for answers |
| Kilo API | Show error, allow retry |
| PDF Parser | Suggest different file format |
| Model List | Use default models |

## Error Display Rules
1. **Never** show raw error objects or stack traces to users
2. **Always** provide actionable guidance in error messages
3. **Always** return `None` or empty string from failed operations
4. **Log** errors to console for developer debugging
5. **Never** swallow errors silently — at minimum show user message

## User Feedback Patterns
- Use `st.error()` for failures that need user action
- Use `st.warning()` for non-critical issues
- Use `st.success()` for completed actions
- Use `st.spinner()` for async operations