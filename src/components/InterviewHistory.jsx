import { useState, useEffect } from 'react';

const STORAGE_KEY = 'ai_interviewer_history';

// Public API for saving sessions
export const saveInterviewSession = (session) => {
  try {
    const history = getInterviewHistory();
    history.unshift({
      ...session,
      id: Date.now() + Math.random().toString(36).slice(2),
      savedAt: new Date().toISOString()
    });
    // Keep max 20 sessions
    const trimmed = history.slice(0, 20);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    return true;
  } catch (err) {
    console.error('Failed to save interview session:', err);
    return false;
  }
};

export const getInterviewHistory = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

export const deleteSession = (id) => {
  try {
    const history = getInterviewHistory();
    const updated = history.filter(s => s.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch {
    return [];
  }
};

export const clearAllHistory = () => {
  localStorage.removeItem(STORAGE_KEY);
};

// Component
const InterviewHistory = ({ onLoadSession, onClose }) => {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);

  useEffect(() => {
    setSessions(getInterviewHistory());
  }, []);

  const handleDelete = (id) => {
    const updated = deleteSession(id);
    setSessions(updated);
    setConfirmDelete(null);
    if (selectedSession?.id === id) setSelectedSession(null);
  };

  const handleClearAll = () => {
    clearAllHistory();
    setSessions([]);
    setSelectedSession(null);
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
      ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const getScoreColor = (score) => {
    if (score >= 7) return '#38ef7d';
    if (score >= 4) return '#ffd200';
    return '#f5576c';
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(10px)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      padding: 'var(--space-xl)',
      overflowY: 'auto',
      animation: 'fadeIn 0.3s ease'
    }}>
      <div className="card scale-in" style={{
        maxWidth: '900px',
        width: '100%',
        maxHeight: '85vh',
        overflow: 'auto',
        position: 'relative',
        marginTop: 'var(--space-xl)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
          <div>
            <h2 style={{
              fontSize: 'var(--font-size-2xl)',
              background: 'linear-gradient(135deg, var(--gradient-ocean-start), var(--gradient-ocean-end))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 800
            }}>
              📚 Interview History
            </h2>
            <p className="text-secondary" style={{ fontSize: 'var(--font-size-sm)' }}>
              {sessions.length} past {sessions.length === 1 ? 'session' : 'sessions'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
            {sessions.length > 0 && (
              <button className="btn btn-danger" onClick={handleClearAll}
                style={{ padding: 'var(--space-sm) var(--space-md)', fontSize: 'var(--font-size-sm)' }}>
                🗑️ Clear All
              </button>
            )}
            <button className="btn btn-secondary" onClick={onClose}
              style={{ padding: 'var(--space-sm) var(--space-md)', fontSize: 'var(--font-size-sm)' }}>
              ✕ Close
            </button>
          </div>
        </div>

        {sessions.length === 0 ? (
          <div className="text-center" style={{ padding: 'var(--space-2xl)' }}>
            <div style={{ fontSize: '4rem', marginBottom: 'var(--space-md)' }}>📭</div>
            <h3 className="mb-sm">No interview history yet</h3>
            <p className="text-secondary">Your completed interviews will appear here</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            {sessions.map((session) => (
              <div
                key={session.id}
                style={{
                  padding: 'var(--space-md) var(--space-lg)',
                  background: selectedSession?.id === session.id
                    ? 'rgba(102, 126, 234, 0.15)'
                    : 'rgba(255, 255, 255, 0.03)',
                  border: selectedSession?.id === session.id
                    ? '1px solid rgba(102, 126, 234, 0.4)'
                    : '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: 'var(--radius-lg)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-md)'
                }}
                onClick={() => setSelectedSession(
                  selectedSession?.id === session.id ? null : session
                )}
              >
                {/* Score */}
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  border: `3px solid ${getScoreColor(session.score || 5)}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background: `${getScoreColor(session.score || 5)}10`
                }}>
                  <span style={{
                    fontSize: 'var(--font-size-lg)',
                    fontWeight: 800,
                    color: getScoreColor(session.score || 5)
                  }}>
                    {session.score || '?'}
                  </span>
                </div>

                {/* Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: '2px' }}>
                    <span style={{ fontWeight: 700, fontSize: 'var(--font-size-base)' }}>
                      {session.mode === 'resume' ? '📄' : '💼'} {session.interviewType || 'Interview'}
                    </span>
                    <span style={{
                      fontSize: 'var(--font-size-xs)',
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      background: session.mode === 'resume' ? 'rgba(56, 239, 125, 0.15)' : 'rgba(102, 126, 234, 0.15)',
                      color: session.mode === 'resume' ? '#38ef7d' : '#667eea'
                    }}>
                      {session.mode === 'resume' ? 'Resume' : 'Job Desc'}
                    </span>
                  </div>
                  <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
                    {formatDate(session.savedAt)} · {session.questionCount || 0} questions
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: 'var(--space-xs)', flexShrink: 0 }}>
                  {confirmDelete === session.id ? (
                    <>
                      <button className="btn btn-danger"
                        style={{ padding: '4px 12px', fontSize: 'var(--font-size-xs)', minWidth: 'auto' }}
                        onClick={(e) => { e.stopPropagation(); handleDelete(session.id); }}>
                        Yes
                      </button>
                      <button className="btn btn-secondary"
                        style={{ padding: '4px 12px', fontSize: 'var(--font-size-xs)', minWidth: 'auto' }}
                        onClick={(e) => { e.stopPropagation(); setConfirmDelete(null); }}>
                        No
                      </button>
                    </>
                  ) : (
                    <button className="btn btn-secondary"
                      style={{ padding: '4px 12px', fontSize: 'var(--font-size-xs)', minWidth: 'auto' }}
                      onClick={(e) => { e.stopPropagation(); setConfirmDelete(session.id); }}>
                      🗑️
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Selected Session Detail */}
        {selectedSession && (
          <div style={{
            marginTop: 'var(--space-lg)',
            padding: 'var(--space-lg)',
            background: 'var(--color-bg-secondary)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            maxHeight: '300px',
            overflow: 'auto'
          }}>
            <h4 className="mb-md" style={{ color: 'var(--color-primary)' }}>📊 Report</h4>
            <div style={{ whiteSpace: 'pre-wrap', fontSize: 'var(--font-size-sm)', lineHeight: 1.7 }}>
              {selectedSession.report || 'No report available'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewHistory;
