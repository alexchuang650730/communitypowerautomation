import React from 'react';
import '../styles/AgentCards.css';

interface Agent {
  id: string;
  name: string;
  icon: string;
  description: string;
}

interface AgentCardsProps {
  agents: Agent[];
  selectedAgentId: string;
  onSelect: (agentId: string) => void;
}

const AgentCards: React.FC<AgentCardsProps> = ({ agents, selectedAgentId, onSelect }) => {
  return (
    <div className="agent-cards">
      {agents.map((agent) => (
        <div 
          key={agent.id}
          className={`agent-card ${agent.id === selectedAgentId ? 'selected' : ''}`}
          onClick={() => onSelect(agent.id)}
        >
          <div className="agent-icon">{agent.icon}</div>
          <div className="agent-name">{agent.name}</div>
          <div className="agent-description">{agent.description}</div>
        </div>
      ))}
    </div>
  );
};

export default AgentCards;
