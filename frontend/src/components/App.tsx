import React, { useState } from 'react';
import './App.css';
import Sidebar from './Sidebar';
import DashboardContent from './DashboardContent';
import WorkflowContent from './WorkflowContent';
import LogView from './LogView';
import CodeView from './CodeView/CodeView';
import SavepointManager from './SavepointManager';
import InputArea from './InputArea';

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [activeAgent, setActiveAgent] = useState('general');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [activeWorkflowType, setActiveWorkflowType] = useState<string>('automation-test');

  // 处理节点选择
  const handleNodeSelect = (nodeId: string | null) => {
    setSelectedNodeId(nodeId);
  };

  // 处理工作流类型切换
  const handleWorkflowTypeChange = (type: string) => {
    setActiveWorkflowType(type);
    setSelectedNodeId(null); // 切换工作流类型时重置选中节点
  };

  // 渲染主内容区域
  const renderMainContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardContent agentType={activeAgent} />;
      case 'workflow':
        return (
          <div className="workflow-container">
            <div className="workflow-main">
              <WorkflowContent 
                agentType={activeAgent} 
                onNodeSelect={handleNodeSelect}
                activeWorkflowType={activeWorkflowType}
                onWorkflowTypeChange={handleWorkflowTypeChange}
              />
              <SavepointManager 
                workflowType={activeWorkflowType}
                selectedNodeId={selectedNodeId}
              />
            </div>
            <div className="workflow-sidebar">
              <LogView 
                agentType={activeAgent} 
                selectedNodeId={selectedNodeId}
                workflowType={activeWorkflowType}
              />
              <CodeView 
                agentType={activeAgent} 
                selectedNodeId={selectedNodeId}
                workflowType={activeWorkflowType}
              />
            </div>
          </div>
        );
      default:
        return <div>选择一个部分查看内容</div>;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">企业多智能体协同平台</h1>
      </header>
      <main className="app-main">
        <Sidebar 
          activeSection={activeSection} 
          onSectionChange={setActiveSection}
          activeAgent={activeAgent}
          onAgentChange={setActiveAgent}
        />
        <div className="content-area">
          {renderMainContent()}
          <InputArea 
            onInputChange={() => {}} 
            onSubmit={() => {}} 
            onFileUpload={() => {}}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
