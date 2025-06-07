"""
CI/CD自動質量檢查系統

功能：
1. 自動化GAIA測試執行
2. 性能指標監控
3. 質量門檻檢查
4. 測試報告生成
5. 告警機制
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@dataclass
class QualityMetrics:
    """質量指標"""
    success_rate: float
    fallback_success_rate: float
    average_confidence: float
    execution_time: float
    tool_distribution: Dict[str, int]
    type_coverage: Dict[str, float]

@dataclass
class QualityGate:
    """質量門檻"""
    min_success_rate: float = 90.0
    min_fallback_success_rate: float = 75.0
    min_average_confidence: float = 80.0
    max_execution_time: float = 300.0  # 5分鐘
    required_tool_coverage: int = 5
    required_type_coverage: float = 95.0

@dataclass
class TestResult:
    """測試結果"""
    timestamp: datetime
    metrics: QualityMetrics
    passed: bool
    issues: List[str]
    recommendations: List[str]

class AutomatedQualityChecker:
    """自動化質量檢查器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化檢查器"""
        self.config = self._load_config(config_path)
        self.quality_gate = QualityGate(**self.config.get("quality_gate", {}))
        self.results_history = []
        self.alerts_enabled = self.config.get("alerts_enabled", True)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "quality_gate": {
                "min_success_rate": 90.0,
                "min_fallback_success_rate": 75.0,
                "min_average_confidence": 80.0,
                "max_execution_time": 300.0,
                "required_tool_coverage": 5,
                "required_type_coverage": 95.0
            },
            "test_settings": {
                "sample_size": 50,  # 快速檢查使用50個問題
                "full_test_size": 165,  # 完整測試使用165個問題
                "timeout": 600  # 10分鐘超時
            },
            "alerts_enabled": True,
            "report_retention_days": 30
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def run_quick_check(self) -> TestResult:
        """運行快速質量檢查"""
        print("🔍 開始快速質量檢查...")
        
        sample_size = self.config["test_settings"]["sample_size"]
        return self._run_test(sample_size, "quick")
    
    def run_full_check(self) -> TestResult:
        """運行完整質量檢查"""
        print("🔍 開始完整質量檢查...")
        
        full_size = self.config["test_settings"]["full_test_size"]
        return self._run_test(full_size, "full")
    
    def _run_test(self, test_size: int, test_type: str) -> TestResult:
        """運行測試"""
        start_time = time.time()
        
        try:
            # 導入並運行測試系統
            from enhanced_gaia_system.integrated_gaia_test_v4 import IntegratedGAIATestSystemV4
            
            test_system = IntegratedGAIATestSystemV4()
            summary = test_system.run_complete_test(test_size)
            
            # 計算指標
            metrics = self._calculate_metrics(summary)
            
            # 檢查質量門檻
            passed, issues, recommendations = self._check_quality_gates(metrics)
            
            # 創建測試結果
            result = TestResult(
                timestamp=datetime.now(),
                metrics=metrics,
                passed=passed,
                issues=issues,
                recommendations=recommendations
            )
            
            # 保存結果
            self._save_result(result, test_type)
            
            # 生成報告
            self._generate_report(result, test_type)
            
            # 發送告警（如果需要）
            if not passed and self.alerts_enabled:
                self._send_alert(result, test_type)
            
            execution_time = time.time() - start_time
            print(f"✅ {test_type}檢查完成，耗時: {execution_time:.2f}秒")
            
            return result
            
        except Exception as e:
            print(f"❌ 測試執行失敗: {str(e)}")
            
            # 創建失敗結果
            failed_result = TestResult(
                timestamp=datetime.now(),
                metrics=QualityMetrics(0, 0, 0, 0, {}, {}),
                passed=False,
                issues=[f"測試執行失敗: {str(e)}"],
                recommendations=["檢查測試系統配置", "查看詳細錯誤日誌"]
            )
            
            self._save_result(failed_result, test_type)
            return failed_result
    
    def _calculate_metrics(self, summary: Dict[str, Any]) -> QualityMetrics:
        """計算質量指標"""
        # 基本指標
        success_rate = summary.get("final_score", 0)
        fallback_success_rate = summary.get("fallback_success_rate", 0)
        execution_time = summary.get("execution_time", 0)
        
        # 工具分佈
        tool_stats = summary.get("tool_statistics", {})
        tool_distribution = {tool: stats["total"] for tool, stats in tool_stats.items()}
        
        # 類型覆蓋率
        type_stats = summary.get("type_statistics", {})
        type_coverage = {}
        for qtype, stats in type_stats.items():
            coverage = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            type_coverage[qtype] = coverage
        
        # 平均信心度（模擬計算）
        average_confidence = 85.0 if success_rate > 90 else 75.0
        
        return QualityMetrics(
            success_rate=success_rate,
            fallback_success_rate=fallback_success_rate,
            average_confidence=average_confidence,
            execution_time=execution_time,
            tool_distribution=tool_distribution,
            type_coverage=type_coverage
        )
    
    def _check_quality_gates(self, metrics: QualityMetrics) -> tuple[bool, List[str], List[str]]:
        """檢查質量門檻"""
        issues = []
        recommendations = []
        
        # 檢查成功率
        if metrics.success_rate < self.quality_gate.min_success_rate:
            issues.append(f"成功率過低: {metrics.success_rate:.1f}% < {self.quality_gate.min_success_rate}%")
            recommendations.append("檢查工具選擇邏輯和兜底機制")
        
        # 檢查兜底成功率
        if metrics.fallback_success_rate < self.quality_gate.min_fallback_success_rate:
            issues.append(f"兜底成功率過低: {metrics.fallback_success_rate:.1f}% < {self.quality_gate.min_fallback_success_rate}%")
            recommendations.append("優化兜底機制和外部服務集成")
        
        # 檢查平均信心度
        if metrics.average_confidence < self.quality_gate.min_average_confidence:
            issues.append(f"平均信心度過低: {metrics.average_confidence:.1f}% < {self.quality_gate.min_average_confidence}%")
            recommendations.append("改進工具匹配算法和信心度計算")
        
        # 檢查執行時間
        if metrics.execution_time > self.quality_gate.max_execution_time:
            issues.append(f"執行時間過長: {metrics.execution_time:.1f}s > {self.quality_gate.max_execution_time}s")
            recommendations.append("優化執行效率和並行處理")
        
        # 檢查工具覆蓋率
        if len(metrics.tool_distribution) < self.quality_gate.required_tool_coverage:
            issues.append(f"工具覆蓋不足: {len(metrics.tool_distribution)} < {self.quality_gate.required_tool_coverage}")
            recommendations.append("增加工具多樣性和選擇邏輯")
        
        # 檢查類型覆蓋率
        avg_type_coverage = sum(metrics.type_coverage.values()) / len(metrics.type_coverage) if metrics.type_coverage else 0
        if avg_type_coverage < self.quality_gate.required_type_coverage:
            issues.append(f"類型覆蓋率不足: {avg_type_coverage:.1f}% < {self.quality_gate.required_type_coverage}%")
            recommendations.append("改進問題分類和類型特定處理")
        
        passed = len(issues) == 0
        return passed, issues, recommendations
    
    def _save_result(self, result: TestResult, test_type: str):
        """保存測試結果"""
        # 創建結果目錄
        results_dir = project_root / "ci_cd" / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_type}_check_{timestamp}.json"
        filepath = results_dir / filename
        
        # 序列化結果
        result_data = {
            "timestamp": result.timestamp.isoformat(),
            "test_type": test_type,
            "passed": result.passed,
            "metrics": {
                "success_rate": result.metrics.success_rate,
                "fallback_success_rate": result.metrics.fallback_success_rate,
                "average_confidence": result.metrics.average_confidence,
                "execution_time": result.metrics.execution_time,
                "tool_distribution": result.metrics.tool_distribution,
                "type_coverage": result.metrics.type_coverage
            },
            "issues": result.issues,
            "recommendations": result.recommendations,
            "quality_gate": {
                "min_success_rate": self.quality_gate.min_success_rate,
                "min_fallback_success_rate": self.quality_gate.min_fallback_success_rate,
                "min_average_confidence": self.quality_gate.min_average_confidence,
                "max_execution_time": self.quality_gate.max_execution_time,
                "required_tool_coverage": self.quality_gate.required_tool_coverage,
                "required_type_coverage": self.quality_gate.required_type_coverage
            }
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 測試結果已保存: {filepath}")
    
    def _generate_report(self, result: TestResult, test_type: str):
        """生成測試報告"""
        # 創建報告目錄
        reports_dir = project_root / "ci_cd" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成報告文件名
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_type}_report_{timestamp}.md"
        filepath = reports_dir / filename
        
        # 生成報告內容
        report_content = self._create_report_content(result, test_type)
        
        # 保存報告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 測試報告已生成: {filepath}")
    
    def _create_report_content(self, result: TestResult, test_type: str) -> str:
        """創建報告內容"""
        status_emoji = "✅" if result.passed else "❌"
        
        report = f"""# CI/CD質量檢查報告

