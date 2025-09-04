#!/usr/bin/env python3
"""
智能职位申请代理
结合Adzuna职位搜索和Browser-use自动申请功能
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from scripts.adzuna_job_search import AdzunaJobSearch
from scripts.browser_automation import JobApplicationBot, create_application_bot


class IntelligentJobApplyAgent:
    """智能职位申请代理"""
    
    def __init__(self):
        self.job_search = AdzunaJobSearch()
        self.application_bot: Optional[JobApplicationBot] = None
        
    async def initialize_bot(self):
        """初始化申请机器人"""
        print("🤖 初始化自动申请机器人...")
        try:
            self.application_bot = await create_application_bot()
            return True
        except Exception as e:
            print(f"❌ 机器人初始化失败: {str(e)}")
            print("💡 请确保已设置OPENAI_API_KEY环境变量")
            return False
    
    def search_jobs(self, query: str, location: str = "Berlin", max_results: int = 5) -> List[Dict]:
        """搜索职位"""
        print(f"🔍 搜索职位: {query} @ {location}")
        
        results = self.job_search.search(query, location=location, max_results=max_results)
        
        if results.get("status") == "success":
            jobs = results.get("data", {}).get("jobs", [])
            print(f"\n✅ 找到 {len(jobs)} 个岗位:")
            
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job.get('title')} - {job.get('company')} ({job.get('location')})")
                print(f"   💰 薪资: {job.get('salary_min', 'N/A')}-{job.get('salary_max', 'N/A')} {job.get('currency', 'EUR')}")
                print(f"   📅 发布时间: {job.get('created', 'N/A')}")
                print(f"   🔗 链接: {job.get('url', 'N/A')[:50]}...")
                print()
                
            return jobs
        else:
            print(f"❌ 搜索失败: {results.get('error', '未知错误')}")
            return []
    
    def filter_jobs(self, jobs: List[Dict], filters: Dict = None) -> List[Dict]:
        """过滤职位"""
        if not filters:
            return jobs
            
        filtered_jobs = []
        
        for job in jobs:
            # 薪资过滤
            if filters.get("min_salary"):
                salary_min = job.get("salary_min")
                if salary_min and salary_min < filters["min_salary"]:
                    continue
            
            # 关键词过滤
            if filters.get("required_keywords"):
                description = job.get("description", "").lower()
                title = job.get("title", "").lower()
                
                has_required_keywords = all(
                    keyword.lower() in description or keyword.lower() in title
                    for keyword in filters["required_keywords"]
                )
                
                if not has_required_keywords:
                    continue
            
            # 排除关键词过滤
            if filters.get("exclude_keywords"):
                description = job.get("description", "").lower()
                title = job.get("title", "").lower()
                
                has_excluded_keywords = any(
                    keyword.lower() in description or keyword.lower() in title
                    for keyword in filters["exclude_keywords"]
                )
                
                if has_excluded_keywords:
                    continue
            
            filtered_jobs.append(job)
        
        print(f"🎯 过滤后剩余 {len(filtered_jobs)} 个符合条件的职位")
        return filtered_jobs
    
    async def auto_apply_jobs(self, jobs: List[Dict]) -> Dict:
        """自动申请职位"""
        if not self.application_bot:
            print("❌ 申请机器人未初始化，请先调用 initialize_bot()")
            return {"status": "error", "message": "机器人未初始化"}
        
        if not jobs:
            print("❌ 没有可申请的职位")
            return {"status": "error", "message": "没有职位数据"}
        
        print(f"🚀 开始自动申请 {len(jobs)} 个职位...")
        
        try:
            results = await self.application_bot.batch_apply(jobs)
            summary = self.application_bot.get_summary()
            
            print(f"\n📊 申请完成!")
            print(f"总申请数: {summary['total_applications']}")
            print(f"成功申请: {summary['successful_applications']}")
            print(f"失败申请: {summary['failed_applications']}")
            print(f"成功率: {summary['success_rate']}")
            
            return {
                "status": "success",
                "summary": summary,
                "results": results
            }
            
        except Exception as e:
            error_msg = f"自动申请过程中出现错误: {str(e)}"
            print(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg}
    
    async def run_full_pipeline(self, 
                               query: str, 
                               location: str = "Berlin", 
                               max_results: int = 5,
                               filters: Dict = None,
                               auto_apply: bool = True) -> Dict:
        """运行完整的搜索和申请流程"""
        
        print("🎯 开始智能职位申请流程")
        print(f"搜索条件: {query} @ {location}")
        print(f"最大结果数: {max_results}")
        print(f"自动申请: {'是' if auto_apply else '否'}")
        
        # 1. 搜索职位
        jobs = self.search_jobs(query, location, max_results)
        
        if not jobs:
            return {"status": "error", "message": "未找到合适的职位"}
        
        # 2. 过滤职位
        if filters:
            jobs = self.filter_jobs(jobs, filters)
            
            if not jobs:
                return {"status": "error", "message": "过滤后没有符合条件的职位"}
        
        # 3. 显示将要申请的职位
        print(f"\n📋 准备申请以下职位:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.get('title')} @ {job.get('company')}")
        
        # 4. 自动申请（如果启用）
        if auto_apply:
            # 初始化申请机器人
            if not await self.initialize_bot():
                return {"status": "error", "message": "申请机器人初始化失败"}
            
            # 执行自动申请
            application_results = await self.auto_apply_jobs(jobs)
            
            # 清理资源
            if self.application_bot:
                await self.application_bot.cleanup()
            
            return {
                "status": "success",
                "search_results": jobs,
                "application_results": application_results
            }
        else:
            return {
                "status": "success", 
                "search_results": jobs,
                "message": "搜索完成，未执行自动申请"
            }
    
    async def cleanup(self):
        """清理资源"""
        if self.application_bot:
            await self.application_bot.cleanup()


# 便捷函数
def search_jobs(query: str = "Python developer", location: str = "Berlin", max_results: int = 3) -> List[Dict]:
    """简单的职位搜索函数（保持向后兼容）"""
    agent = IntelligentJobApplyAgent()
    return agent.search_jobs(query, location, max_results)


async def smart_job_apply(query: str, 
                         location: str = "Berlin", 
                         max_results: int = 5,
                         filters: Dict = None,
                         auto_apply: bool = True) -> Dict:
    """智能职位申请主函数"""
    agent = IntelligentJobApplyAgent()
    
    try:
        result = await agent.run_full_pipeline(
            query=query,
            location=location,
            max_results=max_results,
            filters=filters,
            auto_apply=auto_apply
        )
        
        await agent.cleanup()
        return result
        
    except Exception as e:
        await agent.cleanup()
        return {"status": "error", "message": str(e)}

