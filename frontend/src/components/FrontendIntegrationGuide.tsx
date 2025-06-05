import '../styles/FrontendIntegrationGuide.css';

/**
 * 前端集成指南组件
 * 用于展示如何在现有项目中集成新组件
 */
const FrontendIntegrationGuide = () => {
  return (
    <div className="integration-guide">
      <h1>PowerAutomation前端集成指南</h1>
      
      <section className="guide-section">
        <h2>1. 复制组件文件</h2>
        <p>将GitHub仓库中的组件文件复制到您的项目中：</p>
        <pre>
          {`
# 工作流可视化组件
src/components/N8nWorkflowVisualizer.tsx
src/components/WorkflowIntegrationPanel.tsx

# 节点组件
src/components/workflow-nodes/TriggerNode.tsx
src/components/workflow-nodes/ActionNode.tsx
src/components/workflow-nodes/ConditionNode.tsx
src/components/workflow-nodes/ErrorNode.tsx

# 样式文件
src/styles/N8nWorkflowVisualizer.css
src/styles/WorkflowIntegrationPanel.css
          `}
        </pre>
      </section>
      
      <section className="guide-section">
        <h2>2. 安装依赖</h2>
        <p>确保安装以下依赖：</p>
        <pre>
          {`npm install react-flow-renderer styled-components @mui/material @mui/icons-material`}
        </pre>
      </section>
      
      <section className="guide-section">
        <h2>3. 在App.tsx中集成组件</h2>
        <p>在您的App.tsx中添加以下代码：</p>
        <pre>
          {`
import N8nWorkflowVisualizer from './components/N8nWorkflowVisualizer';
import WorkflowIntegrationPanel from './components/WorkflowIntegrationPanel';
import './styles/N8nWorkflowVisualizer.css';
import './styles/WorkflowIntegrationPanel.css';

// 在您的App组件中添加以下代码（在智能体卡片区域下方）
<div className="workflow-container">
  <WorkflowIntegrationPanel />
  <N8nWorkflowVisualizer />
</div>
          `}
        </pre>
      </section>
      
      <section className="guide-section">
        <h2>4. 添加样式</h2>
        <p>在您的App.css中添加以下样式：</p>
        <pre>
          {`
.workflow-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-top: 20px;
  padding: 0 20px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .workflow-container {
    padding: 0 10px;
  }
}
          `}
        </pre>
      </section>
      
      <section className="guide-section">
        <h2>5. 配置API端点</h2>
        <p>确保在环境配置中设置正确的API端点：</p>
        <pre>
          {`
// .env 或 .env.local 文件
REACT_APP_API_ENDPOINT=http://your-api-endpoint/api
          `}
        </pre>
      </section>
      
      <section className="guide-section">
        <h2>6. 测试集成</h2>
        <p>启动您的应用并验证工作流可视化组件是否正确显示：</p>
        <pre>
          {`npm run dev`}
        </pre>
        <p>您应该能在智能体卡片区域下方看到工作流可视化组件。</p>
      </section>
      
      <section className="guide-section">
        <h2>7. 故障排除</h2>
        <ul>
          <li>如果组件不显示，请检查控制台是否有错误</li>
          <li>确保所有依赖都已正确安装</li>
          <li>验证API端点是否正确配置</li>
          <li>检查样式文件是否正确导入</li>
        </ul>
      </section>
    </div>
  );
};

export default FrontendIntegrationGuide;
