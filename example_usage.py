#!/usr/bin/env python3
"""
智能职位申请代理使用示例
演示如何使用完整的搜索和自动申请功能
"""

import asyncio
import os
from apply_agent import smart_job_apply, IntelligentJobApplyAgent


async def example_basic_usage():
    """基础使用示例"""
    print("🚀 基础使用示例")
    print("=" * 50)
    
    # 基础搜索和申请
    result = await smart_job_apply(
        query="Python Developer",
        location="Berlin",
        max_results=3,
        auto_apply=True  # 设置为False只搜索不申请
    )
    
    if result["status"] == "success":
        print("✅ 流程执行成功!")
        if "application_results" in result:
            summary = result["application_results"]["summary"]
            print(f"申请摘要: {summary}")
    else:
        print(f"❌ 流程执行失败: {result['message']}")


async def example_advanced_usage():
    """高级使用示例 - 带过滤条件"""
    print("\n🎯 高级使用示例 - 带过滤条件")
    print("=" * 50)
    
    # 定义过滤条件
    filters = {
        "min_salary": 50000,  # 最低薪资
        "required_keywords": ["Python", "Django"],  # 必须包含的关键词
        "exclude_keywords": ["Internship", "Junior"]  # 排除的关键词
    }
    
    result = await smart_job_apply(
        query="Senior Python Developer",
        location="Berlin",
        max_results=10,
        filters=filters,
        auto_apply=True
    )
    
    if result["status"] == "success":
        print("✅ 高级搜索完成!")
        search_results = result.get("search_results", [])
        print(f"符合条件的职位数: {len(search_results)}")
    else:
        print(f"❌ 搜索失败: {result['message']}")


async def example_manual_control():
    """手动控制示例 - 分步执行"""
    print("\n🔧 手动控制示例")
    print("=" * 50)
    
    agent = IntelligentJobApplyAgent()
    
    try:
        # 1. 搜索职位
        jobs = agent.search_jobs("Data Scientist", "Munich", 5)
        
        if not jobs:
            print("未找到合适的职位")
            return
        
        # 2. 手动过滤
        print(f"\n找到 {len(jobs)} 个职位，请选择要申请的职位:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']} @ {job['company']}")
        
        # 模拟用户选择（实际使用时可以添加用户输入）
        selected_indices = [0, 1]  # 选择前两个职位
        selected_jobs = [jobs[i] for i in selected_indices if i < len(jobs)]
        
        print(f"\n选择了 {len(selected_jobs)} 个职位进行申请")
        
        # 3. 初始化机器人
        if await agent.initialize_bot():
            # 4. 执行申请
            results = await agent.auto_apply_jobs(selected_jobs)
            print(f"申请结果: {results}")
        
        # 5. 清理资源
        await agent.cleanup()
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        await agent.cleanup()


async def example_search_only():
    """仅搜索示例 - 不执行申请"""
    print("\n🔍 仅搜索示例")
    print("=" * 50)
    
    result = await smart_job_apply(
        query="Machine Learning Engineer",
        location="Hamburg",
        max_results=5,
        auto_apply=False  # 只搜索，不申请
    )
    
    if result["status"] == "success":
        jobs = result["search_results"]
        print(f"✅ 搜索完成，找到 {len(jobs)} 个职位")
        
        # 显示详细信息
        for job in jobs:
            print(f"\n📋 {job['title']} @ {job['company']}")
            print(f"   🏢 地点: {job['location']}")
            print(f"   💰 薪资: {job.get('salary_min', 'N/A')}-{job.get('salary_max', 'N/A')} {job.get('currency', 'EUR')}")
            print(f"   📅 发布: {job['created']}")
            print(f"   🔗 链接: {job['url']}")
    else:
        print(f"❌ 搜索失败: {result['message']}")


def check_environment():
    """检查环境配置"""
    print("🔧 检查环境配置")
    print("=" * 50)
    
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: 已设置")
    
    if missing_vars:
        print(f"\n❌ 缺少以下环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请在 .env 文件中设置这些变量，或者在系统环境中设置")
        return False
    
    print("\n✅ 环境配置检查通过!")
    return True


async def main():
    """主函数"""
    print("🤖 智能职位申请代理 - 使用示例")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n💡 提示: 创建 .env 文件并添加以下内容:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return
    
    try:
        # 运行各种示例
        await example_search_only()
        
        # 询问是否继续执行自动申请示例
        print("\n" + "="*60)
        print("⚠️  接下来的示例将执行自动申请功能")
        print("⚠️  请确保你已经准备好并了解相关风险")
        print("⚠️  建议先在测试环境中运行")
        
        # 在实际使用中，这里可以添加用户确认
        # user_confirm = input("是否继续? (y/N): ").strip().lower()
        # if user_confirm == 'y':
        #     await example_basic_usage()
        #     await example_advanced_usage()
        #     await example_manual_control()
        
        print("\n✅ 示例运行完成!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了程序")
    except Exception as e:
        print(f"\n❌ 运行过程中出现错误: {str(e)}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
