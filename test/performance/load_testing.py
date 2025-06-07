#!/usr/bin/env python3
"""
性能负载测试
测试系统在高负载下的性能表现
"""

import sys
import os
import unittest
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.unified_smart_tool_engine_mcp_v2 import UnifiedSmartToolEngineMCP

class TestLoadTesting(unittest.TestCase):
    """负载测试"""
    
    def setUp(self):
        """测试初始化"""
        self.tool_engine = UnifiedSmartToolEngineMCP()
        self.test_request = {
            "action": "discover_tools",
            "query": "test query"
        }
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        num_threads = 10
        num_requests_per_thread = 5
        
        def make_request():
            """发送单个请求"""
            start_time = time.time()
            try:
                result = self.tool_engine.process(self.test_request)
                end_time = time.time()
                return {
                    "success": True,
                    "response_time": end_time - start_time,
                    "result": result
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "success": False,
                    "response_time": end_time - start_time,
                    "error": str(e)
                }
        
        # 执行并发测试
        results = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for _ in range(num_threads * num_requests_per_thread):
                futures.append(executor.submit(make_request))
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # 分析结果
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results)
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        
        print(f"成功率: {success_rate:.2%}")
        print(f"平均响应时间: {avg_response_time:.3f}秒")
        print(f"失败请求数: {len(failed_requests)}")
        
        # 断言性能要求
        self.assertGreaterEqual(success_rate, 0.95, "成功率应该大于95%")
        self.assertLessEqual(avg_response_time, 5.0, "平均响应时间应该小于5秒")
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行多次请求
        for i in range(100):
            self.tool_engine.process(self.test_request)
            if i % 10 == 0:
                gc.collect()  # 强制垃圾回收
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"初始内存: {initial_memory:.2f} MB")
        print(f"最终内存: {final_memory:.2f} MB")
        print(f"内存增长: {memory_increase:.2f} MB")
        
        # 内存增长不应超过100MB
        self.assertLessEqual(memory_increase, 100, "内存增长应该控制在100MB以内")

if __name__ == "__main__":
    unittest.main()

