import React from 'react';

const Sidebar = ({ config, setConfig }) => {
  return (
    <aside className="sidebar">
      <div className="system-status">
        <div className="status-label">System Status</div>
        <div className="status-indicator">
          <div className="status-dot"></div>
          <span className="status-text">ENCRYPTED & ACTIVE</span>
        </div>
      </div>

      <div className="sidebar-divider"></div>

      <div className="config-section">
        <div className="config-header">🛠️ SYSTEM_CONFIG</div>
        <div className="config-group">
          <label>ACCESS_KEYS</label>
          <input 
            type="password" 
            value={config.apiKey}
            onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
            placeholder="sk-or-..." 
          />
        </div>
        
        <div className="config-group">
          <label>MODEL_ID</label>
          <input 
            type="text" 
            value={config.model}
            onChange={(e) => setConfig({ ...config, model: e.target.value })}
          />
        </div>
      </div>

      <div className="pipeline-visual">
        <div className="pipeline-header">🛰️ DETECTION_NODES [6/6]</div>
        <ul className="node-list">
          {['SPEECH_TRANSCRIPT', 'PATTERN_MATCHING', 'SEMANTIC_ANALYSIS', 'BEHAVIORAL_HEURISTICS', 'LLM_SENTIMENT', 'COMPOSITE_SCORING'].map((node, i) => (
            <li key={i}>
              <span className="node-id">[{String(i + 1).padStart(2, '0')}]</span> {node}
            </li>
          ))}
        </ul>
      </div>

      <footer className="sidebar-footer">
        <div>TERMINAL_VERSION: 1.0.4</div>
        <div>FRAUD_DB_SYNC: OK</div>
      </footer>
    </aside>
  );
};

export default Sidebar;
