import React from 'react';
import './AgentCard.css';

interface AgentCardProps {
  type: 'code' | 'ppt' | 'web' | 'general';
  name: string;
  description: string;
  isSelected: boolean;
  onClick: () => void;
}

const AgentCard: React.FC<AgentCardProps> = ({ 
  type, 
  name, 
  description, 
  isSelected, 
  onClick 
}) => {
  const getIcon = () => {
    switch (type) {
      case 'code':
        return <span className="agent-card-icon code">&#60;/&#62;</span>;
      case 'ppt':
        return <span className="agent-card-icon ppt">P</span>;
      case 'web':
        return <span className="agent-card-icon web">🌐</span>;
      case 'general':
        return <span className="agent-card-icon general">📦</span>;
      default:
        return null;
    }
  };

  return (
    <div 
      className={`agent-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="agent-card-icon-container">
        {getIcon()}
      </div>
      <div className="agent-card-content">
        <h3 className="agent-card-title">{name}</h3>
        <p className="agent-card-description">{description}</p>
      </div>
    </div>
  );
};

export default AgentCard;
