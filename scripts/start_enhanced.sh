#!/bin/bash

# 增强版媒体重命名器启动脚本
# 整合所有历史版本功能的统一启动入口

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
    echo "=================================================="
    echo "        增强版媒体重命名器 V2.0"
    echo "        整合所有历史版本功能"
    echo "=================================================="
    echo ""
}

# 检查Python环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python环境，请先安装Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_info "检测到Python版本: $PYTHON_VERSION"
    
    # 检查Python版本是否 >= 3.8
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖包..."
    
    # 检查pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        log_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    # 检查requirements.txt
    if [ ! -f "requirements.txt" ]; then
        log_error "未找到requirements.txt文件"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖包..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    $PIP_CMD install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        log_success "依赖包安装完成"
    else
        log_error "依赖包安装失败"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f "config.json" ]; then
        log_warning "未找到config.json，将使用默认配置"
        # 可以在这里创建默认配置文件
        # cp config.example.json config.json
    else
        log_success "配置文件存在"
    fi
}

# 启动应用
start_application() {
    log_info "启动增强版媒体重命名器..."
    
    # 检查启动文件
    if [ ! -f "start_enhanced_v2.py" ]; then
        log_error "未找到启动文件 start_enhanced_v2.py"
        exit 1
    fi
    
    # 启动应用
    $PYTHON_CMD start_enhanced_v2.py
    
    if [ $? -eq 0 ]; then
        log_success "应用启动成功"
    else
        log_error "应用启动失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -d, --docker   使用Docker启动"
    echo "  -k, --k8s      使用Kubernetes部署"
    echo "  -t, --test     运行测试"
    echo ""
    echo "示例:"
    echo "  $0              # 本地启动"
    echo "  $0 -d          # Docker启动"
    echo "  $0 -k          # Kubernetes部署"
}

# 使用Docker启动
docker_start() {
    log_info "使用Docker启动..."
    
    if [ ! -f "docker-compose.enhanced.yml" ]; then
        log_error "未找到Docker Compose配置文件"
        exit 1
    fi
    
    docker-compose -f docker-compose.enhanced.yml up -d
    
    if [ $? -eq 0 ]; then
        log_success "Docker容器启动成功"
        echo ""
        echo "服务访问地址:"
        echo "  - Web界面: http://localhost:8090"
        echo "  - API文档: http://localhost:8090/docs"
        echo ""
        echo "查看日志: docker-compose -f docker-compose.enhanced.yml logs -f"
    else
        log_error "Docker容器启动失败"
        exit 1
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    if [ -d "tests" ]; then
        $PYTHON_CMD -m pytest tests/ -v
    else
        log_warning "未找到tests目录，跳过测试"
    fi
}

# 主函数
main() {
    show_banner
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--docker)
                DOCKER_MODE=true
                shift
                ;;
            -k|--k8s)
                K8S_MODE=true
                shift
                ;;
            -t|--test)
                TEST_MODE=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Kubernetes模式
    if [ "$K8S_MODE" = true ]; then
        log_info "Kubernetes部署模式"
        if [ -f "kubernetes/deployment.yaml" ]; then
            kubectl apply -f kubernetes/
            log_success "Kubernetes部署完成"
        else
            log_error "未找到Kubernetes配置文件"
        fi
        exit 0
    fi
    
    # Docker模式
    if [ "$DOCKER_MODE" = true ]; then
        docker_start
        exit 0
    fi
    
    # 测试模式
    if [ "$TEST_MODE" = true ]; then
        check_python
        run_tests
        exit 0
    fi
    
    # 本地启动模式
    check_python
    check_dependencies
    install_dependencies
    check_config
    start_application
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi