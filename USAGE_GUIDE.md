# 🚀 AI Interviewer - Quick Start Guide

## Overview

You've successfully built an **AI-powered interview platform** that:

- ✅ Analyzes resumes using AI
- ✅ Generates personalized interview questions
- ✅ Conducts live video interviews
- ✅ Uses voice (Text-to-Speech and Speech-to-Text)
- ✅ Provides real-time transcripts
- ✅ Creates comprehensive evaluation reports
- ✅ **100% Open Source** - Uses only OpenRouter API and free browser technologies

## 🎯 What You Can Do

### 1. Upload & Analyze Resumes

- Drag & drop PDF or TXT files
- AI extracts skills, experience, education
- Generates relevant interview questions

### 2. Live Video Interviews

- Real-time webcam video
- Video recording capability
- Professional interview environment

### 3. AI Voice Interaction

- **AI Speaks Questions**: Natural text-to-speech
- **Voice Recognition**: Automatic answer transcription
- **Completely Free**: Uses browser's Web Speech API

### 4. Multiple Interview Types

- **Technical**: Coding, algorithms, system design
- **Behavioral**: Soft skills, teamwork, leadership
- **Mixed**: Balanced technical + behavioral
- **Leadership**: Management and strategic thinking

### 5. Comprehensive Reports

- Performance ratings
- Strengths and weaknesses
- Technical assessments
- Hiring recommendations

## 🔧 Setup Instructions

### Step 1: Get Your Free OpenRouter API Key

1. Visit: **https://openrouter.ai/keys**
2. Sign up for a free account
3. Click "Create Key"
4. Copy your API key (starts with `sk-or-v1-`)

### Step 2: Configure the Application

**Option A: Use Environment File (Recommended)**

1. Open `.env` file in the project root
2. Add your API key:
   ```
   VITE_OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```
3. Save the file

**Option B: Enter at Runtime**

- Just paste your key in the "OpenRouter API Key" field when using the app

### Step 3: Run the Application

The app is already running at: **http://localhost:5173**

To restart it later:

```bash
npm run dev
```

## 📖 How to Use

### Conducting an Interview

1. **Upload Resume**

   - Click the upload area or drag a PDF/TXT file
   - Wait for "File uploaded successfully!"

2. **Configure Settings**

   - Enter your API key (if not in .env)
   - Choose interview type
   - Toggle voice and recording options

3. **Start Interview**

   - Click "🚀 Start Interview"
   - Grant camera and microphone permissions
   - AI analyzes resume and generates questions

4. **Answer Questions**

   - Listen to AI's question (spoken aloud if voice enabled)
   - Click "⏺ Start Recording Answer"
   - Speak your answer clearly
   - Click "⏹ Stop & Submit Answer"
   - AI automatically moves to next question

5. **Review Results**
   - After all questions, view comprehensive report
   - Download transcript and evaluation
   - Start new interview or close

### Tips for Best Results

**Resume Upload:**

- Use clean, well-formatted PDFs
- Include clear sections (Skills, Experience, Education)
- Avoid scanned images (text-based PDFs work best)

**During Interview:**

- Speak clearly and at moderate pace
- Wait for the "Listening" indicator before answering
- Keep answers focused and structured
- Use the video preview to check your positioning

**Voice Recognition:**

- Chrome or Edge work best
- Ensure microphone is properly connected
- Grant microphone permissions when prompted
- Speak in a quiet environment

## 🎨 Features Explained

### Resume Analysis

The AI (LLaMA 3.1 8B via OpenRouter) analyzes:

- Work experience and roles
- Technical skills and proficiencies
- Educational background
- Projects and achievements
- Career progression

### Question Generation

Questions are:

- **Personalized**: Based on your specific resume
- **Progressive**: Start easy, get more challenging
- **Relevant**: Match your experience level
- **Varied**: Mix of technical, behavioral, situational

### Voice System

**Text-to-Speech (AI Speaking):**

- Uses browser's native speech synthesis
- Female voice preferred (when available)
- Natural pacing and intonation

**Speech-to-Text (Your Answers):**

- Real-time transcription
- Shows interim results while you speak
- Final transcript captured automatically

### Evaluation Report

Includes:

- **Overall Rating**: 1-10 scale
- **Strengths**: 3-5 key positives
- **Improvements**: Areas to work on
- **Technical Assessment**: Skill evaluation
- **Communication**: How well you articulated
- **Recommendation**: Hire/Maybe/No Hire
- **Detailed Notes**: Specific observations

## 🔐 Privacy & Security

**Your Data:**

- Resume: Processed locally, only text sent to OpenRouter API
- Video: Recorded locally in your browser
- Transcript: Stored in browser memory
- API Key: Stored locally, never transmitted except to OpenRouter

**What's Shared:**

