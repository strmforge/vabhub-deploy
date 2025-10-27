#!/bin/bash

# 媒体管理平台部署脚本
# 作者: Media Renamer Team
# 版本: 1.0.0

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

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 构建镜像
build_image() {
    log_info "构建Docker镜像..."
    docker-compose build
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务重启完成"
}

# 查看服务状态
status_services() {
    log_info "查看服务状态..."
    docker-compose ps
}

# 查看日志
view_logs() {
    log_info "查看服务日志..."
    docker-compose logs -f
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    # 创建备份目录
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份配置文件
    cp -r config "$BACKUP_DIR/"
    cp -r data "$BACKUP_DIR/"
    
    # 备份数据库
    docker-compose exec redis redis-cli save
    docker cp vabhub-redis:/data/dump.rdb "$BACKUP_DIR/"
    
    log_success "数据备份完成: $BACKUP_DIR"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    log_info "恢复数据..."
    
    BACKUP_DIR="$1"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi
    
    # 恢复配置文件
    cp -r "$BACKUP_DIR/config" ./
    cp -r "$BACKUP_DIR/data" ./
    
    # 恢复数据库
    docker cp "$BACKUP_DIR/dump.rdb" vabhub-redis:/data/
    docker-compose exec redis redis-cli load
    
    log_success "数据恢复完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 创建测试环境
    docker-compose -f docker-compose.test.yml up -d
    
    # 运行测试
    docker-compose -f docker-compose.test.yml exec media-renamer python -m pytest tests/
    
    # 清理测试环境
    docker-compose -f docker-compose.test.yml down
    
    log_success "测试完成"
}

# 显示帮助信息
show_help() {
    echo "媒体管理平台部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看服务日志"
    echo "  build     构建镜像"
    echo "  backup    备份数据"
    echo "  restore   恢复数据"
    echo "  test      运行测试"
    echo "  help      显示帮助信息"
    echo ""
}

# 主函数
main() {
    case "$1" in
        "start")
            check_dependencies
            build_image
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            status_services
            ;;
        "logs")
            view_logs
            ;;
        "build")
            check_dependencies
            build_image
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "test")
            run_tests
            ;;
        "help"|""|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"