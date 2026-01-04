import { useState, useEffect, useRef } from 'react';

const VideoInterview = ({ 
  isActive, 
  currentQuestion, 
  onAnswerComplete,
  isAISpeaking,
  onVideoReady 
}) => {
  const [stream, setStream] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  useEffect(() => {
    if (isActive) {
      startCamera();
    } else {
      stopCamera();
    }

    return () => {
      stopCamera();
    };
  }, [isActive]);

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

      // Setup media recorder
      const mediaRecorder = new MediaRecorder(mediaStream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      onVideoReady?.(true);
      setError('');
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Unable to access camera. Please grant camera permissions.');
      onVideoReady?.(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const startRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
      recordedChunksRef.current = [];
      mediaRecorderRef.current.start(100);
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    return new Promise((resolve) => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.onstop = () => {
          const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
          resolve(blob);
          setIsRecording(false);
        };
        mediaRecorderRef.current.stop();
      } else {
        resolve(null);
      }
    });
  };

  const downloadRecording = async () => {
    const blob = await stopRecording();
    if (blob) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `interview_${Date.now()}.webm`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="video-container fade-in">
      {error ? (
        <div className="flex items-center justify-center" style={{ height: '100%', padding: 'var(--space-xl)' }}>
          <div className="text-center">
            <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--space-md)' }}>
              📹
            </div>
            <h3 className="mb-md">Camera Access Required</h3>
            <p className="text-secondary">{error}</p>
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
            <div className="flex justify-between items-center">
              <div>
                {isRecording && (
                  <div className="status-indicator recording">
                    <div className="status-dot"></div>
                    <span>Recording</span>
                  </div>
                )}
                {isAISpeaking && (
                  <div className="status-indicator active">
                    <div className="status-dot"></div>
                    <span>AI Speaking...</span>
                  </div>
                )}
              </div>

              <div className="flex gap-sm">
                {!isRecording ? (
                  <button
                    className="btn btn-danger"
                    onClick={startRecording}
                    disabled={!stream || isAISpeaking}
                  >
                    ⏺ Start Recording Answer
                  </button>
                ) : (
                  <button
                    className="btn btn-success"
                    onClick={async () => {
                      const recording = await stopRecording();
                      onAnswerComplete?.(recording);
                    }}
                  >
                    ⏹ Stop & Submit Answer
                  </button>
                )}
              </div>
            </div>

            {currentQuestion && (
              <div className="mt-md" style={{
                background: 'hsla(220, 18%, 15%, 0.9)',
                backdropFilter: 'blur(20px)',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)'
              }}>
                <h4 className="mb-sm" style={{ color: 'var(--color-primary)' }}>
                  Current Question:
                </h4>
                <p>{currentQuestion}</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default VideoInterview;
