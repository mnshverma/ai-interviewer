const FinalReport = ({ report, onClose, onDownload }) => {
  if (!report) return null;

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
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-lg)',
      animation: 'fadeIn 0.3s ease'
    }}>
      <div className="card scale-in" style={{
        maxWidth: '800px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto',
        position: 'relative'
      }}>
        <button
          className="btn btn-secondary"
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 'var(--space-md)',
            right: 'var(--space-md)',
            minWidth: 'auto',
            padding: 'var(--space-xs) var(--space-sm)'
          }}
        >
          ✕
        </button>

        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--space-md)' }}>
            📊
          </div>
          <h2 style={{ 
            fontSize: 'var(--font-size-3xl)',
            marginBottom: 'var(--space-sm)',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Interview Evaluation Report
          </h2>
          <p className="text-secondary">
            Generated on {new Date().toLocaleString()}
          </p>
        </div>

        <div style={{
          padding: 'var(--space-lg)',
          background: 'var(--color-bg-secondary)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border)',
          marginBottom: 'var(--space-lg)',
          whiteSpace: 'pre-wrap',
          lineHeight: '1.8'
        }}>
          {report}
        </div>

        <div className="flex gap-sm justify-center">
          <button
            className="btn btn-primary"
            onClick={onDownload}
          >
            💾 Download Report
          </button>
          <button
            className="btn btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default FinalReport;
