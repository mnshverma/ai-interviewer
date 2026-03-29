import ScoreVisualization from './ScoreVisualization';
import { useToast } from './Toast';

const FinalReport = ({ report, onClose, onDownload }) => {
  const toast = useToast();

  if (!report) return null;

  const handleCopyReport = async () => {
    try {
      await navigator.clipboard.writeText(report);
      toast.success('Report copied to clipboard!');
    } catch (err) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = report;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      toast.success('Report copied to clipboard!');
    }
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
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-lg)',
      animation: 'fadeIn 0.3s ease'
    }}>
      <div className="card scale-in" style={{
        maxWidth: '900px',
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

        {/* Score Visualization */}
        <ScoreVisualization report={report} />

        <div style={{
          padding: 'var(--space-lg)',
          background: 'var(--color-bg-secondary)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border)',
          marginBottom: 'var(--space-lg)',
          whiteSpace: 'pre-wrap',
          lineHeight: '1.8',
          fontSize: 'var(--font-size-sm)'
        }}>
          {report}
        </div>

        <div className="flex gap-sm justify-center" style={{ flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={onDownload}>
            💾 Download Report
          </button>
          <button className="btn btn-secondary" onClick={handleCopyReport}>
            📋 Copy to Clipboard
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default FinalReport;
