import { useState } from 'react';

const InterviewSettings = ({ onStartInterview, hasData }) => {
  const [interviewType, setInterviewType] = useState('technical');
  const [enableVoice, setEnableVoice] = useState(true);
  const [enableRecording, setEnableRecording] = useState(true);

  const handleStart = () => {
    if (!hasData) {
      alert('Please provide resume or job description first');
      return;
    }

    onStartInterview({
      interviewType,
      enableVoice,
      enableRecording
    });
  };

  return (
    <div className="card fade-in">
      <h2 className="mb-md">⚙️ Interview Settings</h2>

      <div className="input-group">
        <label htmlFor="interview-type">Interview Type</label>
        <select
          id="interview-type"
          className="input"
          value={interviewType}
          onChange={(e) => setInterviewType(e.target.value)}
        >
          <option value="technical">Technical Interview</option>
          <option value="behavioral">Behavioral Interview</option>
          <option value="mixed">Mixed (Technical + Behavioral)</option>
          <option value="leadership">Leadership Interview</option>
        </select>
      </div>

      <div className="input-group">
        <label className="flex items-center gap-sm" style={{ cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={enableVoice}
            onChange={(e) => setEnableVoice(e.target.checked)}
            style={{ width: '20px', height: '20px', cursor: 'pointer' }}
          />
          <span>Enable AI Voice (Text-to-Speech)</span>
        </label>
        <small className="text-tertiary">
          AI will speak questions using browser's voice synthesis
        </small>
      </div>

      <div className="input-group">
        <label className="flex items-center gap-sm" style={{ cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={enableRecording}
            onChange={(e) => setEnableRecording(e.target.checked)}
            style={{ width: '20px', height: '20px', cursor: 'pointer' }}
          />
          <span>Enable Interview Recording</span>
        </label>
        <small className="text-tertiary">
          Record video during the interview for later review
        </small>
      </div>

      <button
        className="btn btn-primary"
        style={{ width: '100%', marginTop: 'var(--space-md)' }}
        onClick={handleStart}
        disabled={!hasData}
      >
        🚀 Start Interview
      </button>

      {!hasData && (
        <p className="text-warning mt-sm text-center" style={{ fontSize: 'var(--font-size-sm)' }}>
          ⚠️ Please provide resume or job description first
        </p>
      )}
    </div>
  );
};

export default InterviewSettings;
