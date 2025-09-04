# 智能职位申请代理 - 设置指南

## 📋 功能概述

这个智能职位申请代理结合了Adzuna职位搜索API和Browser-use自动化库，可以自动搜索职位并使用AI帮助填写申请表单。

### 主要功能
- 🔍 **智能职位搜索**: 使用Adzuna API搜索相关职位
- 🎯 **智能过滤**: 根据薪资、关键词等条件过滤职位
- 🤖 **两步骤自动申请**: 使用两个专门的AI代理进行申请
  - 📍 **导航代理**: 专门负责找到申请按钮和导航到表单
  - 📝 **表单代理**: 专门负责填写和提交申请表单
- 🔗 **共享浏览器会话**: 两个代理使用同一个浏览器，保持状态连续性
- 📊 **进度跟踪**: 实时跟踪申请状态和结果

## 🏗️ 系统架构

### 两步骤申请流程

本系统采用创新的两步骤申请流程，使用两个专门的AI代理：

```
职位URL → 导航代理 → 申请表单 → 表单代理 → 申请完成
```

#### 第一步：导航代理 (Navigation Agent)
- 🎯 **专门职责**: 找到申请按钮，处理页面跳转，导航到真正的申请表单
- 🔍 **核心功能**: 
  - 识别各种类型的申请按钮 (Apply, Bewerben等)
  - 处理外部链接跳转 (LinkedIn, 公司官网等)
  - 识别登录要求并提醒用户
  - 确保到达真正的申请表单页面

#### 第二步：表单代理 (Form Agent)  
- 📝 **专门职责**: 填写申请表单，上传文件，提交申请
- 🔧 **核心功能**:
  - 智能识别表单字段
  - 自动填写个人信息
  - 处理文件上传要求
  - 回答自定义问题
  - 提交申请并验证成功

#### 共享浏览器会话
- 🔗 使用 `BrowserProfile(keep_alive=True)` 确保两个代理共享同一个浏览器实例
- 💾 保持登录状态、Cookie和页面状态的连续性
- ⚡ 提高效率，避免重复导航

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Playwright浏览器

```bash
playwright install chromium
```

### 3. 配置环境变量

创建 `.env` 文件并添加以下配置：

```bash
# OpenAI API配置 (必需)
OPENAI_API_KEY=your_openai_api_key_here

# 可选配置
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# Browser配置
BROWSER_HEADLESS=false
BROWSER_SLOW_MO=1000
BROWSER_TIMEOUT=30000

# 申请配置
MAX_APPLICATIONS_PER_SESSION=5
DELAY_BETWEEN_APPLICATIONS=30
AUTO_SAVE_PROGRESS=true
SCREENSHOT_ON_ERROR=true
```

### 4. 配置个人信息

编辑 `config/personal_data.json` 文件，填入你的个人信息：

```json
{
  "personal_info": {
    "name": "你的姓名",
    "email": "your.email@example.com",
    "phone": "+49-123-456-7890",
    "address": "你的地址",
    "linkedin_profile": "https://linkedin.com/in/yourprofile"
  }
}
```

## 📖 使用方法

### 方法1: 使用便捷函数（推荐）

```python
import asyncio
from apply_agent import smart_job_apply

async def main():
    # 基础使用 - 搜索并自动申请
    result = await smart_job_apply(
        query="Python Developer",
        location="Berlin",
        max_results=5,
        auto_apply=True
    )
    
    print(f"申请结果: {result}")

# 运行
asyncio.run(main())
```

### 方法2: 使用过滤条件

```python
import asyncio
from apply_agent import smart_job_apply

async def main():
    # 定义过滤条件
    filters = {
        "min_salary": 50000,  # 最低薪资
        "required_keywords": ["Python", "Django"],  # 必须包含
        "exclude_keywords": ["Internship", "Junior"]  # 排除关键词
    }
    
    result = await smart_job_apply(
        query="Senior Python Developer",
        location="Berlin",
        max_results=10,
        filters=filters,
        auto_apply=True
    )
    
    print(f"申请结果: {result}")

asyncio.run(main())
```

### 方法3: 仅搜索不申请

```python
import asyncio
from apply_agent import smart_job_apply

async def main():
    result = await smart_job_apply(
        query="Data Scientist",
        location="Munich",
        max_results=10,
        auto_apply=False  # 只搜索，不申请
    )
    
    jobs = result["search_results"]
    for job in jobs:
        print(f"{job['title']} @ {job['company']} - {job['url']}")

asyncio.run(main())
```

### 方法4: 手动控制流程

