import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Shield, Brain, Lock, Zap } from 'lucide-react';

const PROGRESS_STEPS = [
  { label: 'Extracting text from PDF...', icon: FileText },
  { label: 'Scrubbing PII (Presidio)...', icon: Lock },
  { label: 'Querying Medical RAG Engine...', icon: Brain },
  { label: 'Generating AI Analysis...', icon: Zap },
];

export default function FileUploadView({ onUploadComplete }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [progressStep, setProgressStep] = useState(0);

  // Simulate progress steps while waiting for the API
  useEffect(() => {
    if (!isUploading) return;
    setProgressStep(0);
    const timers = [
      setTimeout(() => setProgressStep(1), 3000),
      setTimeout(() => setProgressStep(2), 7000),
      setTimeout(() => setProgressStep(3), 12000),
    ];
    return () => timers.forEach(clearTimeout);
  }, [isUploading]);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    setIsUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/reports/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze report');
      }
      
      onUploadComplete(data);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || 'An unexpected error occurred during upload.');
      setIsUploading(false);
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1
  });

  return (
    <div className="upload-page animate-fade-in">
      
      {/* Hero Section */}
      <div className="upload-hero">
        <h1>
          Your Lab Reports,<br />
          <span className="text-gradient">Decoded by AI</span>
        </h1>
        <p>
          Upload a diagnostic report and MedScan AI will extract lab results, 
          cross-reference medical guidelines via Hybrid RAG, and translate 
          complex biomarkers into simple, actionable insights.
        </p>
      </div>

      {/* Upload Card */}
      <div className="upload-container">
        <div className="glass-panel" style={{ padding: '40px' }}>
          
          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '14px 18px', borderRadius: '10px', color: '#EF4444', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem' }}>
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div 
            {...getRootProps()} 
            className={`dropzone ${isDragActive ? 'active' : ''}`}
            style={{ pointerEvents: isUploading ? 'none' : 'auto', opacity: isUploading ? 0.4 : 1 }}
          >
            <input {...getInputProps()} />
            <div className="dropzone-icon">
              <UploadCloud size={36} />
            </div>
            
            <h3 style={{ marginBottom: '8px', fontSize: '1.2rem' }}>
              {isDragActive ? "Drop the PDF here" : "Drag & Drop your Lab Report"}
            </h3>
            <p className="text-small" style={{ marginBottom: '24px' }}>
              Supported format: PDF only. Maximum size: 10MB
            </p>
            
            <button className="btn-primary" type="button" disabled={isUploading}>
              Browse Files
            </button>
          </div>
          
          <div className="feature-badges">
            <div className="feature-badge">
              <CheckCircle size={15} color="var(--status-normal)" />
              <span>PubMedBERT RAG</span>
            </div>
            <div className="feature-badge">
              <CheckCircle size={15} color="var(--status-normal)" />
              <span>PII Scrubbing</span>
            </div>
            <div className="feature-badge">
              <CheckCircle size={15} color="var(--status-normal)" />
              <span>100% Local Privacy</span>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="steps-section">
        <h2>How It <span className="text-gradient">Works</span></h2>
        <div className="steps-grid">
          <div className="step-card animate-fade-in-up animate-delay-1">
            <div className="step-number">1</div>
            <h4>Upload PDF</h4>
            <p>Drop your lab report and our engine extracts every biomarker, value, and reference range.</p>
          </div>
          <div className="step-card animate-fade-in-up animate-delay-2">
            <div className="step-number">2</div>
            <h4>RAG Analysis</h4>
            <p>Abnormal results are cross-referenced against PubMed-trained medical knowledge via Hybrid Search.</p>
          </div>
          <div className="step-card animate-fade-in-up animate-delay-3">
            <div className="step-number">3</div>
            <h4>AI Insights</h4>
            <p>Get plain-English explanations, possible causes, lifestyle tips, and questions for your doctor.</p>
          </div>
        </div>
      </div>

      {/* Trust Badges */}
      <div className="trust-badges animate-fade-in-up animate-delay-4">
        <div className="trust-badge">
          <Shield size={16} color="#60A5FA" />
          HIPAA-Compliant PII Scrubbing
        </div>
        <div className="trust-badge">
          <Brain size={16} color="#A78BFA" />
          PubMedBERT Medical Embeddings
        </div>
        <div className="trust-badge">
          <Zap size={16} color="#F59E0B" />
          RAGAS Evaluated (Anti-Hallucination)
        </div>
      </div>

      {/* Multi-Step Progress Overlay */}
      {isUploading && (
        <div className="progress-overlay">
          <div className="spinner"></div>
          <h2 className="text-gradient" style={{ fontSize: '1.6rem' }}>Analyzing Report</h2>
          <p style={{ marginBottom: '8px' }}>Processing through the MedScan AI pipeline...</p>
          
          <div className="progress-steps">
            {PROGRESS_STEPS.map((step, idx) => {
              const Icon = step.icon;
              const isDone = idx < progressStep;
              const isActive = idx === progressStep;
              return (
                <div key={idx} className={`progress-step ${isDone ? 'done' : ''} ${isActive ? 'active' : ''}`}>
                  <div className="progress-step-icon">
                    {isDone ? <CheckCircle size={18} /> : <Icon size={18} />}
                  </div>
                  <span className="progress-step-label">{step.label}</span>
                </div>
              );
            })}
          </div>

          <p className="text-small" style={{ marginTop: '24px', opacity: 0.5 }}>This usually takes 15-30 seconds.</p>
        </div>
      )}
    </div>
  );
}
