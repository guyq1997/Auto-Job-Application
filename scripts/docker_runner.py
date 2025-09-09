#!/usr/bin/env python3
"""
Docker容器运行脚本
Docker Container Runner Script
"""

import asyncio
import json
import os
import sys
import argparse
from typing import Dict, List
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append('/app')

try:
    from scripts.unified_automation import create_unified_bot
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)

# 加载环境变量
load_dotenv()

class DockerJobRunner:
    """Docker容器中的职位申请运行器"""
    
    def __init__(self, container_id: str = None):
        self.container_id = container_id or os.getenv("CONTAINER_ID", "unknown")
        self.results_dir = "/app/results"
        self.ensure_results_dir()
    
    def ensure_results_dir(self):
        """确保结果目录存在"""
        os.makedirs(self.results_dir, exist_ok=True)
    
    async def run_single_job(self, job_data: Dict, backend: str = "browser-use") -> Dict:
        """运行单个职位申请"""
        print(f"🐳 容器 {self.container_id} 开始处理职位: {job_data.get('title', 'Unknown')}")
        
        try:
            # 创建机器人实例
            bot = await create_unified_bot(
                backend=backend,
                config_path="/app/config/browser_config.json",
                job_data=job_data
            )
            
            # 执行申请
            result = await bot.apply_to_job()
            
            # 清理资源
            await bot.cleanup()
            
            # 转换为可序列化的字典
            result_dict = {
                "container_id": self.container_id,
                "job_url": result.job_url,
                "job_title": result.job_title,
                "company": result.company,
                "status": result.status,
                "backend_used": result.backend_used,
                "error_message": result.error_message,
                "timestamp": result.timestamp,
                "processing_time": None  # 可以添加处理时间
            }
            
            print(f"✅ 容器 {self.container_id} 完成职位申请: {result.status}")
            return result_dict
            
        except Exception as e:
            error_result = {
                "container_id": self.container_id,
                "job_url": job_data.get("url", ""),
                "job_title": job_data.get("title", "Unknown"),
                "company": job_data.get("company", "Unknown"),
                "status": "failed",
                "backend_used": backend,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
                "processing_time": None
            }
            
            print(f"❌ 容器 {self.container_id} 申请失败: {str(e)}")
            return error_result
    
    async def run_job_batch(self, jobs: List[Dict], backend: str = "browser-use") -> List[Dict]:
        """运行一批职位申请"""
        print(f"🚀 容器 {self.container_id} 开始处理 {len(jobs)} 个职位")
        
        results = []
        for i, job_data in enumerate(jobs, 1):
            print(f"\n📍 处理第 {i}/{len(jobs)} 个职位")
            
            result = await self.run_single_job(job_data, backend)
            results.append(result)
            
            # 保存中间结果
            await self.save_intermediate_result(result)
            
            # 添加延迟避免过于频繁的请求
            if i < len(jobs):
                await asyncio.sleep(2)
        
        # 保存最终结果
        await self.save_batch_results(results)
        
        print(f"🎉 容器 {self.container_id} 完成批处理")
        return results
    
    async def save_intermediate_result(self, result: Dict):
        """保存中间结果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_{self.container_id}_{timestamp}.json"
            filepath = os.path.join(self.results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ 保存中间结果失败: {str(e)}")
    
    async def save_batch_results(self, results: List[Dict]):
        """保存批次结果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_{self.container_id}_{timestamp}.json"
            filepath = os.path.join(self.results_dir, filename)
            
            batch_summary = {
                "container_id": self.container_id,
                "timestamp": timestamp,
                "total_jobs": len(results),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(batch_summary, f, indent=2, ensure_ascii=False)
            
            print(f"💾 批次结果已保存: {filepath}")
            
        except Exception as e:
            print(f"❌ 保存批次结果失败: {str(e)}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Docker容器职位申请运行器")
    
    parser.add_argument(
        "--jobs",
        type=str,
        help="职位数据JSON字符串或文件路径"
    )
    
    parser.add_argument(
        "--backend",
        type=str,
        default="browser-use",
        choices=["browser-use", "openai-computer-use"],
        help="选择自动化后端"
    )
    
    parser.add_argument(
        "--container-id",
        type=str,
        help="容器ID标识"
    )
    
    return parser.parse_args()

async def main():
    """主函数"""
    print("🐳 Docker容器职位申请运行器启动")
    
    # 解析参数
    args = parse_arguments()
    
    # 检查必要的环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 缺少 OPENAI_API_KEY 环境变量")
        sys.exit(1)
    
    # 获取职位数据
    jobs_data = []
    
    if args.jobs:
        try:
            # 尝试作为JSON字符串解析
            if args.jobs.startswith('[') or args.jobs.startswith('{'):
                jobs_data = json.loads(args.jobs)
            else:
                # 尝试作为文件路径读取
                with open(args.jobs, 'r', encoding='utf-8') as f:
                    jobs_data = json.load(f)
        except Exception as e:
            print(f"❌ 解析职位数据失败: {str(e)}")
            sys.exit(1)
    else:

        print(f"❌ 解析环境变量中的职位数据失败: {str(e)}")
        sys.exit(1)

    if not jobs_data:
        print("❌ 没有找到职位数据")
        sys.exit(1)
    
    # 确保jobs_data是列表
    if isinstance(jobs_data, dict):
        jobs_data = [jobs_data]
    
    print(f"📋 准备处理 {len(jobs_data)} 个职位")
    
    # 创建运行器
    runner = DockerJobRunner(container_id=args.container_id)
    
    # 运行批处理
    try:
        results = await runner.run_job_batch(jobs_data, args.backend)
        
        # 输出摘要
        successful = len([r for r in results if r["status"] == "success"])
        failed = len([r for r in results if r["status"] == "failed"])
        
        print(f"\n📊 容器 {runner.container_id} 执行摘要:")
        print(f"   ✅ 成功: {successful}")
        print(f"   ❌ 失败: {failed}")
        print(f"   📁 结果已保存到: {runner.results_dir}")
        
        # 返回适当的退出码
        sys.exit(0 if failed == 0 else 1)
        
    except Exception as e:
        print(f"❌ 批处理执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
