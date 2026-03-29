import { useState } from 'react';
import { useToast } from './Toast';

const InterviewSettings = ({ onStartInterview, hasData }) => {
  const [interviewType, setInterviewType] = useState('technical');
  const [aiModel, setAiModel] = useState('meta-llama/llama-3.3-70b-instruct:free');
  const [enableVoice, setEnableVoice] = useState(true);
  const [practiceMode, setPracticeMode] = useState(false);
  const [timeLimit, setTimeLimit] = useState(120); // seconds per question, 0 = unlimited
  const [difficulty, setDifficulty] = useState('medium');
  const toast = useToast();

  const handleStart = () => {
    if (!hasData) {
      toast.warning('Please provide resume or job description first');
      return;
    }

    onStartInterview({
      interviewType,
      aiModel,
      enableVoice: practiceMode ? false : enableVoice,
      practiceMode,
      timeLimit,
      difficulty
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

      {/* Practice Mode Toggle */}
      <div className="input-group">
        <div
          onClick={() => setPracticeMode(!practiceMode)}
          style={{
            background: practiceMode 
              ? 'linear-gradient(135deg, rgba(247, 151, 30, 0.15), rgba(255, 210, 0, 0.15))'
              : 'linear-gradient(135deg, rgba(247, 151, 30, 0.05), rgba(255, 210, 0, 0.05))',
            padding: 'var(--space-md)',
            borderRadius: 'var(--radius-lg)',
            border: practiceMode 
              ? '2px solid rgba(255, 210, 0, 0.4)'
              : '2px solid rgba(255, 210, 0, 0.15)',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          <label className="flex items-center gap-sm" style={{ cursor: 'pointer', margin: 0 }}>
            <input
              type="checkbox"
              checked={practiceMode}
              onChange={(e) => setPracticeMode(e.target.checked)}
              style={{ width: '24px', height: '24px', cursor: 'pointer', accentColor: 'var(--color-warning)' }}
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
                <span style={{ fontSize: 'var(--font-size-xl)' }}>🎮</span>
                Practice Mode (No Camera)
              </div>
              <small className="text-tertiary" style={{ fontSize: 'var(--font-size-xs)' }}>
                Text-only interview — type your answers instead of speaking
              </small>
            </div>
          </label>
        </div>
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
          style={{ cursor: 'pointer' }}
        >
          <option value="technical">💻 Technical Interview</option>
          <option value="behavioral">🧠 Behavioral Interview</option>
          <option value="mixed">🔄 Mixed (Technical + Behavioral)</option>
          <option value="leadership">👔 Leadership Interview</option>
        </select>
      </div>

      {/* Difficulty Level */}
      <div className="input-group">
        <label htmlFor="difficulty">
          <span style={{ fontSize: 'var(--font-size-lg)' }}>📶</span> Difficulty Level
        </label>
        <select
          id="difficulty"
          className="input"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          style={{ cursor: 'pointer' }}
        >
          <option value="easy">🟢 Easy — Foundational concepts</option>
          <option value="medium">🟡 Medium — Applied knowledge</option>
          <option value="hard">🔴 Hard — Deep technical, system design</option>
        </select>
      </div>

      {/* Time Limit */}
      <div className="input-group">
        <label htmlFor="time-limit">
          <span style={{ fontSize: 'var(--font-size-lg)' }}>⏱️</span> Time Per Question
        </label>
        <select
          id="time-limit"
          className="input"
          value={timeLimit}
          onChange={(e) => setTimeLimit(Number(e.target.value))}
          style={{ cursor: 'pointer' }}
        >
          <option value={60}>1 minute</option>
          <option value={120}>2 minutes (Recommended)</option>
          <option value={180}>3 minutes</option>
          <option value={300}>5 minutes</option>
          <option value={0}>♾️ Unlimited</option>
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
          style={{ cursor: 'pointer' }}
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

      {/* Voice Toggle (only if not practice mode) */}
      {!practiceMode && (
        <div className="input-group">
          <div
            onClick={() => setEnableVoice(!enableVoice)}
            style={{
              background: enableVoice 
                ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(14, 165, 233, 0.15))'
                : 'linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(14, 165, 233, 0.05))',
              padding: 'var(--space-md)',
              borderRadius: 'var(--radius-lg)',
              border: enableVoice 
                ? '2px solid rgba(59, 130, 246, 0.4)'
                : '2px solid rgba(59, 130, 246, 0.2)',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
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
      )}

      {/* Info Box */}
      <div style={{
        padding: 'var(--space-lg)',
        background: practiceMode
          ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1))'
          : 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(14, 165, 233, 0.1))',
        border: practiceMode
          ? '2px solid rgba(245, 158, 11, 0.3)'
          : '2px solid rgba(59, 130, 246, 0.3)',
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
          {practiceMode ? '⌨️' : '✨'}
        </div>
        <h4 style={{ 
          color: practiceMode ? 'var(--color-warning)' : 'var(--color-accent)', 
          marginBottom: 'var(--space-sm)', 
          fontSize: 'var(--font-size-lg)',
          fontWeight: '800',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <span style={{ fontSize: 'var(--font-size-2xl)' }}>{practiceMode ? '⌨️' : '🎤'}</span>
          {practiceMode ? 'Practice Mode' : 'Auto-Recording Enabled'}
        </h4>
        <p className="text-secondary" style={{ fontSize: 'var(--font-size-sm)', margin: 0, lineHeight: '1.6' }}>
          {practiceMode 
            ? <>No camera or microphone needed. <strong>Type your answers</strong> in the text box after each question.</>
            : <>Your answers will be <strong>automatically captured</strong> via speech-to-text. Just speak naturally after each question and pause for 3 seconds when done!</>
          }
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
        {practiceMode ? 'Start Practice' : 'Start Interview'}
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
          {practiceMode ? (
            <>
              <li>Read each question carefully before typing</li>
              <li>Structure your answers with STAR method</li>
              <li>Press Enter or click Submit to send your answer</li>
            </>
          ) : (
            <>
              <li>Speak clearly and at a normal pace</li>
              <li>Pause for 3 seconds to auto-submit answers</li>
              <li>Keep your environment quiet for best results</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
};

export default InterviewSettings;
