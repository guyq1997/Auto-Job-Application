# 🚀 Docker批量申请 - 5分钟快速开始

## 最简单的使用方法

### 1️⃣ 准备工作（2分钟）
```bash
# 进入项目目录
cd Auto-Job-Application

source venv/bin/activate

# 设置API密钥（必需）
export OPENAI_API_KEY="你的OpenAI_API密钥"

# 给脚本添加执行权限
chmod +x run_docker_batch.sh
```

### 2️⃣ 一键启动（1分钟）
```bash
# 使用示例数据运行（10个职位，5个容器并行）
./run_docker_batch.sh
```

### 3️⃣ 查看结果（1分钟）
```bash
# 查看结果文件
ls docker_results/

# 查看成功率
cat docker_results/summary_*.json | grep success_rate
```

### 4️⃣ 使用你自己的职位数据（1分钟）
```bash
# 编辑职位数据
nano my_jobs.json

# 运行你的数据
./run_docker_batch.sh my_jobs.json 3 browser-use
```

## 职位数据格式示例

创建 `my_jobs.json` 文件：
```json
[
  {
    "title": "Python开发工程师",
    "company": "科技公司A", 
    "url": "https://example.com/job1",
    "location": "北京"
  },
  {
    "title": "全栈工程师",
    "company": "创业公司B",
    "url": "https://example.com/job2", 
    "location": "上海"
  }
]
```

## 常用命令

```bash
# 基本用法
./run_docker_batch.sh

# 自定义容器数量（3个容器）
./run_docker_batch.sh example_jobs.json 3

# 使用不同后端
./run_docker_batch.sh example_jobs.json 5 openai-computer-use

# 查看帮助
./run_docker_batch.sh --help

# 清理Docker资源
./run_docker_batch.sh --cleanup
```

## 实时监控

```bash
# 查看正在运行的容器
docker ps

# 查看某个容器的日志
docker logs -f job-bot-1

# 查看资源使用情况
docker stats
```

## 结果说明

执行完成后，`docker_results/` 目录包含：
- `summary_*.json` - 总体结果报告
- `batch_*.json` - 各容器详细结果
- `result_*.json` - 单个申请结果

**就这么简单！🎉**

需要详细文档？查看 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
