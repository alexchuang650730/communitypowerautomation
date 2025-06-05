// 命令行测试脚本
const { exec } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// 创建命令行交互界面
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// 模拟MCP协调器接收指令的测试类
class MCPCoordinatorTester {
  constructor() {
    this.agentStatus = 'idle';
    this.testResults = [];
    this.logFile = path.join(__dirname, 'test_results.json');
  }

  // 启动测试
  async start() {
    console.log('===== 通用智能体命令行测试工具 =====');
    console.log('此工具用于模拟向MCP协调器发送指令并测试通用智能体的六大特性');
    console.log('可用命令:');
    console.log('1. test [特性名称] - 测试特定特性 (自主性|交互性|适应性|社交性|学习性|目标导向)');
    console.log('2. test-all - 测试所有六大特性');
    console.log('3. status - 查看当前测试状态');
    console.log('4. exit - 退出测试');
    console.log('=====================================');
    
    this.promptUser();
  }

  // 提示用户输入
  promptUser() {
    rl.question('> ', (input) => {
      this.processCommand(input);
    });
  }

  // 处理用户命令
  processCommand(input) {
    const args = input.split(' ');
    const command = args[0].toLowerCase();

    switch (command) {
      case 'test':
        if (args.length < 2) {
          console.log('请指定要测试的特性');
        } else {
          this.testFeature(args[1]);
        }
        break;
      case 'test-all':
        this.testAllFeatures();
        break;
      case 'status':
        this.showStatus();
        break;
      case 'exit':
        console.log('退出测试');
        rl.close();
        return;
      default:
        console.log('未知命令，请重试');
    }

    this.promptUser();
  }

  // 测试单个特性
  async testFeature(feature) {
    const validFeatures = ['自主性', '交互性', '适应性', '社交性', '学习性', '目标导向'];
    const featureName = feature.toLowerCase();
    
    let targetFeature = '';
    if (featureName === '自主性' || featureName === 'autonomy') {
      targetFeature = '自主性';
    } else if (featureName === '交互性' || featureName === 'interactivity') {
      targetFeature = '交互性';
    } else if (featureName === '适应性' || featureName === 'adaptability') {
      targetFeature = '适应性';
    } else if (featureName === '社交性' || featureName === 'sociality') {
      targetFeature = '社交性';
    } else if (featureName === '学习性' || featureName === 'learning') {
      targetFeature = '学习性';
    } else if (featureName === '目标导向' || featureName === 'goal-oriented') {
      targetFeature = '目标导向';
    } else {
      console.log(`无效的特性: ${feature}`);
      console.log(`有效的特性: ${validFeatures.join(', ')}`);
      return;
    }

    console.log(`开始测试 ${targetFeature} 特性...`);
    this.agentStatus = 'testing';
    
    // 模拟测试过程
    await this.simulateTest(targetFeature);
    
    console.log(`${targetFeature} 特性测试完成`);
    this.agentStatus = 'idle';
  }

  // 测试所有特性
  async testAllFeatures() {
    const features = ['自主性', '交互性', '适应性', '社交性', '学习性', '目标导向'];
    console.log('开始测试所有六大特性...');
    this.agentStatus = 'testing';
    
    for (const feature of features) {
      console.log(`测试 ${feature} 特性...`);
      await this.simulateTest(feature);
      console.log(`${feature} 特性测试完成`);
    }
    
    console.log('所有特性测试完成');
    this.saveResults();
    this.agentStatus = 'idle';
  }

  // 模拟测试过程
  async simulateTest(feature) {
    return new Promise((resolve) => {
      console.log(`向MCP协调器发送测试 ${feature} 的指令...`);
      
      // 模拟测试延迟
      setTimeout(() => {
        const result = {
          feature: feature,
          timestamp: new Date().toISOString(),
          success: Math.random() > 0.2, // 80%概率成功
          metrics: {
            responseTime: Math.floor(Math.random() * 500) + 100,
            accuracy: Math.floor(Math.random() * 30) + 70,
            efficiency: Math.floor(Math.random() * 30) + 70
          }
        };
        
        if (result.success) {
          console.log(`✅ ${feature} 测试通过`);
        } else {
          console.log(`❌ ${feature} 测试失败`);
        }
        
        this.testResults.push(result);
        resolve();
      }, 2000);
    });
  }

  // 显示当前状态
  showStatus() {
    console.log(`当前状态: ${this.agentStatus}`);
    console.log(`已完成测试: ${this.testResults.length}`);
    
    if (this.testResults.length > 0) {
      console.log('测试结果摘要:');
      const successCount = this.testResults.filter(r => r.success).length;
      console.log(`通过: ${successCount}/${this.testResults.length} (${Math.round(successCount/this.testResults.length*100)}%)`);
    }
  }

  // 保存测试结果
  saveResults() {
    try {
      fs.writeFileSync(this.logFile, JSON.stringify(this.testResults, null, 2));
      console.log(`测试结果已保存到 ${this.logFile}`);
    } catch (err) {
      console.error('保存测试结果失败:', err);
    }
  }
}

// 启动测试器
const tester = new MCPCoordinatorTester();
tester.start();
