import { useState } from 'react';

const InterviewSettings = ({ onStartInterview, hasData }) => {
  const [interviewType, setInterviewType] = useState('technical');
  const [aiModel, setAiModel] = useState('google/gemini-2.0-flash-exp:free');
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
          AI Model (Free)
          <a
            href="https://openrouter.ai/models?order=newest&supported_parameters=tools&max_price=0"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginLeft: 'var(--space-xs)', color: 'var(--color-primary)', fontSize: 'var(--font-size-xs)' }}
          >
            (View All Free Models)
          </a>
        </label>
        <select
          id="ai-model"
          className="input"
          value={aiModel}
          onChange={(e) => setAiModel(e.target.value)}
        >
          <option value="google/gemini-2.0-flash-exp:free">Google Gemini 2.0 Flash (Fast & Smart)</option>
          <option value="nvidia/llama-3.1-nemotron-nano-8b-v1:free">NVIDIA Llama 3.1 Nemotron Nano</option>
          <option value="deepseek/deepseek-chat-v3-0324:free">DeepSeek Chat V3 (Powerful)</option>
          <option value="qwen/qwen2.5-vl-3b-instruct:free">Qwen 2.5 VL 3B</option>
          <option value="mistralai/mistral-small-3.1-24b-instruct:free">Mistral Small 3.1 24B</option>
          <option value="meta-llama/llama-4-scout:free">Meta LLaMA 4 Scout</option>
          <option value="openrouter/auto">Auto (Best Model Selected)</option>
        </select>
        <small className="text-tertiary">
          All models are 100% free. Choose based on your preference.
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