```python
import asyncio
from apply_agent import IntelligentJobApplyAgent

async def main():
    agent = IntelligentJobApplyAgent()
    
    # 1. 搜索职位
    jobs = agent.search_jobs("Python Developer", "Berlin", 5)
    
    # 2. 选择要申请的职位
    selected_jobs = jobs[:2]  # 选择前两个
    
    # 3. 初始化机器人并申请
    if await agent.initialize_bot():
        results = await agent.auto_apply_jobs(selected_jobs)
        print(f"申请结果: {results}")
    
    # 4. 清理资源
    await agent.cleanup()

asyncio.run(main())
```

## 🔧 配置文件说明

### config/browser_config.json
浏览器和申请相关配置：

```json
{
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.1
  },
  "browser_config": {
    "headless": false,
    "slow_mo": 1000,
    "timeout": 30000
  },
  "application_settings": {
    "max_applications_per_session": 5,
    "delay_between_applications": 30
  }
}
```

### config/personal_data.json
个人信息配置，用于自动填写表单

### config/adzuna_config.json
Adzuna API配置

## 📁 文件结构

```
Jobbot/
├── apply_agent.py              # 主要的智能申请代理
├── scripts/
│   ├── adzuna_job_search.py   # Adzuna搜索模块
│   └── browser_automation.py  # 浏览器自动化模块
├── config/
│   ├── personal_data.json     # 个人信息配置
│   ├── adzuna_config.json     # API配置
│   └── browser_config.json    # 浏览器配置
├── example_usage.py           # 使用示例
├── requirements.txt           # 依赖列表
└── screenshots/              # 截图保存目录
```

## ⚠️ 重要提醒

1. **测试环境**: 建议先在测试环境中运行，确保功能正常
2. **API限制**: 注意OpenAI API的使用限制和费用
3. **申请频率**: 不要过于频繁地申请，避免被网站屏蔽
4. **个人信息**: 确保personal_data.json中的信息准确无误
5. **法律合规**: 确保使用符合目标网站的服务条款

## 🐛 故障排除

### 常见问题

1. **ImportError: No module named 'browser_use'**
   ```bash
   pip install browser-use
   ```

2. **Playwright browser not found**
   ```bash
   playwright install chromium
   ```

3. **OpenAI API错误**
   - 检查API key是否正确设置
   - 确认账户有足够的余额

4. **申请失败**
   - 检查网站是否有验证码
   - 确认表单字段是否正确识别
   - 查看截图了解具体错误

### 调试模式

设置浏览器为非无头模式以观察申请过程：

```json
{
  "browser_config": {
    "headless": false,
    "slow_mo": 2000
  }
}
```

## 📞 支持

如果遇到问题，请检查：
1. 所有依赖是否正确安装
2. 环境变量是否正确设置
3. 个人信息配置是否完整
4. 网络连接是否正常

## 🧪 测试两步骤系统

### 运行测试脚本

```bash
python test_two_step_application.py
```

测试脚本提供三种模式：
1. **基础功能测试**: 测试两步骤申请流程
2. **批量申请测试**: 测试多个职位的批量申请
3. **交互式测试**: 手动输入职位URL进行实时测试

### 测试流程说明

```
🚀 初始化
├── 创建BrowserProfile (keep_alive=True)
├── 初始化导航代理
└── 初始化表单代理

📍 第一步：导航代理
├── 接收职位URL和信息
├── 导航到职位页面
├── 寻找申请按钮
├── 处理页面跳转
└── 到达申请表单

📝 第二步：表单代理  
├── 识别表单字段
├── 填写个人信息
├── 处理文件上传
├── 回答自定义问题
└── 提交申请

✅ 完成申请
```

### 系统优势

- ✅ **专业化分工**: 每个代理专注于特定任务，提高成功率
- ✅ **状态连续性**: 共享浏览器会话，保持登录状态
- ✅ **错误隔离**: 导航失败不影响表单填写逻辑
- ✅ **易于调试**: 可以分别测试导航和表单填写功能
- ✅ **灵活扩展**: 可以轻松添加更多专门的代理

## 🔄 更新日志

- v2.0.0: 重大更新 - 两步骤申请系统
  - 🆕 使用两个sequential的Browser-use agents
  - 🆕 导航代理专门负责找到申请表单
  - 🆕 表单代理专门负责填写表单
  - 🆕 共享浏览器会话，保持状态连续性
  - 🆕 提供完整的测试脚本
- v1.0.0: 初始版本，支持基础搜索和申请功能
  - 支持Adzuna API职位搜索
  - 集成Browser-use自动化申请
  - 添加智能过滤和进度跟踪
