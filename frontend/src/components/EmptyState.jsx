import React from 'react';

const EmptyState = () => (
  <div className="empty-state">
    <div className="glass-card animate-in">
      <div className="empty-hero">
        <div className="empty-icon">🛡️</div>
        <h2>FRAUD<span>SENTINEL</span> READY</h2>
        <p>Upload audio, paste a transcript, or try a quick simulation to begin analysis.</p>
      </div>
    </div>

    <div className="status-cards">
      <div className="glass-card mini-card animate-in" style={{ animationDelay: '0.1s' }}>
        <div className="mini-icon">🎙️</div>
        <div className="mini-title">VOICE_READY</div>
        <div className="mini-desc">Audio stream standby</div>
      </div>
      <div className="glass-card mini-card animate-in" style={{ animationDelay: '0.2s' }}>
        <div className="mini-icon">🛰️</div>
        <div className="mini-title">NODE_SYNC</div>
        <div className="mini-desc">6/6 agents online</div>
      </div>
      <div className="glass-card mini-card animate-in" style={{ animationDelay: '0.3s' }}>
        <div className="mini-icon">🔒</div>
        <div className="mini-title">SHIELD_UP</div>
        <div className="mini-desc">Threat DB updated</div>
      </div>
    </div>

    <div className="glass-card animate-in" style={{ animationDelay: '0.4s' }}>
      <div className="card-title">📖 SYSTEM OVERVIEW</div>
      <div className="overview-grid">
        <div className="overview-item">
          <strong style={{ color: 'var(--primary)' }}>[MULTI_LAYER]</strong>
          <p>6-layer agentic pipeline combining rule-bases, semantic embeddings, and LLM reasoning for comprehensive scam detection.</p>
        </div>
        <div className="overview-item">
          <strong style={{ color: 'var(--secondary)' }}>[HYBRID_SCORING]</strong>
          <p>Weighted composite indexing ensures low false-positives while catching complex social engineering tactics.</p>
        </div>
        <div className="overview-item">
          <strong style={{ color: 'var(--warning)' }}>[RAPID_RESPONSE]</strong>
          <p>Real-time transcription via Faster-Whisper allows near-instant analysis of live call data.</p>
        </div>
      </div>
    </div>
  </div>
);

export default EmptyState;
