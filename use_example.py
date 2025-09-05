#!/usr/bin/env python3
"""
OpenAI Computer Use API 使用示例
Example usage of OpenAI Computer Use API for job applications
"""

import asyncio
import json
import os
from typing import Dict, List

# 确保脚本目录在Python路径中
import sys
sys.path.append('scripts')

try:
    from scripts.unified_automation import create_unified_bot, compare_backends
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保安装了所有必需的依赖并正确设置了Python路径")
    exit(1)

# 加载环境变量
load_dotenv()

class OpenAIComputerUseExample:
    """OpenAI Computer Use API 使用示例类"""
    
    def __init__(self):
        """初始化示例类"""
        self.config_path = "config/browser_config.json"
        self.ensure_config_exists()
    
    def ensure_config_exists(self):
        """确保配置文件存在"""
        if not os.path.exists(self.config_path):
            print(f"⚠️ 配置文件不存在: {self.config_path}")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        os.makedirs("config", exist_ok=True)
        
        default_config = {
            "browser_config": {
                "headless": False,
                "slow_mo": 1000,
                "timeout": 30000
            },
            "application_settings": {
                "max_applications_per_session": 3,
                "delay_between_applications": 30
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"✅ 已创建默认配置文件: {self.config_path}")
        except Exception as e:
            print(f"❌ 创建配置文件失败: {str(e)}")

    async def example_single_job_application(self):
        """示例：单个职位申请"""
        print("🎯 示例1: 单个职位申请 (OpenAI Computer Use)")
        print("=" * 60)
        
        # 示例职位数据
        test_job = {
            "title": "Python Developer",
            "company": "Example Company",
            "url": "https://apply.jcd.de/ApplyForm.php?iApplyFormID=600&iJobAdID=100218&iCodeNumber=&tc=3-10&",
            "location": "Berlin, Germany",
            "description": "Looking for an experienced Python developer..."
        }
        
        try:
            # 创建OpenAI Computer Use后端的机器人
            bot = await create_unified_bot(
                backend="browser-use",
                config_path=self.config_path,
                job_data=test_job
            )
            
            print(f"🚀 开始申请职位: {test_job['title']}")
            
            # 执行申请
            result = await bot.apply_to_job()
            
            # 打印结果
            print(f"\n📊 申请结果:")
            print(f"   状态: {result.status}")
            print(f"   后端: {result.backend_used}")
            print(f"   时间: {result.timestamp}")
            
            if result.error_message:
                print(f"   错误: {result.error_message}")
            
            # 清理资源
            await bot.cleanup()
            
        except Exception as e:
            print(f"❌ 单个职位申请示例失败: {str(e)}")

    async def example_batch_job_applications(self):
        """示例：批量职位申请"""
        print("\n🎯 示例2: 批量职位申请 (OpenAI Computer Use)")
        print("=" * 60)
        
        # 示例职位列表
        jobs_list = [
            {
                "title": "Python Developer",
                "company": "TechCorp",
                "url": "https://jobs.techcorp.com/python-dev",
                "location": "Berlin"
            },
            {
                "title": "Backend Engineer", 
                "company": "StartupXYZ",
                "url": "https://careers.startupxyz.com/backend",
                "location": "Munich"
            },
            {
                "title": "Full Stack Developer",
                "company": "BigTech",
                "url": "https://careers.bigtech.com/fullstack",
                "location": "Hamburg"
            }
        ]
        
        try:
            # 创建机器人
            bot = await create_unified_bot(
                backend="openai-computer-use",
                config_path=self.config_path
            )
            
            print(f"🚀 开始批量申请 {len(jobs_list)} 个职位")
            
            # 执行批量申请
            results = await bot.apply_to_multiple_jobs(jobs_list)
            
            # 保存结果
            bot.save_results("openai_computer_use_batch_results.json")
            
            # 清理资源
            await bot.cleanup()
            
        except Exception as e:
            print(f"❌ 批量职位申请示例失败: {str(e)}")

    async def example_backend_comparison(self):
        """示例：后端比较"""
        print("\n🎯 示例3: 后端比较测试")
        print("=" * 60)
        
        # 显示后端特点比较
        compare_backends()
        
        # 测试职位
        test_job = {
            "title": "Software Engineer",
            "company": "Comparison Test",
            "url": "https://example.com/software-engineer",
            "location": "Berlin"
        }
        
        backends_to_test = ["browser-use", "openai-computer-use"]
        results = {}
        
        for backend in backends_to_test:
            print(f"\n🧪 测试后端: {backend}")
            try:
                bot = await create_unified_bot(
                    backend=backend,
                    config_path=self.config_path,
                    job_data=test_job
                )
                
                import time
                start_time = time.time()
                
                result = await bot.apply_to_job()
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[backend] = {
                    "status": result.status,
                    "duration": duration,
                    "error": result.error_message
                }
                
                print(f"   ✅ 结果: {result.status} (耗时: {duration:.2f}秒)")
                
                await bot.cleanup()
                
            except Exception as e:
                results[backend] = {
                    "status": "failed",
                    "duration": 0,
                    "error": str(e)
                }
                print(f"   ❌ 失败: {str(e)}")
        
        # 比较结果
        print(f"\n📊 后端比较结果:")
        for backend, result in results.items():
            print(f"   {backend}: {result['status']} ({result['duration']:.2f}s)")

    def check_prerequisites(self):
        """检查前置条件"""
        print("🔍 检查前置条件...")
        
        # 检查OpenAI API Key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ 缺少 OPENAI_API_KEY 环境变量")
            return False
        else:
            print("✅ OpenAI API Key 已设置")
        
        # 检查个人数据配置
        if not os.path.exists("config/personal_data.json"):
            print("❌ 缺少个人数据配置文件: config/personal_data.json")
            return False
        else:
            print("✅ 个人数据配置文件存在")
        
        # 检查文档文件
        try:
            with open("config/personal_data.json", 'r', encoding='utf-8') as f:
                personal_data = json.load(f)
                documents = personal_data.get("documents", [])
                
                if not documents:
                    print("⚠️ 未配置文档文件")
                else:
                    valid_docs = 0
                    for doc in documents:
                        if os.path.exists(doc.get("file_path", "")):
                            valid_docs += 1
                    
                    print(f"✅ 文档文件: {valid_docs}/{len(documents)} 个可用")
                    
        except Exception as e:
            print(f"⚠️ 检查文档文件时出错: {str(e)}")
        
        return True

    async def run_all_examples(self):
        """运行所有示例"""
        print("🚀 OpenAI Computer Use API 使用示例")
        print("=" * 80)
        
        # 检查前置条件
        if not self.check_prerequisites():
            print("\n❌ 前置条件检查失败，请先配置必要的环境变量和文件")
            return
        
        try:
            # 运行各个示例
            await self.example_single_job_application()
            await self.example_batch_job_applications()
            await self.example_backend_comparison()
            await self.example_with_adzuna_integration()
            
            print("\n✅ 所有示例执行完成！")
            
        except Exception as e:
            print(f"❌ 示例执行失败: {str(e)}")

def main():
    """主函数"""
    print("🤖 OpenAI Computer Use API 职位申请自动化示例")
    print("请选择要运行的示例:")
    print("1. 单个职位申请")
    print("2. 批量职位申请")
    print("3. 后端比较测试")
    print("4. Adzuna集成示例")
    print("5. 运行所有示例")
    print("0. 退出")
    
    choice = input("\n请输入选择 (0-5): ").strip()
    
    example = OpenAIComputerUseExample()
    
    if choice == "1":
        asyncio.run(example.example_single_job_application())
    elif choice == "2":
        asyncio.run(example.example_batch_job_applications())
    elif choice == "3":
        asyncio.run(example.example_backend_comparison())
    elif choice == "4":
        asyncio.run(example.example_with_adzuna_integration())
    elif choice == "5":
        asyncio.run(example.run_all_examples())
    elif choice == "0":
        print("👋 再见！")
    else:
        print("❌ 无效选择，请重新运行程序")

if __name__ == "__main__":
    main()
