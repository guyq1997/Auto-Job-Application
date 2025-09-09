#!/usr/bin/env python3
"""
Docker批量运行管理器
Docker Batch Manager for Parallel Job Applications
"""

import asyncio
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path
import concurrent.futures

class DockerBatchManager:
    """Docker批量运行管理器"""
    
    def __init__(self, max_containers: int = 5, backend: str = "browser-use"):
        self.max_containers = max_containers
        self.backend = backend
        self.image_name = "job-application-bot"
        self.results_dir = Path("./docker_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # 确保Docker镜像存在
        self.ensure_docker_image()
    
    def ensure_docker_image(self):
        """确保Docker镜像已构建"""
        print("🔍 检查Docker镜像...")
        
        try:
            # 检查镜像是否存在
            result = subprocess.run(
                ["docker", "images", "-q", self.image_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                print("🏗️ 构建Docker镜像...")
                self.build_docker_image()
            else:
                print("✅ Docker镜像已存在")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 检查Docker镜像失败: {e}")
            raise
    
    def build_docker_image(self):
        """构建Docker镜像"""
        print("🏗️ 开始构建Docker镜像...")
        
        try:
            # 构建镜像
            result = subprocess.run(
                ["docker", "build", "-t", self.image_name, "."],
                cwd=Path.cwd(),
                check=True
            )
            
            print("✅ Docker镜像构建完成")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker镜像构建失败: {e}")
            raise
    
    def split_jobs_into_batches(self, jobs: List[Dict], batch_size: int = None) -> List[List[Dict]]:
        """将职位列表分割成批次"""
        if batch_size is None:
            # 根据容器数量自动分割
            batch_size = max(1, len(jobs) // self.max_containers)
            if len(jobs) % self.max_containers:
                batch_size += 1
        
        batches = []
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            batches.append(batch)
        
        print(f"📦 将 {len(jobs)} 个职位分割成 {len(batches)} 个批次")
        return batches
    
    def run_container(self, container_id: str, jobs_batch: List[Dict]) -> Tuple[str, int, str]:
        """运行单个Docker容器"""
        print(f"🐳 启动容器 {container_id}，处理 {len(jobs_batch)} 个职位")
        
        try:
            # 创建临时文件存储职位数据
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(jobs_batch, f, indent=2, ensure_ascii=False)
                jobs_file = f.name
            
            # 准备环境变量
            env_vars = [
                f"OPENAI_API_KEY={os.getenv('OPENAI_API_KEY')}",
                f"CONTAINER_ID={container_id}",
                f"Email={os.getenv('Email', '')}",
                f"Password={os.getenv('Password', '')}"
            ]
            
            # 构建Docker运行命令
            docker_cmd = [
                "docker", "run",
                "--rm",  # 运行完成后自动删除容器
                "--name", f"job-bot-{container_id}",
                "-v", f"{jobs_file}:/tmp/jobs.json:ro",  # 挂载职位数据文件
                "-v", f"{self.results_dir.absolute()}:/app/results",  # 挂载结果目录
            ]
            
            # 添加环境变量
            for env_var in env_vars:
                docker_cmd.extend(["-e", env_var])
            
            # 添加镜像和命令
            docker_cmd.extend([
                self.image_name,
                "python", "-m", "scripts.docker_runner",
                "--jobs", "/tmp/jobs.json",
                "--backend", self.backend,
                "--container-id", container_id
            ])
            
            # 运行容器
            start_time = time.time()
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            end_time = time.time()
            
            # 清理临时文件
            os.unlink(jobs_file)
            
            duration = end_time - start_time
            print(f"🏁 容器 {container_id} 完成，耗时 {duration:.1f}s，退出码: {result.returncode}")
            
            return container_id, result.returncode, result.stdout + result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"⏰ 容器 {container_id} 超时")
            # 尝试停止容器
            subprocess.run(["docker", "stop", f"job-bot-{container_id}"], capture_output=True)
            return container_id, -1, "Container timeout"
            
        except Exception as e:
            print(f"❌ 容器 {container_id} 运行失败: {str(e)}")
            return container_id, -2, str(e)
    
    async def run_batch_parallel(self, jobs: List[Dict]) -> Dict:
        """并行运行多个容器批次"""
        print(f"🚀 开始并行批量处理 {len(jobs)} 个职位")
        print(f"📊 使用 {self.max_containers} 个并行容器")
        
        # 分割任务
        job_batches = self.split_jobs_into_batches(jobs)
        
        # 记录开始时间
        start_time = time.time()
        
        # 使用线程池并行运行容器
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_containers) as executor:
            # 提交所有任务
            future_to_container = {}
            for i, batch in enumerate(job_batches):
                container_id = f"batch-{i+1:03d}"
                future = executor.submit(self.run_container, container_id, batch)
                future_to_container[future] = container_id
            
            # 收集结果
            container_results = {}
            for future in concurrent.futures.as_completed(future_to_container):
                container_id = future_to_container[future]
                try:
                    container_id, exit_code, output = future.result()
                    container_results[container_id] = {
                        "exit_code": exit_code,
                        "output": output,
                        "success": exit_code == 0
                    }
                except Exception as e:
                    container_results[container_id] = {
                        "exit_code": -3,
                        "output": str(e),
                        "success": False
                    }
        
        # 记录结束时间
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 收集和汇总结果
        summary = await self.collect_results(container_results, total_duration)
        
        return summary
    
    async def collect_results(self, container_results: Dict, total_duration: float) -> Dict:
        """收集和汇总所有容器的结果"""
        print("📊 收集和汇总结果...")
        
        all_results = []
        successful_containers = 0
        total_jobs_processed = 0
        total_successful_jobs = 0
        total_failed_jobs = 0
        
        # 读取每个容器的结果文件
        for result_file in self.results_dir.glob("batch_*.json"):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    
                    all_results.extend(batch_data.get("results", []))
                    total_jobs_processed += batch_data.get("total_jobs", 0)
                    total_successful_jobs += batch_data.get("successful", 0)
                    total_failed_jobs += batch_data.get("failed", 0)
                    
                    if batch_data.get("successful", 0) > 0:
                        successful_containers += 1
                        
            except Exception as e:
                print(f"⚠️ 读取结果文件失败 {result_file}: {str(e)}")
        
        # 生成汇总报告
        summary = {
            "timestamp": datetime.now().isoformat(),
            "execution_time": total_duration,
            "containers": {
                "total": len(container_results),
                "successful": successful_containers,
                "failed": len(container_results) - successful_containers
            },
            "jobs": {
                "total": total_jobs_processed,
                "successful": total_successful_jobs,
                "failed": total_failed_jobs,
                "success_rate": (total_successful_jobs / total_jobs_processed * 100) if total_jobs_processed > 0 else 0
            },
            "container_results": container_results,
            "detailed_results": all_results
        }
        
        # 保存汇总报告
        summary_file = self.results_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        self.print_summary(summary)
        
        return summary
    
    def print_summary(self, summary: Dict):
        """打印执行摘要"""
        print("\n" + "="*60)
        print("📊 批量执行摘要报告")
        print("="*60)
        
        print(f"⏱️ 总执行时间: {summary['execution_time']:.1f} 秒")
        print(f"🐳 容器统计:")
        print(f"   总数: {summary['containers']['total']}")
        print(f"   成功: {summary['containers']['successful']}")
        print(f"   失败: {summary['containers']['failed']}")
        
        print(f"📋 职位申请统计:")
        print(f"   总数: {summary['jobs']['total']}")
        print(f"   成功: {summary['jobs']['successful']}")
        print(f"   失败: {summary['jobs']['failed']}")
        print(f"   成功率: {summary['jobs']['success_rate']:.1f}%")
        
        print(f"📁 详细结果保存在: {self.results_dir.absolute()}")
        print("="*60)

# 便利函数
async def run_docker_batch(jobs: List[Dict], max_containers: int = 5, backend: str = "browser-use") -> Dict:
    """运行Docker批量处理的便利函数"""
    manager = DockerBatchManager(max_containers=max_containers, backend=backend)
    return await manager.run_batch_parallel(jobs)

if __name__ == "__main__":
    import argparse
    
    def parse_args():
        parser = argparse.ArgumentParser(description="Docker批量职位申请管理器")
        parser.add_argument("--jobs-file", required=True, help="职位数据JSON文件路径")
        parser.add_argument("--max-containers", type=int, default=5, help="最大并行容器数")
        parser.add_argument("--backend", choices=["browser-use", "openai-computer-use"], 
                          default="browser-use", help="自动化后端")
        return parser.parse_args()
    
    async def main():
        args = parse_args()
        
        # 加载.env文件（如果存在）
        from dotenv import load_dotenv
        load_dotenv()
        
        # 检查必要的环境变量
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ 请设置 OPENAI_API_KEY 环境变量")
            print("   在 .env 文件中添加: OPENAI_API_KEY=your_api_key")
            return
        
        # 读取职位数据
        try:
            with open(args.jobs_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
        except Exception as e:
            print(f"❌ 读取职位文件失败: {str(e)}")
            return
        
        # 运行批量处理
        summary = await run_docker_batch(
            jobs=jobs,
            max_containers=args.max_containers,
            backend=args.backend
        )
        
        print(f"🎉 批量处理完成！详细结果请查看: docker_results/")
    
    # 运行主函数
    asyncio.run(main())
