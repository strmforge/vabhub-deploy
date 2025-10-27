#!/bin/bash

# VabHub排行榜服务部署脚本
# 基于media-oneclick和MoviePilot的最佳实践

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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查环境变量
check_env() {
    local required_vars=(
        "SPOTIFY_API_KEY"
        "TMDB_API_KEY"
        "DOUBAN_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_warning "环境变量 $var 未设置，部分功能可能无法使用"
        fi
    done
}

# 创建网络
create_network() {
    if ! docker network ls | grep -q "vabhub-network"; then
        log_info "创建Docker网络 vabhub-network"
        docker network create vabhub-network
    else
        log_info "Docker网络 vabhub-network 已存在"
    fi
}

# 构建镜像
build_images() {
    log_info "构建排行榜服务镜像"
    
    # 检查Dockerfile是否存在
    if [ ! -f "../VabHub-Core/Dockerfile.charts" ]; then
        log_error "Dockerfile.charts 不存在，请先创建"
        exit 1
    fi
    
    docker-compose -f docker-compose.charts.yml build
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动排行榜服务"
    docker-compose -f docker-compose.charts.yml up -d
    
    # 等待服务启动
    sleep 10
    
    # 检查服务状态
    if docker-compose -f docker-compose.charts.yml ps | grep -q "Up"; then
        log_success "排行榜服务启动成功"
    else
        log_error "服务启动失败，请检查日志"
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止排行榜服务"
    docker-compose -f docker-compose.charts.yml down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启排行榜服务"
    docker-compose -f docker-compose.charts.yml restart
    log_success "服务重启完成"
}

# 查看日志
view_logs() {
    local service="$1"
    if [ -z "$service" ]; then
        docker-compose -f docker-compose.charts.yml logs -f
    else
        docker-compose -f docker-compose.charts.yml logs -f "$service"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查"
    
    # 检查API服务
    if curl -f http://localhost:6280/api/charts/health > /dev/null 2>&1; then
        log_success "API服务健康"
    else
        log_error "API服务异常"
        return 1
    fi
    
    # 检查Redis服务
    if docker-compose -f docker-compose.charts.yml exec redis-charts redis-cli ping | grep -q "PONG"; then
        log_success "Redis服务健康"
    else
        log_error "Redis服务异常"
        return 1
    fi
    
    log_success "所有服务健康检查通过"
}

# 显示服务状态
show_status() {
    log_info "当前服务状态"
    docker-compose -f docker-compose.charts.yml ps
    
    echo ""
    echo "服务访问地址："
    echo "- API服务: http://localhost:6280"
    echo "- API文档: http://localhost:6280/docs"
    echo "- Redis管理: localhost:6390"
}

# 主函数
main() {
    case "${1:-}" in
        "start")
            check_docker
            check_env
            create_network
            build_images
            start_services
            health_check
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            view_logs "$2"
            ;;
        "health")
            health_check
            ;;
        "build")
            check_docker
            build_images
            ;;
        *)
            echo "使用方法: $0 {start|stop|restart|status|logs|health|build}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动排行榜服务"
            echo "  stop     - 停止排行榜服务"
            echo "  restart  - 重启排行榜服务"
            echo "  status   - 显示服务状态"
            echo "  logs     - 查看服务日志"
            echo "  health   - 执行健康检查"
            echo "  build    - 构建服务镜像"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"