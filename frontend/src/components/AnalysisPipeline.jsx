import React from 'react';

const AnalysisPipeline = ({ step, message }) => {
  const agentSteps = [
    "SPEECH_TO_TEXT",
    "RULE_DETECTION",
    "SEMANTIC_MATCH",
    "SOCIAL_ENGINEERING",
    "LLM_REASONING",
    "RISK_ORCHESTRATION"
  ];

  return (
    <div className="glass-card animate-in">
      <div className="card-title">🤖 NEURAL_PIPELINE_STATUS</div>
      <div className="pipeline-steps">
        {agentSteps.map((agent, i) => {
          const currentStep = i + 1;
          const isDone = step > currentStep;
          const isActive = step === currentStep;
          
          return (
            <div key={i} className={`agent-step ${isDone ? 'agent-done' : ''} ${isActive ? 'agent-active' : ''}`}>
              <span>
                <span className="status-tag">
                  {isDone ? '[OK]' : isActive ? '[RUN]' : '[...]'}
                </span> {agent}
                {isActive && <span className="step-desc"> - {message}</span>}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AnalysisPipeline;
