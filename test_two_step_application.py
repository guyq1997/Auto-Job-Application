#!/usr/bin/env python3
"""
测试两步骤职位申请流程
演示如何使用两个sequential的Browser-use agents
"""

import asyncio
import os
from scripts.browser_automation import JobApplicationBot


async def test_two_step_application():
    """测试两步骤申请流程"""
    print("🧪 测试两步骤职位申请流程")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置OPENAI_API_KEY环境变量")
        print("💡 在终端中运行: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # 创建申请机器人
    bot = JobApplicationBot()
    
    try:
        # 测试职位数据
        test_job = {
            "title": "Senior Python Developer",
            "company": "Tech Company",
            "location": "Berlin, Germany",
            "url": "https://www.guldberg.de/stellenangebote/stellenanzeige/job-entwicklungsingenieur-hardware-m-w-d-kiel-14606",  # 示例URL
            "description": "We are looking for a Senior Python Developer..."
        }
        
        print(f"\n📋 测试职位信息:")
        print(f"职位: {test_job['title']}")
        print(f"公司: {test_job['company']}")
        print(f"地点: {test_job['location']}")
        print(f"链接: {test_job['url']}")
        
        # 初始化机器人（创建两个agents）
        print("🚀 初始化申请机器人...")
        success = await bot.initialize(job_data=test_job)
        
        if not success:
            print("❌ 机器人初始化失败")
            return
        

        # 执行两步骤申请流程
        print(f"\n🎯 开始两步骤申请流程...")
        result = await bot.apply_to_job()
        
        # 显示结果
        print(f"\n📊 申请结果:")
        print(f"状态: {result.status}")
        print(f"职位: {result.job_title}")
        print(f"公司: {result.company}")
        
        if result.error_message:
            print(f"错误信息: {result.error_message}")
        
        if result.screenshot_path:
            print(f"截图路径: {result.screenshot_path}")
        
        print(f"时间戳: {result.timestamp}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
    
    finally:
        # 清理资源
        await bot.cleanup()
        print("\n✅ 测试完成")


async def test_batch_application():
    """测试批量申请"""
    print("\n🧪 测试批量申请流程")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置OPENAI_API_KEY环境变量")
        return
    
    bot = JobApplicationBot()
    
    try:
        success = await bot.initialize()
        if not success:
            return
        
        # 多个测试职位
        test_jobs = [
            {
                "title": "Python Developer",
                "company": "StartupA",
                "location": "Berlin",
                "url": "https://example1.com/job1"
            },
            {
                "title": "Full Stack Developer", 
                "company": "StartupB",
                "location": "Munich",
                "url": "https://example2.com/job2"
            }
        ]
        
        print(f"📋 准备批量申请 {len(test_jobs)} 个职位")
        
        # 批量申请
        results = await bot.batch_apply(test_jobs)
        
        # 显示摘要
        summary = bot.get_summary()
        print(f"\n📊 批量申请摘要:")
        print(f"总申请数: {summary['total_applications']}")
        print(f"成功申请: {summary['successful_applications']}")
        print(f"失败申请: {summary['failed_applications']}")
        print(f"成功率: {summary['success_rate']}")
        
    except Exception as e:
        print(f"❌ 批量申请测试失败: {str(e)}")
    
    finally:
        await bot.cleanup()


async def interactive_test():
    """交互式测试"""
    print("\n🧪 交互式测试模式")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置OPENAI_API_KEY环境变量")
        return
    
    bot = JobApplicationBot()
    
    try:
        success = await bot.initialize()
        if not success:
            return
        
        print("✅ 机器人已初始化，两个代理已准备就绪")
        print("📝 代理1: 导航代理 - 负责找到申请表单")
        print("📝 代理2: 表单代理 - 负责填写表单")
        
        while True:
            print(f"\n" + "="*40)
            job_url = input("请输入职位URL (或输入 'q' 退出): ").strip()
            
            if job_url.lower() == 'q':
                break
            
            if not job_url.startswith('http'):
                print("⚠️ 请输入有效的URL")
                continue
            
            job_title = input("请输入职位标题: ").strip() or "未知职位"
            company = input("请输入公司名称: ").strip() or "未知公司"
            
            test_job = {
                "title": job_title,
                "company": company,
                "location": "Unknown",
                "url": job_url
            }
            
            print(f"\n🎯 开始申请: {job_title} @ {company}")
            
            try:
                result = await bot.apply_to_job(test_job)
                
                print(f"\n📊 申请结果: {result.status}")
                if result.error_message:
                    print(f"错误: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ 申请失败: {str(e)}")
            
            continue_test = input("\n继续测试? (y/N): ").strip().lower()
            if continue_test != 'y':
                break
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"❌ 交互式测试失败: {str(e)}")
    
    finally:
        await bot.cleanup()


async def main():
    """主测试函数"""
    print("🤖 两步骤职位申请系统测试")
    print("=" * 60)
    print("系统特点:")
    print("✅ 使用两个sequential的Browser-use agents")
    print("✅ Agent 1: 专门负责导航和找到申请表单")
    print("✅ Agent 2: 专门负责填写和提交表单")
    print("✅ 共享同一个浏览器会话，保持状态连续性")
    print("=" * 60)
    
    while True:
        print(f"\n请选择测试模式:")
        print("1. 基础功能测试")
        print("2. 批量申请测试") 
        print("3. 交互式测试")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            await test_two_step_application()
        elif choice == '2':
            await test_batch_application()
        elif choice == '3':
            await interactive_test()
        elif choice == '4':
            print("👋 再见!")
            break
        else:
            print("⚠️ 无效选择，请重试")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
    except Exception as e:
        print(f"\n❌ 测试运行失败: {str(e)}")
