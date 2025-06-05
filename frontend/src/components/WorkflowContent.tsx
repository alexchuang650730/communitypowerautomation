import React, { useState, useEffect } from 'react';
import { useWorkflowContext } from '../App';
import N8nWorkflowVisualizer, { WorkflowNode, NodeType } from './N8nWorkflowVisualizer';
import '../styles/WorkflowContent.css';

interface WorkflowContentProps {
  agentType?: string;
  onNodeSelect?: (nodeId: string | null) => void;
  activeWorkflowType?: string;
  onWorkflowTypeChange?: (type: string) => void;
}

const WorkflowContent: React.FC<WorkflowContentProps> = ({ agentType = 'general' }) => {
  const { 
    selectedNodeId, 
    setSelectedNodeId, 
    activeWorkflowType, 
    setActiveWorkflowType,
    refreshTrigger
  } = useWorkflowContext();
  
  const [activeTab, setActiveTab] = useState<'workflow' | 'docs'>('workflow');
  const [docsUrl, setDocsUrl] = useState<string>('');

  // 自动化测试工作流节点数据
  const automationTestNodes = [
    {
      id: 'integration-test',
      type: 'action' as NodeType,
      position: { x: 100, y: 100 },
      data: {
        name: '集成测试',
        description: '测试组件间的交互',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 1.5,
        memoryUsage: 85,
        cpuUsage: 15
      }
    },
    {
      id: 'e2e-test',
      type: 'action' as NodeType,
      position: { x: 100, y: 250 },
      data: {
        name: '端到端测试',
        description: '测试完整工作流程',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 4.2,
        memoryUsage: 120,
        cpuUsage: 25
      }
    },
    {
      id: 'visual-test',
      type: 'action' as NodeType,
      position: { x: 100, y: 400 },
      data: {
        name: '视觉自动化测试',
        description: '测试UI界面和视觉元素',
        status: 'error' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 3.7,
        memoryUsage: 180,
        cpuUsage: 35
      }
    }
  ];

  // 自动化智能体设计工作流节点数据
  const agentDesignNodes = [
    {
      id: 'general-agent',
      type: 'trigger' as NodeType,
      position: { x: 100, y: 100 },
      data: {
        name: '通用智能体',
        description: '处理用户输入',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'trigger',
        executionTime: 0.8,
        memoryUsage: 100,
        cpuUsage: 20
      }
    },
    {
      id: 'mcp-coordinator',
      type: 'action' as NodeType,
      position: { x: 300, y: 100 },
      data: {
        name: 'MCP协调器',
        description: '协调多个子系统和组件的工作',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 1.5,
        memoryUsage: 75,
        cpuUsage: 15
      }
    },
    {
      id: 'mcp-planner',
      type: 'action' as NodeType,
      position: { x: 500, y: 100 },
      data: {
        name: 'MCP规划器',
        description: '创建详细的执行计划',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 2.1,
        memoryUsage: 110,
        cpuUsage: 25
      }
    },
    {
      id: 'thought-recorder',
      type: 'action' as NodeType,
      position: { x: 300, y: 250 },
      data: {
        name: '思维行为记录器',
        description: '记录智能体的思考过程',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 1.2,
        memoryUsage: 60,
        cpuUsage: 10
      }
    },
    {
      id: 'release-manager',
      type: 'action' as NodeType,
      position: { x: 500, y: 250 },
      data: {
        name: '发布管理器',
        description: '管理系统版本发布和更新',
        status: 'warning' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 3.5,
        memoryUsage: 50,
        cpuUsage: 12
      }
    },
    {
      id: 'supermemory',
      type: 'action' as NodeType,
      position: { x: 700, y: 250 },
      data: {
        name: 'SuperMemory',
        description: '管理智能体的记忆系统',
        status: 'success' as 'idle' | 'running' | 'success' | 'error' | 'warning',
        type: 'action',
        executionTime: 0.6,
        memoryUsage: 120,
        cpuUsage: 18
      }
    }
  ];

  // 根据工作流类型获取对应的节点数据
  const getWorkflowNodes = (type: string): WorkflowNode[] => {
    switch (type) {
      case 'automation-test':
        return automationTestNodes as WorkflowNode[];
      case 'agent-design':
        return agentDesignNodes as WorkflowNode[];
      default:
        return [];
    }
  };

  // 设置文档URL
  useEffect(() => {
    if (activeWorkflowType === 'automation-test') {
      setDocsUrl('https://github.com/yourusername/powerautomation/blob/main/frontend/src/docs/automation_test_workflow.md');
    } else if (activeWorkflowType === 'agent-design') {
      setDocsUrl('https://github.com/yourusername/powerautomation/blob/main/frontend/src/docs/agent_design_workflow.md');
    }
  }, [activeWorkflowType]);

  // 处理节点选择
  const handleNodeSelect = (nodeId: string) => {
    setSelectedNodeId(nodeId === selectedNodeId ? null : nodeId);
  };

  // 处理工作流类型切换
  const handleWorkflowTypeChange = (type: string) => {
    setActiveWorkflowType(type);
    setSelectedNodeId(null);
  };

  return (
    <div className="workflow-content">
      <h2 className="section-title">工作流视图</h2>
      
      <div className="workflow-tabs">
        <button 
          className={`workflow-tab ${activeTab === 'workflow' ? 'active' : ''}`}
          onClick={() => setActiveTab('workflow')}
        >
          工作流
        </button>
        <button 
          className={`workflow-tab ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          文档
        </button>
      </div>
      
      {activeTab === 'workflow' ? (
        <div className="workflow-container">
          <div className="workflow-left-panel">
            <div className="workflow-type-selector">
              <button 
                className={`workflow-type-btn ${activeWorkflowType === 'automation-test' ? 'active' : ''}`}
                onClick={() => handleWorkflowTypeChange('automation-test')}
              >
                自动化测试工作流
              </button>
              <button 
                className={`workflow-type-btn ${activeWorkflowType === 'agent-design' ? 'active' : ''}`}
                onClick={() => handleWorkflowTypeChange('agent-design')}
              >
                自动化智能体设计工作流
              </button>
            </div>
            
            <div className="workflow-visualizer">
              <N8nWorkflowVisualizer 
                nodes={getWorkflowNodes(activeWorkflowType)}
                selectedNodeId={selectedNodeId}
                onNodeSelect={handleNodeSelect}
              />
            </div>
          </div>
          
          <div className="workflow-right-panel">
            {selectedNodeId ? (
              <div className="workflow-sidebar">
                <h3>节点详情</h3>
                {getWorkflowNodes(activeWorkflowType).filter(node => node.id === selectedNodeId).map(node => (
                  <div key={node.id} className="node-detail-card">
                    <div className="node-header">
                      <span className="node-name">{node.data.name}</span>
                      <span className={`node-status ${node.data.status}`}>
                        {node.data.status === 'success' ? '成功' : 
                         node.data.status === 'error' ? '错误' : 
                         node.data.status === 'warning' ? '警告' : '待定'}
                      </span>
                    </div>
                    <div className="node-description">{node.data.description}</div>
                    <div className="node-metrics">
                      <div className="metric">
                        <span className="metric-label">执行时间:</span>
                        <span className="metric-value">{node.data.executionTime}s</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">内存使用:</span>
                        <span className="metric-value">{node.data.memoryUsage}MB</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">CPU使用率:</span>
                        <span className="metric-value">{node.data.cpuUsage}%</span>
                      </div>
                    </div>
                    <div className="node-actions">
                      <button className="node-action-btn">查看源代码</button>
                      <button className="node-action-btn">查看日志</button>
                      {activeWorkflowType === 'automation-test' && (
                        <a 
                          href={`https://github.com/yourusername/powerautomation/blob/main/tests/${
                            node.id === 'integration-test' ? 'integration/component_interaction.test.js' :
                            node.id === 'e2e-test' ? 'e2e/user_workflow.spec.js' :
                            'visual/component_visual.spec.js'
                          }`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="github-link"
                        >
                          在GitHub上查看
                        </a>
                      )}
                      {activeWorkflowType === 'agent-design' && (
                        <a 
                          href={`https://github.com/yourusername/powerautomation/blob/main/agents/${
                            node.id === 'general-agent' ? 'general_agent/general_agent.py' :
                            node.id === 'mcp-coordinator' ? 'mcp/mcp_coordinator.py' :
                            node.id === 'mcp-planner' ? 'mcp/mcp_planner.py' :
                            node.id === 'thought-recorder' ? 'thought_recorder/thought_recorder.py' :
                            node.id === 'release-manager' ? 'release_manager/release_manager.py' :
                            'supermemory/supermemory.py'
                          }`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="github-link"
                        >
                          在GitHub上查看
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="workflow-description">
                <h3>工作流描述</h3>
                {activeWorkflowType === 'automation-test' ? (
                  <div className="workflow-description-content">
                    <p>自动化测试工作流用于执行各类测试，确保系统功能正常运行。</p>
                    <div className="sub-modules">
                      <h4>主要子模块</h4>
                      <ul>
                        <li><strong>集成测试</strong> - 测试组件间的交互</li>
                        <li><strong>端到端测试</strong> - 测试完整工作流程</li>
                        <li><strong>视觉自动化测试</strong> - 测试UI界面和视觉元素</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="workflow-description-content">
                    <p>自动化智能体设计工作流用于构建和管理智能体系统。</p>
                    <div className="sub-modules">
                      <h4>主要子模块</h4>
                      <ul>
                        <li><strong>通用智能体</strong> - 处理用户输入</li>
                        <li><strong>MCP协调器</strong> - 协调多个子系统和组件的工作</li>
                        <li><strong>MCP规划器</strong> - 创建详细的执行计划</li>
                        <li><strong>思维行为记录器</strong> - 记录智能体的思考过程</li>
                        <li><strong>发布管理器</strong> - 管理系统版本发布和更新</li>
                        <li><strong>SuperMemory</strong> - 管理智能体的记忆系统</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="workflow-container">
          <div className="workflow-left-panel">
            <div className="docs-actions">
              {docsUrl && (
                <a 
                  href={docsUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="docs-link"
                >
                  在GitHub上查看完整文档
                </a>
              )}
            </div>
            <div className="docs-frame">
              <iframe 
                src={activeWorkflowType === 'automation-test' 
                  ? '/src/docs/automation_test_workflow.md'
                  : '/src/docs/agent_design_workflow.md'} 
                title="文档"
                className="docs-iframe"
              />
            </div>
          </div>
          <div className="workflow-right-panel">
            <div className="workflow-sidebar">
              <h3>文档目录</h3>
              <ul className="docs-toc">
                <li><a href="#overview">概述</a></li>
                <li><a href="#architecture">架构</a></li>
                <li><a href="#components">组件</a></li>
                <li><a href="#usage">使用方法</a></li>
                <li><a href="#examples">示例</a></li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowContent;
