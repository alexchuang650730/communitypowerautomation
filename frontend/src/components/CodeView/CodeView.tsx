import React, { useState, useEffect } from 'react';
import { useWorkflowContext } from '../../App';
import './CodeView.css';

interface CodeViewProps {
  agentType?: string;
  selectedNodeId?: string | null;
  workflowType?: string;
}

const CodeView: React.FC<CodeViewProps> = ({ agentType = 'general', selectedNodeId: propSelectedNodeId, workflowType: propWorkflowType }) => {
  const workflowContext = useWorkflowContext();
  const selectedNodeId = propSelectedNodeId || (workflowContext ? workflowContext.selectedNodeId : null);
  const activeWorkflowType = propWorkflowType || (workflowContext ? workflowContext.activeWorkflowType : 'automation-test');
  const refreshTrigger = workflowContext ? workflowContext.refreshTrigger : 0;
  
  const [activeTab, setActiveTab] = useState<'code' | 'docs'>('code');
  const [codeContent, setCodeContent] = useState<string>('// 选择一个节点查看代码');
  const [docsUrl, setDocsUrl] = useState<string>('');
  const [githubUrl, setGithubUrl] = useState<string>('');

  // 获取代码内容
  useEffect(() => {
    if (!selectedNodeId) {
      setCodeContent('// 选择一个节点查看代码');
      return;
    }

    // 根据工作流类型和节点ID获取相应的代码
    const fetchCode = async () => {
      try {
        let code = '';
        let githubPath = '';

        if (activeWorkflowType === 'automation-test') {
          switch (selectedNodeId) {
            case 'integration-test':
              code = `// 集成测试代码
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from '../components/agent-cards/AgentCard';
import { WorkflowContent } from '../components/WorkflowContent';

describe('组件交互测试', () => {
  test('AgentCard 与 WorkflowContent 交互', () => {
    // 渲染组件
    render(
      <>
        <AgentCard 
          id="test-agent" 
          name="测试智能体" 
          description="用于测试的智能体"
          status="active" 
        />
        <WorkflowContent agentType="test" />
      </>
    );
    
    // 模拟点击事件
    const agentCard = screen.getByText('测试智能体');
    fireEvent.click(agentCard);
    
    // 验证交互结果
    expect(screen.getByText('测试智能体工作流')).toBeInTheDocument();
  });
  
  test('数据传递正确性', () => {
    // 测试数据
    const testData = { id: 'test-data', value: 'test-value' };
    
    // 渲染组件并传递数据
    render(
      <WorkflowContent 
        agentType="test" 
        testData={testData}
      />
    );
    
    // 验证数据传递
    expect(screen.getByText('test-value')).toBeInTheDocument();
  });
});`;
              githubPath = 'tests/integration/component_interaction.test.js';
              break;
            case 'e2e-test':
              code = `// 端到端测试代码
import { test, expect } from '@playwright/test';

test.describe('端到端测试', () => {
  test('用户登录流程', async ({ page }) => {
    // 访问登录页面
    await page.goto('http://localhost:5178/login');
    
    // 填写登录表单
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password123');
    
    // 点击登录按钮
    await page.click('button[type="submit"]');
    
    // 验证登录成功
    await expect(page.locator('.welcome-message')).toContainText('欢迎, testuser');
  });
  
  test('工作流创建测试', async ({ page }) => {
    // 登录
    await page.goto('http://localhost:5178/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // 导航到工作流页面
    await page.click('text=工作流');
    
    // 创建新工作流
    await page.click('button:has-text("创建工作流")');
    await page.fill('input[name="workflow-name"]', '测试工作流');
    await page.click('button:has-text("保存")');
    
    // 验证工作流创建成功
    await expect(page.locator('.workflow-list')).toContainText('测试工作流');
  });
});`;
              githubPath = 'tests/e2e/user_workflow.spec.js';
              break;
            case 'visual-test':
              code = `// 视觉自动化测试代码
import { test, expect } from '@playwright/test';

test.describe('视觉自动化测试', () => {
  test('组件视觉测试', async ({ page }) => {
    // 访问组件测试页面
    await page.goto('http://localhost:5178/component-test');
    
    // 等待组件完全加载
    await page.waitForSelector('.test-component', { state: 'visible' });
    
    // 对按钮组件进行截图
    await expect(page.locator('.button-component')).toHaveScreenshot('button.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 对卡片组件进行截图
    await expect(page.locator('.card-component')).toHaveScreenshot('card.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 测试响应式布局
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.responsive-component')).toHaveScreenshot('responsive-mobile.png', {
      maxDiffPixelRatio: 0.1
    });
    
    await page.setViewportSize({ width: 1280, height: 800 });
    await expect(page.locator('.responsive-component')).toHaveScreenshot('responsive-desktop.png', {
      maxDiffPixelRatio: 0.1
    });
  });
  
  test('暗色模式视觉测试', async ({ page }) => {
    // 访问测试页面
    await page.goto('http://localhost:5178/component-test');
    
    // 切换到暗色模式
    await page.click('.theme-toggle');
    
    // 等待主题切换完成
    await page.waitForSelector('body.dark-theme', { state: 'visible' });
    
    // 对暗色模式下的组件进行截图
    await expect(page.locator('.button-component')).toHaveScreenshot('button-dark.png', {
      maxDiffPixelRatio: 0.1
    });
  });
});`;
              githubPath = 'tests/visual/component_visual.spec.js';
              break;
            default:
              code = '// 未找到与所选节点对应的代码';
          }
        } else if (activeWorkflowType === 'agent-design') {
          switch (selectedNodeId) {
            case 'general-agent':
              code = `# 通用智能体代码
import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

class GeneralAgent:
    """
    通用智能体类
    处理用户输入，作为系统的主要交互入口
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化通用智能体
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "config", "general_agent.json")
        self.config = self._load_config()
        self.logger = self._setup_logger()
        self.memory_manager = None  # 将在后续初始化SuperMemory
        
        self.logger.info("通用智能体初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {str(e)}")
                return {}
        return {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("GeneralAgent")
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        logger.addHandler(console_handler)
        
        return logger
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            处理结果
        """
        self.logger.info(f"接收用户输入: {user_input}")
        
        # 记录用户输入
        self._record_input(user_input)
        
        # 触发SuperMemory记忆检查
        memory_result = self._check_memory(user_input)
        
        # 路由请求到适当的处理组件
        routing_result = self._route_request(user_input, memory_result)
        
        return {
            "status": "success",
            "input": user_input,
            "memory_result": memory_result,
            "routing_result": routing_result,
            "timestamp": self._get_timestamp()
        }
    
    def _record_input(self, user_input: str) -> None:
        """记录用户输入"""
        self.logger.info("记录用户输入")
        # 实际实现会将输入保存到数据库或日志文件
        pass
    
    def _check_memory(self, user_input: str) -> Dict[str, Any]:
        """触发SuperMemory记忆检查"""
        self.logger.info("触发SuperMemory记忆检查")
        # 实际实现会调用SuperMemory组件
        return {
            "has_memory": False,
            "related_memories": []
        }
    
    def _route_request(self, user_input: str, memory_result: Dict[str, Any]) -> Dict[str, Any]:
        """路由请求到适当的处理组件"""
        self.logger.info("路由请求到适当的处理组件")
        # 实际实现会根据输入内容和记忆结果决定路由目标
        return {
            "target_component": "mcp_coordinator",
            "priority": "normal"
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()`;
              githubPath = 'agents/general_agent/general_agent.py';
              break;
            case 'mcp-coordinator':
              code = `# MCP协调器代码
import os
import sys
import json
import logging
import threading
from typing import Dict, Any, List, Optional

class MCPCoordinator:
    """
    MCP协调器类
    协调多个子系统和组件的工作，确保系统整体协同运行
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化MCP协调器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "config", "mcp_coordinator.json")
        self.config = self._load_config()
        self.logger = self._setup_logger()
        self.active_tasks = {}
        self.task_lock = threading.Lock()
        
        self.logger.info("MCP协调器初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {str(e)}")
                return {}
        return {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("MCPCoordinator")
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        logger.addHandler(console_handler)
        
        return logger
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理请求
        
        Args:
            request: 请求数据
            
        Returns:
            处理结果
        """
        self.logger.info(f"接收请求: {request}")
        
        # 创建任务计划
        task_plan = self._create_task_plan(request)
        
        # 分配任务给各子系统
        allocation_result = self._allocate_tasks(task_plan)
        
        # 监控任务执行状态
        monitoring_result = self._monitor_tasks(allocation_result)
        
        # 汇总执行结果
        summary_result = self._summarize_results(monitoring_result)
        
        return {
            "status": "success",
            "task_plan": task_plan,
            "allocation_result": allocation_result,
            "monitoring_result": monitoring_result,
            "summary_result": summary_result,
            "timestamp": self._get_timestamp()
        }
    
    def _create_task_plan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """创建任务计划"""
        self.logger.info("创建任务计划")
        # 实际实现会根据请求内容创建详细的任务计划
        return {
            "task_id": f"task_{self._get_timestamp()}",
            "steps": [
                {"id": "step_1", "component": "mcp_planner", "action": "create_execution_plan"},
                {"id": "step_2", "component": "thought_recorder", "action": "record_task_progress"},
                {"id": "step_3", "component": "supermemory", "action": "store_memory"}
            ],
            "priority": request.get("priority", "normal")
        }
    
    def _allocate_tasks(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分配任务给各子系统"""
        self.logger.info("分配任务给各子系统")
        # 实际实现会将任务分配给相应的组件
        allocation_result = {
            "allocations": [],
            "status": "success"
        }
        
        for step in task_plan.get("steps", []):
            allocation_result["allocations"].append({
                "step_id": step["id"],
                "component": step["component"],
                "status": "allocated"
            })
        
        return allocation_result
    
    def _monitor_tasks(self, allocation_result: Dict[str, Any]) -> Dict[str, Any]:
        """监控任务执行状态"""
        self.logger.info("监控任务执行状态")
        # 实际实现会实时监控各组件的任务执行情况
        monitoring_result = {
            "task_statuses": [],
            "overall_status": "success"
        }
        
        for allocation in allocation_result.get("allocations", []):
            monitoring_result["task_statuses"].append({
                "step_id": allocation["step_id"],
                "component": allocation["component"],
                "status": "completed",
                "completion_time": self._get_timestamp()
            })
        
        return monitoring_result
    
    def _summarize_results(self, monitoring_result: Dict[str, Any]) -> Dict[str, Any]:
        """汇总执行结果"""
        self.logger.info("汇总执行结果")
        # 实际实现会汇总所有任务的执行结果
        return {
            "success_count": len(monitoring_result.get("task_statuses", [])),
            "failed_count": 0,
            "overall_status": "success",
            "completion_time": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()`;
              githubPath = 'agents/mcp/mcp_coordinator.py';
              break;
            default:
              code = '// 未找到与所选节点对应的代码';
          }
        } else {
          code = '// 未找到与所选工作流类型对应的代码';
        }

        setCodeContent(code);
        setGithubUrl(githubPath ? `https://github.com/example/repo/blob/main/${githubPath}` : '');
      } catch (error) {
        console.error('获取代码内容失败:', error);
        setCodeContent('// 获取代码内容失败');
      }
    };

    fetchCode();
  }, [selectedNodeId, activeWorkflowType, refreshTrigger]);

  // 渲染测试代码内容
  const renderTestCode = () => {
    if (activeWorkflowType === 'automation-test') {
      switch (selectedNodeId) {
        case 'integration-test':
          return (
            <div className="code-section">
              <h3 className="code-section-title">集成测试代码</h3>
              
              <div className="code-block">
                <div className="code-header">
                  <span className="code-filename">integration_test.js</span>
                  <div className="code-actions">
                    <button className="code-action-button">
                      <span className="code-action-icon">📋</span>
                      复制
                    </button>
                    <button className="code-action-button">
                      <span className="code-action-icon">▶️</span>
                      运行
                    </button>
                  </div>
                </div>
                
                <pre className="code-content-block">
                  <code>
                    {codeContent}
                  </code>
                </pre>
              </div>
            </div>
          );
        default:
          return (
            <div className="code-section">
              <pre className="code-content-block">
                <code>
                  {codeContent}
                </code>
              </pre>
            </div>
          );
      }
    }
    
    return (
      <div className="code-section">
        <pre className="code-content-block">
          <code>
            {codeContent}
          </code>
        </pre>
      </div>
    );
  };

  return (
    <div className="code-view">
      <div className="code-view-header">
        <div className="code-view-tabs">
          <button 
            className={`code-view-tab ${activeTab === 'code' ? 'active' : ''}`}
            onClick={() => setActiveTab('code')}
          >
            代码
          </button>
          <button 
            className={`code-view-tab ${activeTab === 'docs' ? 'active' : ''}`}
            onClick={() => setActiveTab('docs')}
          >
            文档
          </button>
        </div>
        
        <div className="code-view-actions">
          {githubUrl && (
            <a 
              href={githubUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="github-link"
            >
              <span className="github-icon">GitHub</span>
            </a>
          )}
        </div>
      </div>
      
      <div className="code-view-content">
        {activeTab === 'code' ? (
          renderTestCode()
        ) : (
          <div className="docs-content">
            <iframe 
              src={docsUrl || 'about:blank'} 
              title="Documentation" 
              className="docs-iframe"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeView;
