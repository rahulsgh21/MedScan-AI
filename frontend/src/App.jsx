import React, { useState, useEffect } from 'react';
import FileUploadView from './components/FileUploadView';
import DashboardView from './components/DashboardView';
import { Shield } from 'lucide-react';

export default function App() {
  const [reportData, setReportData] = useState(null);
  const [backendUp, setBackendUp] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/health', { signal: AbortSignal.timeout(3000) });
        setBackendUp(res.ok);
      } catch {
        setBackendUp(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <header className="header-nav">
        <div className="container flex-between" style={{ padding: '0 24px' }}>
          <div className="flex-center" style={{ gap: '12px' }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #EA580C, #F97316)', 
              padding: '8px', 
              borderRadius: '10px', 
              display: 'flex', 
              alignItems: 'center',
              boxShadow: '0 2px 12px rgba(234, 88, 12, 0.25)'
            }}>
              <Shield size={22} color="white" />
            </div>
            <div className="brand-logo">
              MedScan <span className="text-gradient">AI</span>
            </div>
          </div>
          <div className="flex-center" style={{ gap: '20px' }}>
            <span className="text-small" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                width: '8px',
                height: '8px',
                background: backendUp ? '#059669' : '#DC2626',
                borderRadius: '50%',
                display: 'inline-block',
                boxShadow: backendUp ? '0 0 8px rgba(5,150,105,0.4)' : '0 0 8px rgba(220,38,38,0.4)',
                transition: 'all 0.3s',
              }}></span>
              {backendUp ? 'Backend Active' : 'Backend Offline'}
            </span>
          </div>
        </div>
      </header>

      <main>
        {!reportData ? (
          <FileUploadView onUploadComplete={(data) => setReportData(data)} />
        ) : (
          <DashboardView reportData={reportData} onReset={() => setReportData(null)} />
        )}
      </main>
      
      <footer className="footer">
        <p>Disclaimer: MedScan AI is a portfolio project and not a substitute for professional medical advice.</p>
        <p style={{ marginTop: '6px' }}>Always consult your doctor regarding diagnostic results.</p>
      </footer>
    </>
  );
}
