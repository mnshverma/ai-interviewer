import { useState, useEffect, useRef } from 'react';

const VideoInterview = ({ 
  isActive, 
  currentQuestion, 
  onAnswerComplete,
  isAISpeaking,
  onVideoReady,
  autoStartListening
}) => {
  const [stream, setStream] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [error, setError] = useState('');
  const videoRef = useRef(null);
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);

  useEffect(() => {
    if (isActive) {
      startCamera();
      initializeSpeechRecognition();
    } else {
      stopCamera();
    }

    return () => {
      stopCamera();
      stopListening();
    };
  }, [isActive]);

  // Auto-start listening after AI finishes speaking
  useEffect(() => {
    if (autoStartListening && !isAISpeaking && !isListening) {
      setTimeout(() => {
        startListening();
      }, 500);
    }
  }, [autoStartListening, isAISpeaking]);

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = currentAnswer;

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          }
        }

        setCurrentAnswer(finalTranscript);

        // Reset silence timer - auto-submit after 3 seconds of silence
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = setTimeout(() => {
          if (finalTranscript.trim()) {
            submitAnswer(finalTranscript.trim());
          }
        }, 3000);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech' && currentAnswer.trim()) {
          submitAnswer(currentAnswer.trim());
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: true
      });

      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }

      onVideoReady?.(true);
      setError('');
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
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error('Failed to start recognition:', err);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        // Already stopped
      }
      setIsListening(false);
      clearTimeout(silenceTimerRef.current);
    }
  };

  const submitAnswer = (answer) => {
    stopListening();
    setCurrentAnswer('');
    onAnswerComplete?.(answer);
  };

  return (
    <div className="video-container fade-in">
      {error ? (
        <div className="flex items-center justify-center" style={{ height: '100%', padding: 'var(--space-xl)' }}>
          <div className="text-center">
            <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--space-md)' }}>
              📹
            </div>
            <h3 className="mb-md">Camera & Microphone Required</h3>
            <p className="text-secondary">{error}</p>
            <p className="text-tertiary mt-md" style={{ fontSize: 'var(--font-size-sm)' }}>
              Please enable camera and microphone permissions in your browser settings
            </p>
          </div>
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            className="video-element"
            autoPlay
            playsInline
            muted
          />

          <div className="video-overlay">
            {/* Status Indicators */}
            <div className="flex justify-between items-center mb-md">
              <div className="flex gap-sm">
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
              </div>
            )}

            {/* Current Answer Being Captured */}
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
          </div>
        </>
      )}
    </div>
  );
};

export default VideoInterview;
