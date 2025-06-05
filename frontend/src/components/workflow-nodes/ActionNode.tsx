import React from 'react';

interface ActionNodeProps {
  id: string;
  data: {
    name: string;
    description?: string;
    status?: 'idle' | 'running' | 'success' | 'error' | 'warning';
    type: string;
  };
  selected: boolean;
  onClick: (id: string) => void;
}

const ActionNode: React.FC<ActionNodeProps> = ({ id, data, selected, onClick }) => {
  const handleClick = () => {
    onClick(id);
  };

  return (
    <div 
      className={`workflow-node action ${selected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      <div className="node-header">
        <span className="node-title">{data.name}</span>
        <span className="node-type-badge action">动作</span>
      </div>
      {data.description && (
        <div className="node-content">
          {data.description}
        </div>
      )}
      {data.status && (
        <div className={`node-status-indicator ${data.status}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {data.status === 'success' ? '成功' : 
             data.status === 'error' ? '错误' : 
             data.status === 'warning' ? '警告' : 
             data.status === 'running' ? '运行中' : '待定'}
          </span>
        </div>
      )}
    </div>
  );
};

export default ActionNode;
