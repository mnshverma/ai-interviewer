import { useState, useEffect, useCallback, createContext, useContext } from 'react';

const ToastContext = createContext(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
};

const TOAST_ICONS = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️'
};

const TOAST_COLORS = {
  success: { bg: 'rgba(56, 239, 125, 0.15)', border: 'rgba(56, 239, 125, 0.4)', text: '#38ef7d' },
  error: { bg: 'rgba(245, 87, 108, 0.15)', border: 'rgba(245, 87, 108, 0.4)', text: '#f5576c' },
  warning: { bg: 'rgba(255, 210, 0, 0.15)', border: 'rgba(255, 210, 0, 0.4)', text: '#ffd200' },
  info: { bg: 'rgba(102, 126, 234, 0.15)', border: 'rgba(102, 126, 234, 0.4)', text: '#667eea' }
};

const Toast = ({ id, message, type = 'info', onRemove }) => {
  const [isExiting, setIsExiting] = useState(false);
  const colors = TOAST_COLORS[type] || TOAST_COLORS.info;

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => onRemove(id), 300);
    }, 3500);
    return () => clearTimeout(timer);
  }, [id, onRemove]);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.875rem 1.25rem',
        background: colors.bg,
        backdropFilter: 'blur(20px)',
        border: `1px solid ${colors.border}`,
        borderRadius: '0.75rem',
        color: '#e8eaf6',
        fontSize: '0.9rem',
        fontFamily: 'Inter, -apple-system, sans-serif',
        fontWeight: 500,
        boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
        animation: isExiting ? 'toastOut 0.3s ease forwards' : 'toastIn 0.3s ease',
        cursor: 'pointer',
        minWidth: '280px',
        maxWidth: '420px'
      }}
      onClick={() => { setIsExiting(true); setTimeout(() => onRemove(id), 300); }}
    >
      <span style={{ fontSize: '1.2rem', flexShrink: 0 }}>{TOAST_ICONS[type]}</span>
      <span style={{ flex: 1 }}>{message}</span>
      <span style={{ color: colors.text, fontSize: '0.75rem', opacity: 0.7, flexShrink: 0 }}>✕</span>
    </div>
  );
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const toast = {
    success: (msg) => addToast(msg, 'success'),
    error: (msg) => addToast(msg, 'error'),
    warning: (msg) => addToast(msg, 'warning'),
    info: (msg) => addToast(msg, 'info'),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Toast Container */}
      <div style={{
        position: 'fixed',
        top: '1.5rem',
        right: '1.5rem',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
        pointerEvents: 'none'
      }}>
        {toasts.map(t => (
          <div key={t.id} style={{ pointerEvents: 'all' }}>
            <Toast id={t.id} message={t.message} type={t.type} onRemove={removeToast} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
