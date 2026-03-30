# Error Handling — AI Interviewer

## Principle: Graceful Degradation
The app should **never crash or show raw errors** to the user. Every failure should result in a meaningful message and a way to recover.

## Error Handling Patterns

### 1. API Calls (OpenRouter)
```javascript
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `API error: ${response.status}`);
  }
  const data = await response.json();
  if (!data.choices?.[0]?.message?.content) {
    throw new Error('Empty response from AI model');
  }
  return { success: true, data: data.choices[0].message.content };
} catch (error) {
  console.error('API call failed:', error);
  return { success: false, error: error.message };
}
```

### 2. Browser APIs (Camera, Microphone, Speech)
```javascript
try {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  // use stream...
} catch (error) {
  if (error.name === 'NotAllowedError') {
    showToast('Camera permission denied. Please allow access in browser settings.', 'warning');
  } else if (error.name === 'NotFoundError') {
    showToast('No camera found. Interview will continue without video.', 'info');
  } else {
    showToast('Camera error. Please refresh and try again.', 'error');
  }
}
```

### 3. File Parsing (PDF)
```javascript
try {
  const text = await extractTextFromPDF(file);
  if (!text || text.trim().length < 50) {
    throw new Error('Could not extract meaningful text from this PDF');
  }
  return text;
} catch (error) {
  showToast('Failed to read resume. Try a different file format.', 'error');
  return null;
}
```

## Degradation Strategy

| Feature Failed | Fallback |
|---------------|----------|
| Camera | Show message, continue with audio-only |
| Microphone | Allow text input for answers |
| Speech Recognition | Disable STT, use text input |
| Speech Synthesis | Disable TTS, show text questions only |
| OpenRouter API | Show error, allow API key change or retry |
| PDF Parser | Suggest TXT format upload |
| localStorage | Work without persistence, warn user |

## Error Boundary
`src/components/ErrorBoundary.jsx` wraps the entire app to catch render crashes:
- Shows a friendly "Something went wrong" UI
- Provides "Try Again" button to reset state
- Logs error details to console (for debugging)

## Toast Notifications
Use the `Toast.jsx` component for user-facing messages:
- `error`: Red — something failed, user action may be needed
- `warning`: Yellow — something degraded, app continues
- `success`: Green — action completed successfully
- `info`: Blue — informational message

## Rules
1. **Never** show raw error objects or stack traces to users
2. **Always** provide actionable guidance in error messages
3. **Always** return `{ success, data/error }` from utility functions
4. **Always** clean up resources (streams, listeners) in catch blocks
5. **Log** detailed errors to console for developer debugging
6. **Never** swallow errors silently — at minimum log and show toast
