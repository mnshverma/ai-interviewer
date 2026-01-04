import { useState } from 'react';

const InterviewSettings = ({ onStartInterview, hasData }) => {
  const [interviewType, setInterviewType] = useState('technical');
  const [aiModel, setAiModel] = useState('meta-llama/llama-3.3-70b-instruct:free');
  const [enableVoice, setEnableVoice] = useState(true);
  const [enableRecording, setEnableRecording] = useState(true);

  const handleStart = () => {
    if (!hasData) {
      alert('Please provide resume or job description first');
      return;
    }

    onStartInterview({
      interviewType,
      aiModel,
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
        <label htmlFor="ai-model">
          AI Model (100% Free)
          <a
            href="https://openrouter.ai/models?max_price=0"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginLeft: 'var(--space-xs)', color: 'var(--color-primary)', fontSize: 'var(--font-size-xs)' }}
          >
            (View All)
          </a>
        </label>
        <select
          id="ai-model"
          className="input"
          value={aiModel}
          onChange={(e) => setAiModel(e.target.value)}
        >
          <option value="meta-llama/llama-3.3-70b-instruct:free">Meta LLaMA 3.3 70B (Recommended)</option>
          <option value="nvidia/llama-3.1-nemotron-70b-instruct:free">NVIDIA Nemotron 70B (Powerful)</option>
          <option value="liquid/lfm-40b:free">Liquid LFM 40B (Fast)</option>
          <option value="qwen/qwen-2.5-7b-instruct:free">Qwen 2.5 7B (Efficient)</option>
          <option value="google/gemma-2-9b-it:free">Google Gemma 2 9B</option>
          <option value="microsoft/phi-3-medium-128k-instruct:free">Microsoft Phi 3 Medium</option>
          <option value="microsoft/phi-3-mini-128k-instruct:free">Microsoft Phi 3 Mini (Very Fast)</option>
        </select>
        <small className="text-tertiary">
          All models are completely free with NO credits required.
        </small>
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
