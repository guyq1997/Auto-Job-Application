#!/usr/bin/env python3
"""
Browser Automation Module for Job Applications
使用Browser-use库和LLM自动化职位申请流程
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import base64
from pydantic import BaseModel, Field

try:
    from browser_use import Agent, Browser, ChatOpenAI, Tools
    from dotenv import load_dotenv
    from .prompts import JobApplicationPrompts
    from .captcha_tools import create_captcha_tools
except ImportError as e:
    print(f"❌ 缺少依赖库: {e}")
    print("请运行: pip install -r requirements.txt")
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

class JobApplicationBot:
    """自动化职位申请机器人"""
    
    def __init__(self, config_path: str = "config/browser_config.json", job_data: Dict = None):
        """初始化申请机器人"""
        self.config = self._load_config(config_path)
        self.personal_data = self._load_personal_data()
        self.browser = None
        self.agent = None  # 使用单个agent
        self.job_data = job_data or {}
        self.job_url = self.job_data.get("url", "")
        self.results: List[ApplicationResult] = []
        self.tools = self._create_tools()  # 创建工具集合

    def _load_sensitive_data(self) -> Dict:
        """加载敏感数据"""
        try:
            sensitive_data = {'Username': os.getenv("Email"), 'Password': os.getenv("Password")}
        except Exception as e:
            print(f"❌ 加载敏感数据失败: {str(e)}")
            return {}
        return sensitive_data
        
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
    
    def _get_document_paths(self) -> List[str]:
        """获取文档文件路径列表，用于配置agent的文件访问权限"""
        document_paths = []
        try:
            documents = self.personal_data.get("documents", [])
            for doc in documents:
                file_path = doc.get("file_path", "")
                if file_path and os.path.exists(file_path):
                    document_paths.append(file_path)
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

    def _get_current_browser_session(self):
        """获取当前浏览器会话 - 延迟访问self.agent"""
        if not hasattr(self, 'agent') or not self.agent:
            raise Exception("Browser agent not initialized. Please call initialize() first.")
        return self.agent
    
    def _create_tools(self):
        """创建自定义工具集合"""
        # 返回CAPTCHA工具，截图工具通过单独方法提供
        captcha_tools = create_captcha_tools(bot_instance=self)
        return captcha_tools.get_tools()
    
    

    async def initialize(self, job_data: Dict = None):
        """初始化浏览器和AI代理"""
        print("🚀 初始化浏览器和AI代理...")
        
        # 如果提供了job_data，更新实例变量
        if job_data:
            self.job_data = job_data
            self.job_url = job_data.get("url", "")
        
        # 检查OpenAI API Key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ 请设置OPENAI_API_KEY环境变量")
            return False
        
        try:
            # 从配置获取headless设置，默认为True（无头模式）
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
            
            # 创建保持会话的浏览器配置
            self.browser = Browser(
                headless=headless_mode,
                keep_alive=True
            ) 
            


            # 获取文档文件路径列表
            document_paths = self._get_document_paths()
            initial_prompt = self._create_form_filling_prompt(self.personal_data, self.job_url)

            # 创建单个代理，使用保持会话的浏览器配置和工具
            self.agent = Agent(
                task=initial_prompt,
                llm=self._create_llm_client(),
                browser=self.browser,
                tools=self.tools,  # 添加自定义工具
                vision_detail_level="auto",
                sensitive_data=self._load_sensitive_data(),
                step_timeout=300,
                llm_timeout=180,
                output_schema=ApplicationResult,
                available_file_paths=document_paths  # 添加文件访问权限
            )
            
            
            print("✅ 浏览器和AI代理初始化完成")
            print("📝 使用单个AI代理和保持会话的浏览器配置：")
            print("   🔗 代理将在同一浏览器会话中执行所有任务")
            print("   🤖 已启用智能CAPTCHA识别工具，支持:")
            print("      • 文字验证码 (text)")
            print("      • 数学计算 (math)")  
            print("      • 图像选择 (recaptcha)")
            print("      • 滑块验证码 (slider)")
            print("   🎯 已启用hCaptcha专用工具 (solve_hcaptcha_slider)")
            print("   📸 截图工具可通过 bot.get_screenshot_tools() 获取")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            return False
    
    def _create_llm_client(self):
        """创建LLM客户端"""
        return ChatOpenAI(model="o3",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def apply_to_job(self) -> ApplicationResult:

        """申请单个职位 - 两步骤流程"""
        job_url = self.job_url
        job_title = self.job_data.get("title", "未知职位")
        company = self.job_data.get("company", "未知公司")
        
        print(f"\n🎯 开始申请: {job_title} @ {company}")
        print(f"🔗 链接: {job_url}")
        

        
        try:
            # 第一步：导航到申请表单
            print("📍 第一步：执行导航任务...")
            print(self.browser.id)
            result = await self.agent.run(max_steps=60)
            

            
            print(f"✅ 成功申请: {job_title}")
            
            
            return ApplicationResult(
                job_url=job_url,
                job_title=job_title,
                company=company,
                status=result.status,
                error_message=result.error_message,
            )
                
        except Exception as e:
            error_msg = f"申请过程中出现错误: {str(e)}"
            print(f"❌ {error_msg}")
            
            
            return ApplicationResult(
                job_url=job_url,
                status=result.status,
                error_message=result.error_message,

            )
    
    
    def _create_navigation_prompt(self, job_url: str) -> str:
        """创建导航指令提示"""
        return JobApplicationPrompts.get_navigation_prompt(job_url)
    
    def _create_form_filling_prompt(self, personal_data: Dict, job_url: str) -> str:
        """创建表单填写指令提示，包含智能日期处理"""
        # 获取基础表单填写提示
        form_prompt = JobApplicationPrompts.get_form_filling_prompt(personal_data, job_url)
        
        return form_prompt
    
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                # BrowserProfile会自动管理浏览器生命周期
                # 如果keep_alive=True，浏览器会保持打开直到程序结束
                pass
            print("✅ 资源清理完成")
        except Exception as e:
            print(f"⚠️ 清理资源时出错: {str(e)}")


# 辅助函数
async def create_application_bot(config_path: str = "config/browser_config.json", job_data: Dict = None) -> JobApplicationBot:
    """创建并初始化申请机器人"""
    bot = JobApplicationBot(config_path, job_data)
    success = await bot.initialize(job_data)
    
    if not success:
        raise Exception("申请机器人初始化失败")
    
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
            
            bot = await create_application_bot(job_data=test_job)
            
            result = await bot.apply_to_job()
            print(f"\n📊 申请结果: {result}")
            
            await bot.cleanup()
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    # 运行测试
    asyncio.run(test_bot())
