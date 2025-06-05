import React, { useState, useEffect } from 'react';
import '../styles/SavepointManager.css';

interface Savepoint {
  id: string;
  timestamp: string;
  description: string;
  project_hash: string;
  path: string;
  test_status: 'pending' | 'success' | 'failed';
  deployment_status: 'pending' | 'success' | 'failed';
  created_at: string;
  tags: string[];
  status: 'stable' | 'unstable';
  workflowType?: string;
}

interface RollbackHistory {
  id: string;
  savepoint_id: string;
  timestamp: string;
  reason: string;
  status: 'success' | 'failed';
  before_hash: string;
  after_hash: string;
  files_changed: number;
  created_at: string;
}

interface SavepointManagerProps {
  workflowType?: string;
  selectedNodeId?: string | null;
}

const SavepointManager: React.FC<SavepointManagerProps> = ({
  workflowType = 'automation-test',
  selectedNodeId = null
}) => {
  const [savepoints, setSavepoints] = useState<Savepoint[]>([]);
  const [rollbackHistory, setRollbackHistory] = useState<RollbackHistory[]>([]);
  const [selectedSavepoint, setSelectedSavepoint] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'savepoints' | 'history'>('savepoints');
  const [isCreating, setIsCreating] = useState(false);
  const [newSavepointDesc, setNewSavepointDesc] = useState('');
  const [isRollbackModalOpen, setIsRollbackModalOpen] = useState(false);
  const [rollbackReason, setRollbackReason] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'stable' | 'unstable'>('all');

  // 模拟从后端加载保存点数据
  useEffect(() => {
    const fetchSavepoints = async () => {
      setIsLoading(true);
      try {
        // 实际项目中应该通过API调用获取数据
        // 这里使用模拟数据
        const response = await fetch('/src/data/savepoints.json');
        const data = await response.json();
        setSavepoints(data.savepoints || []);
      } catch (error) {
        console.error('加载保存点数据失败:', error);
        // 使用模拟数据
        setSavepoints([
          {
            id: "sp-001",
            timestamp: "2025-06-01T14:30:00Z",
            description: "初始工作流设计",
            project_hash: "hash123",
            path: "/path/to/savepoint",
            test_status: "success",
            deployment_status: "pending",
            created_at: "2025-06-01T14:30:00Z",
            tags: ["initial", "design"],
            status: "stable"
          },
          {
            id: "sp-002",
            timestamp: "2025-06-01T16:45:00Z",
            description: "集成测试完成",
            project_hash: "hash456",
            path: "/path/to/savepoint2",
            test_status: "success",
            deployment_status: "pending",
            created_at: "2025-06-01T16:45:00Z",
            tags: ["test", "integration"],
            status: "stable"
          }
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    const fetchRollbackHistory = async () => {
      try {
        // 实际项目中应该通过API调用获取数据
        // 这里使用模拟数据
        const response = await fetch('/src/data/rollback_history.json');
        const data = await response.json();
        setRollbackHistory(data || []);
      } catch (error) {
        console.error('加载回滚历史数据失败:', error);
        // 使用模拟数据
        setRollbackHistory([
          {
            id: "rb-001",
            savepoint_id: "sp-001",
            timestamp: "2025-06-01T15:30:00Z",
            reason: "修复集成测试问题",
            status: "success",
            before_hash: "hash123",
            after_hash: "hash456",
            files_changed: 5,
            created_at: "2025-06-01T15:30:00Z"
          }
        ]);
      }
    };

    fetchSavepoints();
    fetchRollbackHistory();
  }, []);

  // 过滤保存点
  const filteredSavepoints = savepoints.filter(savepoint => {
    if (filter === 'all') return true;
    return savepoint.status === filter;
  });

  // 根据工作流类型过滤保存点
  const workflowSavepoints = filteredSavepoints.filter(savepoint => 
    savepoint.workflowType === workflowType
  );

  // 创建新保存点
  const handleCreateSavepoint = async () => {
    if (!newSavepointDesc.trim()) return;
    
    setIsLoading(true);
    try {
      // 实际项目中应该通过API调用创建保存点
      // 这里模拟创建过程
      const newSavepoint = {
        id: `sp-${Date.now()}`,
        timestamp: new Date().toISOString(),
        description: newSavepointDesc,
        project_hash: `hash-${Date.now()}`,
        path: `/path/to/savepoint-${Date.now()}`,
        test_status: "pending" as const,
        deployment_status: "pending" as const,
        created_at: new Date().toISOString(),
        tags: [],
        workflowType,
        status: "stable" as const
      };
      
      setSavepoints([...savepoints, newSavepoint]);
      setNewSavepointDesc('');
      setIsCreating(false);
    } catch (error) {
      console.error('创建保存点失败:', error);
      alert('创建保存点失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 回滚到选定的保存点
  const handleRollback = async () => {
    if (!selectedSavepoint || !rollbackReason.trim()) return;
    
    setIsLoading(true);
    try {
      // 实际项目中应该通过API调用执行回滚
      // 这里模拟回滚过程
      const targetSavepoint = savepoints.find(sp => sp.id === selectedSavepoint);
      if (!targetSavepoint) throw new Error('保存点不存在');
      
      const newRollback = {
        id: `rb-${Date.now()}`,
        savepoint_id: selectedSavepoint,
        timestamp: new Date().toISOString(),
        reason: rollbackReason,
        status: "success" as const,
        before_hash: "current-hash",
        after_hash: targetSavepoint.project_hash,
        files_changed: Math.floor(Math.random() * 10) + 1,
        created_at: new Date().toISOString()
      };
      
      setRollbackHistory([...rollbackHistory, newRollback]);
      setRollbackReason('');
      setIsRollbackModalOpen(false);
      setSelectedSavepoint(null);
      
      // 显示成功消息
      alert(`已成功回滚到保存点: ${targetSavepoint.description}`);
    } catch (error) {
      console.error('回滚失败:', error);
      alert('回滚失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 格式化时间戳
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch (e) {
      return timestamp;
    }
  };

  return (
    <div className="savepoint-manager">
      <h2 className="section-title">保存点与回滚管理</h2>
      
      <div className="savepoint-tabs">
        <button 
          className={`savepoint-tab ${activeTab === 'savepoints' ? 'active' : ''}`}
          onClick={() => setActiveTab('savepoints')}
        >
          保存点
        </button>
        <button 
          className={`savepoint-tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          回滚历史
        </button>
      </div>
      
      {activeTab === 'savepoints' && (
        <div className="savepoint-content">
          <div className="savepoint-actions">
            <div className="filter-controls">
              <label>筛选: </label>
              <select 
                value={filter} 
                onChange={(e) => setFilter(e.target.value as any)}
                className="filter-select"
              >
                <option value="all">全部</option>
                <option value="stable">稳定</option>
                <option value="unstable">不稳定</option>
              </select>
            </div>
            
            <button 
              className="create-savepoint-btn"
              onClick={() => setIsCreating(true)}
              disabled={isLoading}
            >
              创建保存点
            </button>
          </div>
          
          {isCreating && (
            <div className="create-savepoint-form">
              <input
                type="text"
                placeholder="保存点描述"
                value={newSavepointDesc}
                onChange={(e) => setNewSavepointDesc(e.target.value)}
                className="savepoint-input"
              />
              <div className="form-actions">
                <button 
                  className="save-btn"
                  onClick={handleCreateSavepoint}
                  disabled={!newSavepointDesc.trim() || isLoading}
                >
                  保存
                </button>
                <button 
                  className="cancel-btn"
                  onClick={() => {
                    setIsCreating(false);
                    setNewSavepointDesc('');
                  }}
                >
                  取消
                </button>
              </div>
            </div>
          )}
          
          {isLoading ? (
            <div className="loading-indicator">加载中...</div>
          ) : (
            <div className="savepoint-list">
              {workflowSavepoints.length > 0 ? (
                workflowSavepoints.map((savepoint) => (
                  <div 
                    key={savepoint.id} 
                    className={`savepoint-item ${selectedSavepoint === savepoint.id ? 'selected' : ''} ${savepoint.status}`}
                    onClick={() => setSelectedSavepoint(savepoint.id === selectedSavepoint ? null : savepoint.id)}
                  >
                    <div className="savepoint-header">
                      <span className="savepoint-id">{savepoint.id}</span>
                      <span className={`savepoint-status ${savepoint.status}`}>
                        {savepoint.status === 'stable' ? '稳定' : '不稳定'}
                      </span>
                    </div>
                    <div className="savepoint-description">{savepoint.description}</div>
                    <div className="savepoint-timestamp">
                      创建于: {formatTimestamp(savepoint.created_at)}
                    </div>
                    <div className="savepoint-tags">
                      {savepoint.tags.map((tag, index) => (
                        <span key={index} className="savepoint-tag">{tag}</span>
                      ))}
                    </div>
                    
                    {selectedSavepoint === savepoint.id && (
                      <div className="savepoint-actions">
                        <button 
                          className="rollback-btn"
                          onClick={() => setIsRollbackModalOpen(true)}
                        >
                          回滚到此保存点
                        </button>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-savepoints-message">
                  没有找到与当前工作流相关的保存点
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'history' && (
        <div className="history-content">
          {isLoading ? (
            <div className="loading-indicator">加载中...</div>
          ) : (
            <div className="history-list">
              {rollbackHistory.length > 0 ? (
                rollbackHistory.map((history) => {
                  const relatedSavepoint = savepoints.find(sp => sp.id === history.savepoint_id);
                  return (
                    <div key={history.id} className="history-item">
                      <div className="history-header">
                        <span className="history-id">{history.id}</span>
                        <span className={`history-status ${history.status}`}>
                          {history.status === 'success' ? '成功' : '失败'}
                        </span>
                      </div>
                      <div className="history-reason">
                        原因: {history.reason}
                      </div>
                      <div className="history-savepoint">
                        回滚到: {relatedSavepoint?.description || history.savepoint_id}
                      </div>
                      <div className="history-details">
                        <div>变更文件数: {history.files_changed}</div>
                        <div>执行时间: {formatTimestamp(history.created_at)}</div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="no-history-message">
                  没有回滚历史记录
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {isRollbackModalOpen && (
        <div className="modal-overlay">
          <div className="rollback-modal">
            <h3>回滚确认</h3>
            <p>您确定要回滚到以下保存点吗？</p>
            <div className="selected-savepoint-info">
              {savepoints.find(sp => sp.id === selectedSavepoint)?.description}
            </div>
            <div className="rollback-form">
              <label>回滚原因:</label>
              <textarea
                value={rollbackReason}
                onChange={(e) => setRollbackReason(e.target.value)}
                placeholder="请输入回滚原因"
                className="rollback-reason-input"
              />
            </div>
            <div className="modal-actions">
              <button 
                className="confirm-btn"
                onClick={handleRollback}
                disabled={!rollbackReason.trim() || isLoading}
              >
                确认回滚
              </button>
              <button 
                className="cancel-btn"
                onClick={() => {
                  setIsRollbackModalOpen(false);
                  setRollbackReason('');
                }}
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavepointManager;
