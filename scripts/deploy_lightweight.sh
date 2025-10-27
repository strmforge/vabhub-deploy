#!/bin/bash

# VabHub 轻量级部署脚本
# 模仿 MoviePilot 模式，支持快速部署和库分离

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示横幅
show_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   VabHub 轻量级部署工具                    ║"
    echo "║                模仿 MoviePilot 部署模式                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python版本: $PYTHON_VERSION"
    else
        log_error "未找到Python3，请先安装Python3.8+"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 已安装"
    else
        log_warning "未找到pip3，尝试安装..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        else
            log_error "无法自动安装pip3，请手动安装"
            exit 1
        fi
    fi
    
    # 检查项目目录
    if [ ! -f "requirements.txt" ]; then
        log_error "未在项目根目录中运行，请切换到项目根目录"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    # 创建虚拟环境（可选）
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_success "虚拟环境已激活"
    fi
    
    # 升级pip
    pip3 install --upgrade pip
    
    # 安装依赖
    pip3 install -r requirements.txt
    
    log_success "依赖安装完成"
}

# 运行系统检测
run_system_detection() {
    log_info "运行系统检测..."
    
    python3 -c "
import sys
sys.path.append('.')
from core.system_detector import create_system_detector
detector = create_system_detector()
detector.run_comprehensive_detection()
detector.print_detection_summary()
"
}

# 配置库管理
setup_library_config() {
    log_info "配置库管理..."
    
    # 检查库配置文件
    if [ ! -f "config/libraries.yaml" ]; then
        log_info "创建默认库配置..."
        python3 -c "
import sys
sys.path.append('.')
from core.library_manager import create_library_manager
manager = create_library_manager()
print('默认库配置已创建')
"
    else
        log_success "库配置文件已存在"
    fi
    
    # 显示库配置
    python3 -c "
import sys
sys.path.append('.')
from core.library_manager import create_library_manager
manager = create_library_manager()
stats = manager.get_library_stats()
print(f'当前配置库数: {stats[\"total_libraries\"]}')
print(f'启用库数: {stats[\"enabled_libraries\"]}')
"
}

# 选择部署模式
select_deployment_mode() {
    echo ""
    echo "🎯 选择部署模式:"
    echo "1. 开发模式 (快速启动，支持热重载)"
    echo "2. 生产模式 (优化性能，支持多进程)"
    echo "3. Docker模式 (容器化部署)"
    echo "4. 仅后端API模式"
    echo ""
    
    read -p "请选择模式 (1-4, 默认1): " mode_choice
    mode_choice=${mode_choice:-1}
    
    case $mode_choice in
        1)
            DEPLOY_MODE="dev"
            log_info "选择开发模式"
            ;;
        2)
            DEPLOY_MODE="prod"
            log_info "选择生产模式"
            ;;
        3)
            DEPLOY_MODE="docker"
            log_info "选择Docker模式"
            ;;
        4)
            DEPLOY_MODE="api"
            log_info "选择仅后端API模式"
            ;;
        *)
            DEPLOY_MODE="dev"
            log_info "默认选择开发模式"
            ;;
    esac
}

# 开发模式部署
deploy_dev() {
    log_info "启动开发模式..."
    
    # 使用轻量级启动器
    python3 start_lightweight.py
}

# 生产模式部署
deploy_prod() {
    log_info "启动生产模式..."
    
    # 检查是否安装了gunicorn
    if ! pip3 show gunicorn &> /dev/null; then
        log_info "安装gunicorn..."
        pip3 install gunicorn
    fi
    
    # 使用gunicorn启动
    log_info "使用gunicorn启动服务..."
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8090 app.main:create_app
}

# Docker模式部署
deploy_docker() {
    log_info "Docker模式部署..."
    
    # 检查Docker是否安装
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 使用Docker Compose启动
    log_info "使用Docker Compose启动服务..."
    docker-compose up -d
    
    log_success "Docker服务已启动"
    echo "服务地址: http://localhost:8090"
}

# API模式部署
deploy_api() {
    log_info "启动仅后端API模式..."
    
    # 使用轻量级启动器的后端模式
    python3 start_lightweight.py --mode backend
}

# 主部署函数
deploy_main() {
    show_banner
    check_requirements
    install_dependencies
    run_system_detection
    setup_library_config
    select_deployment_mode
    
    case $DEPLOY_MODE in
        "dev")
            deploy_dev
            ;;
        "prod")
            deploy_prod
            ;;
        "docker")
            deploy_docker
            ;;
        "api")
            deploy_api
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo ""
    echo "VabHub 轻量级部署工具"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -d, --dev      开发模式部署"
    echo "  -p, --prod     生产模式部署"
    echo "  -c, --docker   Docker模式部署"
    echo "  -a, --api      仅后端API模式部署"
    echo "  -i, --install  仅安装依赖"
    echo "  -s, --status   显示系统状态"
    echo ""
}

# 显示系统状态
show_status() {
    show_banner
    check_requirements
    run_system_detection
}

# 参数解析
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    -d|--dev)
        DEPLOY_MODE="dev"
        deploy_main
        ;;
    -p|--prod)
        DEPLOY_MODE="prod"
        deploy_main
        ;;
    -c|--docker)
        DEPLOY_MODE="docker"
        deploy_main
        ;;
    -a|--api)
        DEPLOY_MODE="api"
        deploy_main
        ;;
    -i|--install)
        show_banner
        check_requirements
        install_dependencies
        exit 0
        ;;
    -s|--status)
        show_status
        exit 0
        ;;
    *)
        # 默认交互式部署
        deploy_main
        ;;
esac