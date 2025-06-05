import React from 'react';
import '../../styles/WorkflowNodes.css';

export interface SimpleNodeProps {
  id: string;
  data?: {
    name?: string;
    description?: string;
    status?: 'idle' | 'running' | 'success' | 'error' | 'warning';
    executionState?: 'pending' | 'active' | 'completed' | 'failed';
    timestamp?: string;
    type?: string;
    errorType?: string;
    errorMessage?: string;
    executionTime?: number;
    memoryUsage?: number;
    cpuUsage?: number;
    logRefs?: string[];
    codeRefs?: string[];
  };
  selected?: boolean;
  onClick?: (id: string) => void;
}

const TriggerNode: React.FC<SimpleNodeProps> = ({ id, data = {}, selected = false, onClick }) => {
  const handleClick = () => {
    if (onClick) {
      onClick(id);
    }
  };

  // 添加默认值和空值检查
  const { 
    name = '触发器', 
    description = '', 
    status = '', 
    timestamp = '', 
    type = '默认' 
  } = data || {};

  return (
    <div 
      className={`workflow-node workflow-node-trigger ${selected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      <div className="workflow-node-header">
        <span className="workflow-node-type">触发器: {type}</span>
        {status && (
          <span className="workflow-node-status" style={{ backgroundColor: '#2196F3' }}>
            {status}
          </span>
        )}
      </div>
      <div className="workflow-node-name">{name}</div>
      {description && (
        <div className="workflow-node-description">{description}</div>
      )}
      {timestamp && (
        <div className="workflow-node-timestamp">上次触发: {timestamp}</div>
      )}
    </div>
  );
};

export default TriggerNode;
