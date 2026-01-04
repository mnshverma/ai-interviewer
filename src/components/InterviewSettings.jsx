import { useState } from 'react';

const InterviewSettings = ({ onStartInterview, hasData }) => {
  const [interviewType, setInterviewType] = useState('technical');
  const [aiModel, setAiModel] = useState('meta-llama/llama-3.3-70b-instruct:free');
  const [enableVoice, setEnableVoice] = useState(true);

  const handleStart = () => {
    if (!hasData) {
      alert('⚠️ Please provide resume or job description first');
      return;
    }

    onStartInterview({
      interviewType,
      aiModel,
      enableVoice
    });
  };

  return (
    <div className="card fade-in">
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <h2 style={{ 
          fontSize: 'var(--font-size-2xl)', 
          marginBottom: 'var(--space-sm)',
          background: 'linear-gradient(135deg, var(--gradient-ocean-start), var(--gradient-ocean-end))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: '800'
        }}>
          ⚙️ Interview Settings
        </h2>
        <p className="text-secondary" style={{ fontSize: 'var(--font-size-sm)' }}>
          Configure your AI-powered interview experience
        </p>
      </div>

      {/* Interview Type */}
      <div className="input-group">
        <label htmlFor="interview-type">
          <span style={{ fontSize: 'var(--font-size-lg)' }}>🎯</span> Interview Type
        </label>
        <select
          id="interview-type"
          className="input"
          value={interviewType}
          onChange={(e) => setInterviewType(e.target.value)}
          style={{
            background: 'linear-gradient(135deg, rgba(56, 239, 125, 0.05), rgba(17, 153, 142, 0.05))',
            cursor: 'pointer'
          }}
        >
          <option value="technical">💻 Technical Interview</option>
          <option value="behavioral">🧠 Behavioral Interview</option>
          <option value="mixed">🔄 Mixed (Technical + Behavioral)</option>
          <option value="leadership">👔 Leadership Interview</option>
        </select>
      </div>

      {/* AI Model */}
      <div className="input-group">
        <label htmlFor="ai-model">
          <span style={{ fontSize: 'var(--font-size-lg)' }}>🤖</span> AI Model (100% Free)
          <a
            href="https://openrouter.ai/models?max_price=0"
            target="_blank"
            rel="noopener noreferrer"
            style={{ 
              marginLeft: 'var(--space-sm)', 
              color: 'var(--color-primary)',
              fontSize: 'var(--font-size-xs)',
              textDecoration: 'none',
              padding: 'var(--space-xs) var(--space-sm)',
              background: 'rgba(56, 239, 125, 0.1)',
              borderRadius: 'var(--radius-md)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => e.target.style.background = 'rgba(56, 239, 125, 0.2)'}
            onMouseLeave={(e) => e.target.style.background = 'rgba(56, 239, 125, 0.1)'}
          >
            🔍 View All
          </a>
        </label>
        <select
          id="ai-model"
          className="input"
          value={aiModel}
          onChange={(e) => setAiModel(e.target.value)}
          style={{
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05))',
            cursor: 'pointer'
          }}
        >
          <option value="meta-llama/llama-3.3-70b-instruct:free">⭐ Meta LLaMA 3.3 70B (Recommended)</option>
          <option value="nvidia/llama-3.1-nemotron-70b-instruct:free">💪 NVIDIA Nemotron 70B (Powerful)</option>
          <option value="liquid/lfm-40b:free">⚡ Liquid LFM 40B (Fast)</option>
          <option value="qwen/qwen-2.5-7b-instruct:free">🎯 Qwen 2.5 7B (Efficient)</option>
          <option value="google/gemma-2-9b-it:free">🔷 Google Gemma 2 9B</option>
          <option value="microsoft/phi-3-medium-128k-instruct:free">📘 Microsoft Phi 3 Medium</option>
          <option value="microsoft/phi-3-mini-128k-instruct:free">🚀 Microsoft Phi 3 Mini</option>
        </select>
        <small className="text-tertiary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
          <span style={{ fontSize: 'var(--font-size-lg)' }}>✅</span>
          All models are completely free with NO credits required
        </small>
      </div>

      {/* Voice Toggle */}
      <div className="input-group">
        <div style={{
          background: 'linear-gradient(135deg, rgba(56, 239, 125, 0.05), rgba(17, 153, 142, 0.05))',
          padding: 'var(--space-md)',
          borderRadius: 'var(--radius-lg)',
          border: '2px solid rgba(56, 239, 125, 0.2)',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onClick={() => setEnableVoice(!enableVoice)}
        style={{
          background: enableVoice 
            ? 'linear-gradient(135deg, rgba(56, 239, 125, 0.15), rgba(17, 153, 142, 0.15))'
            : 'linear-gradient(135deg, rgba(56, 239, 125, 0.05), rgba(17, 153, 142, 0.05))',
          padding: 'var(--space-md)',
          borderRadius: 'var(--radius-lg)',
          border: enableVoice 
            ? '2px solid rgba(56, 239, 125, 0.4)'
            : '2px solid rgba(56, 239, 125, 0.2)',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}>
          <label className="flex items-center gap-sm" style={{ cursor: 'pointer', margin: 0 }}>
            <input
              type="checkbox"
              checked={enableVoice}
              onChange={(e) => setEnableVoice(e.target.checked)}
              style={{ 
                width: '24px', 
                height: '24px', 
                cursor: 'pointer',
                accentColor: 'var(--color-primary)'
              }}
            />
            <div style={{ flex: 1 }}>
              <div style={{ 
                fontSize: 'var(--font-size-base)', 
                fontWeight: '700',
                marginBottom: 'var(--space-xs)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-xs)'
              }}>
                <span style={{ fontSize: 'var(--font-size-xl)' }}>🔊</span>
                Enable AI Voice (Text-to-Speech)
              </div>
              <small className="text-tertiary" style={{ fontSize: 'var(--font-size-xs)' }}>
                AI will speak questions using browser's voice synthesis
              </small>
            </div>
          </label>
        </div>
      </div>

      {/* Auto-Recording Notice */}
      <div style={{
        padding: 'var(--space-lg)',
        background: 'linear-gradient(135deg, rgba(56, 239, 125, 0.1), rgba(17, 153, 142, 0.1))',
        border: '2px solid rgba(56, 239, 125, 0.3)',
        borderRadius: 'var(--radius-xl)',
        marginBottom: 'var(--space-lg)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          right: 0,
          fontSize: '80px',
          opacity: '0.1',
          transform: 'rotate(15deg)'
        }}>
          ✨
        </div>
        <h4 style={{ 
          color: 'var(--color-accent)', 
          marginBottom: 'var(--space-sm)', 
          fontSize: 'var(--font-size-lg)',
          fontWeight: '800',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <span style={{ fontSize: 'var(--font-size-2xl)' }}>🎤</span>
          Auto-Recording Enabled
        </h4>
        <p className="text-secondary" style={{ fontSize: 'var(--font-size-sm)', margin: 0, lineHeight: '1.6' }}>
          Your answers will be <strong>automatically captured</strong> via speech-to-text. 
          Just speak naturally after each question and pause for 3 seconds when done!
        </p>
      </div>

      {/* Start Button */}
      <button
        className="btn btn-primary"
        style={{ 
          width: '100%', 
          padding: 'var(--space-lg)',
          fontSize: 'var(--font-size-lg)',
          fontWeight: '800',
          letterSpacing: '0.05em',
          textTransform: 'uppercase'
        }}
        onClick={handleStart}
        disabled={!hasData}
      >
        <span style={{ fontSize: 'var(--font-size-2xl)' }}>🚀</span>
        Start Interview
      </button>

      {/* Warning Message */}
      {!hasData && (
        <div style={{
          marginTop: 'var(--space-md)',
          padding: 'var(--space-md)',
          background: 'linear-gradient(135deg, rgba(255, 210, 0, 0.1), rgba(247, 151, 30, 0.1))',
          border: '2px solid rgba(255, 210, 0, 0.3)',
          borderRadius: 'var(--radius-lg)',
          textAlign: 'center'
        }}>
          <p style={{ 
            color: 'var(--color-warning)', 
            fontSize: 'var(--font-size-sm)',
            fontWeight: '600',
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--space-sm)'
          }}>
            <span style={{ fontSize: 'var(--font-size-xl)' }}>⚠️</span>
            Please provide resume or job description first
          </p>
        </div>
      )}

      {/* Quick Tips */}
      <div style={{
        marginTop: 'var(--space-lg)',
        padding: 'var(--space-md)',
        background: 'rgba(102, 126, 234, 0.05)',
        border: '1px solid rgba(102, 126, 234, 0.2)',
        borderRadius: 'var(--radius-lg)'
      }}>
        <h5 style={{ 
          color: 'var(--color-secondary)', 
          fontSize: 'var(--font-size-sm)',
          fontWeight: '700',
          marginBottom: 'var(--space-xs)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          💡 Quick Tips
        </h5>
        <ul style={{ 
          fontSize: 'var(--font-size-xs)', 
          color: 'var(--color-text-secondary)',
          margin: 0,
          paddingLeft: 'var(--space-lg)',
          lineHeight: '1.8'
        }}>
          <li>Speak clearly and at a normal pace</li>
          <li>Pause for 3 seconds to auto-submit answers</li>
          <li>Keep your environment quiet for best results</li>
        </ul>
      </div>
    </div>
  );
};

export default InterviewSettings;