- Resume text (for analysis)
- Interview transcript (for evaluation)
- Nothing else!

**What's NOT Shared:**

- Video recordings
- Audio recordings
- Personal API keys
- Any other data

## 💰 Cost Breakdown

**100% FREE when using:**

- ✅ OpenRouter free tier (LLaMA 3.1 8B)
- ✅ Web Speech API (browser native)
- ✅ WebRTC (browser native)
- ✅ pdf.js (open source)

**OpenRouter Free Tier:**

- Meta LLaMA 3.1 8B Instruct: FREE
- Rate limits apply but generous
- No credit card required

**Alternatives (Paid Options):**
If you want premium models:

- GPT-4: ~$0.03-0.06 per interview
- Claude 3: ~$0.02-0.04 per interview
- Still very affordable!

## 🛠️ Customization

### Change AI Model

Edit `src/utils/openRouterAPI.js`:

```javascript
model: "meta-llama/llama-3.1-8b-instruct:free";
```

**Available Free Models:**

- `meta-llama/llama-3.1-8b-instruct:free`
- `google/gemma-2-9b-it:free`
- `microsoft/phi-3-medium-128k-instruct:free`

### Modify Question Prompts

In `openRouterAPI.js`, edit the `generateInterviewQuestions` function's system prompt.

### Change UI Theme

Edit `src/index.css`:

- Color variables in `:root`
- Background gradients
- Animations and effects

### Adjust Speech Settings

In `src/utils/speechService.js`:

```javascript
utterance.rate = 0.95; // Speed (0.1-10)
utterance.pitch = 1.0; // Pitch (0-2)
utterance.volume = 1.0; // Volume (0-1)
```

## 🐛 Troubleshooting

### Camera Issues

**Problem**: Camera not detected
**Solutions:**

1. Grant camera permissions in browser
2. Check if other apps are using camera
3. Try different browser (Chrome recommended)
4. Restart browser

### Microphone Issues

**Problem**: Speech recognition not working
**Solutions:**

1. Grant microphone permissions
2. Check Privacy settings (Windows Settings > Privacy > Microphone)
3. Test microphone in other apps
4. Use headset microphone for better accuracy

### API Errors

**Problem**: "OpenRouter API error"
**Solutions:**

1. Verify API key is correct
2. Check internet connection
3. Ensure you haven't exceeded rate limits
4. Try again in a few minutes

### Resume Not Parsing

**Problem**: "Failed to process file"
**Solutions:**

1. Ensure file is PDF or TXT
2. Try converting to plain text first
3. Check file isn't corrupted
4. Reduce file size if very large

### Speech Not Working

**Problem**: AI not speaking
**Solutions:**

1. Ensure "Enable AI Voice" is checked
2. Check browser supports Web Speech API
3. Unmute browser tab
4. Check system volume

## 📊 Performance Tips

**For Faster Interviews:**

- Use faster AI model (e.g., LLaMA 3.1 8B)
- Shorter resumes = faster analysis
- Disable voice for text-only mode
- Disable recording if not needed

**For Better Accuracy:**

- Use premium models (GPT-4, Claude)
- Provide detailed, structured resume
- Speak clearly during answers
- Use quality microphone

## 🚀 Advanced Features

### Batch Interviews

Process multiple candidates:

1. Complete one interview
2. Click "Start Over"
3. Upload new resume
4. Repeat

### Custom Scenarios

Modify prompts for:

- Specific job roles
- Industry-specific questions
- Company culture fit
- Skills assessments

### Integration

Export data for:

- ATS (Applicant Tracking Systems)
- HR databases
- Analytics platforms
- Custom workflows

## 📞 Support & Resources

**Documentation:**

- Full README: `/README.md`
- Code comments in source files

**API Documentation:**

- OpenRouter: https://openrouter.ai/docs
- Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

**Community:**

- GitHub Issues (if you create a repo)
- Stack Overflow
- OpenRouter Discord

## 🎓 Next Steps

**Enhance the Platform:**

1. Add more interview types
2. Implement skill-specific assessments
3. Create question banks
4. Add analytics dashboard
5. Multi-language support

**Deploy to Production:**

```bash
npm run build
```

Then deploy to:

- Netlify
- Vercel
- GitHub Pages
- Your own server

**Create Mobile Version:**

- Responsive design already included
- Add PWA capabilities
- Native app with React Native

---

## ✅ You're All Set!

Your AI Interviewer platform is ready to use. Start conducting professional interviews powered by AI!

**Quick Start:**

1. Open http://localhost:5173
2. Upload a resume
3. Enter API key
4. Click "Start Interview"
5. Grant permissions
6. Begin interviewing!

**Need Help?**

- Check troubleshooting section
- Review code comments
- Check browser console for errors
- Verify API key and permissions

**Happy Interviewing! 🎉**
