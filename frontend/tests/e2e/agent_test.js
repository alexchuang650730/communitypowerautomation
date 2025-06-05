// 通用智能体端到端测试脚本
const { test, expect } = require('@playwright/test');

// 测试通用智能体的六大定义特性
test.describe('通用智能体六大定义特性测试', () => {
  // 特性1: 自主性 - 测试智能体能否独立完成任务
  test('自主性测试', async ({ page }) => {
    // 访问应用
    await page.goto('http://localhost:5173/');
    
    // 切换到工作流视图
    await page.click('text=工作流');
    
    // 选择通用智能体
    await page.click('text=通用智能体');
    
    // 验证通用智能体节点存在
    await expect(page.locator('#general-agent')).toBeVisible();
    
    // 点击通用智能体节点
    await page.click('#general-agent');
    
    // 验证日志中显示自主处理的记录
    await expect(page.locator('.log-entries')).toContainText('通用智能体处理成功');
  });

  // 特性2: 交互性 - 测试智能体与用户的交互能力
  test('交互性测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // 输入区域应该可见
    await expect(page.locator('.input-area')).toBeVisible();
    
    // 输入测试指令
    await page.fill('.input-textarea', '分析当前系统状态');
    await page.click('.submit-button');
    
    // 验证响应
    await expect(page.locator('.response-area')).toContainText('系统状态');
  });

  // 特性3: 适应性 - 测试智能体对不同情境的适应能力
  test('适应性测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    
    // 切换不同的工作流类型
    await page.click('text=自动化测试工作流');
    await expect(page.locator('.workflow-visualizer')).toContainText('集成测试');
    
    await page.click('text=自动化智能体设计工作流');
    await expect(page.locator('.workflow-visualizer')).toContainText('通用智能体');
    
    // 验证智能体能适应不同工作流
    await expect(page.locator('.memory-status-card')).toBeVisible();
  });

  // 特性4: 社交性 - 测试智能体与其他组件的协作能力
  test('社交性测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    await page.click('text=自动化智能体设计工作流');
    
    // 验证MCP协调器与通用智能体的连接
    await expect(page.locator('#mcp-coordinator')).toBeVisible();
    
    // 点击MCP协调器节点
    await page.click('#mcp-coordinator');
    
    // 验证日志中显示协作记录
    await expect(page.locator('.log-entries')).toContainText('分配任务给各子系统');
  });

  // 特性5: 学习性 - 测试智能体的学习和记忆能力
  test('学习性测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    await page.click('text=自动化智能体设计工作流');
    
    // 验证SuperMemory组件存在
    await expect(page.locator('#supermemory')).toBeVisible();
    
    // 点击SuperMemory节点
    await page.click('#supermemory');
    
    // 验证记忆状态显示
    await expect(page.locator('.memory-status-card')).toContainText('SuperMemory.ai 记忆状态');
  });

  // 特性6: 目标导向 - 测试智能体的目标规划和执行能力
  test('目标导向测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    await page.click('text=自动化智能体设计工作流');
    
    // 验证MCP规划器存在
    await expect(page.locator('#mcp-planner')).toBeVisible();
    
    // 点击MCP规划器节点
    await page.click('#mcp-planner');
    
    // 验证日志中显示规划记录
    await expect(page.locator('.log-entries')).toContainText('创建执行步骤');
    await expect(page.locator('.log-entries')).toContainText('分析任务依赖关系');
  });
});
