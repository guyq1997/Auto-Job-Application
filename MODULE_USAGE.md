# Adzuna Job Search 模块使用指南

## 📦 模块简介

`adzuna_job_search.py` 现在是一个标准的Python模块，可以在其他脚本中轻松调用。它提供了简洁的API来搜索Adzuna平台上的招聘信息。

## 🚀 快速开始

### 作为模块导入使用

```python
from scripts.adzuna_job_search import AdzunaJobSearch

# 创建搜索实例
job_search = AdzunaJobSearch()

# 搜索岗位
results = job_search.search("Python developer", location="Berlin")
print(job_search.format_results(results))
```

### 作为命令行脚本使用

```bash
python scripts/adzuna_job_search.py "Python developer" --location "Berlin"
```

## 🔧 主要类和方法

### AdzunaJobSearch 类

这是模块的主要接口，提供了简洁的API：

#### 初始化
```python
job_search = AdzunaJobSearch(config_path="config/adzuna_config.json")
```

#### 主要方法

1. **search()** - 基本搜索
```python
results = job_search.search(
    keywords="Python developer",
    location="Berlin",
    country="germany",
    max_results=20,
    salary_min=50000,
    salary_max=80000,
    contract_type="permanent",
    sort_by="salary"
)
```

2. **quick_search()** - 快速搜索，直接返回岗位列表
```python
jobs = job_search.quick_search("Data Scientist", location="Munich", max_results=10)
for job in jobs:
    print(f"{job['title']} - {job['company']}")
```

3. **search_and_format()** - 搜索并格式化输出（一步到位）
```python
formatted_output = job_search.search_and_format("DevOps Engineer", location="Frankfurt")
print(formatted_output)
```

4. **get_categories()** - 获取岗位分类
```python
categories = job_search.get_categories("germany")
```

5. **get_salary_stats()** - 获取薪资统计
```python
salary_stats = job_search.get_salary_stats("Python developer", location="Berlin")
```

6. **format_results()** - 格式化搜索结果
```python
formatted_text = job_search.format_results(search_results)
```

## 💡 使用示例

### 示例1: 基本搜索和处理
```python
from scripts.adzuna_job_search import AdzunaJobSearch

job_search = AdzunaJobSearch()

# 搜索柏林的Python开发者岗位
results = job_search.search("Python developer", location="Berlin", max_results=5)

if results.get("status") == "success":
    jobs = results.get("data", {}).get("jobs", [])
    for job in jobs:
        print(f"职位: {job['title']}")
        print(f"公司: {job['company']}")
        print(f"地点: {job['location']}")
        if job.get('salary_min'):
            print(f"薪资: €{job['salary_min']:,}+")
        print("-" * 40)
```

### 示例2: 批量搜索不同技术栈
```python
tech_stacks = ["Python Django", "React TypeScript", "DevOps AWS"]

for tech in tech_stacks:
    print(f"\n🔍 搜索: {tech}")
    jobs = job_search.quick_search(tech, max_results=3)
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} - {job['company']}")
```

### 示例3: 高薪岗位筛选
```python
# 搜索高薪岗位
results = job_search.search(
    "Senior Python Developer",
    location="Munich", 
    salary_min=80000,
    sort_by="salary"
)

if results.get("status") == "success":
    jobs = results.get("data", {}).get("jobs", [])
    high_salary_jobs = [j for j in jobs if j.get('salary_min', 0) >= 80000]
    
    print(f"找到 {len(high_salary_jobs)} 个高薪岗位:")
    for job in high_salary_jobs:
        salary_info = f"€{job.get('salary_min', 0):,}"
        if job.get('salary_max'):
            salary_info += f"-{job.get('salary_max'):,}"
        print(f"• {job['title']} - {job['company']} ({salary_info})")
```

### 示例4: 创建自定义搜索函数
```python
def find_remote_jobs(keywords, min_salary=None):
    """搜索远程工作岗位"""
    job_search = AdzunaJobSearch()
    
    # 搜索包含remote关键词的岗位
    remote_keywords = f"{keywords} remote"
    results = job_search.search(
        remote_keywords,
        salary_min=min_salary,
        max_results=20
    )
    
    if results.get("status") == "success":
        jobs = results.get("data", {}).get("jobs", [])
        # 进一步筛选包含remote的岗位
        remote_jobs = [
            job for job in jobs 
            if any(word in job.get('title', '').lower() + job.get('description', '').lower() 
                   for word in ['remote', 'home', 'telecommute'])
        ]
        return remote_jobs
    return []

# 使用自定义函数
remote_python_jobs = find_remote_jobs("Python developer", min_salary=60000)
print(f"找到 {len(remote_python_jobs)} 个远程Python岗位")
```

## 📁 文件结构

```
Jobbot/
├── scripts/
│   ├── __init__.py                 # 包初始化文件
│   ├── adzuna_job_search.py       # 主模块文件
│   └── ...
├── config/
│   └── adzuna_config.json         # API配置文件
├── example_usage.py               # 使用示例
└── MODULE_USAGE.md               # 本文档
```

## ⚙️ 配置

确保 `config/adzuna_config.json` 文件包含正确的API凭据：

```json
{
  "api_credentials": {
    "app_id": "YOUR_ADZUNA_APP_ID",
    "app_key": "YOUR_ADZUNA_APP_KEY"
  },
  "default_settings": {
    "country": "de",
    "results_per_page": 20,
    "max_days_old": 30,
    "sort_by": "date"
  }
}
```

## 🌍 支持的国家

- Germany (德国): `"germany"` 或 `"de"`
- UK (英国): `"uk"` 或 `"gb"`
- USA (美国): `"usa"` 或 `"us"`
- Canada (加拿大): `"canada"` 或 `"ca"`
- Australia (澳大利亚): `"australia"` 或 `"au"`
- 其他欧洲国家...

## 🔍 搜索参数

- `keywords`: 搜索关键词（必填）
- `location`: 地点（可选）
- `country`: 国家（默认 "germany"）
- `max_results`: 最大结果数量（默认 20，最大 50）
- `max_days_old`: 岗位发布时间限制（天数）
- `salary_min/salary_max`: 薪资范围
- `contract_type`: 合同类型
- `sort_by`: 排序方式（"date", "relevance", "salary"）

## 🚨 错误处理

模块会自动处理常见错误：

```python
results = job_search.search("Python developer")

if results.get("status") == "success":
    # 处理成功结果
    jobs = results.get("data", {}).get("jobs", [])
else:
    # 处理错误
    error_msg = results.get("error", "未知错误")
    print(f"搜索失败: {error_msg}")
```

## 🎯 最佳实践

1. **缓存结果**: 对于相同的搜索，考虑缓存结果避免重复API调用
2. **错误处理**: 始终检查返回结果的状态
3. **合理限制**: 使用适当的 `max_results` 值
4. **具体关键词**: 使用具体的关键词获得更精准的结果

## 🔗 相关文件

- 运行 `python example_usage.py` 查看完整的使用示例
- 查看 `scripts/adzuna_job_search.py` 了解更多技术细节
