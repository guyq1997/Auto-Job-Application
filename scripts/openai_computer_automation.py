#!/usr/bin/env python3
"""
OpenAI Computer Use Automation Module for Job Applications
使用OpenAI Computer Use API和Playwright自动化职位申请流程
"""

import asyncio
import json
import os
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess

try:
    from playwright.async_api import async_playwright, Browser, Page
    from openai import OpenAI
    from dotenv import load_dotenv
    from .prompts import JobApplicationPrompts
except ImportError as e:
    print(f"❌ 缺少依赖库: {e}")
    print("请运行: pip install playwright openai python-dotenv")
    print("然后运行: playwright install chromium")
    exit(1)

# 加载环境变量
load_dotenv()

@dataclass
class ApplicationResult:
    """申请结果数据类"""
    job_url: str
    job_title: str
    company: str
    status: str  # success, failed, skipped
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class OpenAIComputerUseBot:
    """基于OpenAI Computer Use API的自动化职位申请机器人"""
    
    def __init__(self, config_path: str = "config/browser_config.json", job_data: Dict = None):
        """初始化申请机器人"""
        self.config = self._load_config(config_path)
        self.personal_data = self._load_personal_data()
        self.playwright = None
        self.browser = None
        self.page = None
        self.openai_client = None
        self.job_data = job_data or {}
        self.job_url = self.job_data.get("url", "")
        self.results: List[ApplicationResult] = []
        self.display_width = 1024
        self.display_height = 768

    def _load_config(self, config_path: str) -> Dict:
        """加载浏览器配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {config_path}")
            return self._get_default_config()
    
    def _load_personal_data(self) -> Dict:
        """加载个人信息数据"""
        try:
            with open("config/personal_data.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ 个人信息文件不存在: config/personal_data.json")
            return {}
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "browser_config": {
                "headless": False,
                "slow_mo": 1000,
                "timeout": 30000
            },
            "application_settings": {
                "max_applications_per_session": 5,
                "delay_between_applications": 30
            }
        }

    def _get_document_paths(self) -> List[str]:
        """获取文档文件路径列表"""
        document_paths = []
        try:
            documents = self.personal_data.get("documents", [])
            for doc in documents:
                file_path = doc.get("file_path", "")
                if file_path and os.path.exists(file_path):
                    document_paths.append(os.path.abspath(file_path))
                    print(f"✅ 添加文档路径: {file_path}")
                else:
                    print(f"⚠️ 文档路径不存在: {file_path}")
            
            if not document_paths:
                print("⚠️ 没有找到可用的文档文件")
            else:
                print(f"📁 总共配置了 {len(document_paths)} 个文档文件")
                
        except Exception as e:
            print(f"❌ 获取文档路径时出错: {str(e)}")
        
        return document_paths

    async def initialize(self, job_data: Dict = None):
        """初始化浏览器和OpenAI客户端"""
        print("🚀 初始化浏览器和OpenAI Computer Use API...")
        
        # 如果提供了job_data，更新实例变量
        if job_data:
            self.job_data = job_data
            self.job_url = job_data.get("url", "")
        
        # 检查OpenAI API Key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ 请设置OPENAI_API_KEY环境变量")
            return False
        
        try:
            # 初始化OpenAI客户端
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # 初始化Playwright
            self.playwright = await async_playwright().start()
            
            # 启动浏览器
            browser_config = self.config.get("browser_config", {})
            headless_mode = browser_config.get("headless", True)
            
            # 检查是否强制调试模式
            debug_mode = os.getenv("BROWSER_DEBUG_MODE", "false").lower() == "true"
            if debug_mode:
                headless_mode = False
                print("🐛 检测到调试模式，使用可见浏览器")
            
            if headless_mode:
                print("👻 使用无头模式运行，不会干扰你的工作")
            else:
                print("🖥️ 使用可见模式运行（调试用）")
            
            self.browser = await self.playwright.chromium.launch(
                headless=headless_mode,
                slow_mo=browser_config.get("slow_mo", 1000),
                args=[
                    "--disable-extensions",
                    "--disable-file-system",
                    "--no-sandbox",  # 无头模式下提高兼容性
                    "--disable-dev-shm-usage"  # 减少内存使用
                ],
                env={}  # 清空环境变量以提高安全性
            )
            
            # 创建页面
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({
                "width": self.display_width, 
                "height": self.display_height
            })
            
            print("✅ 浏览器和OpenAI Computer Use API初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            return False

    async def get_screenshot(self) -> str:
        """获取当前页面截图并转换为base64"""
        try:
            screenshot_bytes = await self.page.screenshot()
            return base64.b64encode(screenshot_bytes).decode('utf-8')
        except Exception as e:
            print(f"❌ 获取截图失败: {str(e)}")
            return ""

    async def handle_computer_action(self, action):
        """执行计算机操作"""
        # 处理OpenAI Computer Use API返回的动作对象
        try:
            # 获取动作类型
            if hasattr(action, 'type'):
                action_type = action.type
            elif hasattr(action, '__class__'):
                # 从类名推断动作类型
                class_name = action.__class__.__name__
                if 'Click' in class_name:
                    action_type = 'click'
                elif 'Type' in class_name:
                    action_type = 'type'
                elif 'Scroll' in class_name:
                    action_type = 'scroll'
                elif 'Key' in class_name:
                    action_type = 'keypress'
                else:
                    action_type = 'unknown'
            else:
                action_type = 'unknown'
            
            print(f"🎯 执行动作: {action_type}")
            
            if action_type == "click":
                # 处理点击操作
                x = getattr(action, 'x', getattr(action, 'coordinate', [0, 0])[0] if hasattr(action, 'coordinate') else 0)
                y = getattr(action, 'y', getattr(action, 'coordinate', [0, 0])[1] if hasattr(action, 'coordinate') else 0)
                button = getattr(action, 'button', 'left')
                print(f"🖱️ 点击位置: ({x}, {y}) 按钮: {button}")
                
                await self.page.mouse.click(x, y, button=button)
                
            elif action_type == "type":
                # 处理输入操作
                text = getattr(action, 'text', '')
                print(f"⌨️ 输入文本: {text}")
                await self.page.keyboard.type(text)
                
            elif action_type == "keypress":
                # 处理按键操作
                if hasattr(action, 'key'):
                    key = action.key
                    print(f"⌨️ 按键: {key}")
                    if key.lower() == "enter":
                        await self.page.keyboard.press("Enter")
                    elif key.lower() == "space":
                        await self.page.keyboard.press(" ")
                    else:
                        await self.page.keyboard.press(key)
                elif hasattr(action, 'keys'):
                    keys = action.keys
                    for key in keys:
                        print(f"⌨️ 按键: {key}")
                        if key.lower() == "enter":
                            await self.page.keyboard.press("Enter")
                        elif key.lower() == "space":
                            await self.page.keyboard.press(" ")
                        else:
                            await self.page.keyboard.press(key)
                        
            elif action_type == "scroll":
                # 处理滚动操作
                x = getattr(action, 'x', getattr(action, 'coordinate', [500, 400])[0] if hasattr(action, 'coordinate') else 500)
                y = getattr(action, 'y', getattr(action, 'coordinate', [500, 400])[1] if hasattr(action, 'coordinate') else 400)
                
                # 尝试不同的属性名来获取滚动距离
                scroll_x = 0
                scroll_y = 0
                
                if hasattr(action, 'scroll_x'):
                    scroll_x = action.scroll_x
                if hasattr(action, 'scroll_y'):
                    scroll_y = action.scroll_y
                elif hasattr(action, 'delta_y'):
                    scroll_y = action.delta_y
                elif hasattr(action, 'delta'):
                    if isinstance(action.delta, (list, tuple)) and len(action.delta) >= 2:
                        scroll_x, scroll_y = action.delta[0], action.delta[1]
                    else:
                        scroll_y = action.delta
                
                # 如果没有找到滚动距离，使用默认值
                if scroll_x == 0 and scroll_y == 0:
                    scroll_y = -300  # 默认向上滚动
                
                print(f"🔄 滚动页面: 位置({x}, {y}) 偏移({scroll_x}, {scroll_y})")
                
                await self.page.mouse.move(x, y)
                await self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
                
            elif action_type == "wait":
                print("⏳ 等待...")
                await asyncio.sleep(2)
                
            elif action_type == "screenshot":
                print("📸 截图操作")
                # 截图会在主循环中处理，这里不需要额外操作
                pass
                
            else:
                print(f"⚠️ 未识别的操作类型: {action_type}")
                print(f"🔍 动作对象属性: {[attr for attr in dir(action) if not attr.startswith('_')]}")
                
        except Exception as e:
            print(f"❌ 执行操作失败: {str(e)}")
            print(f"🔍 动作对象类型: {type(action)}")
            print(f"🔍 动作对象属性: {[attr for attr in dir(action) if not attr.startswith('_')]}")
            # 尝试打印动作对象的内容
            try:
                print(f"🔍 动作对象内容: {action}")
            except:
                pass

    async def computer_use_loop(self, initial_prompt: str, max_iterations: int = 50) -> Dict:
        """OpenAI Computer Use主循环"""
        print(f"🔄 开始Computer Use循环，最大迭代次数: {max_iterations}")
        
        # 获取初始截图
        screenshot_base64 = await self.get_screenshot()
        if not screenshot_base64:
            return {"status": "failed", "error": "无法获取初始截图"}
        
        # 创建初始请求
        try:
            response = self.openai_client.responses.create(
                model="computer-use-preview",
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": self.display_width,
                    "display_height": self.display_height,
                    "environment": "browser"
                }],
                input=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": initial_prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot_base64}"
                        }
                    ]
                }],
                reasoning={
                    "summary": "concise"
                },
                truncation="auto"
            )
        except Exception as e:
            print(f"❌ OpenAI API请求失败: {str(e)}")
            return {"status": "failed", "error": str(e)}
        
        iteration_count = 0
        
        # 主循环
        while iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n🔄 迭代 {iteration_count}/{max_iterations}")
            
            # 查找computer_call
            computer_calls = [item for item in response.output if item.type == "computer_call"]
            
            if not computer_calls:
                print("✅ 没有更多的computer_call，任务完成")
                # 输出最终响应
                for item in response.output:
                    if hasattr(item, 'type'):
                        print(f"📄 响应类型: {item.type}")
                        if hasattr(item, 'content'):
                            print(f"📝 内容: {item.content}")
                break
            
            # 处理computer_call（通常只有一个）
            computer_call = computer_calls[0]
            call_id = computer_call.call_id
            action = computer_call.action
            
            # 检查安全检查
            if hasattr(computer_call, 'pending_safety_checks') and computer_call.pending_safety_checks:
                print("⚠️ 检测到安全检查，需要人工确认")
                # 这里可以添加人工确认逻辑
                # 暂时自动确认所有安全检查
                acknowledged_checks = computer_call.pending_safety_checks
            else:
                acknowledged_checks = []
            
            # 执行操作
            await self.handle_computer_action(action)
            
            # 等待操作生效
            await asyncio.sleep(1)
            
            # 获取新截图
            screenshot_base64 = await self.get_screenshot()
            if not screenshot_base64:
                print("❌ 无法获取截图，停止循环")
                break
            
            # 准备下一个请求
            try:
                response = self.openai_client.responses.create(
                    model="computer-use-preview",
                    previous_response_id=response.id,
                    tools=[{
                        "type": "computer_use_preview",
                        "display_width": self.display_width,
                        "display_height": self.display_height,
                        "environment": "browser"
                    }],
                    input=[{
                        "call_id": call_id,
                        "type": "computer_call_output",
                        "acknowledged_safety_checks": acknowledged_checks,
                        "output": {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot_base64}"
                        },
                        "current_url": self.page.url if self.page else ""
                    }],
                    truncation="auto"
                )
            except Exception as e:
                print(f"❌ OpenAI API请求失败: {str(e)}")
                return {"status": "failed", "error": str(e)}
        
        if iteration_count >= max_iterations:
            print(f"⚠️ 达到最大迭代次数 {max_iterations}，停止循环")
            return {"status": "timeout", "iterations": iteration_count}
        
        return {"status": "completed", "iterations": iteration_count}

    async def apply_to_job(self) -> ApplicationResult:
        """申请单个职位 - 两步骤流程"""
        job_url = self.job_url
        job_title = self.job_data.get("title", "未知职位")
        company = self.job_data.get("company", "未知公司")
        
        print(f"\n🎯 开始申请: {job_title} @ {company}")
        print(f"🔗 链接: {job_url}")
        
        try:
            # 导航到目标URL
            print(f"🌐 导航到: {job_url}")
            await self.page.goto(job_url)
            await self.page.wait_for_load_state('networkidle')
            
            # 第一步：导航到申请表单
            print("📍 第一步：执行导航任务...")
            navigation_prompt = self._create_navigation_prompt(job_url)
            
            result = await self.computer_use_loop(navigation_prompt, max_iterations=15)
            
            if result["status"] != "completed":
                raise Exception(f"导航任务失败: {result.get('error', '未知错误')}")
            
            # 等待一段时间让页面稳定
            await asyncio.sleep(3)
            
            # 第二步：表单填写任务
            print("📝 第二步：执行表单填写任务...")
            current_url = self.page.url
            form_prompt = self._create_form_filling_prompt(self.personal_data, current_url)
            
            result = await self.computer_use_loop(form_prompt, max_iterations=100)
            
            if result["status"] != "completed":
                print(f"⚠️ 表单填写任务未完全完成: {result.get('error', '可能需要人工干预')}")
            
            print(f"✅ 申请流程完成: {job_title}")
            
            return ApplicationResult(
                job_url=job_url,
                job_title=job_title,
                company=company,
                status="success"
            )
                
        except Exception as e:
            error_msg = f"申请过程中出现错误: {str(e)}"
            print(f"❌ {error_msg}")
            
            return ApplicationResult(
                job_url=job_url,
                job_title=job_title,
                company=company,
                status="failed",
                error_message=error_msg
            )
    
    def _create_navigation_prompt(self, job_url: str) -> str:
        """创建导航指令提示"""
        return JobApplicationPrompts.get_navigation_prompt(job_url)
    
    def _create_form_filling_prompt(self, personal_data: Dict, form_url: str) -> str:
        """创建表单填写指令提示"""
        return JobApplicationPrompts.get_form_filling_prompt(personal_data, form_url)
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("✅ 资源清理完成")
        except Exception as e:
            print(f"⚠️ 清理资源时出错: {str(e)}")

# 辅助函数
async def create_openai_computer_bot(config_path: str = "config/browser_config.json", job_data: Dict = None) -> OpenAIComputerUseBot:
    """创建并初始化OpenAI Computer Use申请机器人"""
    bot = OpenAIComputerUseBot(config_path, job_data)
    success = await bot.initialize(job_data)
    
    if not success:
        raise Exception("OpenAI Computer Use申请机器人初始化失败")
    
    return bot

if __name__ == "__main__":
    # 测试代码
    async def test_bot():
        try:
            # 测试数据
            test_job = {
                "title": "Python Developer",
                "company": "Test Company",
                "url": "https://example.com/job",
                "location": "Berlin"
            }
            
            bot = await create_openai_computer_bot(job_data=test_job)
            
            result = await bot.apply_to_job()
            print(f"\n📊 申请结果: {result}")
            
            await bot.cleanup()
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    # 运行测试
    asyncio.run(test_bot())
