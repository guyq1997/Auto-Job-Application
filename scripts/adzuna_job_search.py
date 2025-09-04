"""
Adzuna Job Search Module
使用 Adzuna API 进行岗位搜索的Python模块

This module provides a clean interface for searching job postings using the Adzuna API.
It can be used both as a standalone script and as an importable module.

Example usage as module:
    from scripts.adzuna_job_search import AdzunaJobSearch
    
    # Create search instance
    job_search = AdzunaJobSearch()
    
    # Search for jobs
    results = job_search.search("Python developer", location="Berlin")
    
    # Print formatted results
    print(job_search.format_results(results))

Example usage as script:
    python scripts/adzuna_job_search.py "Python developer" --location "Berlin"
"""

import requests
import json
import os
import argparse
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JobPosting:
    """岗位信息数据类"""
    title: str
    company: str
    location: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    currency: str
    description: str
    url: str
    created: str
    category: str
    contract_type: Optional[str] = None
    contract_time: Optional[str] = None


class AdzunaJobSearchTool:
    """Adzuna 岗位搜索工具类"""
    
    def __init__(self, config_path: str = "config/adzuna_config.json"):
        """
        初始化 Adzuna 搜索工具
        
        Args:
            config_path: Adzuna API 配置文件路径
        """
        self.config_path = config_path
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / config_path
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        # Adzuna API 基础 URL
        self.base_url = "https://api.adzuna.com/v1/api"
        
        # 支持的国家代码
        self.supported_countries = {
            'germany': 'de',
            '德国': 'de',
            'uk': 'gb',
            '英国': 'gb',
            'usa': 'us',
            '美国': 'us',
            'canada': 'ca',
            '加拿大': 'ca',
            'australia': 'au',
            '澳大利亚': 'au',
            'france': 'fr',
            '法国': 'fr',
            'netherlands': 'nl',
            '荷兰': 'nl',
            'austria': 'at',
            '奥地利': 'at',
            'switzerland': 'ch',
            '瑞士': 'ch',
            'italy': 'it',
            '意大利': 'it',
            'spain': 'es',
            '西班牙': 'es',
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not self.config_file.exists():
                self._create_sample_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading Adzuna config: {e}")
            return {}
    
    def _create_sample_config(self):
        """创建示例配置文件"""
        sample_config = {
            "api_credentials": {
                "app_id": "YOUR_ADZUNA_APP_ID",
                "app_key": "YOUR_ADZUNA_APP_KEY"
            },
            "default_settings": {
                "country": "de",
                "results_per_page": 20,
                "max_days_old": 30,
                "sort_by": "date"
            },
            "setup_instructions": {
                "step_1": "Visit https://developer.adzuna.com/ to create an account",
                "step_2": "Create a new app to get your app_id and app_key",
                "step_3": "Replace YOUR_ADZUNA_APP_ID and YOUR_ADZUNA_APP_KEY with your actual credentials",
                "step_4": "Delete this setup_instructions section after configuration"
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
    
    def _get_country_code(self, country: str) -> str:
        """获取国家代码"""
        country_lower = country.lower()
        return self.supported_countries.get(country_lower, country_lower)
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 API 请求"""
        credentials = self.config.get('api_credentials', {})
        app_id = credentials.get('app_id')
        app_key = credentials.get('app_key')
        
        if not app_id or not app_key or app_id == "YOUR_ADZUNA_APP_ID":
            return {
                "error": "Adzuna API credentials not configured",
                "suggestion": f"Please update {self.config_file} with your Adzuna API credentials",
                "setup_url": "https://developer.adzuna.com/"
            }
        
        # 添加认证参数
        params.update({
            'app_id': app_id,
            'app_key': app_key
        })
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "endpoint": endpoint,
                "params": params
            }
    
    def search_jobs(
        self,
        keywords: str,
        location: Optional[str] = None,
        country: str = "germany",
        max_results: int = 20,
        max_days_old: int = 30,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        contract_type: Optional[str] = None,
        sort_by: str = "date"
    ) -> Dict[str, Any]:
        """
        搜索岗位信息
        
        Args:
            keywords: 搜索关键词（必填）
            location: 地点（可选，如 "Berlin", "Munich"）
            country: 国家（默认 "germany"）
            max_results: 最大结果数量（默认 20）
            max_days_old: 岗位发布时间限制（天数，默认 30）
            salary_min: 最低薪资（可选）
            salary_max: 最高薪资（可选）
            contract_type: 合同类型（可选，如 "permanent", "contract", "temporary"）
            sort_by: 排序方式（"date", "relevance", "salary"，默认 "date"）
            
        Returns:
            Dict: 包含搜索结果的字典
        """
        if not keywords:
            return {
                "error": "Keywords parameter is required",
                "suggestion": "Please provide search keywords"
            }
        
        # 获取国家代码
        country_code = self._get_country_code(country)
        
        # 构建 API 端点
        endpoint = f"{self.base_url}/jobs/{country_code}/search/1"
        
        # 构建请求参数
        params = {
            'what': keywords,
            'results_per_page': min(max_results, 50),  # API 限制每页最多50个结果
            'max_days_old': max_days_old,
            'sort_by': sort_by
        }
        
        # 添加可选参数
        if location:
            params['where'] = location
        if salary_min:
            params['salary_min'] = salary_min
        if salary_max:
            params['salary_max'] = salary_max
        if contract_type:
            params['full_time'] = 1 if contract_type.lower() in ['permanent', 'full-time', 'full_time'] else 0
        
        # 发送请求
        response_data = self._make_request(endpoint, params)
        
        if 'error' in response_data:
            return response_data
        
        # 解析结果
        results = response_data.get('results', [])
        total_count = response_data.get('count', 0)
        
        # 格式化岗位信息
        formatted_jobs = []
        for job in results:
            try:
                formatted_job = {
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', {}).get('display_name', 'N/A'),
                    'location': job.get('location', {}).get('display_name', 'N/A'),
                    'salary_min': job.get('salary_min'),
                    'salary_max': job.get('salary_max'),
                    'currency': job.get('currency', 'EUR'),
                    'description': job.get('description', 'N/A')[:500] + '...' if len(job.get('description', '')) > 500 else job.get('description', 'N/A'),
                    'url': job.get('redirect_url', 'N/A'),
                    'created': job.get('created', 'N/A'),
                    'category': job.get('category', {}).get('label', 'N/A'),
                    'contract_type': job.get('contract_type'),
                    'contract_time': job.get('contract_time')
                }
                formatted_jobs.append(formatted_job)
            except Exception as e:
                print(f"Error formatting job: {e}")
                continue
        
        return {
            "status": "success",
            "data": {
                "jobs": formatted_jobs,
                "total_count": total_count,
                "returned_count": len(formatted_jobs),
                "search_params": {
                    "keywords": keywords,
                    "location": location,
                    "country": country,
                    "max_results": max_results,
                    "max_days_old": max_days_old
                }
            },
            "description": f"在 {country} 搜索关键词 '{keywords}' 的岗位结果"
        }
    
    def get_job_categories(self, country: str = "germany") -> Dict[str, Any]:
        """
        获取岗位分类信息
        
        Args:
            country: 国家（默认 "germany"）
            
        Returns:
            Dict: 包含岗位分类的字典
        """
        country_code = self._get_country_code(country)
        endpoint = f"{self.base_url}/jobs/{country_code}/categories"
        
        response_data = self._make_request(endpoint, {})
        
        if 'error' in response_data:
            return response_data
        
        categories = response_data.get('results', [])
        
        return {
            "status": "success",
            "data": categories,
            "count": len(categories),
            "description": f"{country} 的岗位分类列表"
        }
    
    def get_salary_stats(
        self,
        keywords: str,
        location: Optional[str] = None,
        country: str = "germany"
    ) -> Dict[str, Any]:
        """
        获取薪资统计信息
        
        Args:
            keywords: 搜索关键词
            location: 地点（可选）
            country: 国家（默认 "germany"）
            
        Returns:
            Dict: 包含薪资统计的字典
        """
        country_code = self._get_country_code(country)
        endpoint = f"{self.base_url}/jobs/{country_code}/salaries"
        
        params = {'what': keywords}
        if location:
            params['where'] = location
        
        response_data = self._make_request(endpoint, params)
        
        if 'error' in response_data:
            return response_data
        
        return {
            "status": "success",
            "data": response_data,
            "description": f"关键词 '{keywords}' 在 {country} 的薪资统计信息"
        }


def format_job_results(result: Dict[str, Any]) -> str:
    """格式化岗位搜索结果为易读的字符串格式"""
    if result.get("status") != "success":
        if "error" in result:
            return f"❌ 搜索失败: {result['error']}\n"
        return "❌ 搜索失败: 未知错误\n"
    
    data = result.get("data", {})
    jobs = data.get("jobs", [])
    total_count = data.get("total_count", 0)
    search_params = data.get("search_params", {})
    
    # 构建输出字符串
    output = []
    output.append("=" * 80)
    output.append(f"🔍 岗位搜索结果")
    output.append("=" * 80)
    output.append(f"关键词: {search_params.get('keywords', 'N/A')}")
    if search_params.get('location'):
        output.append(f"地点: {search_params.get('location')}")
    output.append(f"国家: {search_params.get('country', 'N/A')}")
    output.append(f"总计找到: {total_count} 个岗位")
    output.append(f"显示: {len(jobs)} 个岗位")
    output.append("=" * 80)
    
    if not jobs:
        output.append("😔 未找到匹配的岗位")
        return "\n".join(output)
    
    for i, job in enumerate(jobs, 1):
        output.append(f"\n📋 岗位 #{i}")
        output.append("-" * 50)
        output.append(f"🏢 职位: {job.get('title', 'N/A')}")
        output.append(f"🏛️  公司: {job.get('company', 'N/A')}")
        output.append(f"📍 地点: {job.get('location', 'N/A')}")
        
        # 薪资信息
        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')
        currency = job.get('currency', 'EUR')
        
        if salary_min and salary_max:
            output.append(f"💰 薪资: {salary_min:,.0f} - {salary_max:,.0f} {currency}")
        elif salary_min:
            output.append(f"💰 薪资: {salary_min:,.0f}+ {currency}")
        elif salary_max:
            output.append(f"💰 薪资: 最高 {salary_max:,.0f} {currency}")
        else:
            output.append("💰 薪资: 面议")
        
        output.append(f"📂 分类: {job.get('category', 'N/A')}")
        output.append(f"📅 发布时间: {job.get('created', 'N/A')}")
        
        # 合同信息
        if job.get('contract_type'):
            output.append(f"📋 合同类型: {job.get('contract_type')}")
        if job.get('contract_time'):
            output.append(f"⏰ 工作时间: {job.get('contract_time')}")
        
        # 描述（截取前200字符）
        description = job.get('description', 'N/A')
        if len(description) > 200:
            description = description[:200] + "..."
        output.append(f"📝 描述: {description}")
        
        # URL
        if job.get('url') != 'N/A':
            output.append(f"🔗 链接: {job.get('url')}")
    
    output.append("\n" + "=" * 80)
    return "\n".join(output)


# 创建全局工具实例（向后兼容）
adzuna_search_tool = AdzunaJobSearchTool()


class AdzunaJobSearch:
    """
    Adzuna岗位搜索模块的主要接口类
    提供简洁的API供其他脚本调用
    """
    
    def __init__(self, config_path: str = "config/adzuna_config.json"):
        """
        初始化搜索实例
        
        Args:
            config_path: 配置文件路径
        """
        self.tool = AdzunaJobSearchTool(config_path)
    
    def search(
        self,
        keywords: str,
        location: Optional[str] = None,
        country: str = "germany",
        max_results: int = 20,
        max_days_old: int = 30,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        contract_type: Optional[str] = None,
        sort_by: str = "date"
    ) -> Dict[str, Any]:
        """
        搜索岗位（简化接口）
        
        Args:
            keywords: 搜索关键词
            location: 地点（可选）
            country: 国家（默认 "germany"）
            max_results: 最大结果数量（默认 20）
            max_days_old: 岗位发布时间限制（天数，默认 30）
            salary_min: 最低薪资（可选）
            salary_max: 最高薪资（可选）
            contract_type: 合同类型（可选）
            sort_by: 排序方式（默认 "date"）
            
        Returns:
            Dict: 搜索结果
        """
        return self.tool.search_jobs(
            keywords=keywords,
            location=location,
            country=country,
            max_results=max_results,
            max_days_old=max_days_old,
            salary_min=salary_min,
            salary_max=salary_max,
            contract_type=contract_type,
            sort_by=sort_by
        )
    
    def get_categories(self, country: str = "germany") -> Dict[str, Any]:
        """
        获取岗位分类
        
        Args:
            country: 国家（默认 "germany"）
            
        Returns:
            Dict: 岗位分类信息
        """
        return self.tool.get_job_categories(country)
    
    def get_salary_stats(
        self,
        keywords: str,
        location: Optional[str] = None,
        country: str = "germany"
    ) -> Dict[str, Any]:
        """
        获取薪资统计
        
        Args:
            keywords: 搜索关键词
            location: 地点（可选）
            country: 国家（默认 "germany"）
            
        Returns:
            Dict: 薪资统计信息
        """
        return self.tool.get_salary_stats(keywords, location, country)
    
    def format_results(self, result: Dict[str, Any]) -> str:
        """
        格式化搜索结果为易读字符串
        
        Args:
            result: 搜索结果字典
            
        Returns:
            str: 格式化后的结果字符串
        """
        return format_job_results(result)
    
    def search_and_format(
        self,
        keywords: str,
        location: Optional[str] = None,
        country: str = "germany",
        max_results: int = 20,
        **kwargs
    ) -> str:
        """
        搜索并格式化结果（一步到位）
        
        Args:
            keywords: 搜索关键词
            location: 地点（可选）
            country: 国家（默认 "germany"）
            max_results: 最大结果数量（默认 20）
            **kwargs: 其他搜索参数
            
        Returns:
            str: 格式化后的搜索结果
        """
        result = self.search(
            keywords=keywords,
            location=location,
            country=country,
            max_results=max_results,
            **kwargs
        )
        return self.format_results(result)
    
    def quick_search(self, keywords: str, location: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        快速搜索，直接返回岗位列表
        
        Args:
            keywords: 搜索关键词
            location: 地点（可选）
            max_results: 最大结果数量（默认 10）
            
        Returns:
            List[Dict]: 岗位列表
        """
        result = self.search(keywords, location, max_results=max_results)
        if result.get("status") == "success":
            return result.get("data", {}).get("jobs", [])
        return []


def search_jobs_by_keywords(
    keywords: str,
    location: Optional[str] = None,
    country: str = "germany",
    max_results: int = 20,
    max_days_old: int = 30,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    contract_type: Optional[str] = None,
    sort_by: str = "date"
) -> Dict[str, Any]:
    """
    LLM工具函数：根据关键词搜索岗位
    
    Args:
        keywords: 搜索关键词（必填）
        location: 地点（可选）
        country: 国家（默认 "germany"）
        max_results: 最大结果数量（默认 20）
        max_days_old: 岗位发布时间限制（天数，默认 30）
        salary_min: 最低薪资（可选）
        salary_max: 最高薪资（可选）
        contract_type: 合同类型（可选）
        sort_by: 排序方式（默认 "date"）
        
    Returns:
        Dict: 岗位搜索结果
    """
    return adzuna_search_tool.search_jobs(
        keywords=keywords,
        location=location,
        country=country,
        max_results=max_results,
        max_days_old=max_days_old,
        salary_min=salary_min,
        salary_max=salary_max,
        contract_type=contract_type,
        sort_by=sort_by
    )


def get_job_categories(country: str = "germany") -> Dict[str, Any]:
    """
    LLM工具函数：获取岗位分类
    
    Args:
        country: 国家（默认 "germany"）
        
    Returns:
        Dict: 岗位分类信息
    """
    return adzuna_search_tool.get_job_categories(country)


def get_salary_statistics(
    keywords: str,
    location: Optional[str] = None,
    country: str = "germany"
) -> Dict[str, Any]:
    """
    LLM工具函数：获取薪资统计
    
    Args:
        keywords: 搜索关键词
        location: 地点（可选）
        country: 国家（默认 "germany"）
        
    Returns:
        Dict: 薪资统计信息
    """
    return adzuna_search_tool.get_salary_stats(keywords, location, country)


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Adzuna 岗位搜索工具 - 直接搜索并显示招聘信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python adzuna_job_search.py "Python developer" --location "Berlin" --country germany
  python adzuna_job_search.py "Data Scientist" --max-results 10 --salary-min 50000
  python adzuna_job_search.py "机器学习" --country germany --sort-by salary
  python adzuna_job_search.py --categories --country germany
  python adzuna_job_search.py --salary-stats "Python developer" --location "Munich"

支持的国家:
  germany/德国, uk/英国, usa/美国, canada/加拿大, australia/澳大利亚,
  france/法国, netherlands/荷兰, austria/奥地利, switzerland/瑞士,
  italy/意大利, spain/西班牙
        """)
    
    # 主要功能选择
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "keywords", 
        nargs="?", 
        help="搜索关键词（如：'Python developer', 'Data Scientist'）"
    )
    group.add_argument(
        "--categories", 
        action="store_true", 
        help="获取岗位分类列表"
    )
    group.add_argument(
        "--salary-stats", 
        metavar="KEYWORDS", 
        help="获取指定关键词的薪资统计"
    )
    
    # 搜索参数
    parser.add_argument(
        "--location", "-l",
        help="搜索地点（如：Berlin, Munich, London）"
    )
    parser.add_argument(
        "--country", "-c",
        default="germany",
        help="搜索国家（默认：germany）"
    )
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=20,
        help="最大结果数量（默认：20，最大：50）"
    )
    parser.add_argument(
        "--max-days-old", "-d",
        type=int,
        default=30,
        help="岗位发布时间限制（天数，默认：30）"
    )
    parser.add_argument(
        "--salary-min",
        type=int,
        help="最低薪资要求"
    )
    parser.add_argument(
        "--salary-max",
        type=int,
        help="最高薪资要求"
    )
    parser.add_argument(
        "--contract-type",
        choices=["permanent", "contract", "temporary", "full-time", "part-time"],
        help="合同类型"
    )
    parser.add_argument(
        "--sort-by", "-s",
        choices=["date", "relevance", "salary"],
        default="date",
        help="排序方式（默认：date）"
    )
    
    # 输出选项
    parser.add_argument(
        "--json",
        action="store_true",
        help="以JSON格式输出结果"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细信息"
    )
    
    return parser


def main():
    """主函数 - 命令行入口"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        if args.categories:
            # 获取岗位分类
            if args.verbose:
                print(f"🔍 正在获取 {args.country} 的岗位分类...")
            
            result = get_job_categories(args.country)
            
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                if result.get("status") == "success":
                    categories = result.get("data", [])
                    print("=" * 60)
                    print(f"📂 {args.country.upper()} 岗位分类列表")
                    print("=" * 60)
                    for category in categories:
                        print(f"🏷️  {category.get('label', 'N/A')} (ID: {category.get('tag', 'N/A')})")
                    print(f"\n总计: {len(categories)} 个分类")
                else:
                    print(f"❌ 获取分类失败: {result.get('error', '未知错误')}")
        
        elif args.salary_stats:
            # 获取薪资统计
            if args.verbose:
                print(f"🔍 正在获取 '{args.salary_stats}' 的薪资统计...")
            
            result = get_salary_statistics(args.salary_stats, args.location, args.country)
            
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                if result.get("status") == "success":
                    print("=" * 60)
                    print(f"💰 薪资统计信息")
                    print("=" * 60)
                    print(f"关键词: {args.salary_stats}")
                    if args.location:
                        print(f"地点: {args.location}")
                    print(f"国家: {args.country}")
                    print("\n统计数据:")
                    print(json.dumps(result.get("data", {}), ensure_ascii=False, indent=2))
                else:
                    print(f"❌ 获取薪资统计失败: {result.get('error', '未知错误')}")
        
        else:
            # 搜索岗位
            if not args.keywords:
                parser.error("需要提供搜索关键词，或使用 --categories 或 --salary-stats 选项")
            
            if args.verbose:
                print(f"🔍 正在搜索关键词 '{args.keywords}' 的岗位...")
                if args.location:
                    print(f"📍 地点: {args.location}")
                print(f"🌍 国家: {args.country}")
            
            result = search_jobs_by_keywords(
                keywords=args.keywords,
                location=args.location,
                country=args.country,
                max_results=args.max_results,
                max_days_old=args.max_days_old,
                salary_min=args.salary_min,
                salary_max=args.salary_max,
                contract_type=args.contract_type,
                sort_by=args.sort_by
            )
            
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(format_job_results(result))
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# 保持向后兼容的测试功能
def run_tests():
    """运行测试示例"""
    print("=== Adzuna 岗位搜索工具测试 ===")
    
    # 测试搜索岗位
    print("\n1. 搜索 Python 开发者岗位:")
    result = search_jobs_by_keywords(
        keywords="Python developer",
        location="Berlin",
        country="germany",
        max_results=5
    )
    print(format_job_results(result))
    
    # 测试获取岗位分类
    print("\n2. 获取岗位分类:")
    categories = get_job_categories("germany")
    if categories.get("status") == "success":
        cats = categories.get("data", [])[:5]  # 只显示前5个
        for cat in cats:
            print(f"  - {cat.get('label', 'N/A')}")
        print(f"  ... 总计 {len(categories.get('data', []))} 个分类")
    
    # 测试薪资统计
    print("\n3. 获取薪资统计:")
    salary_stats = get_salary_statistics("Python developer", "Berlin", "germany")
    print(f"状态: {salary_stats.get('status', 'unknown')}")


if __name__ == "__main__":
    # 如果没有命令行参数，运行测试
    if len(sys.argv) == 1:
        print("💡 提示: 使用 --help 查看使用说明")
        print("🧪 运行测试模式...\n")
        run_tests()
    else:
        main()
