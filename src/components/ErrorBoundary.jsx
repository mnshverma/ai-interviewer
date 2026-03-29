import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #0f2027, #203a43, #2c5364)',
          padding: '2rem'
        }}>
          <div style={{
            maxWidth: '600px',
            width: '100%',
            background: 'rgba(30, 39, 73, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '2px solid rgba(245, 87, 108, 0.3)',
            borderRadius: '1.5rem',
            padding: '3rem',
            textAlign: 'center',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>⚠️</div>
            <h2 style={{
              fontSize: '1.875rem',
              fontWeight: 800,
              color: '#f5576c',
              marginBottom: '1rem',
              fontFamily: 'Inter, -apple-system, sans-serif'
            }}>
              Something went wrong
            </h2>
            <p style={{
              color: '#a5b4fc',
              marginBottom: '1.5rem',
              lineHeight: 1.6,
              fontFamily: 'Inter, -apple-system, sans-serif'
            }}>
              The application encountered an unexpected error. You can try reloading the page or resetting the app.
            </p>

            {this.state.error && (
              <div style={{
                padding: '1rem',
                background: 'rgba(245, 87, 108, 0.1)',
                border: '1px solid rgba(245, 87, 108, 0.3)',
                borderRadius: '0.75rem',
                marginBottom: '1.5rem',
                textAlign: 'left',
                fontSize: '0.875rem',
                color: '#f5576c',
                fontFamily: 'monospace',
                wordBreak: 'break-word'
              }}>
                {this.state.error.toString()}
              </div>
            )}

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button
                onClick={this.handleReset}
                style={{
                  padding: '0.75rem 2rem',
                  background: 'linear-gradient(135deg, #11998e, #38ef7d)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '1rem',
                  fontSize: '1rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontFamily: 'Inter, -apple-system, sans-serif'
                }}
              >
                🔄 Try Again
              </button>
              <button
                onClick={() => window.location.reload()}
                style={{
                  padding: '0.75rem 2rem',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '1rem',
                  fontSize: '1rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontFamily: 'Inter, -apple-system, sans-serif'
                }}
              >
                🔃 Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