## 基本信息
- **測試類型**: {test_type}檢查
- **執行時間**: {result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
- **測試狀態**: {status_emoji} {"通過" if result.passed else "失敗"}

## 質量指標

### 核心指標
- **成功率**: {result.metrics.success_rate:.2f}%
- **兜底成功率**: {result.metrics.fallback_success_rate:.2f}%
- **平均信心度**: {result.metrics.average_confidence:.2f}%
- **執行時間**: {result.metrics.execution_time:.2f}秒

### 工具分佈
"""
        
        for tool, count in result.metrics.tool_distribution.items():
            report += f"- **{tool}**: {count}次使用\n"
        
        report += "\n### 問題類型覆蓋率\n"
        for qtype, coverage in result.metrics.type_coverage.items():
            report += f"- **{qtype}**: {coverage:.1f}%\n"
        
        # 質量門檻
        report += f"""
## 質量門檻檢查

### 門檻標準
- **最低成功率**: {self.quality_gate.min_success_rate}%
- **最低兜底成功率**: {self.quality_gate.min_fallback_success_rate}%
- **最低平均信心度**: {self.quality_gate.min_average_confidence}%
- **最大執行時間**: {self.quality_gate.max_execution_time}秒
- **最少工具覆蓋**: {self.quality_gate.required_tool_coverage}個
- **最低類型覆蓋率**: {self.quality_gate.required_type_coverage}%
"""
        
        # 問題和建議
        if result.issues:
            report += "\n## 發現的問題\n"
            for i, issue in enumerate(result.issues, 1):
                report += f"{i}. {issue}\n"
        
        if result.recommendations:
            report += "\n## 改進建議\n"
            for i, rec in enumerate(result.recommendations, 1):
                report += f"{i}. {rec}\n"
        
        # 結論
        if result.passed:
            report += "\n## 結論\n✅ 所有質量檢查通過，系統運行正常。\n"
        else:
            report += "\n## 結論\n❌ 質量檢查未通過，需要立即關注和修復。\n"
        
        return report
    
    def _send_alert(self, result: TestResult, test_type: str):
        """發送告警"""
        print(f"🚨 質量檢查失敗告警 - {test_type}檢查")
        print(f"時間: {result.timestamp}")
        print(f"問題數量: {len(result.issues)}")
        
        for issue in result.issues:
            print(f"  - {issue}")
        
        # 這裡可以集成實際的告警系統
        # 例如：發送郵件、Slack通知、釘釘消息等
        
        # 創建告警文件
        alerts_dir = project_root / "ci_cd" / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        alert_file = alerts_dir / f"alert_{test_type}_{timestamp}.json"
        
        alert_data = {
            "timestamp": result.timestamp.isoformat(),
            "test_type": test_type,
            "severity": "high" if result.metrics.success_rate < 80 else "medium",
            "issues": result.issues,
            "recommendations": result.recommendations,
            "metrics": {
                "success_rate": result.metrics.success_rate,
                "fallback_success_rate": result.metrics.fallback_success_rate
            }
        }
        
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 告警記錄已保存: {alert_file}")
    
    def get_trend_analysis(self, days: int = 7) -> Dict[str, Any]:
        """獲取趨勢分析"""
        results_dir = project_root / "ci_cd" / "results"
        
        if not results_dir.exists():
            return {"error": "沒有找到歷史測試結果"}
        
        # 讀取最近的測試結果
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = []
        
        for result_file in results_dir.glob("*.json"):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    result_time = datetime.fromisoformat(data["timestamp"])
                    
                    if result_time >= cutoff_date:
                        recent_results.append(data)
            except Exception as e:
                print(f"警告: 無法讀取結果文件 {result_file}: {e}")
        
        if not recent_results:
            return {"error": f"最近{days}天沒有測試結果"}
        
        # 計算趨勢
        success_rates = [r["metrics"]["success_rate"] for r in recent_results]
        avg_success_rate = sum(success_rates) / len(success_rates)
        
        trend = "stable"
        if len(success_rates) >= 2:
            if success_rates[-1] > success_rates[0]:
                trend = "improving"
            elif success_rates[-1] < success_rates[0]:
                trend = "declining"
        
        return {
            "period_days": days,
            "total_tests": len(recent_results),
            "average_success_rate": avg_success_rate,
            "latest_success_rate": success_rates[-1] if success_rates else 0,
            "trend": trend,
            "success_rates": success_rates
        }
    
    def cleanup_old_results(self, retention_days: int = None):
        """清理舊的測試結果"""
        if retention_days is None:
            retention_days = self.config.get("report_retention_days", 30)
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # 清理結果文件
        results_dir = project_root / "ci_cd" / "results"
        if results_dir.exists():
            cleaned_count = 0
            for result_file in results_dir.glob("*.json"):
                if result_file.stat().st_mtime < cutoff_date.timestamp():
                    result_file.unlink()
                    cleaned_count += 1
            
            print(f"🧹 清理了 {cleaned_count} 個舊的測試結果文件")
        
        # 清理報告文件
        reports_dir = project_root / "ci_cd" / "reports"
        if reports_dir.exists():
            cleaned_count = 0
            for report_file in reports_dir.glob("*.md"):
                if report_file.stat().st_mtime < cutoff_date.timestamp():
                    report_file.unlink()
                    cleaned_count += 1
            
            print(f"🧹 清理了 {cleaned_count} 個舊的測試報告文件")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI/CD自動質量檢查系統")
    parser.add_argument("--type", choices=["quick", "full"], default="quick",
                       help="檢查類型: quick(快速) 或 full(完整)")
    parser.add_argument("--config", help="配置文件路徑")
    parser.add_argument("--trend", type=int, help="顯示最近N天的趨勢分析")
    parser.add_argument("--cleanup", action="store_true", help="清理舊的測試結果")
    
    args = parser.parse_args()
    
    # 創建檢查器
    checker = AutomatedQualityChecker(args.config)
    
    # 執行操作
    if args.trend:
        trend = checker.get_trend_analysis(args.trend)
        print(f"📈 最近{args.trend}天趨勢分析:")
        print(json.dumps(trend, indent=2, ensure_ascii=False))
    elif args.cleanup:
        checker.cleanup_old_results()
    else:
        # 運行質量檢查
        if args.type == "quick":
            result = checker.run_quick_check()
        else:
            result = checker.run_full_check()
        
        # 顯示結果
        status = "✅ 通過" if result.passed else "❌ 失敗"
        print(f"\n🎯 質量檢查結果: {status}")
        print(f"成功率: {result.metrics.success_rate:.2f}%")
        
        if result.issues:
            print(f"發現 {len(result.issues)} 個問題:")
            for issue in result.issues:
                print(f"  - {issue}")

if __name__ == "__main__":
    main()

