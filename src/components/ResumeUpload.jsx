import { useState, useRef } from 'react';
import { extractTextFromFile } from '../utils/pdfParser';

const ResumeUpload = ({ onResumeUploaded }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileName, setFileName] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await processFile(files[0]);
    }
  };

  const handleFileSelect = async (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      await processFile(files[0]);
    }
  };

  const processFile = async (file) => {
    setError('');
    setIsProcessing(true);
    setFileName(file.name);

    const result = await extractTextFromFile(file);
    
    setIsProcessing(false);

    if (result.success) {
      onResumeUploaded({
        fileName: file.name,
        text: result.text,
        fileSize: file.size
      });
    } else {
      setError(result.error || 'Failed to process file');
      setFileName('');
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="card fade-in">
      <h2 className="mb-md">📄 Upload Resume</h2>
      <p className="text-secondary mb-lg">
        Upload your resume in PDF or TXT format. The AI will analyze it to generate personalized interview questions.
      </p>

      <div
        className={`file-upload-area ${isDragging ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          accept=".pdf,.txt,.doc,.docx"
          onChange={handleFileSelect}
        />

        {isProcessing ? (
          <div className="flex flex-col items-center">
            <div className="loading-spinner mb-md"></div>
            <p>Processing {fileName}...</p>
          </div>
        ) : fileName ? (
          <div className="flex flex-col items-center">
            <div className="upload-icon">✅</div>
            <h3 className="mb-sm">{fileName}</h3>
            <p className="text-secondary">File uploaded successfully!</p>
            <button 
              className="btn btn-secondary mt-md"
              onClick={(e) => {
                e.stopPropagation();
                setFileName('');
                setError('');
              }}
            >
              Upload Different File
            </button>
          </div>
        ) : (
          <>
            <div className="upload-icon">📤</div>
            <h3 className="mb-sm">Drop your resume here</h3>
            <p className="text-secondary">or click to browse</p>
            <p className="text-tertiary mt-sm" style={{ fontSize: 'var(--font-size-sm)' }}>
              Supported formats: PDF, TXT, DOC, DOCX
            </p>
          </>
        )}
      </div>

      {error && (
        <div className="mt-md" style={{ 
          padding: 'var(--space-md)', 
          background: 'hsla(0, 80%, 60%, 0.1)',
          border: '1px solid var(--color-danger)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--color-danger)'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
