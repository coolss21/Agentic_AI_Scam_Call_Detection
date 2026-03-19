import React, { useState } from 'react';

const getRiskColor = (score) => {
  if (score < 30) return '#00e676';
  if (score < 60) return '#fcd34d';
  if (score < 85) return '#f97316';
  return '#ff003c';
};

const ResultDashboard = ({ result }) => {
  const [activeTab, setActiveTab] = useState('keywords');
  const riskColor = getRiskColor(result.risk_score);
  const sevColor = result.severity === 'high' || result.severity === 'critical' ? '#ff003c' : '#00f2ff';

  const scoreLabels = {
    rule_score: 'PATTERN MATCH',
    semantic_score: 'SEMANTIC INTENT',
    social_score: 'SOCIAL MANIP',
    llm_score: 'COGNITIVE REASON',
  };

  return (
    <div className="result-dashboard animate-in">
      {/* Top Row: Gauge + Summary */}
      <div className="result-top">
        <div className="glass-card gauge-card">
          <div className="card-title" style={{ justifyContent: 'center' }}>🛡️ THREAT INDEX</div>
          <div className="gauge-wrapper">
            <svg viewBox="0 0 200 200" className="gauge-svg">
              <circle cx="100" cy="100" r="88" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="12" />
              <circle
                cx="100" cy="100" r="88" fill="none"
                stroke={riskColor}
                strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={`${(result.risk_score / 100) * 553} 553`}
                transform="rotate(-90 100 100)"
                style={{ filter: `drop-shadow(0 0 8px ${riskColor})`, transition: 'stroke-dasharray 1s ease-out' }}
              />
            </svg>
            <div className="gauge-center">
              <div className="gauge-number" style={{ color: riskColor }}>{Math.round(result.risk_score)}</div>
              <div className="gauge-label" style={{ color: riskColor, borderColor: riskColor }}>{result.risk_level?.toUpperCase()}</div>
            </div>
          </div>
          <div className="gauge-type">
            IDENTIFIED AS: <span style={{ color: riskColor, fontWeight: 800 }}>{result.scam_type_display?.toUpperCase()}</span>
          </div>
        </div>

        <div className="glass-card summary-card" style={{ borderLeft: `4px solid ${sevColor}` }}>
          <div className="card-title">🔍 ANALYTICAL SUMMARY</div>
          <p className="summary-text">{result.explanation || 'Analysis complete. See breakdown below.'}</p>
          <div className="rec-box" style={{ borderColor: `${sevColor}30` }}>
            <div className="rec-label" style={{ color: sevColor }}>Protocol Recommendation</div>
            <div className="rec-text">{result.recommendation}</div>
          </div>
        </div>
      </div>

      {/* Score Bars */}
      <div className="glass-card">
        <div className="card-title">📊 SIGNAL DECOMPOSITION</div>
        <div className="score-bars">
          {Object.entries(result.component_scores || {}).map(([key, val]) => {
            if (val === null || val === undefined) return null;
            const color = getRiskColor(val);
            return (
              <div key={key} className="score-bar-row">
                <div className="bar-label">
                  <span>{scoreLabels[key] || key.toUpperCase()}</span>
                  <span style={{ color }}>{Math.round(val)}%</span>
                </div>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${val}%`, background: color, boxShadow: `0 0 10px ${color}` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Forensic Tabs */}
      <div className="glass-card">
        <div className="forensic-tabs">
          {[{ id: 'keywords', label: '🏷️ KEYWORDS' }, { id: 'intents', label: '🧠 INTENTS' }, { id: 'tactics', label: '🎭 TACTICS' }].map(t => (
            <button key={t.id} className={`ftab ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>
              {t.label}
            </button>
          ))}
        </div>

        <div className="tab-body">
          {activeTab === 'keywords' && (
            <div className="pill-grid">
              {result.indicators?.length > 0
                ? result.indicators.map((ind, i) => <span key={i} className="indicator-pill"># {ind.toUpperCase()}</span>)
                : <p className="empty-msg">No pattern matches found.</p>}
            </div>
          )}
          {activeTab === 'intents' && (
            <div className="intent-list">
              {result.semantic_details?.detected_intents?.length > 0
                ? result.semantic_details.detected_intents.slice(0, 5).map((intent, i) => (
                  <div key={i} className="intent-item">
                    <div className="intent-head">
                      <span style={{ color: 'var(--primary)' }}>{intent.intent?.toUpperCase()}</span>
                      <span>{intent.confidence?.toFixed(1)}%</span>
                    </div>
                    <p className="intent-match">"{intent.matched_sentence}"</p>
                  </div>
                ))
                : <p className="empty-msg">No semantic anomalies detected.</p>}
            </div>
          )}
          {activeTab === 'tactics' && (
            <div className="pill-grid">
              {result.tactics_used?.length > 0
                ? result.tactics_used.map((t, i) => <span key={i} className="indicator-pill tactic-pill">🎭 {t.toUpperCase()}</span>)
                : <p className="empty-msg">No manipulation tactics detected.</p>}
            </div>
          )}
        </div>
      </div>

      {/* Transcript */}
      {result.transcript && (
        <details className="glass-card transcript-details">
          <summary className="card-title" style={{ cursor: 'pointer' }}>💾 RAW TRANSCRIPT</summary>
          <pre className="raw-transcript">{result.transcript}</pre>
        </details>
      )}

      {result.llm_analysis_summary && (
        <details className="glass-card transcript-details">
          <summary className="card-title" style={{ cursor: 'pointer' }}>🧠 LLM REASONING LOGS</summary>
          <div className="llm-content">{result.llm_analysis_summary}</div>
        </details>
      )}
    </div>
  );
};

export default ResultDashboard;
