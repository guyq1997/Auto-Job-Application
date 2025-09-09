#!/bin/bash

# Docker批量职位申请启动脚本
# Docker Batch Job Application Runner

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查必要的环境变量
check_env() {
    print_message $BLUE "🔍 检查环境变量..."
    
    # 如果.env文件存在，先加载它
    if [ -f ".env" ]; then
        print_message $BLUE "📄 加载 .env 文件..."
        set -a  # 自动导出变量
        source .env
        set +a  # 关闭自动导出
    else
        print_message $YELLOW "⚠️ 警告: .env 文件不存在，某些功能可能受限"
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_message $RED "❌ 错误: 请设置 OPENAI_API_KEY 环境变量"
        echo "   export OPENAI_API_KEY=your_api_key"
        echo "   或在 .env 文件中设置: OPENAI_API_KEY=your_api_key"
        exit 1
    fi
    
    print_message $GREEN "✅ 环境变量检查完成"
}

# 检查Docker
check_docker() {
    print_message $BLUE "🐳 检查Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_message $RED "❌ 错误: Docker 未安装"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_message $RED "❌ 错误: Docker 未运行"
        exit 1
    fi
    
    print_message $GREEN "✅ Docker 检查完成"
}

# 构建Docker镜像
build_image() {
    print_message $BLUE "🏗️ 构建Docker镜像..."
    
    docker build -t job-application-bot . || {
        print_message $RED "❌ Docker镜像构建失败"
        exit 1
    }
    
    print_message $GREEN "✅ Docker镜像构建完成"
}

# 创建结果目录
create_results_dir() {
    mkdir -p docker_results
    print_message $GREEN "📁 结果目录已创建: ./docker_results"
}

# 运行批量处理
run_batch() {
    local jobs_file=${1:-"jobs_data.json"}
    local max_containers=${2:-5}
    local backend=${3:-"browser-use"}
    
    print_message $BLUE "🚀 开始批量处理..."
    print_message $YELLOW "📋 职位文件: $jobs_file"
    print_message $YELLOW "🐳 最大容器数: $max_containers"
    print_message $YELLOW "🤖 后端: $backend"
    
    if [ ! -f "$jobs_file" ]; then
        print_message $RED "❌ 错误: 职位文件不存在: $jobs_file"
        exit 1
    fi
    
    python docker_batch_manager.py \
        --jobs-file "$jobs_file" \
        --max-containers "$max_containers" \
        --backend "$backend" || {
        print_message $RED "❌ 批量处理失败"
        exit 1
    }
    
    print_message $GREEN "🎉 批量处理完成！"
}

# 清理Docker资源
cleanup() {
    print_message $BLUE "🧹 清理Docker资源..."
    
    # 停止所有job-bot容器
    docker ps -q --filter "name=job-bot-" | xargs -r docker stop
    
    # 删除所有job-bot容器
    docker ps -aq --filter "name=job-bot-" | xargs -r docker rm
    
    print_message $GREEN "✅ 清理完成"
}

# 显示帮助信息
show_help() {
    echo "Docker批量职位申请运行器"
    echo ""
    echo "用法:"
    echo "  $0 [选项] [职位文件] [最大容器数] [后端]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -c, --cleanup  清理Docker资源"
    echo "  -b, --build    只构建Docker镜像"
    echo ""
    echo "参数:"
    echo "  职位文件       JSON格式的职位数据文件 (默认: example_jobs.json)"
    echo "  最大容器数     并行运行的最大容器数 (默认: 5)"
    echo "  后端          自动化后端 (browser-use|openai-computer-use, 默认: browser-use)"
    echo ""
    echo "示例:"
    echo "  $0                                    # 使用默认设置"
    echo "  $0 my_jobs.json 3 browser-use        # 自定义参数"
    echo "  $0 --cleanup                         # 清理资源"
    echo "  $0 --build                           # 只构建镜像"
    echo ""
    echo "环境变量:"
    echo "  OPENAI_API_KEY  必需的OpenAI API密钥"
    echo "  Email           可选的邮箱（用于登录）"
    echo "  Password        可选的密码（用于登录）"
}

# 主函数
main() {
    print_message $GREEN "🤖 Docker批量职位申请运行器"
    print_message $GREEN "================================"
    
    # 解析参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--cleanup)
            cleanup
            exit 0
            ;;
        -b|--build)
            check_docker
            build_image
            exit 0
            ;;
    esac
    
    # 执行检查
    check_env
    check_docker
    create_results_dir
    
    # 构建镜像
    build_image
    
    # 运行批量处理
    run_batch "$1" "$2" "$3"
    
    print_message $GREEN "📊 查看详细结果: ./docker_results/"
}

# 错误处理
trap cleanup EXIT

# 运行主函数
main "$@"
