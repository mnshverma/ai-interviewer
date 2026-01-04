# 🏗️ AI Interviewer - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│  (React Components + Modern CSS + Animations)                │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─► Resume Upload & Analysis
             │   └─► PDF Parser (pdf.js)
             │
             ├─► Interview Configuration
             │   └─► API Key Management
             │
             ├─► Video Interview
             │   ├─► WebRTC (Camera Access)
             │   └─► MediaRecorder API
             │
             ├─► Voice System
             │   ├─► Speech Synthesis (TTS)
             │   └─► Speech Recognition (STT)
             │
             └─► AI Processing
                 └─► OpenRouter API (LLaMA 3.1)
                     ├─► Resume Analysis
                     ├─► Question Generation
                     ├─► Answer Evaluation
                     └─► Final Report
```

## Technology Stack

### Frontend Framework

- **React 18**: Component-based UI
- **Vite**: Fast build tool and dev server
- **Vanilla CSS**: Custom design system (no framework dependencies)

### AI/LLM Integration

- **OpenRouter API**: Gateway to open-source models
- **Model**: Meta LLaMA 3.1 8B Instruct (Free)
- **Alternatives**: Gemma 2 9B, Phi-3 Medium (all free)

### Speech Technology

- **Web Speech API**: Browser-native
  - `SpeechSynthesis`: Text-to-Speech
  - `SpeechRecognition`: Speech-to-Text
- **No external dependencies**
- **Completely free**

### Video Technology

- **WebRTC**: Real-time communication
- **MediaRecorder API**: Video recording
- **getUserMedia**: Camera/microphone access
- **Local processing only**

### Document Processing

- **pdf.js**: Mozilla's PDF parser
- **Text extraction** from PDF files
- **Client-side processing**

## Component Architecture

### Core Components

```
src/
├── App.jsx                    # Main orchestrator
├── components/
│   ├── ResumeUpload.jsx      # File upload & parsing
│   ├── InterviewSettings.jsx # Configuration UI
│   ├── VideoInterview.jsx    # Camera & recording
│   ├── TranscriptPanel.jsx   # Real-time transcript
│   └── FinalReport.jsx       # Evaluation results
├── utils/
│   ├── openRouterAPI.js      # AI API integration
│   ├── pdfParser.js          # Resume parsing
│   └── speechService.js      # Voice services
└── index.css                  # Design system
```

### State Management

**No Redux/Context Needed** - Simple useState in App.jsx:

```javascript
const [resumeData, setResumeData] = useState(null);
const [interviewConfig, setInterviewConfig] = useState(null);
const [interviewState, setInterviewState] = useState("setup");
const [resumeAnalysis, setResumeAnalysis] = useState("");
const [questions, setQuestions] = useState([]);
const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
const [transcript, setTranscript] = useState([]);
const [isAISpeaking, setIsAISpeaking] = useState(false);
const [isListening, setIsListening] = useState(false);
const [finalReport, setFinalReport] = useState(null);
```

## Data Flow

### 1. Resume Upload Flow

```
User uploads file
    ↓
extractTextFromFile() → pdf.js extracts text
    ↓
setResumeData() → Store in state
    ↓
Enable "Start Interview" button
```

### 2. Interview Initialization Flow

```
User clicks "Start Interview"
    ↓
handleStartInterview()
    ↓
analyzeResume() → OpenRouter API
    ↓
generateInterviewQuestions() → OpenRouter API
    ↓
setQuestions() → Store questions
    ↓
startInterviewing() → Begin interview
    ↓
speechService.speak() → AI speaks greeting
```

### 3. Interview Question Flow

```
Display question on screen
    ↓
speechService.speak(question) → TTS
    ↓
User clicks "Start Recording"
    ↓
speechService.startListening() → STT
    ↓
User speaks answer
    ↓
finalAnswer captured
    ↓
addToTranscript() → Add to transcript
    ↓
evaluateAnswer() → OpenRouter API (optional)
    ↓
Next question or complete interview
```

### 4. Interview Completion Flow

```
All questions answered
    ↓
completeInterview()
    ↓
generateFinalReport() → OpenRouter API
    ↓
Display report modal
    ↓
User downloads report/transcript
```

## API Integration

### OpenRouter API Calls

**1. Resume Analysis**

```javascript
POST https://openrouter.ai/api/v1/chat/completions
Headers:
  - Authorization: Bearer {apiKey}
  - Content-Type: application/json
Body:
  - model: "meta-llama/llama-3.1-8b-instruct:free"
  - messages: [system, user]
  - temperature: 0.7
  - max_tokens: 1500
```

**2. Question Generation**

```javascript
Similar to above, but with:
  - temperature: 0.8
  - max_tokens: 2000
  - Specific prompt for question generation
```

**3. Answer Evaluation** (Optional)

```javascript
Similar to above, but with:
  - temperature: 0.7
  - max_tokens: 300
  - Evaluation criteria in prompt
```

**4. Final Report**

```javascript
Similar to above, but with:
  - max_tokens: 2500
  - Comprehensive evaluation prompt
```

### Rate Limiting

- Free tier: Varies by model
- Handled with try/catch
- User-friendly error messages

## Speech Services

### Text-to-Speech (SpeechSynthesis)

```javascript
class SpeechService {
  speak(text, options = {}) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options.rate || 0.95;
    utterance.pitch = options.pitch || 1.0;
    utterance.volume = options.volume || 1.0;

    // Voice selection
    const voices = speechSynthesis.getVoices();
    utterance.voice = voices.find(
      (v) => v.lang.startsWith("en") && v.name.includes("Female")
    );

