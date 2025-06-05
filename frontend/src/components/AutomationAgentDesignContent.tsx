import React, { useState } from 'react';
import '../styles/AutomationAgentDesignContent.css';

interface AutomationAgentDesignContentProps {
  agentType?: string;
}

const AutomationAgentDesignContent: React.FC<AutomationAgentDesignContentProps> = ({ agentType = 'general' }) => {
  const [activeModule, setActiveModule] = useState('problem-solving');

  return (
    <div className="agent-design-content">
      <h3 className="module-title">自动化智能体设计工作流</h3>
      
      <div className="module-tabs">
        <button 
          className={`module-tab ${activeModule === 'problem-solving' ? 'active' : ''}`}
          onClick={() => setActiveModule('problem-solving')}
        >
          问题解决流程
        </button>
        <button 
          className={`module-tab ${activeModule === 'thought-recording' ? 'active' : ''}`}
          onClick={() => setActiveModule('thought-recording')}
        >
          思维行为记录
        </button>
        <button 
          className={`module-tab ${activeModule === 'release-management' ? 'active' : ''}`}
          onClick={() => setActiveModule('release-management')}
        >
          发布管理
        </button>
        <button 
          className={`module-tab ${activeModule === 'test-collection' ? 'active' : ''}`}
          onClick={() => setActiveModule('test-collection')}
        >
          测试与问题收集
        </button>
      </div>
      
      <div className="module-content">
        {activeModule === 'problem-solving' && (
          <div className="module-detail">
            <h4>问题解决流程</h4>
            <div className="flow-diagram">
              <div className="flow-step">
                <div className="step-icon">👤</div>
                <div className="step-content">
                  <h5>通用智能体</h5>
                  <p>接收用户输入，初步分析问题</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="flow-step">
                <div className="step-icon">🔄</div>
                <div className="step-content">
                  <h5>MCP协调器</h5>
                  <p>协调各子系统工作，分发任务</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="flow-step">
                <div className="step-icon">📝</div>
                <div className="step-content">
                  <h5>MCP规划器 & MCP头脑风暴</h5>
                  <p>规划问题解决方案，生成多种解决思路</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="flow-step">
                <div className="step-icon">🔍</div>
                <div className="step-content">
                  <h5>Agent问题解决器</h5>
                  <p>将问题传递给manus.im进行处理</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="flow-step">
                <div className="step-icon">💡</div>
                <div className="step-content">
                  <h5>Manus.im</h5>
                  <p>执行最终问题解决，返回结果</p>
                </div>
              </div>
            </div>
            <div className="additional-info">
              <h5>主动问题解决</h5>
              <p>ProactiveProblemSolver通过读取视觉自动化测试README文件以及集成测试、单元测试的结果，再次要求manus.im进行问题定位分析解决</p>
            </div>
          </div>
        )}
        
        {activeModule === 'thought-recording' && (
          <div className="module-detail">
            <h4>思维行为记录</h4>
            <p>通过ThoughtActionRecorder实现智能体思维和行为的记录与分析</p>
            
            <div className="recording-categories">
              <div className="category-card">
                <div className="category-icon">📊</div>
                <h5>任务进度</h5>
                <p>记录任务执行的各个阶段和完成情况</p>
                <ul>
                  <li>任务启动时间</li>
                  <li>各阶段完成状态</li>
                  <li>任务完成度百分比</li>
                  <li>预计剩余时间</li>
                </ul>
              </div>
              
              <div className="category-card">
                <div className="category-icon">💬</div>
                <h5>用户历史回复及分析</h5>
                <p>记录用户交互历史并进行分析</p>
                <ul>
                  <li>用户输入内容</li>
                  <li>情感分析</li>
                  <li>意图识别</li>
                  <li>关键词提取</li>
                </ul>
              </div>
              
              <div className="category-card">
                <div className="category-icon">🔄</div>
                <h5>创建及更新、取代消除动作</h5>
                <p>记录系统执行的各类操作</p>
                <ul>
                  <li>文件创建记录</li>
                  <li>内容更新历史</li>
                  <li>替换操作日志</li>
                  <li>删除动作追踪</li>
                </ul>
              </div>
              
              <div className="category-card">
                <div className="category-icon">✅</div>
                <h5>更新以及完成的工作</h5>
                <p>记录工作完成情况和更新历史</p>
                <ul>
                  <li>已完成任务列表</li>
                  <li>更新历史记录</li>
                  <li>版本变更追踪</li>
                  <li>工作成果统计</li>
                </ul>
              </div>
            </div>
            
            <div className="knowledge-management">
              <h5>知识管理功能</h5>
              <div className="knowledge-features">
                <div className="feature-item">
                  <h6>测试历史追踪</h6>
                  <p>记录并分析历史测试结果，识别趋势和模式</p>
                </div>
                <div className="feature-item">
                  <h6>历史数据分析</h6>
                  <p>分析历史测试数据，识别趋势和模式</p>
                </div>
                <div className="feature-item">
                  <h6>知识库构建</h6>
                  <p>积累常见问题和解决方案，形成项目专属知识库</p>
                </div>
                <div className="feature-item">
                  <h6>知识图谱集成</h6>
                  <p>构建测试知识图谱，支持复杂关系查询和推理</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeModule === 'release-management' && (
          <div className="module-detail">
            <h4>发布管理</h4>
            <p>通过ReleaseManager实现代码发布和部署的自动化管理</p>
            
            <div className="feature-list">
              <div className="feature-item">
                <div className="feature-icon">🔍</div>
                <div className="feature-content">
                  <h5>检查GitHub上是否有新的release</h5>
                  <p>自动监控GitHub仓库，检测新的发布版本</p>
                  <ul>
                    <li>定期轮询GitHub API</li>
                    <li>比对本地和远程版本</li>
                    <li>发送新版本通知</li>
                  </ul>
                </div>
              </div>
              
              <div className="feature-item">
                <div className="feature-icon">⬇️</div>
                <div className="feature-content">
                  <h5>下载release代码到指定的本地路径</h5>
                  <p>自动获取最新代码并部署到指定位置</p>
                  <ul>
                    <li>支持ZIP/TAR下载</li>
                    <li>支持Git克隆</li>
                    <li>自动解压缩</li>
                    <li>文件完整性校验</li>
                  </ul>
                </div>
              </div>
              
              <div className="feature-item">
                <div className="feature-icon">🔑</div>
                <div className="feature-content">
                  <h5>支持SSH密钥认证</h5>
                  <p>使用安全的SSH密钥进行身份验证</p>
                  <ul>
                    <li>密钥管理</li>
                    <li>自动认证</li>
                    <li>安全连接</li>
                  </ul>
                </div>
              </div>
              
              <div className="feature-item">
                <div className="feature-icon">⬆️</div>
                <div className="feature-content">
                  <h5>提供代码上传功能，自动处理提交和推送</h5>
                  <p>简化代码提交和发布流程</p>
                  <ul>
                    <li>自动暂存更改</li>
                    <li>生成提交信息</li>
                    <li>执行推送操作</li>
                    <li>处理合并冲突</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeModule === 'test-collection' && (
          <div className="module-detail">
            <h4>测试与问题收集</h4>
            <p>通过TestAndIssueCollector执行视觉自动化测试，收集问题并更新README文件</p>
            
            <div className="process-steps">
              <div className="process-step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h5>执行指定的测试脚本</h5>
                  <p>自动运行各类测试脚本，确保系统功能正常</p>
                  <div className="code-example">
                    <pre><code>// 执行测试示例
python run_visual_tests.py --config=config.json</code></pre>
                  </div>
                </div>
              </div>
              
              <div className="process-step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h5>分析测试日志，提取问题信息</h5>
                  <p>从测试输出中识别和提取问题信息</p>
                  <div className="code-example">
                    <pre><code>// 日志分析示例
analyze_logs("test_output.log", "issues.json")</code></pre>
                  </div>
                </div>
              </div>
              
              <div className="process-step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h5>将问题信息结构化存储</h5>
                  <p>以结构化格式保存问题信息，便于后续处理</p>
                  <div className="structured-data">
                    <pre><code>{`{
  "issues": [
    {
      "id": "ISSUE-001",
      "type": "UI",
      "severity": "medium",
      "description": "按钮点击无响应",
      "location": "HomePage.js:45",
      "screenshot": "issue001.png"
    }
  ]
}`}</code></pre>
                  </div>
                </div>
              </div>
              
              <div className="process-step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h5>更新README文件，添加测试发现的问题</h5>
                  <p>自动将发现的问题更新到项目README文件中</p>
                  <div className="readme-example">
                    <pre><code>## 已知问题

### UI问题
- [ISSUE-001] 按钮点击无响应 (中等优先级)
  位置: HomePage.js:45
  [查看截图](./screenshots/issue001.png)

### 功能问题
- [ISSUE-002] 数据加载失败 (高优先级)
  位置: DataService.js:78</code></pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AutomationAgentDesignContent;
