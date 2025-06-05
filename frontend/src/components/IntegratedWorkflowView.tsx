import React, { ReactNode } from 'react';
import '../styles/IntegratedWorkflowView.css';

interface IntegratedWorkflowViewProps {
  children: ReactNode;
}

const IntegratedWorkflowView: React.FC<IntegratedWorkflowViewProps> = ({ children }) => {
  return (
    <div className="integrated-workflow-view">
      <div className="workflow-header">
        <div className="workflow-tabs">
          <div className="workflow-tab active">工作流视图</div>
          <div className="workflow-tab">代码视图</div>
          <div className="workflow-tab">日志视图</div>
        </div>
        <div className="workflow-controls">
          <button className="control-button">
            <span className="control-icon">▶️</span>
            运行
          </button>
          <button className="control-button">
            <span className="control-icon">⏸️</span>
            暂停
          </button>
          <button className="control-button">
            <span className="control-icon">⏹️</span>
            停止
          </button>
        </div>
      </div>
      <div className="workflow-content">
        {children}
      </div>
    </div>
  );
};

export default IntegratedWorkflowView;
