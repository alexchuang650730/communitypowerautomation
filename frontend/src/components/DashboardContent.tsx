import React from 'react';
import '../styles/DashboardContent.css';

interface DashboardContentProps {
  agentType: string;
}

const DashboardContent: React.FC<DashboardContentProps> = ({ agentType }) => {
  // 根据不同智能体类型渲染不同内容
  const renderAgentSpecificContent = () => {
    switch (agentType) {
      case 'general':
        return (
          <div className="dashboard-container">
            <div className="dashboard-left-panel">
              <div className="dashboard-overview">
                <h3 className="overview-title">通用智能体概述</h3>
                <p className="overview-description">
                  通用智能体是一种多功能AI助手，能够处理各类通用任务，包括但不限于代码测试、文档生成、数据分析和问题排查。
                  它集成了多种先进能力，可以适应不同场景需求，提供高效、准确的解决方案。
                </p>
                <p className="overview-description">
                  通过六大核心特性和五大治理原则，通用智能体能够在保证质量和安全的前提下，为企业提供全方位的智能化支持。
                </p>
                <div className="overview-image">
                  <div className="agent-icon">📋</div>
                </div>
              </div>
            </div>
            
            <div className="dashboard-right-panel">
              <div className="right-panel-section">
                <h3 className="subsection-title">通用智能体六大特性</h3>
                <div className="feature-cards">
                  <div className="feature-card">
                    <div className="feature-icon">🌐</div>
                    <h4>1. 平台特性</h4>
                    <ul>
                      <li>多平台集成能力：支持与GitHub、CI/CD平台、本地开发环境的无缝集成</li>
                      <li>跨环境兼容性：在Windows、macOS和Linux环境下保持一致的功能表现</li>
                      <li>API接口标准化：提供统一的REST API接口，支持第三方系统调用</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">🖥️</div>
                    <h4>2. UI布局特性</h4>
                    <ul>
                      <li>两栏式布局：左侧展示任务进度和ThoughtActionRecorder思考过程，右侧展示代码和画面回放</li>
                      <li>实时状态反馈：通过视觉元素直观展示测试状态和进度</li>
                      <li>响应式设计：自适应不同屏幕尺寸，确保在桌面和移动设备上的良好体验</li>
                      <li>主题定制：支持明暗主题切换和企业级视觉风格定制</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">💬</div>
                    <h4>3. 提示词特性</h4>
                    <ul>
                      <li>上下文感知提示：根据测试阶段和问题类型生成针对性提示</li>
                      <li>多语言支持：支持中英文等多语言提示和报告生成</li>
                      <li>技术术语识别：准确识别并解释测试和开发领域的专业术语</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">🧠</div>
                    <h4>4. 思维特性</h4>
                    <ul>
                      <li>测试策略规划：自动分析代码结构，制定最优测试策略</li>
                      <li>问题根因分析：通过调用Manus能力，深入分析测试失败原因</li>
                      <li>修复方案生成：基于历史数据和最佳实践，提供针对性修复建议</li>
                      <li>优先级排序：智能评估问题严重性，合理安排修复顺序</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">📄</div>
                    <h4>5. 内容特性</h4>
                    <ul>
                      <li>测试报告生成：自动生成结构化、可视化的测试报告</li>
                      <li>GitHub集成：将测试结果自动提交到GitHub，支持Issue创建和更新</li>
                      <li>代码注释生成：为测试用例和修复代码生成清晰的注释</li>
                      <li>文档更新：自动更新README和相关文档，反映最新测试状态</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">💾</div>
                    <h4>6. 记忆特性</h4>
                    <ul>
                      <li>测试历史追踪：记录并分析历史测试结果，识别趋势和模式</li>
                      <li>知识库构建：积累常见问题和解决方案，形成项目专属知识库</li>
                      <li>ReleaseManager能力：监控GitHub release事件，自动下载代码到指定路径，支持SSH密钥认证，处理代码上传和推送</li>
                      <li>持续学习：通过每次测试和修复过程不断优化测试策略和问题解决方法</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="right-panel-section">
                <h3 className="subsection-title">通用智能体五大核心治理原则</h3>
                <div className="governance-cards">
                  <div className="governance-card">
                    <div className="governance-icon">🛡️</div>
                    <h4>结构保护原则</h4>
                    <p>所有扩展基于原有文件结构，未修改现有结构</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">⚙️</div>
                    <h4>兼容性原则</h4>
                    <p>新功能与现有功能保持向后兼容</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">📐</div>
                    <h4>空间利用原则</h4>
                    <p>UI扩展只在空白区域进行，不影响原有控件</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">🧩</div>
                    <h4>模块化原则</h4>
                    <p>所有新功能作为独立模块添加，不修改现有代码逻辑</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">🔄</div>
                    <h4>一致性原则</h4>
                    <p>保持与现有代码风格和架构的一致性</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'code':
        return (
          <div className="dashboard-container">
            <div className="dashboard-left-panel">
              <div className="dashboard-overview">
                <h3 className="overview-title">代码智能体概述</h3>
                <p className="overview-description">
                  代码智能体专注于代码生成、调试和优化，能够理解多种编程语言和框架，
                  提供高质量的代码解决方案和技术支持。
                </p>
                <div className="overview-image">
                  <div className="agent-icon">💻</div>
                </div>
              </div>
            </div>
            <div className="dashboard-right-panel">
              <div className="right-panel-section">
                <h3 className="subsection-title">代码智能体特性</h3>
                <p className="placeholder-text">代码智能体的特性内容将在此显示</p>
              </div>
              <div className="right-panel-section">
                <h3 className="subsection-title">代码智能体治理原则</h3>
                <p className="placeholder-text">代码智能体的治理原则将在此显示</p>
              </div>
            </div>
          </div>
        );
      case 'ppt':
        return (
          <div className="dashboard-container">
            <div className="dashboard-left-panel">
              <div className="dashboard-overview">
                <h3 className="overview-title">PPT智能体概述</h3>
                <p className="overview-description">
                  PPT智能体专注于创建和编辑专业演示文稿，能够根据用户需求生成结构化、
                  视觉吸引力强的幻灯片，支持多种模板和风格定制。
                </p>
                <div className="overview-image">
                  <div className="agent-icon">📊</div>
                </div>
              </div>
            </div>
            
            <div className="dashboard-right-panel">
              <div className="right-panel-section">
                <h3 className="subsection-title">PPT智能体六大特性</h3>
                <div className="feature-cards">
                  <div className="feature-card">
                    <div className="feature-icon">🌐</div>
                    <h4>1. 平台特性</h4>
                    <ul>
                      <li>PowerAutomation集成：与PowerAutomation平台无缝集成，实现统一任务管理和路由</li>
                      <li>文件格式处理：支持多种输入文件格式（文本、Markdown、数据文件）和输出格式（PPTX, PDF, 图片）</li>
                      <li>外部API集成：支持调用外部API获取数据、图片或增强内容生成能力</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">🖥️</div>
                    <h4>2. UI布局特性</h4>
                    <ul>
                      <li>专用PPT界面：提供专门用于PPT创建和编辑的用户界面</li>
                      <li>进度可视化：直观显示PPT生成任务的进度和状态</li>
                      <li>响应式设计：UI布局自适应不同屏幕尺寸</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">💬</div>
                    <h4>3. 提示词与模板特性</h4>
                    <ul>
                      <li>自然语言理解：理解用户通过自然语言提出的PPT创建需求（主题、大纲、风格等）</li>
                      <li>模板管理：提供、选择和管理PPT模板库，支持自定义模板</li>
                      <li>上下文提示：根据用户输入和选择的模板，提供智能化的内容填充和设计建议提示</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">🧠</div>
                    <h4>4. 思维与内容生成特性</h4>
                    <ul>
                      <li>AI内容生成：利用AI能力（如Skywork）生成PPT的核心内容、摘要和讲者备注</li>
                      <li>布局优化：根据内容自动选择和优化幻灯片布局</li>
                      <li>视觉元素建议：根据幻灯片内容智能建议合适的图片、图表或图标</li>
                      <li>逻辑流程与连贯性：确保PPT内容逻辑清晰、流程连贯、前后呼应</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">📄</div>
                    <h4>5. 内容特性</h4>
                    <ul>
                      <li>多模态输入处理：处理文本、数据、图片等多种输入素材，并将其整合到PPT中</li>
                      <li>PPT生成引擎：基于python-pptx或其他库生成高质量的PPTX文件</li>
                      <li>多格式导出：支持将生成的PPT导出为PDF、图片序列等多种格式</li>
                      <li>视觉证据整合：整合pptagent生成的视觉证据（如PPT截图）用于验证和报告</li>
                    </ul>
                  </div>
                  
                  <div className="feature-card">
                    <div className="feature-icon">💾</div>
                    <h4>6. 记忆特性</h4>
                    <ul>
                      <li>任务历史管理：记录所有PPT生成任务的详细历史，包括输入、配置和结果</li>
                      <li>模板记忆：存储和管理用户上传的自定义模板和常用模板</li>
                      <li>生成检查点：在PPT生成过程中保存检查点，支持从中断处恢复或回滚</li>
                      <li>用户偏好记忆：记忆用户的常用风格、模板和导出设置</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="right-panel-section">
                <h3 className="subsection-title">PPT智能体五大核心治理原则</h3>
                <div className="governance-cards">
                  <div className="governance-card">
                    <div className="governance-icon">🛡️</div>
                    <h4>结构保护原则</h4>
                    <p>所有PPT生成和编辑操作保持原始文档结构完整性，不破坏用户已有内容</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">⚙️</div>
                    <h4>兼容性原则</h4>
                    <p>生成的PPT文件与主流演示软件兼容，确保跨平台使用体验一致</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">📐</div>
                    <h4>空间利用原则</h4>
                    <p>幻灯片布局优化空间利用，确保内容清晰可读且视觉平衡</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">🧩</div>
                    <h4>模块化原则</h4>
                    <p>PPT内容以模块化方式组织，便于用户后续编辑和重用</p>
                  </div>
                  
                  <div className="governance-card">
                    <div className="governance-icon">🔄</div>
                    <h4>一致性原则</h4>
                    <p>整个PPT保持设计风格、字体、配色和布局的一致性</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'web':
        return (
          <div className="dashboard-container">
            <div className="dashboard-left-panel">
              <div className="dashboard-overview">
                <h3 className="overview-title">网页智能体概述</h3>
                <p className="overview-description">
                  网页智能体专注于设计和开发网页应用，能够根据用户需求创建响应式、
                  交互性强的网站，支持多种前端框架和设计风格。
                </p>
                <div className="overview-image">
                  <div className="agent-icon">🌐</div>
                </div>
              </div>
            </div>
            <div className="dashboard-right-panel">
              <div className="right-panel-section">
                <h3 className="subsection-title">网页智能体特性</h3>
                <p className="placeholder-text">网页智能体的特性内容将在此显示</p>
              </div>
              <div className="right-panel-section">
                <h3 className="subsection-title">网页智能体治理原则</h3>
                <p className="placeholder-text">网页智能体的治理原则将在此显示</p>
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div className="dashboard-container">
            <div className="dashboard-left-panel">
              <div className="dashboard-overview">
                <h3 className="overview-title">智能体概述</h3>
                <p className="overview-description">
                  请选择智能体类型查看详细信息
                </p>
              </div>
            </div>
            <div className="dashboard-right-panel">
              <div className="right-panel-section">
                <p className="placeholder-text">选择智能体后将显示相关特性</p>
              </div>
              <div className="right-panel-section">
                <p className="placeholder-text">选择智能体后将显示相关治理原则</p>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="dashboard-content">
      <h2 className="section-title">智能体能力与治理</h2>
      {renderAgentSpecificContent()}
    </div>
  );
};

export default DashboardContent;
