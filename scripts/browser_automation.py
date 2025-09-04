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

try:
    from browser_use import Agent, BrowserProfile, ChatOpenAI
    from dotenv import load_dotenv
    from .prompts import JobApplicationPrompts
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
    screenshot_path: Optional[str] = None
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
        self.browser_profile = None
        self.agent = None  # 使用单个agent
        self.job_data = job_data or {}
        self.job_url = self.job_data.get("url", "")
        self.results: List[ApplicationResult] = []
        
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
            # 创建保持会话的浏览器配置
            self.browser_profile = BrowserProfile(keep_alive=True)
            
            # 创建初始任务提示
            initial_prompt = self._create_navigation_prompt(self.job_url)
            
            # 创建单个代理，使用保持会话的浏览器配置
            self.agent = Agent(
                task=initial_prompt,
                llm=self._create_llm_client(),
                browser_profile=self.browser_profile
            )
            
            print("✅ 浏览器和AI代理初始化完成")
            print("📝 使用单个AI代理和保持会话的浏览器配置：")
            print("   🔗 代理将在同一浏览器会话中执行所有任务")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            return False
    
    def _create_llm_client(self):
        """创建LLM客户端"""
        return ChatOpenAI(model="gpt-4o",
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
            await self.agent.run(max_steps=20)
            
            # 等待一段时间让页面稳定
            await asyncio.sleep(3)
            
            # 第二步：添加表单填写任务
            print("📝 第二步：添加表单填写任务...")
            form_prompt = self._create_form_filling_prompt(self.job_data)
            self.agent.add_new_task(form_prompt)
            await self.agent.run(max_steps=100)
            
            print(f"✅ 成功申请: {job_title}")
            return ApplicationResult(
                job_url=job_url,
                job_title=job_title,
                company=company,
                status="success"
            )
                
        except Exception as e:
            error_msg = f"申请过程中出现错误: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 错误时截图
            screenshot_path = await self._take_screenshot(f"error_{int(time.time())}")
            
            return ApplicationResult(
                job_url=job_url,
                job_title=job_title,
                company=company,
                status="failed",
                error_message=error_msg,
                screenshot_path=screenshot_path
            )
    
    
    def _create_navigation_prompt(self, job_url: str) -> str:
        """创建导航指令提示"""
        return JobApplicationPrompts.get_navigation_prompt(job_url)
    
    def _create_form_filling_prompt(self, job_data: Dict) -> str:
        """创建表单填写指令提示"""
        return JobApplicationPrompts.get_form_filling_prompt(job_data, self.personal_data)
    
    async def _take_screenshot(self, filename: str) -> str:
        """截图保存"""
        try:
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{filename}.png"
            
            # 由于使用BrowserProfile，截图功能需要通过agent实现
            # 这里返回路径，实际截图可能需要在agent内部处理
            return str(screenshot_path)
        except Exception as e:
            print(f"⚠️ 截图失败: {str(e)}")
            return None
    
    
    async def batch_apply(self, jobs_data: List[Dict]) -> List[ApplicationResult]:
        """批量申请职位"""
        print(f"🚀 开始批量申请 {len(jobs_data)} 个职位")
        
        max_applications = self.config["application_settings"]["max_applications_per_session"]
        delay_between = self.config["application_settings"]["delay_between_applications"]
        
        # 限制申请数量
        jobs_to_apply = jobs_data[:max_applications]
        
        for i, job_data in enumerate(jobs_to_apply, 1):
            print(f"\n📝 申请进度: {i}/{len(jobs_to_apply)}")
            
            # 更新当前job_data
            self.job_data = job_data
            self.job_url = job_data.get("url", "")
            
            # 申请职位
            result = await self.apply_to_job()
            self.results.append(result)
            
            # 保存进度
            if self.config["application_settings"].get("auto_save_progress", True):
                self._save_progress()
            
            # 如果不是最后一个，等待一段时间
            if i < len(jobs_to_apply):
                print(f"⏳ 等待 {delay_between} 秒后继续下一个申请...")
                await asyncio.sleep(delay_between)
        
        return self.results
    
    def _save_progress(self):
        """保存申请进度"""
        try:
            progress_file = Path("application_progress.json")
            progress_data = {
                "timestamp": datetime.now().isoformat(),
                "total_applications": len(self.results),
                "successful_applications": len([r for r in self.results if r.status == "success"]),
                "failed_applications": len([r for r in self.results if r.status == "failed"]),
                "results": [
                    {
                        "job_url": r.job_url,
                        "job_title": r.job_title,
                        "company": r.company,
                        "status": r.status,
                        "error_message": r.error_message,
                        "timestamp": r.timestamp
                    } for r in self.results
                ]
            }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存进度失败: {str(e)}")
    
    def get_summary(self) -> Dict:
        """获取申请摘要"""
        total = len(self.results)
        successful = len([r for r in self.results if r.status == "success"])
        failed = len([r for r in self.results if r.status == "failed"])
        
        return {
            "total_applications": total,
            "successful_applications": successful,
            "failed_applications": failed,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            "results": self.results
        }
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser_profile:
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
