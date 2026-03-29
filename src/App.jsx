import { useState, useCallback, useRef } from 'react';
import DataInput from './components/DataInput';
import InterviewSettings from './components/InterviewSettings';
import VideoInterview from './components/VideoInterview';
import TranscriptPanel from './components/TranscriptPanel';
import FinalReport from './components/FinalReport';
import InterviewHistory, { saveInterviewSession } from './components/InterviewHistory';
import { useToast } from './components/Toast';
import { analyzeResume, analyzeJobDescription, generateInterviewQuestions, evaluateAnswer, generateFinalReport } from './utils/openRouterAPI';
import { speechService } from './utils/speechService';
import './index.css';

function App() {
  // State management
  const [inputData, setInputData] = useState(null);
  const [interviewConfig, setInterviewConfig] = useState(null);
  const [interviewState, setInterviewState] = useState('setup');
  const [resumeAnalysis, setResumeAnalysis] = useState('');
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [transcript, setTranscript] = useState([]);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [finalReport, setFinalReport] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState('');
  const [recordedVideo, setRecordedVideo] = useState(null);

  const transcriptRef = useRef([]);
  const toast = useToast();

  // Handle data input
  const handleDataProvided = useCallback((data) => {
    setInputData(data);
    setError('');
  }, []);

  // Start interview process
  const handleStartInterview = useCallback(async (config) => {
    setInterviewConfig(config);
    setInterviewState('analyzing');
    setError('');

    try {
      let analysisResult;
      
      if (inputData.mode === 'resume') {
        analysisResult = await analyzeResume(inputData.text, config.aiModel);
      } else {
        analysisResult = await analyzeJobDescription(inputData.text, config.aiModel);
      }
      
      if (!analysisResult.success) {
        throw new Error(analysisResult.error || 'Failed to analyze input');
      }

      setResumeAnalysis(analysisResult.analysis);

      // Generate questions with difficulty level
      const questionsResult = await generateInterviewQuestions(
        analysisResult.analysis,
        config.interviewType,
        config.aiModel,
        config.difficulty
      );

      if (!questionsResult.success || questionsResult.questions.length === 0) {
        throw new Error('Failed to generate interview questions');
      }

      setQuestions(questionsResult.questions);
      setInterviewState('ready');

      setTimeout(() => {
        startInterviewing(config, questionsResult.questions[0]);
      }, 1000);

    } catch (err) {
      console.error('Interview start error:', err);
      setError(err.message);
      toast.error('Failed to start interview: ' + err.message);
      setInterviewState('setup');
    }
  }, [inputData]);

  // Start interviewing
  const startInterviewing = useCallback(async (config, firstQuestion) => {
    setInterviewState('interviewing');

    const inputLabel = inputData?.mode === 'resume' ? 'resume' : 'job description';
    const greeting = `Hello! I'm your AI interviewer. I've reviewed your ${inputLabel} and prepared ${questions.length} questions for you. Let's begin with the first question.`;
    
    addToTranscript('interviewer', greeting);

    if (config.enableVoice && !config.practiceMode) {
      setIsAISpeaking(true);
      try {
        await speechService.speak(greeting);
        await new Promise(resolve => setTimeout(resolve, 500));
        await speechService.speak(firstQuestion);
      } catch (err) {
        console.error('Speech error:', err);
      }
      setIsAISpeaking(false);
    }

    addToTranscript('interviewer', firstQuestion);
  }, [questions.length, inputData]);

  // Add to transcript
  const addToTranscript = useCallback((speaker, text, feedback = null) => {
    const entry = { speaker, text, feedback, timestamp: Date.now() };
    setTranscript(prev => {
      const updated = [...prev, entry];
      transcriptRef.current = updated;
      return updated;
    });
  }, []);

  // Handle answer completion
  const handleAnswerComplete = useCallback(async (answerText) => {
    if (!interviewConfig || !answerText?.trim()) return;

    addToTranscript('candidate', answerText);

    const currentQuestion = questions[currentQuestionIndex];
    
    try {
      const evaluation = await evaluateAnswer(
        currentQuestion,
        answerText,
        resumeAnalysis,
        interviewConfig.aiModel
      );

      if (evaluation.success && evaluation.feedback) {
        setTranscript(prev => {
          const updated = [...prev];
          updated[updated.length - 1].feedback = evaluation.feedback;
          transcriptRef.current = updated;
          return updated;
        });
      }
    } catch (err) {
      console.error('Evaluation error:', err);
    }

    moveToNextQuestion();
  }, [interviewConfig, questions, currentQuestionIndex, resumeAnalysis, addToTranscript]);

  // Skip question
  const handleSkipQuestion = useCallback(() => {
    addToTranscript('candidate', '(Question skipped)');
    toast.info('Question skipped');
    moveToNextQuestion();
  }, [addToTranscript]);

  // Move to next question
  const moveToNextQuestion = useCallback(async () => {
    const nextIndex = currentQuestionIndex + 1;
    
    if (nextIndex < questions.length) {
      setCurrentQuestionIndex(nextIndex);
      const nextQuestion = questions[nextIndex];
      
      addToTranscript('interviewer', nextQuestion);

      if (interviewConfig?.enableVoice && !interviewConfig?.practiceMode) {
        setIsAISpeaking(true);
        try {
          await speechService.speak(nextQuestion);
        } catch (err) {
          console.error('Speech error:', err);
        }
        setIsAISpeaking(false);
      }
    } else {
      await completeInterview();
    }
  }, [interviewConfig, questions, currentQuestionIndex, addToTranscript]);

  // Complete interview
  const completeInterview = useCallback(async () => {
    setInterviewState('completed');

    const closingMessage = "Thank you for completing the interview! I'm generating your evaluation report now.";
    addToTranscript('interviewer', closingMessage);

    if (interviewConfig?.enableVoice && !interviewConfig?.practiceMode) {
      try {
        await speechService.speak(closingMessage);
      } catch (err) {
        console.error('Speech error:', err);
      }
    }

    try {
      const latestTranscript = transcriptRef.current;
      const transcriptText = latestTranscript
        .map(t => `${t.speaker.toUpperCase()}: ${t.text}`)
        .join('\n\n');

      const reportResult = await generateFinalReport(
        transcriptText,
        resumeAnalysis,
        interviewConfig.aiModel
      );

      if (reportResult.success) {
        setFinalReport(reportResult.report);
        setShowReport(true);

        // Save to history
        const scoreMatch = reportResult.report.match(/(?:overall|performance)\s*(?:score|rating)?[\s:]*(\d+)/i);
        saveInterviewSession({
          mode: inputData?.mode || 'resume',
          interviewType: interviewConfig?.interviewType || 'mixed',
          score: scoreMatch ? parseInt(scoreMatch[1]) : null,
          questionCount: questions.length,
          report: reportResult.report,
          transcript: transcriptText
        });
        toast.success('Interview completed! Report saved to history.');
      } else {
        throw new Error(reportResult.error);
      }
    } catch (err) {
      console.error('Report generation error:', err);
      setError('Failed to generate final report: ' + err.message);
      toast.error('Failed to generate report');
    }
  }, [interviewConfig, resumeAnalysis, addToTranscript, inputData, questions.length]);

  // Handle video recording ready
  const handleRecordingReady = useCallback((blob) => {
    setRecordedVideo(blob);
    toast.success('Interview video recording saved!');
  }, []);

  // Download recorded video
  const handleDownloadVideo = useCallback(() => {
    if (!recordedVideo) return;
    const url = URL.createObjectURL(recordedVideo);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview_recording_${Date.now()}.webm`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Video downloaded!');
  }, [recordedVideo]);

  // Download report
  const handleDownloadReport = useCallback(() => {
    if (!finalReport) return;
    const blob = new Blob([finalReport], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview_report_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Report downloaded!');
  }, [finalReport]);

  // Reset interview
  const handleReset = useCallback(() => {
    setInputData(null);
    setInterviewConfig(null);
    setInterviewState('setup');
    setResumeAnalysis('');
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setTranscript([]);
    transcriptRef.current = [];
    setFinalReport(null);
    setShowReport(false);
    setRecordedVideo(null);
    setError('');
    speechService.stopSpeaking();
    speechService.stopListening();
  }, []);

  // Render UI based on state
  const renderContent = () => {
    switch (interviewState) {
      case 'setup':
        return (
          <div className="grid grid-2" style={{ height: '100%', padding: 'var(--space-lg)', gap: 'var(--space-lg)' }}>
            <DataInput onDataProvided={handleDataProvided} />
            <InterviewSettings 
              onStartInterview={handleStartInterview} 
              hasData={inputData !== null} 
            />
          </div>
        );

      case 'analyzing':
        return (
          <div className="flex items-center justify-center" style={{ height: '100%' }}>
            <div className="card text-center scale-in">
              <div className="loading-spinner" style={{ margin: '0 auto var(--space-lg)' }}></div>
              <h2 className="mb-md">🔍 Analyzing...</h2>
              <p className="text-secondary">
                AI is analyzing the {inputData?.mode === 'resume' ? 'resume' : 'job description'} and generating personalized interview questions
              </p>
              {interviewConfig?.difficulty && (
                <p className="text-tertiary mt-sm" style={{ fontSize: 'var(--font-size-sm)' }}>
                  Difficulty: {interviewConfig.difficulty.charAt(0).toUpperCase() + interviewConfig.difficulty.slice(1)}
                </p>
              )}
            </div>
          </div>
        );

      case 'ready':
        return (
          <div className="flex items-center justify-center" style={{ height: '100%' }}>
            <div className="card text-center scale-in">
              <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--space-lg)' }}>
                ✅
              </div>
              <h2 className="mb-md">Interview Ready!</h2>
              <p className="text-secondary mb-lg">
                {questions.length} questions generated. Starting {interviewConfig?.practiceMode ? 'practice' : 'interview'}...
              </p>
              <div className="loading-spinner" style={{ margin: '0 auto' }}></div>
            </div>
          </div>
        );

      case 'interviewing':
      case 'completed':
        return (
          <div style={{ 
            height: '100%', 
            padding: 'var(--space-lg)', 
            display: 'grid',
            gridTemplateColumns: interviewConfig?.practiceMode ? '1fr 1fr' : '1.5fr 1fr',
            gap: 'var(--space-lg)'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
              <VideoInterview
                isActive={true}
                currentQuestion={questions[currentQuestionIndex]}
                onAnswerComplete={handleAnswerComplete}
                onSkipQuestion={handleSkipQuestion}
                isAISpeaking={isAISpeaking}
                onVideoReady={() => {}}
                autoStartListening={true}
                practiceMode={interviewConfig?.practiceMode || false}
                timeLimit={interviewConfig?.timeLimit || 0}
                onRecordingReady={handleRecordingReady}
              />
              
              {interviewState === 'completed' && (
                <div className="card text-center">
                  <h3 className="mb-md">🎉 Interview Completed!</h3>
                  <p className="text-secondary mb-md">
                    Your evaluation report is ready
                  </p>
                  <div className="flex gap-sm justify-center" style={{ flexWrap: 'wrap' }}>
                    <button className="btn btn-primary" onClick={() => setShowReport(true)}>
                      📊 View Report
                    </button>
                    {recordedVideo && (
                      <button className="btn btn-secondary" onClick={handleDownloadVideo}>
                        🎥 Download Video
                      </button>
                    )}
                    <button className="btn btn-secondary" onClick={handleReset}>
                      🔄 New Interview
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
              <div className="card">
                <h3 className="mb-md">📋 Progress</h3>
                <div className="mb-md">
                  <div className="flex justify-between mb-sm">
                    <span>Question {Math.min(currentQuestionIndex + 1, questions.length)} of {questions.length}</span>
                    <span className="text-secondary">
                      {Math.round((Math.min(currentQuestionIndex + 1, questions.length) / questions.length) * 100)}%
                    </span>
                  </div>
                  <div style={{
                    width: '100%',
                    height: '8px',
                    background: 'var(--color-bg-tertiary)',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${(Math.min(currentQuestionIndex + 1, questions.length) / questions.length) * 100}%`,
                      height: '100%',
                      background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
                      transition: 'width 0.5s ease'
                    }} />
                  </div>
                </div>

                {/* Difficulty badge */}
                {interviewConfig?.difficulty && (
                  <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 'var(--space-xs)',
                    padding: '4px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    background: interviewConfig.difficulty === 'easy' ? 'rgba(56,239,125,0.1)' :
                      interviewConfig.difficulty === 'hard' ? 'rgba(245,87,108,0.1)' : 'rgba(255,210,0,0.1)',
                    color: interviewConfig.difficulty === 'easy' ? '#38ef7d' :
                      interviewConfig.difficulty === 'hard' ? '#f5576c' : '#ffd200'
                  }}>
                    {interviewConfig.difficulty === 'easy' ? '🟢' : interviewConfig.difficulty === 'hard' ? '🔴' : '🟡'}
                    {interviewConfig.difficulty.charAt(0).toUpperCase() + interviewConfig.difficulty.slice(1)}
                  </div>
                )}
              </div>

              <TranscriptPanel 
                transcript={transcript}
                isActive={true}
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="app-container">
      <div className="animated-bg"></div>
      
      <div className="main-content">
        <header className="app-header">
          <div className="header-content">
            <div className="logo-section">
              <img src="/logo.svg" alt="Manver" className="logo-icon" style={{ width: '44px', height: '44px' }} />
              <div className="logo-text">
                <h1>Manver AI Interviewer</h1>
                <p>Smart Interview Platform</p>
              </div>
            </div>

            <div className="header-actions">
              {/* History Button (always visible) */}
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowHistory(true)}
                style={{ padding: 'var(--space-sm) var(--space-md)', fontSize: 'var(--font-size-sm)' }}
              >
                📚 History
              </button>

              {interviewState !== 'setup' && (
                <>
                  <div className="status-indicator" style={{ background: 'var(--color-bg-tertiary)' }}>
                    <span>
                      {interviewState === 'analyzing' && '🔍 Analyzing'}
                      {interviewState === 'ready' && '⏳ Preparing'}
                      {interviewState === 'interviewing' && (interviewConfig?.practiceMode ? '🎮 Practice' : '🎤 Live Interview')}
                      {interviewState === 'completed' && '✅ Completed'}
                    </span>
                  </div>
                  <button className="btn btn-secondary" onClick={handleReset}>
                    🏠 Start Over
                  </button>
                </>
              )}
            </div>
          </div>
        </header>

        <main style={{ flex: 1, overflow: 'auto' }}>
          {error && (
            <div style={{
              padding: 'var(--space-md)',
              background: 'hsla(0, 80%, 60%, 0.1)',
              border: '1px solid var(--color-danger)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-danger)',
              margin: 'var(--space-lg)'
            }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {renderContent()}
        </main>
      </div>

      {showReport && (
        <FinalReport
          report={finalReport}
          onClose={() => setShowReport(false)}
          onDownload={handleDownloadReport}
        />
      )}

      {showHistory && (
        <InterviewHistory
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  );
}

export default App;
