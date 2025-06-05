import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import DashboardContent from './components/DashboardContent';
import WorkflowContent from './components/WorkflowContent';
import LogView from './components/LogView';
import CodeView from './components/CodeView/CodeView';
import SavepointManager from './components/SavepointManager';
import InputArea from './components/InputArea';
import AutomationAgentDesignContent from './components/AutomationAgentDesignContent';
import AgentCards from './components/AgentCards';

// 创建全局状态上下文
interface WorkflowContextType {
  selectedNodeId: string | null;
  setSelectedNodeId: (id: string | null) => void;
  activeWorkflowType: string;
  setActiveWorkflowType: (type: string) => void;
  activeSavepoint: string | null;
  setActiveSavepoint: (id: string | null) => void;
  refreshTrigger: number;
  triggerRefresh: () => void;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

// 自定义Hook用于访问上下文
export const useWorkflowContext = () => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflowContext must be used within a WorkflowProvider');
  }
  return context;
};

// 智能体数据
const agentData = [
  {
    id: 'code',
    name: '代码智能体',
    icon: '💻',
    description: '专注于代码生成、调试和优化的智能体'
  },
  {
    id: 'ppt',
    name: 'PPT智能体',
    icon: '📊',
    description: '创建和编辑专业演示文稿的智能体'
  },
  {
    id: 'web',
    name: '网页智能体',
    icon: '🌐',
    description: '设计和开发网页应用的智能体'
  },
  {
    id: 'general',
    name: '通用智能体',
    icon: '📋',
    description: '处理各类通用任务的多功能智能体'
  }
];

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [activeAgent, setActiveAgent] = useState('general');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [activeWorkflowType, setActiveWorkflowType] = useState<string>('automation-test');
  const [activeSavepoint, setActiveSavepoint] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // 触发全局刷新的函数
  const triggerRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // 处理工作流类型切换
  const handleWorkflowTypeChange = (type: string) => {
    setActiveWorkflowType(type);
    setSelectedNodeId(null); // 切换工作流类型时重置选中节点
    setActiveSavepoint(null); // 重置活动保存点
  };

  // 获取当前选中的智能体信息
  const getSelectedAgentInfo = () => {
    const agent = agentData.find(a => a.id === activeAgent);
    return agent || agentData[3]; // 默认返回通用智能体
  };

  // 渲染主内容区域
  const renderMainContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardContent agentType={activeAgent} />;
      case 'workflow':
        return (
          <WorkflowContext.Provider value={{
            selectedNodeId,
            setSelectedNodeId,
            activeWorkflowType,
            setActiveWorkflowType,
            activeSavepoint,
            setActiveSavepoint,
            refreshTrigger,
            triggerRefresh
          }}>
            <WorkflowContent agentType={activeAgent} />
          </WorkflowContext.Provider>
        );
      case 'agent':
        const selectedAgent = getSelectedAgentInfo();
        return (
          <div className="agent-page-container">
            <h2 className="agent-page-title">智能体选择</h2>
            <AgentCards 
              agents={agentData} 
              selectedAgentId={activeAgent} 
              onSelect={setActiveAgent} 
            />
            <div className="agent-input-container">
              <InputArea 
                onInputChange={() => {}} 
                onSubmit={() => {}} 
                onFileUpload={() => {}}
                selectedAgentName={selectedAgent.name}
                selectedAgentIcon={selectedAgent.icon}
              />
            </div>
          </div>
        );
      case 'settings':
        return <div className="settings-container">设置页面内容</div>;
      default:
        return <div>选择一个部分查看内容</div>;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo-container">
          <h1 className="app-title">
            <span className="platform-name-blue">企业级多智能体协同平台</span>
            <span className="platform-name-black">PowerAutomation</span>
          </h1>
        </div>
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
        </div>
      </main>
    </div>
  );
}

export default App;
