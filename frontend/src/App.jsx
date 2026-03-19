import React, { useState, useRef } from 'react';
import Hero from './components/Hero';
import Sidebar from './components/Sidebar';
import AnalysisPipeline from './components/AnalysisPipeline';
import ResultDashboard from './components/ResultDashboard';
import EmptyState from './components/EmptyState';
import { DEMO_TRANSCRIPTS } from './data/demoTranscripts';
import './App.css';

const API_BASE = '/api';

function App() {
  const [transcript, setTranscript] = useState('');
  const [activeTab, setActiveTab] = useState('text');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [pipelineMessage, setPipelineMessage] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const fileInputRef = useRef(null);
  const [config, setConfig] = useState({
    apiKey: localStorage.getItem('fs_apiKey') || '',
    model: 'openai/gpt-4o-mini',
    baseUrl: 'https://openrouter.ai/api/v1',
  });

  const handleAnalyze = async (text) => {
    if (!text || !text.trim()) return;
    setTranscript(text);
    setIsAnalyzing(true);
    setResult(null);
    setError(null);
    setPipelineStep(1);
    setPipelineMessage('Initializing neural pipeline...');

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          transcript: text,
          api_key: config.apiKey || '',
          model: config.model,
          base_url: config.baseUrl,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errData.detail || `Server error ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.type === 'progress') {
                setPipelineStep(data.step);
                setPipelineMessage(data.message);
              } else if (data.type === 'result') {
                setResult(data.data);
              } else if (data.type === 'error') {
                setError(data.message || 'Analysis failed on the server');
              }
            } catch (e) { /* skip malformed */ }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFileName(file.name);
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('api_key', config.apiKey || '');

    try {
      const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errData.detail || `Upload failed: ${res.status}`);
      }
      const data = await res.json();
      setTranscript(data.transcript);
      setActiveTab('text');
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDemo = (key) => {
    const demo = DEMO_TRANSCRIPTS[key];
    if (demo) handleAnalyze(demo.transcript);
  };

  return (
    <div className="app-layout">
      <Sidebar config={config} setConfig={setConfig} />

      <main className="main-area">
        <Hero />

        <div className="workspace">
          {/* ── Left: Input Panel ────────────────────────────── */}
          <div className="panel-left">
            <div className="glass-card">
              <div className="scanner-line" />
              <div className="card-title">📥 DATA INGESTION</div>

              <div className="input-tabs">
                <button className={activeTab === 'audio' ? 'tab active' : 'tab'} onClick={() => setActiveTab('audio')}>
                  🎙️ AUDIO
                </button>
                <button className={activeTab === 'text' ? 'tab active' : 'tab'} onClick={() => setActiveTab('text')}>
                  📝 TEXT
                </button>
              </div>

              {activeTab === 'audio' && (
                <div className="upload-zone" onClick={() => fileInputRef.current?.click()}>
                  <input ref={fileInputRef} type="file" accept=".wav,.mp3,.ogg,.m4a,.flac,.wma,.mp4,.avi,.mov,.mkv,.webm" onChange={handleFileUpload} hidden />
                  <div className="upload-icon">{isUploading ? '⏳' : '📂'}</div>
                  <div className="upload-text">
                    {isUploading ? 'PROCESSING...' : uploadedFileName || 'Click to upload audio / video'}
                  </div>
                  <div className="upload-hint">WAV, MP3, OGG, M4A, FLAC, MP4, AVI, MOV</div>
                </div>
              )}

              {activeTab === 'text' && (
                <>
                  <textarea
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Paste or type a phone call transcript here..."
                    className="text-input"
                    rows={6}
                  />
                  <button
                    className="btn-primary"
                    onClick={() => handleAnalyze(transcript)}
                    disabled={isAnalyzing || !transcript.trim()}
                  >
                    {isAnalyzing ? '⚡ ANALYZING...' : '🔍 RUN DETECTION ENGINE'}
                  </button>
                </>
              )}
            </div>

            {/* Demo Buttons */}
            <div className="glass-card" style={{ animationDelay: '0.1s' }}>
              <div className="card-title">🧪 QUICK SIMULATIONS</div>
              <div className="demo-grid">
                {Object.entries(DEMO_TRANSCRIPTS).map(([key, data]) => (
                  <button key={key} className="demo-btn" onClick={() => handleDemo(key)} disabled={isAnalyzing}>
                    {data.title}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* ── Right: Results Panel ─────────────────────────── */}
          <div className="panel-right">
            {error && (
              <div className="glass-card error-card">
                <div className="card-title" style={{ color: 'var(--warning)' }}>⚠️ ERROR</div>
                <p>{error}</p>
                <button className="btn-dismiss" onClick={() => setError(null)}>Dismiss</button>
              </div>
            )}

            {isAnalyzing && <AnalysisPipeline step={pipelineStep} message={pipelineMessage} />}
            {result && !isAnalyzing && <ResultDashboard result={result} />}
            {!isAnalyzing && !result && !error && <EmptyState />}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
