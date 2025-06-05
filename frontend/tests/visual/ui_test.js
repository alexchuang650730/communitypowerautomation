// 视觉自动化测试脚本
const { test, expect } = require('@playwright/test');

// 测试通用智能体UI表现
test.describe('通用智能体UI视觉测试', () => {
  // 测试主界面视觉表现
  test('主界面视觉测试', async ({ page }) => {
    // 访问应用
    await page.goto('http://localhost:5173/');
    
    // 等待页面完全加载
    await page.waitForLoadState('networkidle');
    
    // 截取主界面截图
    await expect(page).toHaveScreenshot('main-dashboard.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 测试响应式布局
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500); // 等待响应式布局调整
    await expect(page).toHaveScreenshot('main-dashboard-tablet.png', {
      maxDiffPixelRatio: 0.1
    });
    
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('main-dashboard-mobile.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 恢复视口大小
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  // 测试工作流视图视觉表现
  test('工作流视图视觉测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // 切换到工作流视图
    await page.click('text=工作流');
    await page.waitForLoadState('networkidle');
    
    // 截取工作流视图截图
    await expect(page).toHaveScreenshot('workflow-view.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 切换不同的工作流类型
    await page.click('text=自动化测试工作流');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('automation-test-workflow.png', {
      maxDiffPixelRatio: 0.1
    });
    
    await page.click('text=自动化智能体设计工作流');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('agent-design-workflow.png', {
      maxDiffPixelRatio: 0.1
    });
  });

  // 测试节点交互视觉表现
  test('节点交互视觉测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    await page.click('text=自动化智能体设计工作流');
    
    // 点击通用智能体节点
    await page.click('#general-agent');
    await page.waitForTimeout(500);
    
    // 截取节点选中状态截图
    await expect(page).toHaveScreenshot('selected-node.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 验证节点详情卡片显示
    await expect(page.locator('.node-detail-card')).toBeVisible();
    await expect(page).toHaveScreenshot('node-details.png', {
      maxDiffPixelRatio: 0.1
    });
  });

  // 测试日志视图视觉表现
  test('日志视图视觉测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    await page.click('text=自动化智能体设计工作流');
    
    // 验证日志视图显示
    await expect(page.locator('.log-view')).toBeVisible();
    
    // 截取日志视图截图
    await expect(page.locator('.log-view')).toHaveScreenshot('log-view.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 切换到文档标签
    await page.click('text=文档');
    await page.waitForTimeout(500);
    
    // 截取文档视图截图
    await expect(page.locator('.docs-content')).toHaveScreenshot('docs-view.png', {
      maxDiffPixelRatio: 0.1
    });
  });

  // 测试代码视图视觉表现
  test('代码视图视觉测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.click('text=工作流');
    await page.click('text=自动化智能体设计工作流');
    
    // 点击通用智能体节点
    await page.click('#general-agent');
    
    // 验证代码视图显示
    await expect(page.locator('.code-view')).toBeVisible();
    
    // 截取代码视图截图
    await expect(page.locator('.code-view')).toHaveScreenshot('code-view.png', {
      maxDiffPixelRatio: 0.1
    });
  });

  // 测试输入区域视觉表现
  test('输入区域视觉测试', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // 验证输入区域显示
    await expect(page.locator('.input-area')).toBeVisible();
    
    // 截取输入区域截图
    await expect(page.locator('.input-area')).toHaveScreenshot('input-area.png', {
      maxDiffPixelRatio: 0.1
    });
    
    // 输入测试文本
    await page.fill('.input-textarea', '这是一段测试文本，用于验证输入区域的视觉表现');
    await page.waitForTimeout(500);
    
    // 截取输入文本后的截图
    await expect(page.locator('.input-area')).toHaveScreenshot('input-area-with-text.png', {
      maxDiffPixelRatio: 0.1
    });
  });
});
