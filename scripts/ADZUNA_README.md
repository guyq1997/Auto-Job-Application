# Adzuna 岗位搜索工具

这是一个使用 Adzuna API 进行岗位搜索的 LLM 工具，可以根据关键词搜索全球各地的工作岗位。

## 功能特性

- 🔍 **关键词搜索**: 根据职位关键词搜索相关岗位
- 🌍 **多国支持**: 支持德国、英国、美国、加拿大等多个国家
- 💰 **薪资筛选**: 支持按薪资范围筛选岗位
- 📍 **地点筛选**: 支持按具体城市或地区筛选
- 📊 **薪资统计**: 获取特定岗位的薪资统计信息
- 🏷️ **分类浏览**: 获取不同国家的岗位分类信息
- ⏰ **时间筛选**: 支持按岗位发布时间筛选

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 API 密钥

1. 访问 [Adzuna Developer Portal](https://developer.adzuna.com/) 创建账户
2. 创建新应用获取 `app_id` 和 `app_key`
3. 编辑 `config/adzuna_config.json` 文件：
   ```json
   {
     "api_credentials": {
       "app_id": "your_actual_app_id",
       "app_key": "your_actual_app_key"
     },
     "default_settings": {
       "country": "de",
       "results_per_page": 20,
       "max_days_old": 30,
       "sort_by": "date"
     }
   }
   ```

## LLM 工具函数

### 1. search_jobs_by_keywords()

根据关键词搜索岗位信息。

**参数：**
- `keywords` (str, 必填): 搜索关键词
- `location` (str, 可选): 地点（如 "Berlin", "Munich"）
- `country` (str, 默认 "germany"): 国家
- `max_results` (int, 默认 20): 最大结果数量
- `max_days_old` (int, 默认 30): 岗位发布时间限制（天数）
- `salary_min` (int, 可选): 最低薪资
- `salary_max` (int, 可选): 最高薪资
- `contract_type` (str, 可选): 合同类型
- `sort_by` (str, 默认 "date"): 排序方式

**示例：**
```python
result = search_jobs_by_keywords(
    keywords="Python developer",
    location="Berlin",
    country="germany",
    max_results=10,
    salary_min=50000
)
```

### 2. get_job_categories()

获取指定国家的岗位分类信息。

**参数：**
- `country` (str, 默认 "germany"): 国家

**示例：**
```python
categories = get_job_categories("germany")
```

### 3. get_salary_statistics()

获取特定关键词的薪资统计信息。

**参数：**
- `keywords` (str, 必填): 搜索关键词
- `location` (str, 可选): 地点
- `country` (str, 默认 "germany"): 国家

**示例：**
```python
salary_stats = get_salary_statistics(
    keywords="Data scientist",
    location="Munich",
    country="germany"
)
```

## 支持的国家

| 中文名 | 英文名 | 代码 |
|--------|--------|------|
| 德国 | Germany | de |
| 英国 | UK | gb |
| 美国 | USA | us |
| 加拿大 | Canada | ca |
| 澳大利亚 | Australia | au |
| 法国 | France | fr |
| 荷兰 | Netherlands | nl |
| 奥地利 | Austria | at |
| 瑞士 | Switzerland | ch |
| 意大利 | Italy | it |
| 西班牙 | Spain | es |

## 使用示例

```python
# 导入工具函数
from scripts.adzuna_job_search import search_jobs_by_keywords

# 搜索柏林的 Python 开发者岗位
jobs = search_jobs_by_keywords(
    keywords="Python developer",
    location="Berlin",
    country="germany",
    max_results=5,
    max_days_old=7,  # 只看最近7天的岗位
    sort_by="date"
)

# 打印结果
if jobs["status"] == "success":
    for job in jobs["data"]["jobs"]:
        print(f"职位: {job['title']}")
        print(f"公司: {job['company']}")
        print(f"地点: {job['location']}")
        print(f"薪资: {job['salary_min']}-{job['salary_max']} {job['currency']}")
        print(f"链接: {job['url']}")
        print("-" * 50)
```

## 测试工具

运行测试脚本来验证工具功能：

```bash
python test_adzuna.py
```

## 注意事项

1. **API 限制**: Adzuna API 有请求频率限制，请合理使用
2. **数据准确性**: 岗位信息来源于第三方，建议访问原始链接获取最新信息
3. **薪资信息**: 并非所有岗位都包含薪资信息
4. **地区差异**: 不同国家的岗位信息结构可能略有不同

## 错误处理

工具会自动处理常见错误并返回友好的错误信息：
- API 密钥未配置
- 网络连接问题
- API 请求失败
- 参数验证错误

所有错误都会在返回结果中包含 `error` 字段和相应的 `suggestion`。
