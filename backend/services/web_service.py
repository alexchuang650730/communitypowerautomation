"""
Web Agent服务模块

提供Web Agent相关的服务功能，包括网页抓取、截图、内容分析等。
"""

import os
import time
import uuid
from datetime import datetime
from playwright.sync_api import sync_playwright
from powerautomation_integration.agents.web.web_agent import WebAgent

class WebService:
    def __init__(self):
        self.screenshots_dir = os.path.join(os.getcwd(), 'data', 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.web_agent = WebAgent()
    
    def take_screenshot(self, url, full_page=False):
        """
        获取指定网页的截图
        
        参数:
        - url: 网页URL
        - full_page: 是否截取整个页面
        
        返回:
        - 截图文件路径
        """
        screenshot_filename = f"{uuid.uuid4()}.png"
        screenshot_path = os.path.join(self.screenshots_dir, screenshot_filename)
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=screenshot_path, full_page=full_page)
            browser.close()
        
        return screenshot_path
    
    def extract_html_content(self, url):
        """
        提取网页HTML内容
        
        参数:
        - url: 网页URL
        
        返回:
        - HTML内容
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            html_content = page.content()
            browser.close()
        
        return html_content
    
    def execute_browser_actions(self, url, actions):
        """
        在浏览器中执行一系列操作
        
        参数:
        - url: 起始网页URL
        - actions: 操作列表，每个操作是一个字典，包含type和params
        
        返回:
        - 执行结果
        """
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            
            for action in actions:
                action_type = action.get('type')
                params = action.get('params', {})
                
                if action_type == 'click':
                    selector = params.get('selector')
                    if selector:
                        page.click(selector)
                        results.append(f"点击元素: {selector}")
                
                elif action_type == 'fill':
                    selector = params.get('selector')
                    value = params.get('value')
                    if selector and value:
                        page.fill(selector, value)
                        results.append(f"填写表单: {selector} = {value}")
                
                elif action_type == 'navigate':
                    target_url = params.get('url')
                    if target_url:
                        page.goto(target_url, wait_until="networkidle")
                        results.append(f"导航到: {target_url}")
                
                elif action_type == 'wait':
                    timeout = params.get('timeout', 1000)
                    page.wait_for_timeout(timeout)
                    results.append(f"等待: {timeout}ms")
                
                elif action_type == 'screenshot':
                    screenshot_filename = f"{uuid.uuid4()}.png"
                    screenshot_path = os.path.join(self.screenshots_dir, screenshot_filename)
                    page.screenshot(path=screenshot_path)
                    results.append(f"截图: {screenshot_path}")
            
            browser.close()
        
        return results
    
    def extract_structured_data(self, url, selectors):
        """
        从网页中提取结构化数据
        
        参数:
        - url: 网页URL
        - selectors: 选择器字典，键是数据字段名，值是CSS选择器
        
        返回:
        - 提取的数据列表
        """
        data = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            
            # 获取匹配的元素数量
            first_selector = list(selectors.values())[0]
            elements_count = page.eval_on_selector_all(first_selector, "elements => elements.length")
            
            # 提取每个元素的数据
            for i in range(elements_count):
                item = {}
                for field, selector in selectors.items():
                    elements = page.query_selector_all(selector)
                    if i < len(elements):
                        item[field] = elements[i].inner_text()
                    else:
                        item[field] = ""
                
                if item:
                    data.append(item)
            
            browser.close()
        
        return data
    
    def analyze_web_content(self, url, analysis_type="general", analysis_query=""):
        """
        分析网页内容
        
        参数:
        - url: 网页URL
        - analysis_type: 分析类型
        - analysis_query: 分析查询
        
        返回:
        - 分析结果
        """
        return self.web_agent.execute({
            "type": "analyze_content",
            "url": url,
            "analysis_type": analysis_type,
            "analysis_query": analysis_query
        })
    
    def extract_web_data(self, url, extraction_query=""):
        """
        提取网页数据
        
        参数:
        - url: 网页URL
        - extraction_query: 提取查询
        
        返回:
        - 提取结果
        """
        return self.web_agent.execute({
            "type": "extract_data",
            "url": url,
            "extraction_query": extraction_query
        })
    
    def automate_web_task(self, url, task):
        """
        自动化网页任务
        
        参数:
        - url: 网页URL
        - task: 任务描述
        
        返回:
        - 执行结果
        """
        return self.web_agent.execute({
            "type": "automate_task",
            "url": url,
            "task": task
        })
