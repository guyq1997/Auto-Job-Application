"""
Jobbot Scripts Package
招聘机器人脚本包

This package contains various job search and recruitment tools.
"""

# 导入主要的类和函数，方便外部使用
from .adzuna_job_search import AdzunaJobSearch, AdzunaJobSearchTool, format_job_results

__version__ = "1.0.0"
__author__ = "Jobbot Team"

# 定义包的公共接口
__all__ = [
    "AdzunaJobSearch",
    "AdzunaJobSearchTool", 
    "format_job_results"
]
