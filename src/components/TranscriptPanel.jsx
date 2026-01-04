import { useEffect, useRef } from 'react';

const TranscriptPanel = ({ transcript, isActive }) => {
  const transcriptEndRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new transcript added
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  if (!isActive || transcript.length === 0) {
    return (
      <div className="card fade-in">
        <h3 className="mb-md">📝 Interview Transcript</h3>
        <div className="text-center text-secondary" style={{ padding: 'var(--space-xl)' }}>
          <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--space-md)' }}>
            💬
          </div>
          <p>Interview transcript will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card fade-in">
      <h3 className="mb-md">📝 Interview Transcript</h3>
      
      <div className="transcript-container">
        {transcript.map((entry, index) => (
          <div
            key={index}
            className={`transcript-item ${entry.speaker}`}
          >
            <div className="flex justify-between items-start mb-xs">
              <strong style={{ 
                color: entry.speaker === 'interviewer' ? 'var(--color-primary)' : 'var(--color-accent)'
              }}>
                {entry.speaker === 'interviewer' ? '🤖 AI Interviewer' : '👤 Candidate'}
              </strong>
              <span className="text-tertiary" style={{ fontSize: 'var(--font-size-xs)' }}>
                {new Date(entry.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <p style={{ whiteSpace: 'pre-wrap' }}>{entry.text}</p>
            {entry.feedback && (
              <div className="mt-sm" style={{
                padding: 'var(--space-sm)',
                background: 'hsla(220, 90%, 56%, 0.1)',
                borderLeft: '2px solid var(--color-primary)',
                borderRadius: 'var(--radius-sm)',
                fontSize: 'var(--font-size-sm)'
              }}>
                <strong>💡 Feedback:</strong> {entry.feedback}
              </div>
            )}
          </div>
        ))}
        <div ref={transcriptEndRef} />
      </div>

      <div className="mt-md flex gap-sm">
        <button
          className="btn btn-secondary"
          onClick={() => {
            const text = transcript.map(t => 
              `[${new Date(t.timestamp).toLocaleTimeString()}] ${t.speaker.toUpperCase()}: ${t.text}`
            ).join('\n\n');
            
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `interview_transcript_${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          💾 Download Transcript
        </button>
      </div>
    </div>
  );
};

export default TranscriptPanel;
