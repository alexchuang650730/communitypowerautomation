import React, { useState, useEffect } from 'react';
import { useWorkflowContext } from '../App';
import '../styles/LogView.css';

interface LogEntry {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  nodeId?: string;
  details?: string;
  workflowType?: string;
}

interface MemoryStatus {
  status: 'success' | 'warning' | 'error';
  statusText: string;
  trigger: {
    name: string;
    status: 'active' | 'inactive';
  };
  agent: string;
  lastTriggered: string;
}

interface LogViewProps {
  agentType?: string;
  selectedNodeId?: string | null;
  workflowType?: string;
}

const LogView: React.FC<LogViewProps> = ({ agentType = 'general', selectedNodeId: propSelectedNodeId, workflowType: propWorkflowType }) => {
  const workflowContext = useWorkflowContext();
  const selectedNodeId = propSelectedNodeId || (workflowContext ? workflowContext.selectedNodeId : null);
  const activeWorkflowType = propWorkflowType || (workflowContext ? workflowContext.activeWorkflowType : 'automation-test');
  const refreshTrigger = workflowContext ? workflowContext.refreshTrigger : 0;
  
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [memoryStatus, setMemoryStatus] = useState<MemoryStatus>({
    status: 'success',
    statusText: '完整记忆成功',
    trigger: {
      name: 'AGENT',
      status: 'active'
    },
    agent: '接收用户输入',
    lastTriggered: '2025-06-02 10:30'
  });
  const [activeTab, setActiveTab] = useState<'logs' | 'docs'>('logs');
  const [docsUrl, setDocsUrl] = useState<string>('');

  // 自动化测试工作流日志数据
  const automationTestLogs: LogEntry[] = [
    {
      timestamp: '2025-06-02 10:30:00',
      level: 'info',
      message: '开始执行集成测试节点',
      nodeId: 'integration-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:30:05',
      level: 'info',
      message: '初始化测试环境',
      nodeId: 'integration-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:30:10',
      level: 'success',
      message: '组件交互测试通过',
      nodeId: 'integration-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:30:15',
      level: 'info',
      message: '集成测试节点执行成功',
      nodeId: 'integration-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:31:00',
      level: 'info',
      message: '开始执行端到端测试节点',
      nodeId: 'e2e-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:31:05',
      level: 'info',
      message: '获取浏览器实例',
      nodeId: 'e2e-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:31:10',
      level: 'success',
      message: '用户登录流程测试通过',
      nodeId: 'e2e-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:31:15',
      level: 'success',
      message: '工作流创建测试通过',
      nodeId: 'e2e-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:31:20',
      level: 'info',
      message: '端到端测试节点执行成功',
      nodeId: 'e2e-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:32:00',
      level: 'info',
      message: '开始执行视觉自动化测试节点',
      nodeId: 'visual-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:32:05',
      level: 'info',
      message: '获取浏览器实例',
      nodeId: 'visual-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:32:10',
      level: 'info',
      message: '访问组件测试页面',
      nodeId: 'visual-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:32:15',
      level: 'warning',
      message: '按钮组件视觉差异接近阈值',
      nodeId: 'visual-test',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:32:20',
      level: 'error',
      message: '图像比较失败: 差异超过阈值',
      nodeId: 'visual-test',
      details: 'diffPercentage: 0.15, threshold: 0.1',
      workflowType: 'automation-test'
    },
    {
      timestamp: '2025-06-02 10:32:25',
      level: 'error',
      message: '视觉自动化测试节点执行失败',
      nodeId: 'visual-test',
      workflowType: 'automation-test'
    }
  ];

  // 自动化智能体设计工作流日志数据
  const agentDesignLogs: LogEntry[] = [
    {
      timestamp: '2025-06-02 10:30:00',
      level: 'info',
      message: '通用智能体开始处理用户输入',
      nodeId: 'general-agent',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:05',
      level: 'info',
      message: '记录用户输入',
      nodeId: 'general-agent',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:10',
      level: 'info',
      message: '触发SuperMemory记忆检查',
      nodeId: 'general-agent',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:15',
      level: 'success',
      message: '通用智能体处理成功',
      nodeId: 'general-agent',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:20',
      level: 'info',
      message: 'MCP协调器开始工作',
      nodeId: 'mcp-coordinator',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:25',
      level: 'info',
      message: '创建任务计划',
      nodeId: 'mcp-coordinator',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:30',
      level: 'info',
      message: '分配任务给各子系统',
      nodeId: 'mcp-coordinator',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:35',
      level: 'success',
      message: 'MCP协调器执行成功',
      nodeId: 'mcp-coordinator',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:40',
      level: 'info',
      message: 'MCP规划器开始工作',
      nodeId: 'mcp-planner',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:45',
      level: 'info',
      message: '创建执行步骤',
      nodeId: 'mcp-planner',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:50',
      level: 'info',
      message: '分析任务依赖关系',
      nodeId: 'mcp-planner',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:30:55',
      level: 'info',
      message: '创建执行图',
      nodeId: 'mcp-planner',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:00',
      level: 'info',
      message: '优化执行顺序',
      nodeId: 'mcp-planner',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:05',
      level: 'info',
      message: '思维行为记录器开始工作',
      nodeId: 'thought-recorder',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:10',
      level: 'info',
      message: '记录任务进度',
      nodeId: 'thought-recorder',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:15',
      level: 'info',
      message: '分析用户历史回复',
      nodeId: 'thought-recorder',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:20',
      level: 'success',
      message: '思维行为记录器执行成功',
      nodeId: 'thought-recorder',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:25',
      level: 'info',
      message: '发布管理器开始工作',
      nodeId: 'release-manager',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:30',
      level: 'info',
      message: '检查GitHub上是否有新的release',
      nodeId: 'release-manager',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:35',
      level: 'info',
      message: '检查本地版本',
      nodeId: 'release-manager',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:40',
      level: 'info',
      message: '比较版本',
      nodeId: 'release-manager',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:45',
      level: 'warning',
      message: '权限不足，无法推送到主分支',
      nodeId: 'release-manager',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:50',
      level: 'info',
      message: 'SuperMemory开始工作',
      nodeId: 'supermemory',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:31:55',
      level: 'info',
      message: '记录记忆',
      nodeId: 'supermemory',
      workflowType: 'agent-design'
    },
    {
      timestamp: '2025-06-02 10:32:00',
      level: 'success',
      message: 'SuperMemory执行成功',
      nodeId: 'supermemory',
      workflowType: 'agent-design'
    }
  ];

  // 根据工作流类型获取对应的日志数据
  const getWorkflowLogs = (type: string) => {
    switch (type) {
      case 'automation-test':
        return automationTestLogs;
      case 'agent-design':
        return agentDesignLogs;
      default:
        return [];
    }
  };

  // 根据工作流类型获取对应的记忆状态
  const getMemoryStatusForWorkflow = (type: string): MemoryStatus => {
    if (type === 'agent-design') {
      return {
        status: 'success',
        statusText: '完整记忆成功',
        trigger: {
          name: 'AGENT',
          status: 'active'
        },
        agent: '接收用户输入',
        lastTriggered: '2025-06-02 10:30'
      };
    } else {
      return {
        status: 'warning',
        statusText: '部分记忆成功',
        trigger: {
          name: 'TEST',
          status: 'active'
        },
        agent: '自动化测试',
        lastTriggered: '2025-06-02 10:32'
      };
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

  // 当工作流类型变化时，更新记忆状态
  useEffect(() => {
    setMemoryStatus(getMemoryStatusForWorkflow(activeWorkflowType));
  }, [activeWorkflowType]);

  // 当选中节点或工作流类型变化时，过滤日志
  useEffect(() => {
    const workflowLogs = getWorkflowLogs(activeWorkflowType);
    
    if (selectedNodeId) {
      // 如果有选中节点，过滤出与该节点相关的日志
      const nodeRelatedLogs = workflowLogs.filter(
        log => log.nodeId === selectedNodeId
      );
      setFilteredLogs(nodeRelatedLogs);
    } else {
      // 如果没有选中节点，显示当前工作流的所有日志
      setFilteredLogs(workflowLogs);
    }
  }, [selectedNodeId, activeWorkflowType, refreshTrigger]);

  return (
    <div className="log-view">
      <h2 className="section-title">日志视图</h2>
      
      {selectedNodeId && (
        <div className="selected-node-info">
          <span className="selected-node-label">当前选中节点:</span>
          <span className="selected-node-id">{selectedNodeId}</span>
        </div>
      )}
      
      <div className="log-tabs">
        <button 
          className={`log-tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          日志
        </button>
        <button 
          className={`log-tab ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          文档
        </button>
      </div>
      
      {activeTab === 'logs' ? (
        <div className="log-content">
          {activeWorkflowType === 'agent-design' && (
            <div className="log-section">
              <h3 className="log-section-title">SuperMemory记忆状态</h3>
              
              {/* SuperMemory.ai记忆状态卡片 */}
              <div className="memory-status-card">
                <div className="memory-status-header">
                  <span className="memory-status-title">SuperMemory.ai 记忆状态</span>
                  <span className={`memory-status-badge ${memoryStatus.status}`}>{memoryStatus.statusText}</span>
                </div>
                
                <div className="memory-status-content">
                  <div className="memory-status-item">
                    <span className="status-label">触发器:</span>
                    <span className="status-value">{memoryStatus.trigger.name}</span>
                    <span className={`status-badge ${memoryStatus.trigger.status}`}>
                      {memoryStatus.trigger.status === 'active' ? '活跃' : '非活跃'}
                    </span>
                  </div>
                  <div className="memory-status-item">
                    <span className="status-label">通用智能体:</span>
                    <span className="status-value">{memoryStatus.agent}</span>
                  </div>
                  <div className="memory-status-item">
                    <span className="status-label">上次触发:</span>
                    <span className="status-value">{memoryStatus.lastTriggered}</span>
                  </div>
                </div>
                
                <a href="https://supermemory.ai/" target="_blank" rel="noopener noreferrer" className="memory-link">查看完整记忆 →</a>
              </div>
            </div>
          )}
          
          <div className="log-section">
            <h3 className="log-section-title">系统日志</h3>
            <div className="log-entries">
              {filteredLogs.map((log, index) => (
                <div key={index} className={`log-entry ${log.nodeId === selectedNodeId ? 'highlighted' : ''}`}>
                  <span className="log-timestamp">{log.timestamp}</span>
                  <span className={`log-level ${log.level}`}>{log.level.toUpperCase()}</span>
                  <span className="log-message">{log.message}</span>
                  {log.details && (
                    <div className="log-details">
                      <pre>{log.details}</pre>
                    </div>
                  )}
                </div>
              ))}
              {filteredLogs.length === 0 && (
                <div className="no-logs-message">
                  没有与当前节点相关的日志记录
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="docs-content">
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
      )}
    </div>
  );
};

export default LogView;
