# PowerAutomation 测试框架

## 📋 **测试目录结构**

```
test/
├── unit/                    # 单元测试
│   ├── adapters/           # 适配器单元测试
│   ├── core/               # 核心组件单元测试
│   └── tools/              # 工具单元测试
├── integration/            # 集成测试
│   ├── multi_model_synergy.py          # 多模型协同测试
│   ├── mcptool_kilocode_integration.py # MCPTool与Kilocode集成
│   └── workflow_integration.py         # 工作流集成测试
├── e2e/                    # 端到端测试
│   ├── release_workflow.py             # 发布工作流测试
│   ├── thought_action_workflow.py      # 思考行动工作流测试
│   └── tool_discovery_workflow.py      # 工具发现工作流测试
├── mcp_compliance/         # MCP协议合规性测试
│   ├── compliance_checker.py           # 合规性检查器
│   └── protocol_validation.py          # 协议验证器
├── performance/            # 性能测试
│   ├── load_testing.py                 # 负载测试
│   └── stress_testing.py               # 压力测试
└── automation/             # 自动化测试工具
    ├── test_runner.py                  # 测试运行器
    ├── report_generator.py             # 报告生成器
    └── ci_integration.py               # CI集成工具
```

## 🧪 **测试分类说明**

### 📦 **单元测试 (Unit Tests)**
- **目的**: 测试单个组件或函数的功能
- **范围**: 适配器、核心组件、工具函数
- **特点**: 快速执行、独立性强、覆盖率高

### 🔗 **集成测试 (Integration Tests)**
- **目的**: 测试组件间的交互和集成
- **范围**: 多模型协同、API集成、工作流集成
- **特点**: 验证接口兼容性、数据流正确性

### 🎯 **端到端测试 (E2E Tests)**
- **目的**: 测试完整的用户场景和业务流程
- **范围**: 发布流程、工作流执行、工具发现
- **特点**: 模拟真实使用场景、验证整体功能

### ✅ **MCP合规性测试**
- **目的**: 验证MCP协议标准符合性
- **范围**: 协议格式、接口规范、错误处理
- **特点**: 确保协议兼容性、标准化

### ⚡ **性能测试**
- **目的**: 验证系统性能和稳定性
- **范围**: 负载测试、压力测试、内存使用
- **特点**: 量化性能指标、发现性能瓶颈

### 🤖 **自动化测试工具**
- **目的**: 提供测试执行和报告生成工具
- **范围**: 测试运行、报告生成、CI集成
- **特点**: 自动化执行、详细报告、持续集成

## 🚀 **快速开始**

### 运行所有测试
```bash
cd /home/ubuntu/powerautomation
python -m test.automation.test_runner
```

### 运行特定测试类型
```bash
# 运行集成测试
python -m pytest test/integration/

# 运行端到端测试
python -m pytest test/e2e/

# 运行性能测试
python -m pytest test/performance/
```

### 生成测试报告
```bash
python -m test.automation.report_generator
```

## 📊 **测试报告**

测试报告将生成在 `test_reports/` 目录中：
- `test_report.html` - 详细的HTML格式报告
- `test_report.json` - 机器可读的JSON格式报告
- `test_summary.txt` - 简要的文本摘要报告

## 🔧 **配置要求**

### 环境变量
```bash
export CLAUDE_API_KEY="your_claude_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
export KILO_API_KEY="your_kilo_api_key"
export SUPERMEMORY_API_KEY="your_supermemory_api_key"
export GITHUB_TOKEN="your_github_token"
```

### 依赖包
```bash
pip install pytest pytest-asyncio psutil
```

## 📈 **测试指标**

### 目标指标
- **单元测试覆盖率**: > 90%
- **集成测试成功率**: > 95%
- **端到端测试成功率**: > 90%
- **性能测试响应时间**: < 5秒
- **MCP合规性**: 100%

### 监控指标
- 测试执行时间
- 内存使用情况
- API调用成功率
- 错误率和失败模式

## 🔄 **持续集成**

测试框架支持与CI/CD系统集成：
- GitHub Actions
- Jenkins
- GitLab CI
- 其他CI系统

## 📝 **编写测试指南**

### 测试命名规范
- 测试文件: `test_*.py` 或 `*_test.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 测试结构
```python
import unittest

class TestExample(unittest.TestCase):
    def setUp(self):
        """测试初始化"""
        pass
    
    def test_feature(self):
        """测试特定功能"""
        # Arrange
        # Act
        # Assert
        pass
    
    def tearDown(self):
        """测试清理"""
        pass
```

## 🐛 **故障排除**

### 常见问题
1. **API密钥未配置**: 检查环境变量设置
2. **依赖包缺失**: 运行 `pip install -r requirements.txt`
3. **权限问题**: 确保测试文件有执行权限
4. **网络连接**: 检查API服务可访问性

### 调试技巧
- 使用 `pytest -v` 获取详细输出
- 使用 `pytest -s` 显示print输出
- 使用 `pytest --pdb` 进入调试模式

---

**PowerAutomation测试框架 - 确保代码质量，提升开发效率！** 🚀

