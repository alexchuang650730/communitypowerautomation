import React, { useState, useEffect } from 'react';
import '../styles/WorkflowIntegrationPanel.css';

interface WorkflowStatus {
  isRunning: boolean;
  currentNode: string | null;
  startTime: string;
  lastUpdateTime: string;
}

interface WorkflowData {
  nodes: any[];
  connections: any[];
  status: WorkflowStatus;
}

const WorkflowIntegrationPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'timeline' | 'savepoints' | 'history'>('timeline');
  const [workflowData, setWorkflowData] = useState<WorkflowData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 模拟从API获取工作流数据
    const fetchWorkflowData = async () => {
      try {
        setLoading(true);
        // 实际项目中，这里应该是从API获取数据
        // const response = await fetch('/api/workflow/integration');
        // const data = await response.json();
        
        // 模拟数据
        const mockData: WorkflowData = {
          nodes: [
            {
              id: 'node_1',
              type: 'trigger',
              name: 'GitHub Release',
              description: '检测到新版本 v1.0.0',
              status: 'success',
              timestamp: '2025-06-01T14:00:00',
              data: {
                release_version: 'v1.0.0',
                release_url: 'https://github.com/example/repo/releases/tag/v1.0.0'
              }
            },
            {
              id: 'node_2',
              type: 'action',
              name: '下载代码',
              description: '从GitHub下载代码',
              status: 'success',
              timestamp: '2025-06-01T14:01:30',
              data: {
                path: '/home/user/downloads/v1.0.0'
              }
            },
            {
              id: 'node_3',
              type: 'action',
              name: '运行测试',
              description: '执行单元测试',
              status: 'running',
              timestamp: '2025-06-01T14:02:45',
              data: {
                test_type: 'unit',
                test_path: 'src/main.py'
              }
            }
          ],
          connections: [
            {
              id: 'conn_1',
              source: 'node_1',
              target: 'node_2',
              type: 'success'
            },
            {
              id: 'conn_2',
              source: 'node_2',
              target: 'node_3',
              type: 'success'
            }
          ],
          status: {
            isRunning: true,
            currentNode: 'node_3',
            startTime: '2025-06-01T14:00:00',
            lastUpdateTime: '2025-06-01T14:02:45'
          }
        };
        
        setWorkflowData(mockData);
        setLoading(false);
      } catch (err) {
        setError('加载工作流数据失败');
        setLoading(false);
        console.error('Error fetching workflow data:', err);
      }
    };

    fetchWorkflowData();

    // 设置定时刷新
    const intervalId = setInterval(() => {
      fetchWorkflowData();
    }, 10000); // 每10秒刷新一次

    return () => clearInterval(intervalId);
  }, []);

  const renderTimeline = () => {
    if (!workflowData) return null;

    return (
      <div className="workflow-timeline">
        {workflowData.nodes.map((node) => (
          <div 
            key={node.id} 
            className={`timeline-item ${node.status}`}
          >
            <div className="timeline-time">
              {new Date(node.timestamp).toLocaleTimeString()}
            </div>
            <div className="timeline-content">
              <div className="timeline-header">
                <span className="timeline-type">{node.type}</span>
                <span className="timeline-name">{node.name}</span>
              </div>
              <div className="timeline-description">{node.description}</div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderSavepoints = () => {
    // 模拟保存点数据
    const savepoints = [
      {
        id: 'sp_1234',
        timestamp: '2025-06-01T13:45:00',
        description: '测试通过的版本',
        project_hash: 'abc123def456',
        path: '/home/user/savepoints/sp_1234'
      },
      {
        id: 'sp_1233',
        timestamp: '2025-06-01T12:30:00',
        description: '初始版本',
        project_hash: '789ghi101112',
        path: '/home/user/savepoints/sp_1233'
      }
    ];

    return (
      <div className="workflow-savepoints">
        {savepoints.map((savepoint) => (
          <div key={savepoint.id} className="savepoint-item">
            <div className="savepoint-header">
              <span className="savepoint-id">{savepoint.id}</span>
              <span className="savepoint-time">
                {new Date(savepoint.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="savepoint-description">{savepoint.description}</div>
            <div className="savepoint-hash">Hash: {savepoint.project_hash}</div>
            <div className="savepoint-actions">
              <button className="savepoint-button">回滚到此版本</button>
              <button className="savepoint-button">查看详情</button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderHistory = () => {
    // 模拟回滚历史数据
    const rollbackHistory = [
      {
        id: 'rb_567',
        timestamp: '2025-06-01T11:20:00',
        savepoint_id: 'sp_1232',
        status: 'success',
        reason: '修复测试失败',
        user: 'admin'
      },
      {
        id: 'rb_566',
        timestamp: '2025-05-31T16:45:00',
        savepoint_id: 'sp_1230',
        status: 'failed',
        reason: '自动回滚 - 连续测试失败',
        error: '回滚后验证失败',
        user: 'system'
      }
    ];

    return (
      <div className="workflow-history">
        {rollbackHistory.map((history) => (
          <div 
            key={history.id} 
            className={`history-item ${history.status}`}
          >
            <div className="history-header">
              <span className="history-id">{history.id}</span>
              <span className="history-time">
                {new Date(history.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="history-savepoint">保存点: {history.savepoint_id}</div>
            <div className="history-reason">原因: {history.reason}</div>
            <div className="history-user">执行者: {history.user}</div>
            {history.error && (
              <div className="history-error">错误: {history.error}</div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'timeline':
        return renderTimeline();
      case 'savepoints':
        return renderSavepoints();
      case 'history':
        return renderHistory();
      default:
        return null;
    }
  };

  if (loading) {
    return <div className="workflow-integration-loading">加载中...</div>;
  }

  if (error) {
    return <div className="workflow-integration-error">{error}</div>;
  }

  return (
    <div className="workflow-integration-panel">
      <div className="workflow-tabs">
        <button 
          className={`tab-button ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          工作节点时间线
        </button>
        <button 
          className={`tab-button ${activeTab === 'savepoints' ? 'active' : ''}`}
          onClick={() => setActiveTab('savepoints')}
        >
          保存点列表
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          回滚历史
        </button>
      </div>
      <div className="workflow-content">
        {renderContent()}
      </div>
      {workflowData && workflowData.status.isRunning && (
        <div className="workflow-status-bar">
          <div className="status-indicator running"></div>
          <div className="status-text">
            工作流正在运行 - 当前节点: {workflowData.status.currentNode}
          </div>
          <div className="status-time">
            开始时间: {new Date(workflowData.status.startTime).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowIntegrationPanel;
