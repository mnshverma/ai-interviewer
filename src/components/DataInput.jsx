import { useState, useRef } from 'react';
import { extractTextFromFile } from '../utils/pdfParser';

const DataInput = ({ onDataProvided }) => {
  const [inputMode, setInputMode] = useState('resume'); // 'resume' or 'jobdesc'
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileName, setFileName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
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
      onDataProvided({
        mode: 'resume',
        fileName: file.name,
        text: result.text,
        fileSize: file.size
      });
    } else {
      setError(result.error || 'Failed to process file');
      setFileName('');
    }
  };

  const handleJobDescSubmit = () => {
    if (!jobDescription.trim()) {
      alert('Please enter a job description');
      return;
    }

    onDataProvided({
      mode: 'jobdesc',
      text: jobDescription.trim()
    });
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const clearData = () => {
    setFileName('');
    setJobDescription('');
    setError('');
    onDataProvided(null);
  };

  return (
    <div className="card fade-in">
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <h2 style={{ 
          fontSize: 'var(--font-size-2xl)', 
          marginBottom: 'var(--space-sm)',
          background: 'linear-gradient(135deg, var(--gradient-emerald-start), var(--gradient-emerald-end))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: '800'
        }}>
          📋 Interview Preparation
        </h2>
        <p className="text-secondary" style={{ fontSize: 'var(--font-size-sm)' }}>
          Choose your input method to generate personalized questions
        </p>
      </div>
      
      {/* Mode Selector with Icons */}
      <div style={{ 
        display: 'flex', 
        gap: 'var(--space-sm)', 
        marginBottom: 'var(--space-lg)',
        padding: 'var(--space-sm)',
        background: 'rgba(0, 0, 0, 0.2)',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid rgba(255, 255, 255, 0.05)'
      }}>
        <button
          className={`btn ${inputMode === 'resume' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setInputMode('resume');
            clearData();
          }}
          style={{ 
            flex: 1,
            padding: 'var(--space-md)',
            fontSize: 'var(--font-size-base)',
            fontWeight: '700'
          }}
        >
          📄 Upload Resume
        </button>
        <button
          className={`btn ${inputMode === 'jobdesc' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setInputMode('jobdesc');
            clearData();
          }}
          style={{ 
            flex: 1,
            padding: 'var(--space-md)',
            fontSize: 'var(--font-size-base)',
            fontWeight: '700'
          }}
        >
          💼 Job Description
        </button>
      </div>

      {inputMode === 'resume' ? (
        <>
          <p className="text-secondary mb-lg">
            Upload a resume to generate personalized interview questions based on the candidate's background.
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
                <p className="text-secondary">Resume uploaded successfully!</p>
                <button 
                  className="btn btn-secondary mt-md"
                  onClick={(e) => {
                    e.stopPropagation();
                    clearData();
                  }}
                >
                  Upload Different File
                </button>
              </div>
            ) : (
              <>
                <div className="upload-icon">📤</div>
                <h3 className="mb-sm">Drop resume here</h3>
                <p className="text-secondary">or click to browse</p>
                <p className="text-tertiary mt-sm" style={{ fontSize: 'var(--font-size-sm)' }}>
                  Supported formats: PDF, TXT, DOC, DOCX
                </p>
              </>
            )}
          </div>
        </>
      ) : (
        <>
          <p className="text-secondary mb-lg">
            Enter a job description to generate relevant interview questions for this role.
          </p>

          <div className="input-group">
            <label htmlFor="job-desc">Job Description *</label>
            <textarea
              id="job-desc"
              className="input"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here...

Example:
We are looking for a Senior Frontend Developer with 5+ years of experience in React, TypeScript, and modern web technologies. The ideal candidate will lead our UI development team and architect scalable applications..."
              rows="12"
              style={{
                resize: 'vertical',
                fontFamily: 'var(--font-family)',
                fontSize: 'var(--font-size-sm)'
              }}
            />
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%' }}
            onClick={handleJobDescSubmit}
            disabled={!jobDescription.trim()}
          >
            ✅ Use This Job Description
          </button>

          {jobDescription.trim() && (
            <button
              className="btn btn-secondary mt-sm"
              style={{ width: '100%' }}
              onClick={clearData}
            >
              Clear
            </button>
          )}
        </>
      )}

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

export default DataInput;
