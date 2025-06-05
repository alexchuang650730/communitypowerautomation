import React from 'react';
import '../styles/Sidebar.css';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (sectionId: string) => void;
  activeAgent: string;
  onAgentChange: (agentId: string) => void;
}

// 智能体数据
const agentData = [
  {
    id: 'code',
    name: '代码智能体',
    icon: '💻',
  },
  {
    id: 'ppt',
    name: 'PPT智能体',
    icon: '📊',
  },
  {
    id: 'web',
    name: '网页智能体',
    icon: '🌐',
  },
  {
    id: 'general',
    name: '通用智能体',
    icon: '📋',
  }
];

const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSectionChange, activeAgent, onAgentChange }) => {
  // 处理智能体点击，同时切换section和agent
  const handleAgentClick = (agentId: string) => {
    onAgentChange(agentId);
    onSectionChange('agent'); // 添加section切换，确保内容区更新
  };

  // 获取当前选中的智能体信息
  const getSelectedAgentInfo = () => {
    const agent = agentData.find(a => a.id === activeAgent);
    return agent || agentData[3]; // 默认返回通用智能体
  };

  // 获取当前选中的智能体
  const selectedAgent = getSelectedAgentInfo();

  return (
    <div className="sidebar">
      <div className="sidebar-menu">
        <div 
          className={`sidebar-item ${activeSection === 'dashboard' ? 'active' : ''}`}
          onClick={() => onSectionChange('dashboard')}
        >
          <div className="sidebar-icon">🏠</div>
          <div className="sidebar-text">仪表盘</div>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'workflow' ? 'active' : ''}`}
          onClick={() => onSectionChange('workflow')}
        >
          <div className="sidebar-icon">🔄</div>
          <div className="sidebar-text">工作流</div>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'agent' ? 'active' : ''}`}
          onClick={() => handleAgentClick(activeAgent)}
        >
          <div className="sidebar-icon">{selectedAgent.icon}</div>
          <div className="sidebar-text">{selectedAgent.name}</div>
        </div>
        <div 
          className={`sidebar-item sidebar-bottom ${activeSection === 'settings' ? 'active' : ''}`}
          onClick={() => onSectionChange('settings')}
        >
          <div className="sidebar-icon">⚙️</div>
          <div className="sidebar-text">设置</div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
