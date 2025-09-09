#!/usr/bin/env python3
"""
Docker批量申请故障排除工具
Troubleshooting tool for Docker batch job applications
"""

import json
import os
import subprocess
import sys
from pathlib import Path

class TroubleshootTool:
    """故障排除工具"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues_found = []
        self.fixes_applied = []
    
    def print_header(self):
        """打印头部信息"""
        print("🔧 Docker批量申请故障排除工具")
        print("=" * 50)
        print()
    
    def check_docker(self):
        """检查Docker状态"""
        print("🐳 检查Docker...")
        
        # 检查Docker是否安装
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker已安装: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.issues_found.append("Docker未安装或不在PATH中")
            print("❌ Docker未安装")
            print("   解决方案: 请安装Docker Desktop")
            return False
        
        # 检查Docker是否运行
        try:
            subprocess.run(["docker", "info"], 
                         capture_output=True, check=True)
            print("✅ Docker服务正在运行")
        except subprocess.CalledProcessError:
            self.issues_found.append("Docker服务未运行")
            print("❌ Docker服务未运行")
            print("   解决方案: 启动Docker Desktop")
            return False
        
        # 检查Docker权限
        try:
            subprocess.run(["docker", "ps"], 
                         capture_output=True, check=True)
            print("✅ Docker权限正常")
        except subprocess.CalledProcessError:
            self.issues_found.append("Docker权限问题")
            print("❌ Docker权限问题")
            print("   解决方案: sudo usermod -aG docker $USER")
            return False
        
        return True
    
    def check_environment(self):
        """检查环境变量"""
        print("\n🌍 检查环境变量...")
        
        # 检查OpenAI API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.issues_found.append("缺少OPENAI_API_KEY环境变量")
            print("❌ OPENAI_API_KEY未设置")
            print("   解决方案: export OPENAI_API_KEY='your_api_key'")
            return False
        elif not api_key.startswith("sk-"):
            self.issues_found.append("OPENAI_API_KEY格式可能不正确")
            print("⚠️ OPENAI_API_KEY格式可能不正确")
            print("   API密钥应该以 'sk-' 开头")
        else:
            print("✅ OPENAI_API_KEY已设置")
        
        # 检查可选环境变量
        optional_vars = ["Email", "Password"]
        for var in optional_vars:
            if os.getenv(var):
                print(f"✅ {var}已设置")
            else:
                print(f"ℹ️ {var}未设置（可选）")
        
        return True
    
    def check_files(self):
        """检查必要文件"""
        print("\n📁 检查必要文件...")
        
        required_files = [
            "Dockerfile",
            "docker_batch_manager.py",
            "run_docker_batch.sh",
            "scripts/docker_runner.py",
            "scripts/unified_automation.py",
            "config/browser_config.json",
            "config/personal_data.json",
            "example_jobs.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"❌ {file_path}")
        
        if missing_files:
            self.issues_found.append(f"缺少必要文件: {', '.join(missing_files)}")
            return False
        
        return True
    
    def check_permissions(self):
        """检查文件权限"""
        print("\n🔐 检查文件权限...")
        
        executable_files = [
            "run_docker_batch.sh"
        ]
        
        for file_path in executable_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                if os.access(full_path, os.X_OK):
                    print(f"✅ {file_path} 可执行")
                else:
                    self.issues_found.append(f"{file_path}没有执行权限")
                    print(f"❌ {file_path} 没有执行权限")
                    print(f"   解决方案: chmod +x {file_path}")
        
        return True
    
    def check_config_files(self):
        """检查配置文件"""
        print("\n⚙️ 检查配置文件...")
        
        # 检查browser_config.json
        browser_config_path = self.project_root / "config/browser_config.json"
        if browser_config_path.exists():
            try:
                with open(browser_config_path, 'r') as f:
                    config = json.load(f)
                
                # 检查关键配置
                browser_config = config.get("browser_config", {})
                if "headless" in browser_config:
                    headless = browser_config["headless"]
                    print(f"✅ 浏览器配置: headless={headless}")
                    if not headless:
                        print("   建议: 使用headless=true以避免干扰")
                else:
                    print("⚠️ 浏览器配置中缺少headless设置")
                
            except json.JSONDecodeError:
                self.issues_found.append("browser_config.json格式错误")
                print("❌ browser_config.json格式错误")
                return False
        
        # 检查personal_data.json
        personal_data_path = self.project_root / "config/personal_data.json"
        if personal_data_path.exists():
            try:
                with open(personal_data_path, 'r') as f:
                    data = json.load(f)
                
                if "personal_info" in data:
                    print("✅ 个人信息配置存在")
                else:
                    print("⚠️ 个人信息配置中缺少personal_info")
                
                if "documents" in data:
                    docs = data["documents"]
                    print(f"✅ 配置了{len(docs)}个文档")
                    
                    # 检查文档文件是否存在
                    for doc in docs:
                        doc_path = doc.get("file_path", "")
                        if doc_path and os.path.exists(doc_path):
                            print(f"   ✅ {doc_path}")
                        else:
                            print(f"   ❌ {doc_path} 不存在")
                            self.issues_found.append(f"文档文件不存在: {doc_path}")
                
            except json.JSONDecodeError:
                self.issues_found.append("personal_data.json格式错误")
                print("❌ personal_data.json格式错误")
                return False
        
        return True
    
    def check_docker_image(self):
        """检查Docker镜像"""
        print("\n🖼️ 检查Docker镜像...")
        
        try:
            result = subprocess.run(["docker", "images", "-q", "job-application-bot"],
                                  capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                print("✅ Docker镜像已存在")
                return True
            else:
                print("❌ Docker镜像不存在")
                print("   解决方案: 运行 ./run_docker_batch.sh 会自动构建镜像")
                return False
                
        except subprocess.CalledProcessError:
            print("❌ 检查Docker镜像失败")
            return False
    
    def check_running_containers(self):
        """检查运行中的容器"""
        print("\n🏃 检查运行中的容器...")
        
        try:
            result = subprocess.run(["docker", "ps", "--filter", "name=job-bot", "--format", "{{.Names}}"],
                                  capture_output=True, text=True, check=True)
            
            containers = [c.strip() for c in result.stdout.split() if c.strip()]
            
            if containers:
                print(f"ℹ️ 发现{len(containers)}个运行中的job-bot容器:")
                for container in containers:
                    print(f"   🏃 {container}")
                print("   如果需要，可以运行 ./run_docker_batch.sh --cleanup 清理")
            else:
                print("✅ 没有运行中的job-bot容器")
            
            return True
            
        except subprocess.CalledProcessError:
            print("❌ 检查运行容器失败")
            return False
    
    def check_results_directory(self):
        """检查结果目录"""
        print("\n📊 检查结果目录...")
        
        results_dir = self.project_root / "docker_results"
        
        if not results_dir.exists():
            print("ℹ️ 结果目录不存在，将在首次运行时创建")
            return True
        
        # 检查结果文件
        summary_files = list(results_dir.glob("summary_*.json"))
        batch_files = list(results_dir.glob("batch_*.json"))
        
        print(f"ℹ️ 结果目录存在，包含:")
        print(f"   📄 {len(summary_files)} 个汇总文件")
        print(f"   📄 {len(batch_files)} 个批次文件")
        
        if summary_files:
            latest_summary = max(summary_files, key=lambda x: x.stat().st_mtime)
            print(f"   📅 最新汇总: {latest_summary.name}")
        
        return True
    
    def auto_fix(self):
        """自动修复一些问题"""
        print("\n🔧 尝试自动修复...")
        
        # 修复脚本权限
        script_path = self.project_root / "run_docker_batch.sh"
        if script_path.exists() and not os.access(script_path, os.X_OK):
            try:
                subprocess.run(["chmod", "+x", str(script_path)], check=True)
                self.fixes_applied.append("添加了run_docker_batch.sh执行权限")
                print("✅ 已修复: run_docker_batch.sh执行权限")
            except subprocess.CalledProcessError:
                print("❌ 无法修复脚本权限")
        
        # 创建结果目录
        results_dir = self.project_root / "docker_results"
        if not results_dir.exists():
            try:
                results_dir.mkdir(exist_ok=True)
                self.fixes_applied.append("创建了docker_results目录")
                print("✅ 已创建: docker_results目录")
            except Exception:
                print("❌ 无法创建结果目录")
    
    def print_summary(self):
        """打印总结"""
        print("\n" + "=" * 50)
        print("📋 检查总结")
        print("=" * 50)
        
        if not self.issues_found:
            print("🎉 恭喜！没有发现问题，系统准备就绪！")
            print("\n你可以开始使用:")
            print("   ./run_docker_batch.sh")
        else:
            print(f"❌ 发现 {len(self.issues_found)} 个问题:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        
        if self.fixes_applied:
            print(f"\n✅ 已自动修复 {len(self.fixes_applied)} 个问题:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        print("\n如需更多帮助，请查看:")
        print("   • DOCKER_GUIDE.md - 详细使用指南")
        print("   • QUICK_START.md - 快速开始指南")
    
    def run_diagnostics(self):
        """运行完整诊断"""
        self.print_header()
        
        # 运行所有检查
        checks = [
            self.check_docker,
            self.check_environment,
            self.check_files,
            self.check_permissions,
            self.check_config_files,
            self.check_docker_image,
            self.check_running_containers,
            self.check_results_directory
        ]
        
        for check in checks:
            check()
        
        # 尝试自动修复
        self.auto_fix()
        
        # 打印总结
        self.print_summary()

def main():
    """主函数"""
    tool = TroubleshootTool()
    tool.run_diagnostics()

if __name__ == "__main__":
    main()