    return new Promise((resolve, reject) => {
      utterance.onend = resolve;
      utterance.onerror = reject;
      speechSynthesis.speak(utterance);
    });
  }
}
```

### Speech-to-Text (SpeechRecognition)

```javascript
startListening(onResult, onEnd, onError) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  recognition.onresult = (event) => {
    let finalTranscript = '';
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }

    onResult({ interim: interimTranscript, final: finalTranscript });
  };

  recognition.start();
}
```

## Video Recording

### WebRTC Implementation

```javascript
// Get camera access
const stream = await navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: "user",
  },
  audio: true,
});

// Setup MediaRecorder
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: "video/webm;codecs=vp8,opus",
});

mediaRecorder.ondataavailable = (event) => {
  if (event.data.size > 0) {
    recordedChunks.push(event.data);
  }
};

// Start/Stop recording
mediaRecorder.start(100); // 100ms chunks
mediaRecorder.stop();

// Create downloadable blob
const blob = new Blob(recordedChunks, { type: "video/webm" });
```

## PDF Parsing

### pdf.js Integration

```javascript
import * as pdfjsLib from "pdfjs-dist";

// Set worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

// Load PDF
const arrayBuffer = await file.arrayBuffer();
const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

// Extract text from all pages
for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
  const page = await pdf.getPage(pageNum);
  const textContent = await page.getTextContent();
  const pageText = textContent.items.map((item) => item.str).join(" ");
  fullText += pageText + "\n";
}
```

## Security Considerations

### API Key Protection

- **Environment Variables**: `.env` file (git-ignored)
- **Local Storage**: Optional encrypted storage
- **Never Logged**: No console.log of API keys
- **HTTPS Only**: In production

### Data Privacy

- **No Server Storage**: All processing client-side
- **Local Recording**: Videos never uploaded
- **Minimal API Calls**: Only necessary data sent to OpenRouter
- **No Analytics**: No user tracking

### Browser Permissions

- **Camera**: Required for video
- **Microphone**: Required for voice
- **Explicit Consent**: User must grant permissions
- **Revokable**: Can be disabled anytime

## Performance Optimizations

### Code Splitting

```javascript
// Dynamic imports for pdf.js
const pdfjsLib = await import("pdfjs-dist");
```

### Lazy Loading

- Components loaded on demand
- PDF worker loaded only when needed

### State Optimization

- Minimal re-renders
- useCallback for event handlers
- Efficient transcript updates

### Memory Management

- Clean up video streams
- Stop speech synthesis
- Release blob URLs

## Browser Compatibility

### Supported Browsers

✅ **Chrome 70+** (Recommended)
✅ **Edge 79+** (Chromium-based)
✅ **Firefox 70+**
⚠️ **Safari 14+** (Limited speech recognition)

### Feature Detection

```javascript
// Check speech recognition
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  // Enable voice features
}

// Check camera
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  // Enable video features
}
```

## Error Handling

### Graceful Degradation

- **No Camera**: Show message, continue with audio only
- **No Microphone**: Allow text input instead
- **No Speech API**: Disable voice, use text interface
- **API Failures**: Show error, allow retry

### Error Recovery

```javascript
try {
  const result = await analyzeResume(text, apiKey);
  if (!result.success) {
    throw new Error(result.error);
  }
} catch (error) {
  console.error("Analysis failed:", error);
  setError(error.message);
  setInterviewState("setup");
}
```

## Deployment

### Build for Production

```bash
npm run build
```

**Output:**

- `dist/` folder with optimized bundle
- Minified CSS and JS
- Static assets

### Deployment Options

**1. Netlify/Vercel:**

```bash
# netlify.toml or vercel.json
{
  "build": {
    "command": "npm run build",
    "publish": "dist"
  },
  "env": {
    "VITE_OPENROUTER_API_KEY": "@openrouter-key"
  }
}
```

**2. Static Hosting:**

- Upload `dist/` folder
- Configure environment variables
- Enable HTTPS

**3. Docker:**

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npx", "serve", "-s", "dist"]
```

## Monitoring & Analytics

### Basic Logging

```javascript
// Interview metrics
const metrics = {
  resumeAnalysisTime: Date.now() - startTime,
  questionsGenerated: questions.length,
  interviewDuration: endTime - startTime,
  transcriptLength: transcript.length,
};
```

### Error Tracking

- Console errors for debugging
- User-friendly error messages
- Optional integration with Sentry/LogRocket

## Future Enhancements

### Planned Features

1. **Multi-Language Support**: i18n integration
2. **Custom Question Banks**: Pre-defined question sets
3. **Analytics Dashboard**: Interview metrics
4. **Candidate Portal**: Multi-session support
5. **Screen Sharing**: Technical assessments
6. **Code Editor**: Live coding challenges
7. **AI Proctoring**: Attention detection
8. **Team Collaboration**: Multi-interviewer mode

### Performance Improvements

1. **Service Worker**: Offline capability
2. **IndexedDB**: Local data persistence
3. **WebAssembly**: Faster PDF parsing
4. **Optimistic Updates**: Better UX

### Integration Possibilities

1. **ATS Systems**: Lever, Greenhouse, etc.
2. **Calendar**: Google Calendar, Outlook
3. **Email**: Automated follow-ups
4. **Slack/Teams**: Notifications

## Contributing

### Code Style

- ESLint configuration
- Prettier for formatting
- Comment complex logic
- PropTypes for components

### Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Write tests
4. Submit PR with description

---

## 📚 Resources

- **React Docs**: https://react.dev
- **Vite Docs**: https://vitejs.dev
- **OpenRouter**: https://openrouter.ai/docs
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **WebRTC**: https://webrtc.org
- **pdf.js**: https://mozilla.github.io/pdf.js/

---

**Built with ❤️ using open-source technologies**
