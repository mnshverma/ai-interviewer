# 🎯 AI Interviewer

**Resume-Based Live Video Interview Platform**

An AI-powered interviewer that analyzes your resume and conducts live video interviews with real-time questions, speech recognition, and comprehensive evaluation reports.

## ✨ Features

- **📄 Resume Analysis**: Upload PDF/TXT resumes for AI-powered analysis
- **🎤 Live Video Interview**: Real-time webcam interview with video recording
- **🤖 AI-Generated Questions**: Personalized questions based on your resume
- **🗣️ Voice Interaction**: Text-to-Speech questions and Speech-to-Text answers
- **📝 Real-time Transcript**: Live transcript with timestamps and feedback
- **📊 Evaluation Report**: Comprehensive AI-generated performance report
- **🔒 100% Open Source**: Uses only OpenRouter API and open-source technologies

## 🚀 Tech Stack

- **Frontend**: React + Vite
- **AI/LLM**: OpenRouter API (LLaMA 3.1 8B - Free)
- **Speech**: Web Speech API (Browser Native)
- **Video**: WebRTC (Browser Native)
- **PDF Parsing**: pdf.js (Mozilla Open Source)
- **Styling**: Vanilla CSS with modern design system

## 📋 Prerequisites

1. **OpenRouter API Key** (Free):

   - Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
   - Sign up and get your free API key
   - Free tier includes access to LLaMA and other open-source models

2. **Modern Browser**:
   - Chrome, Edge, or Firefox (latest versions)
   - Camera and microphone permissions required

## 🛠️ Installation

1. **Clone or navigate to the project**:

   ```bash
   cd c:\automation\ai-interviewer
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Configure environment**:

   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key:
     ```
     VITE_OPENROUTER_API_KEY=sk-or-v1-...
     ```

4. **Run the application**:

   ```bash
   npm run dev
   ```

5. **Open in browser**:
   - Navigate to `http://localhost:5173`

## 📖 How to Use

### Step 1: Upload Resume

- Click or drag-and-drop your resume (PDF or TXT format)
- AI will extract and analyze the content

### Step 2: Configure Interview

- Enter your OpenRouter API key (if not in .env)
- Select interview type:
  - **Technical**: Programming, system design, algorithms
  - **Behavioral**: Leadership, teamwork, communication
  - **Mixed**: Combination of technical and behavioral
  - **Leadership**: Management and decision-making
- Enable/disable AI voice and recording

### Step 3: Start Interview

- Grant camera and microphone permissions
- AI will greet you and ask the first question
- Listen to the question (AI speaks aloud if voice is enabled)

### Step 4: Answer Questions

- Click "Start Recording Answer" to begin
- Speak your answer clearly
- Click "Stop & Submit Answer" when done
- AI will automatically move to the next question

### Step 5: View Results

- After all questions, view your comprehensive evaluation report
- Download transcript and report for your records

## 🎨 Features in Detail

### Resume Analysis

- Extracts key information from resumes
- Identifies skills, experience, and education
- Uses AI to understand context and relevance

### Interview Types

- **Technical**: Focuses on coding, algorithms, system design
- **Behavioral**: Assesses soft skills, leadership, teamwork
- **Mixed**: Balanced approach for comprehensive evaluation
- **Leadership**: Management, strategic thinking, decision-making

### Voice Interaction

- **Text-to-Speech**: AI speaks questions naturally
- **Speech-to-Text**: Your answers are transcribed automatically
- **Voice Selection**: Uses best available system voice
- Completely free using browser's Web Speech API

### Video Recording

- Records your interview session
- Download recording for review
- WebRTC-based, no external servers

### Real-time Transcript

- Live transcript with speaker identification
- Timestamps for each exchange
- AI feedback on answers
- Downloadable as text file

### Evaluation Report

- Overall performance rating (1-10)
- Key strengths and areas for improvement
- Technical competency assessment
- Communication skills rating
- Hiring recommendation
- Detailed notes and observations

## 🔐 Privacy & Security

- **API Key**: Stored locally in `.env` file, never shared
- **Video**: Processed locally in your browser
- **Resume**: Never uploaded to external servers (except OpenRouter for analysis)
- **Transcript**: Stored locally until you download or close the session

## 🆓 Cost

**100% Free** when using:

- OpenRouter's free tier (LLaMA 3.1 8B Instruct)
- Browser's native Web Speech API
- Browser's native WebRTC

No hidden costs, no subscriptions, no credit card required.

## 🛠️ Development

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Customize

- **Design**: Edit `src/index.css` for styling
- **AI Model**: Change model in `src/utils/openRouterAPI.js`
- **Questions**: Modify prompts in `openRouterAPI.js`

## 📝 Supported File Formats

- ✅ PDF (.pdf)
- ✅ Plain Text (.txt)
- ⚠️ DOCX (.docx) - Limited support

## 🐛 Troubleshooting

**Camera not working?**

- Grant camera permissions in browser
- Check if another app is using the camera
- Try refreshing the page

**Microphone not working?**

- Grant microphone permissions
- Check browser's privacy settings
- Ensure microphone is properly connected

**Speech recognition not working?**

- Use Chrome, Edge, or Firefox
- Check microphone settings
- Speak clearly and wait for the listening indicator

**API errors?**

- Verify your OpenRouter API key is correct
- Check your internet connection
- Ensure you haven't exceeded free tier limits

## 🤝 Contributing

This is an open-source project. Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Share with others

## 📄 License

MIT License - Free to use, modify, and distribute

## 🙏 Acknowledgments

- **OpenRouter**: For providing free access to open-source LLMs
- **Mozilla**: For pdf.js library
- **Web Speech API**: For free speech recognition and synthesis
- **WebRTC**: For enabling real-time video communication

---

**Made with ❤️ using only open-source technologies**
