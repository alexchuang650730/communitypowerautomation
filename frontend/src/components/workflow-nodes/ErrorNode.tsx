import React from 'react';
import '../../styles/WorkflowNodes.css';
import { SimpleNodeProps } from './TriggerNode';

interface ErrorNodeProps extends SimpleNodeProps {
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
}

const ErrorNode: React.FC<ErrorNodeProps> = ({ 
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
    name = '错误', 
    description = '', 
    status = '', 
    timestamp = '', 
    type = '默认',
    errorType = '',
    errorMessage = ''
  } = data || {};

  return (
    <div 
      className={`workflow-node workflow-node-error ${selected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      <div className="workflow-node-header">
        <span className="workflow-node-type">错误: {type}</span>
        {status && (
          <span className="workflow-node-status" style={{ backgroundColor: '#F44336' }}>
            {status}
          </span>
        )}
      </div>
      <div className="workflow-node-name">{name}</div>
      {description && (
        <div className="workflow-node-description">{description}</div>
      )}
      {errorType && (
        <div className="workflow-node-error-type">错误类型: {errorType}</div>
      )}
      {errorMessage && (
        <div className="workflow-node-error-message">错误信息: {errorMessage}</div>
      )}
      {timestamp && (
        <div className="workflow-node-timestamp">发生时间: {timestamp}</div>
      )}
    </div>
  );
};

export default ErrorNode;
