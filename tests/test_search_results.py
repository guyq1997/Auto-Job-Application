#!/usr/bin/env python3
"""
测试脚本：展示Adzuna搜索结果的详细结构
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.adzuna_job_search import AdzunaJobSearch

def test_search_results():
    """测试并展示搜索结果的详细结构"""
    
    print("🔍 Adzuna搜索结果结构测试")
    print("=" * 60)
    
    # 创建搜索实例
    job_search = AdzunaJobSearch()
    
    # 执行搜索
    print("正在搜索 'Python developer' 在柏林的岗位...")
    results = job_search.search("Python developer", location="Berlin", max_results=2)
    
    print("\n📊 完整搜索结果结构:")
    print("-" * 40)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    
    if results.get("status") == "success":
        data = results.get("data", {})
        jobs = data.get("jobs", [])
        
        print(f"\n✅ 搜索成功!")
        print(f"📈 总计找到: {data.get('total_count', 0)} 个岗位")
        print(f"📋 返回数量: {data.get('returned_count', 0)} 个岗位")
        
        if jobs:
            print(f"\n🔍 第一个岗位的详细信息:")
            print("-" * 40)
            first_job = jobs[0]
            
            print("📋 岗位字段和值:")
            for key, value in first_job.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
            
            print(f"\n📝 岗位描述（完整）:")
            print("-" * 40)
            print(first_job.get('description', 'N/A'))
            
            print(f"\n🔗 完整URL:")
            print(first_job.get('url', 'N/A'))
            
        print(f"\n📊 所有岗位概览:")
        print("-" * 40)
        for i, job in enumerate(jobs, 1):
            print(f"{i}. 【{job.get('title', 'N/A')}】")
            print(f"   🏢 公司: {job.get('company', 'N/A')}")
            print(f"   📍 地点: {job.get('location', 'N/A')}")
            print(f"   💰 薪资: {job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')} {job.get('currency', 'EUR')}")
            print(f"   📅 发布: {job.get('created', 'N/A')}")
            print(f"   📂 分类: {job.get('category', 'N/A')}")
            print(f"   📋 合同: {job.get('contract_type', 'N/A')} / {job.get('contract_time', 'N/A')}")
            print()
    else:
        print(f"❌ 搜索失败: {results.get('error', '未知错误')}")
        if 'suggestion' in results:
            print(f"💡 建议: {results['suggestion']}")
        if 'setup_url' in results:
            print(f"🔗 设置链接: {results['setup_url']}")

def test_formatted_output():
    """测试格式化输出"""
    print("\n" + "=" * 60)
    print("🎨 格式化输出测试")
    print("=" * 60)
    
    job_search = AdzunaJobSearch()
    
    # 使用格式化输出
    formatted_result = job_search.search_and_format(
        "Data Scientist", 
        location="Munich", 
        max_results=2
    )
    
    print("📄 格式化输出结果:")
    print("-" * 40)
    print(formatted_result)

if __name__ == "__main__":
    try:
        test_search_results()
        test_formatted_output()
        print("\n✅ 测试完成!")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
