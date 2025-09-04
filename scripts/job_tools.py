"""
Job Application Tools for LLM Usage
求职申请工具模块，供LLM使用

This module provides tools for retrieving personal information, documents, 
work experience, and education background for job applications.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class WorkExperience:
    """工作经验数据类"""
    company: str
    position: str
    start_date: str
    end_date: Optional[str]  # None表示当前工作
    location: str
    description: str
    technologies: List[str]
    achievements: List[str]


@dataclass
class Education:
    """教育背景数据类"""
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    location: str
    gpa: Optional[str] = None
    honors: List[str] = None
    relevant_courses: List[str] = None



class JobApplicationTools:
    """求职申请工具类"""
    
    def __init__(self, config_path: str = "config/personal_data.json"):
        """
        初始化工具类
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / config_path
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(exist_ok=True)
        
        # 如果配置文件不存在，创建示例配置
        if not self.config_file.exists():
            self._create_sample_config()
    
    def _create_sample_config(self):
        """创建示例配置文件"""
        sample_data = {
            "work_experience": [
                {
                    "company": "TechCorp GmbH",
                    "position": "软件工程师",
                    "start_date": "2020-03-01",
                    "end_date": None,
                    "location": "柏林，德国",
                    "description": "负责开发和维护公司的核心产品，使用Python和JavaScript技术栈",
                    "technologies": ["Python", "JavaScript", "React", "Django", "PostgreSQL"],
                    "achievements": [
                        "将系统性能提升了30%",
                        "领导了新功能的开发，用户满意度提升20%",
                        "指导了2名初级开发者"
                    ]
                },
                {
                    "company": "StartupXYZ",
                    "position": "全栈开发者",
                    "start_date": "2018-06-01",
                    "end_date": "2020-02-28",
                    "location": "慕尼黑，德国",
                    "description": "在创业公司担任全栈开发者，参与产品从0到1的开发",
                    "technologies": ["Node.js", "Vue.js", "MongoDB", "Docker"],
                    "achievements": [
                        "独立开发了公司的MVP产品",
                        "建立了CI/CD流程",
                        "获得了公司最佳员工奖"
                    ]
                }
            ],
            "education": [
                {
                    "institution": "慕尼黑工业大学",
                    "degree": "计算机科学硕士",
                    "field_of_study": "人工智能与机器学习",
                    "start_date": "2016-10-01",
                    "end_date": "2018-09-30",
                    "location": "慕尼黑，德国",
                    "gpa": "1.5",
                    "honors": ["优秀毕业生", "院长奖学金"],
                    "relevant_courses": ["机器学习", "深度学习", "算法设计", "软件工程"]
                },
                {
                    "institution": "清华大学",
                    "degree": "计算机科学学士",
                    "field_of_study": "计算机科学与技术",
                    "start_date": "2012-09-01",
                    "end_date": "2016-07-01",
                    "location": "北京，中国",
                    "gpa": "3.8/4.0",
                    "honors": ["优秀学生干部", "学业奖学金"],
                    "relevant_courses": ["数据结构", "操作系统", "数据库系统", "计算机网络"]
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            return {}
    
    
    def get_work_experience(self, company: Optional[str] = None) -> Dict[str, Any]:
        """
        获取工作经验信息
        
        Args:
            company: 公司名称筛选 (可选)
            
        Returns:
            Dict: 包含工作经验的字典
        """
        config = self._load_config()
        work_experience = config.get('work_experience', [])
        
        if not work_experience:
            return {
                "error": "No work experience found in config",
                "suggestion": "Please add your work experience to the config file"
            }
        
        # 如果指定了公司名称，进行筛选
        if company:
            work_experience = [exp for exp in work_experience 
                             if company.lower() in exp.get('company', '').lower()]
        
        # 计算工作时长
        for exp in work_experience:
            start_date = exp.get('start_date')
            end_date = exp.get('end_date')
            
            if start_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()
                duration_days = (end - start).days
                duration_years = round(duration_days / 365.25, 1)
                exp['duration_years'] = duration_years
                exp['is_current'] = end_date is None
        
        return {
            "status": "success",
            "data": work_experience,
            "count": len(work_experience),
            "description": f"工作经验列表{'（筛选公司：' + company + '）' if company else ''}"
        }
    
    def get_education_background(self, degree_level: Optional[str] = None) -> Dict[str, Any]:
        """
        获取教育背景信息
        
        Args:
            degree_level: 学位级别筛选 (可选，如 "bachelor", "master", "phd")
            
        Returns:
            Dict: 包含教育背景的字典
        """
        config = self._load_config()
        education = config.get('education', [])
        
        if not education:
            return {
                "error": "No education background found in config",
                "suggestion": "Please add your education background to the config file"
            }
        
        # 如果指定了学位级别，进行筛选
        if degree_level:
            education = [edu for edu in education 
                        if degree_level.lower() in edu.get('degree', '').lower()]
        
        # 按结束时间排序（最新的在前）
        education.sort(key=lambda x: x.get('end_date', ''), reverse=True)
        
        return {
            "status": "success",
            "data": education,
            "count": len(education),
            "description": f"教育背景列表{'（筛选学位：' + degree_level + '）' if degree_level else ''}"
        }


# 创建全局工具实例
job_tools = JobApplicationTools()


def get_work_experience(company: Optional[str] = None) -> Dict[str, Any]:
    """
    LLM工具函数：获取工作经验
    
    Args:
        company: 公司名称 (可选)
        
    Returns:
        Dict: 工作经验信息
    """
    return job_tools.get_work_experience(company)


def get_education_background(degree_level: Optional[str] = None) -> Dict[str, Any]:
    """
    LLM工具函数：获取教育背景
    
    Args:
        degree_level: 学位级别 (可选)
        
    Returns:
        Dict: 教育背景信息
    """
    return job_tools.get_education_background(degree_level)


# 示例用法
if __name__ == "__main__":
    
    print("\n=== 工作经验 ===")
    print(json.dumps(get_work_experience(), ensure_ascii=False, indent=2))
    
    print("\n=== 教育背景 ===")
    print(json.dumps(get_education_background(), ensure_ascii=False, indent=2))
