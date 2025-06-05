import React from 'react';
import '../../styles/WorkflowNodes.css';
import { SimpleNodeProps } from './TriggerNode';

interface ConditionNodeProps extends SimpleNodeProps {
  data?: {
    name?: string;
    description?: string;
    status?: 'idle' | 'running' | 'success' | 'error' | 'warning';
    executionState?: 'pending' | 'active' | 'completed' | 'failed';
    timestamp?: string;
    type?: string;
    condition?: string;
    executionTime?: number;
    memoryUsage?: number;
    cpuUsage?: number;
    logRefs?: string[];
    codeRefs?: string[];
  };
}

const ConditionNode: React.FC<ConditionNodeProps> = ({ 
  id, 
  data = {}, 
  selected = false, 
  onClick 
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(id);
    }
  };

  // 添加默认值和空值检查
  const { 
    name = '条件', 
    description = '', 
    status = '', 
    timestamp = '', 
    type = '默认',
    condition = ''
  } = data || {};

  return (
    <div 
      className={`workflow-node workflow-node-condition ${selected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      <div className="workflow-node-header">
        <span className="workflow-node-type">条件: {type}</span>
        {status && (
          <span className="workflow-node-status" style={{ backgroundColor: '#FF9800' }}>
            {status}
          </span>
        )}
      </div>
      <div className="workflow-node-name">{name}</div>
      {description && (
        <div className="workflow-node-description">{description}</div>
      )}
      {condition && (
        <div className="workflow-node-condition-expr">条件表达式: {condition}</div>
      )}
      {timestamp && (
        <div className="workflow-node-timestamp">评估时间: {timestamp}</div>
      )}
    </div>
  );
};

export default ConditionNode;
