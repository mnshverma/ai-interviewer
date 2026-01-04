import { useState, useCallback } from 'react';
import DataInput from './components/DataInput';
import InterviewSettings from './components/InterviewSettings';
import VideoInterview from './components/VideoInterview';
import TranscriptPanel from './components/TranscriptPanel';
import FinalReport from './components/FinalReport';
import { analyzeResume, analyzeJobDescription, generateInterviewQuestions, evaluateAnswer, generateFinalReport } from './utils/openRouterAPI';
import { speechService } from './utils/speechService';
import './index.css';

function App() {
  // State management
  const [inputData, setInputData] = useState(null); // Changed from resumeData
  const [interviewConfig, setInterviewConfig] = useState(null);
  const [interviewState, setInterviewState] = useState('setup'); // setup, analyzing, ready, interviewing, completed
  const [resumeAnalysis, setResumeAnalysis] = useState('');
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [transcript, setTranscript] = useState([]);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [finalReport, setFinalReport] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const [error, setError] = useState('');

  // Handle data input (resume or job description)
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
      
      // Analyze based on input mode
      if (inputData.mode === 'resume') {
        analysisResult = await analyzeResume(inputData.text, config.aiModel);
      } else {
        analysisResult = await analyzeJobDescription(inputData.text, config.aiModel);
      }
      
      if (!analysisResult.success) {
        throw new Error(analysisResult.error || 'Failed to analyze input');
      }

      setResumeAnalysis(analysisResult.analysis);

      // Generate questions
      const questionsResult = await generateInterviewQuestions(
        analysisResult.analysis,
        config.interviewType,
        config.aiModel
      );

      if (!questionsResult.success || questionsResult.questions.length === 0) {
        throw new Error('Failed to generate interview questions');
      }

      setQuestions(questionsResult.questions);
      setInterviewState('ready');

      // Wait a moment then start interviewing
      setTimeout(() => {
        startInterviewing(config, questionsResult.questions[0]);
      }, 1000);

    } catch (err) {
      console.error('Interview start error:', err);
      setError(err.message);
      setInterviewState('setup');
    }
  }, [inputData]);

  // Start interviewing
  const startInterviewing = useCallback(async (config, firstQuestion) => {
    setInterviewState('interviewing');

    // Add greeting to transcript
    const greeting = `Hello! I'm your AI interviewer. I've reviewed your resume and prepared ${questions.length} questions for you. Let's begin with the first question.`;
    
    addToTranscript('interviewer', greeting);

    if (config.enableVoice) {
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
  }, [questions.length]);

  // Add to transcript
  const addToTranscript = useCallback((speaker, text, feedback = null) => {
    setTranscript(prev => [
      ...prev,
      {
        speaker,
        text,
        feedback,
        timestamp: Date.now()
      }
    ]);
  }, []);

  // Handle answer completion (receives answer text directly from VideoInterview)
  const handleAnswerComplete = useCallback(async (answerText) => {
    if (!interviewConfig || !answerText?.trim()) return;

    // Add answer to transcript
    addToTranscript('candidate', answerText);

    // Optional: Evaluate answer
    const currentQuestion = questions[currentQuestionIndex];
    
    try {
      const evaluation = await evaluateAnswer(
        currentQuestion,
        answerText,
        resumeAnalysis,
        interviewConfig.aiModel
      );

      if (evaluation.success && evaluation.feedback) {
        // Update the last transcript entry with feedback
        setTranscript(prev => {
          const updated = [...prev];
          updated[updated.length - 1].feedback = evaluation.feedback;
          return updated;
        });
      }
    } catch (err) {
      console.error('Evaluation error:', err);
    }

    // Move to next question
    const nextIndex = currentQuestionIndex + 1;
    
    if (nextIndex < questions.length) {
      setCurrentQuestionIndex(nextIndex);
      const nextQuestion = questions[nextIndex];
      
      addToTranscript('interviewer', nextQuestion);

      if (interviewConfig.enableVoice) {
        setIsAISpeaking(true);
        try {
          await speechService.speak(nextQuestion);
        } catch (err) {
          console.error('Speech error:', err);
        }
        setIsAISpeaking(false);
      }
    } else {
      // Interview complete
      await completeInterview();
    }
  }, [interviewConfig, questions, currentQuestionIndex, resumeAnalysis, addToTranscript]);

  // Complete interview
  const completeInterview = useCallback(async () => {
    setInterviewState('completed');

    const closingMessage = "Thank you for completing the interview! I'm generating your evaluation report now.";
    addToTranscript('interviewer', closingMessage);

    if (interviewConfig.enableVoice) {
      try {
        await speechService.speak(closingMessage);
      } catch (err) {
        console.error('Speech error:', err);
      }
    }

    // Generate final report
    try {
      const transcriptText = transcript
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
      } else {
        throw new Error(reportResult.error);
      }
    } catch (err) {
      console.error('Report generation error:', err);
      setError('Failed to generate final report: ' + err.message);
    }
  }, [interviewConfig, transcript, resumeAnalysis, addToTranscript]);

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
    setFinalReport(null);
    setShowReport(false);
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
                {questions.length} questions generated. Starting interview...
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
            gridTemplateColumns: '1.5fr 1fr',
            gap: 'var(--space-lg)'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
              <VideoInterview
                isActive={true}
                currentQuestion={questions[currentQuestionIndex]}
                onAnswerComplete={handleAnswerComplete}
                isAISpeaking={isAISpeaking}
                onVideoReady={() => {}}
                autoStartListening={true}
              />
              
              {interviewState === 'completed' && (
                <div className="card text-center">
                  <h3 className="mb-md">🎉 Interview Completed!</h3>
                  <p className="text-secondary mb-md">
                    Your evaluation report is ready
                  </p>
                  <div className="flex gap-sm justify-center">
                    <button className="btn btn-primary" onClick={() => setShowReport(true)}>
                      📊 View Report
                    </button>
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
                    <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
                    <span className="text-secondary">
                      {Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}%
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
                      width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`,
                      height: '100%',
                      background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
                      transition: 'width 0.5s ease'
                    }} />
                  </div>
                </div>

                {isListening && (
                  <div className="status-indicator active">
                    <div className="status-dot"></div>
                    <span>Listening to your answer...</span>
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
              <div className="logo-icon">🎯</div>
              <div className="logo-text">
                <h1>AI Interviewer</h1>
                <p>Resume-Based Live Interview Platform</p>
              </div>
            </div>

            <div className="header-actions">
              {interviewState !== 'setup' && (
                <>
                  <div className="status-indicator" style={{ background: 'var(--color-bg-tertiary)' }}>
                    <span>
                      {interviewState === 'analyzing' && '🔍 Analyzing'}
                      {interviewState === 'ready' && '⏳ Preparing'}
                      {interviewState === 'interviewing' && '🎤 Live Interview'}
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
    </div>
  );
}

export default App;
