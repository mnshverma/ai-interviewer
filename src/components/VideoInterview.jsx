import { useState, useEffect, useRef, useCallback } from 'react';

const VideoInterview = ({ 
  isActive, 
  currentQuestion, 
  onAnswerComplete,
  onSkipQuestion,
  isAISpeaking,
  onVideoReady,
  autoStartListening,
  practiceMode = false,
  timeLimit = 0,
  onRecordingReady
}) => {
  const [stream, setStream] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [error, setError] = useState('');
  const [manualInput, setManualInput] = useState('');
  const [speechSupported, setSpeechSupported] = useState(true);
  const [timeRemaining, setTimeRemaining] = useState(timeLimit);
  const [isRecording, setIsRecording] = useState(false);
  const videoRef = useRef(null);
  
  // Connect stream to video element when ready
  useEffect(() => {
    if (videoRef.current && stream && videoRef.current.srcObject !== stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const currentAnswerRef = useRef('');
  const timerIntervalRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  useEffect(() => {
    currentAnswerRef.current = currentAnswer;
  }, [currentAnswer]);

  useEffect(() => {
    if (isActive && !practiceMode) {
      startCamera();
      initializeSpeechRecognition();
    } else if (isActive && practiceMode) {
      setSpeechSupported(false);
    }

    return () => {
      stopCamera();
      stopListening();
      stopTimer();
      stopRecording();
      if (recognitionRef.current) {
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;
        recognitionRef.current = null;
      }
    };
  }, [isActive, practiceMode]);

  // Auto-start listening after AI finishes speaking (voice mode only)
  useEffect(() => {
    if (autoStartListening && !isAISpeaking && !isListening && speechSupported && !practiceMode) {
      const timer = setTimeout(() => {
        startListening();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [autoStartListening, isAISpeaking, speechSupported, practiceMode]);

  // Reset timer when question changes
  useEffect(() => {
    if (timeLimit > 0 && currentQuestion) {
      setTimeRemaining(timeLimit);
      startTimer();
    }
    return () => stopTimer();
  }, [currentQuestion, timeLimit]);

  // Timer logic
  const startTimer = () => {
    stopTimer();
    if (timeLimit <= 0) return;
    timerIntervalRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          // Time's up — auto-submit whatever we have
          clearInterval(timerIntervalRef.current);
          const answer = currentAnswerRef.current.trim() || manualInput?.trim() || '(No answer — time expired)';
          submitAnswer(answer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  };

  // Video Recording
  const startRecording = (mediaStream) => {
    try {
      const options = { mimeType: 'video/webm;codecs=vp9,opus' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'video/webm';
      }
      const recorder = new MediaRecorder(mediaStream, options);
      recordedChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) recordedChunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        onRecordingReady?.(blob);
      };

      recorder.start(1000); // Collect data every second
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (e) { /* ignore */ }
    }
    setIsRecording(false);
  };

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) { /* ignore */ }
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;
      }

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = currentAnswerRef.current;
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          }
        }
        setCurrentAnswer(finalTranscript);
        currentAnswerRef.current = finalTranscript;

        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = setTimeout(() => {
          if (finalTranscript.trim()) submitAnswer(finalTranscript.trim());
        }, 3000);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech' && currentAnswerRef.current.trim()) {
          submitAnswer(currentAnswerRef.current.trim());
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      setSpeechSupported(true);
    } else {
      setSpeechSupported(false);
    }
  };

  const startCamera = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Webcam API is not supported in this browser context (requires localhost or HTTPS).');
      }
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true, // More compatible fallback than strict resolution constraints
        audio: true
      });
      setStream(mediaStream);
      if (videoRef.current) videoRef.current.srcObject = mediaStream;
      onVideoReady?.(true);
      setError('');
      // Auto-start video recording
      startRecording(mediaStream);
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Unable to access camera and microphone. Please grant permissions.');
      onVideoReady?.(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setCurrentAnswer('');
      currentAnswerRef.current = '';
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) { console.error('Failed to start recognition:', err); }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (err) { /* ignore */ }
      setIsListening(false);
      clearTimeout(silenceTimerRef.current);
    }
  };

  const submitAnswer = useCallback((answer) => {
    stopListening();
    stopTimer();
    setCurrentAnswer('');
    currentAnswerRef.current = '';
    setManualInput('');
    onAnswerComplete?.(answer);
  }, [onAnswerComplete]);

  const handleManualSubmit = () => {
    if (manualInput.trim()) submitAnswer(manualInput.trim());
  };

  const handleManualKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleManualSubmit();
    }
  };

  const handleReplay = () => {
    if (currentQuestion && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(currentQuestion);
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSkip = () => {
    stopListening();
    stopTimer();
    setCurrentAnswer('');
    currentAnswerRef.current = '';
    setManualInput('');
    onSkipQuestion?.();
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    if (timeRemaining <= 10) return '#f5576c';
    if (timeRemaining <= 30) return '#ffd200';
    return '#38ef7d';
  };

  // Practice Mode UI (text-only)
  if (practiceMode) {
    return (
      <div className="card fade-in" style={{ position: 'relative' }}>
        {/* Timer */}
        {timeLimit > 0 && (
          <div style={{
            position: 'absolute',
            top: 'var(--space-md)',
            right: 'var(--space-md)',
            padding: 'var(--space-sm) var(--space-md)',
            background: `${getTimerColor()}15`,
            border: `2px solid ${getTimerColor()}40`,
            borderRadius: 'var(--radius-full)',
            fontWeight: 700,
            fontSize: 'var(--font-size-lg)',
            color: getTimerColor(),
            fontVariantNumeric: 'tabular-nums',
            animation: timeRemaining <= 10 ? 'recordingPulse 1s ease-in-out infinite' : 'none'
          }}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
        )}

        <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)', textAlign: 'center' }}>🎮</div>
        <h3 className="text-center mb-lg" style={{ color: 'var(--color-warning)' }}>Practice Mode</h3>

        {/* Question */}
        {currentQuestion && (
          <div style={{
            padding: 'var(--space-lg)',
            background: 'rgba(56, 239, 125, 0.05)',
            border: '2px solid rgba(56, 239, 125, 0.3)',
            borderRadius: 'var(--radius-lg)',
            marginBottom: 'var(--space-lg)'
          }}>
            <h4 style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-sm)' }}>❓ Question:</h4>
            <p style={{ fontSize: 'var(--font-size-lg)', lineHeight: 1.7 }}>{currentQuestion}</p>
          </div>
        )}

        {/* Answer Input */}
        <div style={{ marginBottom: 'var(--space-md)' }}>
          <textarea
            className="input"
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            onKeyDown={handleManualKeyDown}
            placeholder="Type your answer here... (Press Enter to submit, Shift+Enter for new line)"
            rows="5"
            style={{ fontSize: 'var(--font-size-base)', resize: 'vertical' }}
          />
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: 'var(--space-sm)', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={handleManualSubmit}
            disabled={!manualInput.trim()}
            style={{ flex: 1 }}
          >
            ✅ Submit Answer
          </button>
          <button className="btn btn-secondary" onClick={handleSkip} style={{ minWidth: 'auto' }}>
            ⏭️ Skip
          </button>
          <button className="btn btn-secondary" onClick={handleReplay} style={{ minWidth: 'auto' }}>
            🔁 Replay
          </button>
        </div>
      </div>
    );
  }

  // Full Video Interview UI
  return (
    <div className="video-container fade-in">
      {error ? (
        <div className="flex items-center justify-center" style={{ height: '100%', padding: 'var(--space-xl)' }}>
          <div className="text-center">
            <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--space-md)' }}>📹</div>
            <h3 className="mb-md">Camera & Microphone Required</h3>
            <p className="text-secondary">{error}</p>
            <p className="text-tertiary mt-md" style={{ fontSize: 'var(--font-size-sm)' }}>
              Please enable camera and microphone permissions in your browser settings
            </p>
          </div>
        </div>
      ) : (
        <>
          <video ref={videoRef} className="video-element" autoPlay playsInline muted />

          <div className="video-overlay">
            {/* Top Bar: Status + Timer */}
            <div className="flex justify-between items-center mb-md">
              <div className="flex gap-sm">
                {isRecording && (
                  <div className="status-indicator recording">
                    <div className="status-dot"></div>
                    <span>⏺ REC</span>
                  </div>
                )}
                {isAISpeaking && (
                  <div className="status-indicator active">
                    <div className="status-dot"></div>
                    <span>🤖 AI Speaking...</span>
                  </div>
                )}
                {isListening && (
                  <div className="status-indicator recording">
                    <div className="status-dot"></div>
                    <span>🎤 Listening...</span>
                  </div>
                )}
              </div>

              {/* Timer */}
              {timeLimit > 0 && (
                <div style={{
                  padding: 'var(--space-sm) var(--space-md)',
                  background: `${getTimerColor()}20`,
                  border: `2px solid ${getTimerColor()}50`,
                  borderRadius: 'var(--radius-full)',
                  fontWeight: 700,
                  fontSize: 'var(--font-size-lg)',
                  color: getTimerColor(),
                  fontVariantNumeric: 'tabular-nums',
                  animation: timeRemaining <= 10 ? 'recordingPulse 1s ease-in-out infinite' : 'none'
                }}>
                  ⏱️ {formatTime(timeRemaining)}
                </div>
              )}
            </div>

            {/* Current Question */}
            {currentQuestion && (
              <div style={{
                background: 'hsla(220, 18%, 15%, 0.95)',
                backdropFilter: 'blur(20px)',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                border: '2px solid var(--color-primary)',
                marginBottom: 'var(--space-md)'
              }}>
                <h4 style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-sm)' }}>
                  ❓ Question:
                </h4>
                <p style={{ fontSize: 'var(--font-size-lg)' }}>{currentQuestion}</p>
                {/* Skip & Replay */}
                <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 'var(--space-sm)' }}>
                  <button
                    className="btn btn-secondary"
                    onClick={handleSkip}
                    style={{ padding: '4px 12px', fontSize: 'var(--font-size-xs)', minWidth: 'auto' }}
                  >
                    ⏭️ Skip
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={handleReplay}
                    style={{ padding: '4px 12px', fontSize: 'var(--font-size-xs)', minWidth: 'auto' }}
                  >
                    🔁 Replay
                  </button>
                </div>
              </div>
            )}

            {/* Current Answer */}
            {isListening && currentAnswer && (
              <div style={{
                background: 'hsla(160, 70%, 50%, 0.1)',
                backdropFilter: 'blur(20px)',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                border: '2px solid var(--color-accent)',
              }}>
                <h4 style={{ color: 'var(--color-accent)', marginBottom: 'var(--space-sm)' }}>
                  💬 Your Answer:
                </h4>
                <p style={{ fontSize: 'var(--font-size-base)' }}>{currentAnswer}</p>
                <small className="text-tertiary mt-sm" style={{ display: 'block' }}>
                  ⏱️ Auto-submitting in 3 seconds after you stop speaking...
                </small>
              </div>
            )}

            {/* Manual Input Fallback */}
            {!speechSupported && currentQuestion && (
              <div style={{
                background: 'hsla(220, 18%, 15%, 0.95)',
                backdropFilter: 'blur(20px)',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                border: '2px solid var(--color-secondary)',
                marginTop: 'var(--space-md)'
              }}>
                <textarea
                  className="input"
                  value={manualInput}
                  onChange={(e) => setManualInput(e.target.value)}
                  onKeyDown={handleManualKeyDown}
                  placeholder="Type your answer... (Enter to submit)"
                  rows="3"
                  style={{ fontSize: 'var(--font-size-sm)', marginBottom: 'var(--space-sm)' }}
                />
                <button className="btn btn-primary" onClick={handleManualSubmit}
                  disabled={!manualInput.trim()} style={{ width: '100%' }}>
                  ✅ Submit Answer
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default VideoInterview;
