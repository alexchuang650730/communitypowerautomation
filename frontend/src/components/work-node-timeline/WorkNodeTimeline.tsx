import React, { useState, useEffect } from 'react';
import './WorkNodeTimeline.css';

interface WorkNode {
  id: string;
  name: string;
  timestamp: string;
  status: 'success' | 'pending' | 'failed' | 'running';
  type: 'savepoint' | 'rollback' | 'test' | 'deploy' | 'error';
  details?: string;
}

interface WorkNodeTimelineProps {
  onNodeSelect?: (node: WorkNode) => void;
}

const WorkNodeTimeline: React.FC<WorkNodeTimelineProps> = ({ onNodeSelect }) => {
  const [nodes, setNodes] = useState<WorkNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // 模拟从API获取工作节点数据
    const fetchWorkNodes = async () => {
      try {
        setLoading(true);
        // 实际项目中，这里应该是从API获取数据
        // const response = await fetch('/api/work-nodes');
        // const data = await response.json();
        
        // 模拟数据
        const mockData: WorkNode[] = [
          {
            id: 'node_1',
            name: '初始化项目',
            timestamp: '2025-06-01 10:15:22',
            status: 'success',
            type: 'savepoint',
            details: '项目初始化完成，创建基础目录结构'
          },
          {
            id: 'node_2',
            name: '添加核心功能',
            timestamp: '2025-06-01 11:30:45',
            status: 'success',
            type: 'savepoint',
            details: '实现核心功能模块，包括工作流驱动和事件系统'
          },
          {
            id: 'node_3',
            name: '运行集成测试',
            timestamp: '2025-06-01 13:45:10',
            status: 'running',
            type: 'test',
            details: '执行自动化集成测试，验证系统功能'
          },
          {
            id: 'node_4',
            name: '部署测试环境',
            timestamp: '2025-06-01 14:20:30',
            status: 'pending',
            type: 'deploy',
            details: '准备部署到测试环境'
          },
          {
            id: 'node_5',
            name: '回滚到版本1.2',
            timestamp: '2025-06-01 09:10:05',
            status: 'success',
            type: 'rollback',
            details: '由于兼容性问题，回滚到版本1.2'
          }
        ];
        
        setNodes(mockData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching work nodes:', err);
        setLoading(false);
      }
    };

    fetchWorkNodes();

    // 设置定时刷新
    const intervalId = setInterval(() => {
      fetchWorkNodes();
    }, 30000); // 每30秒刷新一次

    return () => clearInterval(intervalId);
  }, []);

  const handleNodeClick = (node: WorkNode) => {
    setSelectedNode(node.id === selectedNode ? null : node.id);
    if (onNodeSelect && node.id !== selectedNode) {
      onNodeSelect(node);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return '#4CAF50';
      case 'pending':
        return '#FFC107';
      case 'failed':
        return '#F44336';
      case 'running':
        return '#2196F3';
      default:
        return '#9E9E9E';
    }
  };

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'savepoint':
        return '💾';
      case 'rollback':
        return '⏮️';
      case 'test':
        return '🧪';
      case 'deploy':
        return '🚀';
      case 'error':
        return '⚠️';
      default:
        return '📌';
    }
  };

  if (loading) {
    return <div className="work-node-loading">加载工作节点...</div>;
  }

  return (
    <div className="work-node-timeline">
      <div className="work-node-header">
        <h2>工作节点时间线</h2>
        <button className="refresh-button" onClick={() => setNodes([...nodes])}>
          刷新
        </button>
      </div>
      
      <div className="timeline-container">
        <div className="timeline-line"></div>
        {nodes.map((node) => (
          <div 
            key={node.id}
            className={`timeline-node ${node.id === selectedNode ? 'selected' : ''}`}
            onClick={() => handleNodeClick(node)}
          >
            <div 
              className="node-indicator"
              style={{ backgroundColor: getStatusColor(node.status) }}
            >
              <span className="node-type-icon">{getNodeTypeIcon(node.type)}</span>
            </div>
            <div className="node-content">
              <div className="node-header">
                <h4 className="node-name">{node.name}</h4>
                <span className="node-timestamp">{node.timestamp}</span>
              </div>
              {node.id === selectedNode && node.details && (
                <div className="node-details">
                  {node.details}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkNodeTimeline;
