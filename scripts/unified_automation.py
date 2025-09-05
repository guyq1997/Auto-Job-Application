#!/usr/bin/env python3
"""
统一自动化模块 - 支持browser-use和OpenAI Computer Use API
Unified Automation Module - Support both browser-use and OpenAI Computer Use API
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from .browser_automation import JobApplicationBot, create_application_bot
    from .openai_computer_automation import OpenAIComputerUseBot, create_openai_computer_bot
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ 缺少依赖库: {e}")
    print("请确保安装了所有必需的依赖")
    exit(1)

# 加载环境变量
load_dotenv()

class AutomationBackend(Enum):
    """自动化后端类型"""
    BROWSER_USE = "browser-use"
    OPENAI_COMPUTER_USE = "openai-computer-use"

@dataclass
class UnifiedApplicationResult:
    """统一申请结果数据类"""
    job_url: str
    job_title: str
    company: str
    status: str  # success, failed, skipped
    backend_used: str  # 使用的后端类型
    error_message: Optional[str] = None
    timestamp: str = None
    iterations: Optional[int] = None  # OpenAI Computer Use特有
    
    def __post_init__(self):
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()

class UnifiedJobApplicationBot:
    """统一职位申请机器人 - 支持多种自动化后端"""
    
    def __init__(self, 
                 backend: AutomationBackend = AutomationBackend.BROWSER_USE,
                 config_path: str = "config/browser_config.json", 
                 job_data: Dict = None):
        """
        初始化统一申请机器人
        
        Args:
            backend: 选择的自动化后端
            config_path: 配置文件路径
            job_data: 职位数据
        """
        self.backend = backend
        self.config_path = config_path
        self.job_data = job_data or {}
        self.bot = None
        self.results: List[UnifiedApplicationResult] = []
        
        print(f"🤖 初始化统一申请机器人，后端: {backend.value}")

    async def initialize(self, job_data: Dict = None):
        """初始化选定的后端"""
        if job_data:
            self.job_data = job_data
            
        print(f"🚀 正在初始化 {self.backend.value} 后端...")
        
        try:
            if self.backend == AutomationBackend.BROWSER_USE:
                self.bot = await create_application_bot(self.config_path, self.job_data)
                print("✅ Browser-use 后端初始化完成")
                
            elif self.backend == AutomationBackend.OPENAI_COMPUTER_USE:
                self.bot = await create_openai_computer_bot(self.config_path, self.job_data)
                print("✅ OpenAI Computer Use 后端初始化完成")
                
            else:
                raise ValueError(f"不支持的后端类型: {self.backend}")
                
            return True
            
        except Exception as e:
            print(f"❌ 后端初始化失败: {str(e)}")
            return False

    async def apply_to_job(self, job_data: Dict = None) -> UnifiedApplicationResult:
        """申请单个职位"""
        if job_data:
            self.job_data = job_data
            if hasattr(self.bot, 'job_data'):
                self.bot.job_data = job_data
                self.bot.job_url = job_data.get("url", "")
        
        job_title = self.job_data.get("title", "未知职位")
        company = self.job_data.get("company", "未知公司")
        job_url = self.job_data.get("url", "")
        
        print(f"\n🎯 使用 {self.backend.value} 后端申请职位")
        print(f"📝 职位: {job_title} @ {company}")
        
        try:
            # 调用具体后端的申请方法
            if self.backend == AutomationBackend.BROWSER_USE:
                result = await self.bot.apply_to_job()
                
                # 转换为统一结果格式
                unified_result = UnifiedApplicationResult(
                    job_url=result.job_url,
                    job_title=result.job_title,
                    company=result.company,
                    status=result.status,
                    backend_used=self.backend.value,
                    error_message=result.error_message,
                    timestamp=result.timestamp
                )
                
            elif self.backend == AutomationBackend.OPENAI_COMPUTER_USE:
                result = await self.bot.apply_to_job()
                
                # 转换为统一结果格式
                unified_result = UnifiedApplicationResult(
                    job_url=result.job_url,
                    job_title=result.job_title,
                    company=result.company,
                    status=result.status,
                    backend_used=self.backend.value,
                    error_message=result.error_message,
                    timestamp=result.timestamp
                )
                
            else:
                raise ValueError(f"不支持的后端类型: {self.backend}")
            
            self.results.append(unified_result)
            return unified_result
            
        except Exception as e:
            error_msg = f"申请过程中出现错误: {str(e)}"
            print(f"❌ {error_msg}")
            
            unified_result = UnifiedApplicationResult(
                job_url=job_url,
                job_title=job_title,
                company=company,
                status="failed",
                backend_used=self.backend.value,
                error_message=error_msg
            )
            
            self.results.append(unified_result)
            return unified_result

    async def apply_to_multiple_jobs(self, jobs_list: List[Dict]) -> List[UnifiedApplicationResult]:
        """批量申请多个职位"""
        print(f"📋 开始批量申请 {len(jobs_list)} 个职位，使用 {self.backend.value} 后端")
        
        results = []
        
        for i, job_data in enumerate(jobs_list, 1):
            print(f"\n📍 处理第 {i}/{len(jobs_list)} 个职位")
            
            try:
                result = await self.apply_to_job(job_data)
                results.append(result)
                
                # 如果不是最后一个职位，添加延迟
                if i < len(jobs_list):
                    delay = self.bot.config.get("application_settings", {}).get("delay_between_applications", 30)
                    print(f"⏳ 等待 {delay} 秒后处理下一个职位...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 处理职位失败: {str(e)}")
                continue
        
        print(f"\n📊 批量申请完成，总共处理 {len(results)} 个职位")
        self._print_batch_summary(results)
        
        return results

    def _print_batch_summary(self, results: List[UnifiedApplicationResult]):
        """打印批量申请结果摘要"""
        success_count = len([r for r in results if r.status == "success"])
        failed_count = len([r for r in results if r.status == "failed"])
        
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {failed_count}")
        print(f"🤖 使用后端: {self.backend.value}")
        
        if failed_count > 0:
            print("\n❌ 失败的申请:")
            for result in results:
                if result.status == "failed":
                    print(f"  - {result.job_title} @ {result.company}: {result.error_message}")

    async def cleanup(self):
        """清理资源"""
        try:
            if self.bot:
                await self.bot.cleanup()
            print("✅ 统一机器人资源清理完成")
        except Exception as e:
            print(f"⚠️ 清理资源时出错: {str(e)}")

    def get_results(self) -> List[UnifiedApplicationResult]:
        """获取所有申请结果"""
        return self.results

    def save_results(self, file_path: str = None):
        """保存申请结果到文件"""
        if not file_path:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"application_results_{self.backend.value}_{timestamp}.json"
        
        try:
            results_data = []
            for result in self.results:
                results_data.append({
                    "job_url": result.job_url,
                    "job_title": result.job_title,
                    "company": result.company,
                    "status": result.status,
                    "backend_used": result.backend_used,
                    "error_message": result.error_message,
                    "timestamp": result.timestamp,
                    "iterations": result.iterations
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 申请结果已保存到: {file_path}")
            
        except Exception as e:
            print(f"❌ 保存结果失败: {str(e)}")

# 便利函数
async def create_unified_bot(backend: str = "browser-use", 
                           config_path: str = "config/browser_config.json",
                           job_data: Dict = None) -> UnifiedJobApplicationBot:
    """
    创建统一申请机器人的便利函数
    
    Args:
        backend: 后端类型 ("browser-use" 或 "openai-computer-use")
        config_path: 配置文件路径
        job_data: 职位数据
    
    Returns:
        初始化后的统一申请机器人
    """
    # 字符串到枚举的映射
    backend_mapping = {
        "browser-use": AutomationBackend.BROWSER_USE,
        "openai-computer-use": AutomationBackend.OPENAI_COMPUTER_USE,
        "openai": AutomationBackend.OPENAI_COMPUTER_USE,  # 简化别名
        "computer-use": AutomationBackend.OPENAI_COMPUTER_USE  # 简化别名
    }
    
    if backend not in backend_mapping:
        raise ValueError(f"不支持的后端类型: {backend}. 支持的类型: {list(backend_mapping.keys())}")
    
    backend_enum = backend_mapping[backend]
    
    bot = UnifiedJobApplicationBot(backend_enum, config_path, job_data)
    success = await bot.initialize(job_data)
    
    if not success:
        raise Exception(f"统一申请机器人初始化失败，后端: {backend}")
    
    return bot

def compare_backends():
    """比较不同后端的特点"""
    print("🔍 自动化后端比较:")
    print("\n1. Browser-use 后端:")
    print("   ✅ 成熟稳定，专为浏览器自动化设计")
    print("   ✅ 内置智能等待和错误处理")
    print("   ✅ 支持复杂的表单交互")
    print("   ❌ 依赖特定的browser-use库")
    
    print("\n2. OpenAI Computer Use 后端:")
    print("   ✅ 使用最新的OpenAI Computer Use API")
    print("   ✅ 更强的视觉理解和推理能力")
    print("   ✅ 原生支持截图分析")
    print("   ❌ 新技术，可能不如browser-use稳定")
    print("   ❌ 需要更多的API调用成本")

if __name__ == "__main__":
    # 测试代码
    async def test_unified_bot():
        """测试统一机器人"""
        try:
            # 测试数据
            test_job = {
                "title": "Python Developer",
                "company": "Test Company",
                "url": "https://example.com/job",
                "location": "Berlin"
            }
            
            # 显示后端比较
            compare_backends()
            
            # 测试browser-use后端
            print("\n🧪 测试 browser-use 后端:")
            try:
                bot1 = await create_unified_bot("browser-use", job_data=test_job)
                result1 = await bot1.apply_to_job()
                print(f"📊 Browser-use 结果: {result1.status}")
                await bot1.cleanup()
            except Exception as e:
                print(f"❌ Browser-use 测试失败: {str(e)}")
            
            # 测试OpenAI Computer Use后端
            print("\n🧪 测试 OpenAI Computer Use 后端:")
            try:
                bot2 = await create_unified_bot("openai-computer-use", job_data=test_job)
                result2 = await bot2.apply_to_job()
                print(f"📊 OpenAI Computer Use 结果: {result2.status}")
                await bot2.cleanup()
            except Exception as e:
                print(f"❌ OpenAI Computer Use 测试失败: {str(e)}")
            
        except Exception as e:
            print(f"❌ 统一测试失败: {str(e)}")
    
    # 运行测试
    asyncio.run(test_unified_bot())
