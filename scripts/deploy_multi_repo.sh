#!/bin/bash

# VabHub 多仓库部署脚本
# 支持从多个GitHub仓库部署完整的VabHub系统

set -e

# 配置变量
VABHUB_ORG="vabhub"
REPOS=("vabhub-core" "vabhub-frontend" "vabhub-plugins" "vabhub-resources")
DEPLOY_DIR="./deploy"
CONFIG_DIR="./config"
BACKUP_DIR="./backups"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查依赖
check_dependencies() {
    log "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，请先安装 Docker"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose 未安装，请先安装 Docker Compose"
    fi
    
    if ! command -v git &> /dev/null; then
        error "Git 未安装，请先安装 Git"
    fi
    
    log "所有依赖检查通过"
}

# 初始化部署环境
init_deploy() {
    log "初始化多仓库部署环境..."
    
    # 创建部署目录
    mkdir -p "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
    
    # 克隆或更新仓库
    for repo in "${REPOS[@]}"; do
        if [ -d "$repo" ]; then
            log "更新仓库: $repo"
            cd "$repo"
            git pull origin main
            cd ..
        else
            log "克隆仓库: $repo"
            git clone "https://github.com/$VABHUB_ORG/$repo.git"
        fi
    done
    
    # 复制配置文件
    mkdir -p "$CONFIG_DIR"
    cp -r ../config/* "$CONFIG_DIR/" 2>/dev/null || warn "没有找到配置文件模板"
    
    log "部署环境初始化完成"
}

# 构建 Docker 镜像
build_images() {
    log "构建 Docker 镜像..."
    
    cd "$DEPLOY_DIR"
    
    # 构建核心服务镜像
    if [ -d "vabhub-core" ]; then
        log "构建 VabHub Core 镜像"
        cd vabhub-core
        docker build -t vabhub/vabhub-core:latest .
        cd ..
    fi
    
    # 构建前端镜像
    if [ -d "vabhub-frontend" ]; then
        log "构建 VabHub Frontend 镜像"
        cd vabhub-frontend
        docker build -t vabhub/vabhub-frontend:latest .
        cd ..
    fi
    
    # 构建插件镜像
    if [ -d "vabhub-plugins" ]; then
        log "构建 VabHub Plugins 镜像"
        cd vabhub-plugins
        docker build -t vabhub/vabhub-plugins:latest .
        cd ..
    fi
    
    log "所有镜像构建完成"
}

# 启动服务
start_services() {
    log "启动 VabHub 服务..."
    
    cd "$DEPLOY_DIR/.."
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        warn "未找到 .env 文件，使用默认配置"
        cp .env.example .env 2>/dev/null || warn "未找到 .env.example 文件"
    fi
    
    # 启动服务
    docker-compose -f docker-compose.multi-repo.yml up -d
    
    log "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services
}

# 检查服务状态
check_services() {
    log "检查服务状态..."
    
    # 检查核心服务
    if curl -f http://localhost:8090/api/health > /dev/null 2>&1; then
        log "✓ VabHub Core 服务运行正常"
    else
        error "✗ VabHub Core 服务启动失败"
    fi
    
    # 检查前端服务
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        log "✓ VabHub Frontend 服务运行正常"
    else
        warn "✗ VabHub Frontend 服务可能有问题"
    fi
    
    log "所有服务检查完成"
}

# 停止服务
stop_services() {
    log "停止 VabHub 服务..."
    
    cd "$DEPLOY_DIR/.."
    docker-compose -f docker-compose.multi-repo.yml down
    
    log "服务已停止"
}

# 重启服务
restart_services() {
    log "重启 VabHub 服务..."
    
    stop_services
    start_services
}

# 备份数据
backup_data() {
    log "备份 VabHub 数据..."
    
    mkdir -p "$BACKUP_DIR"
    DATE=$(date +%Y%m%d_%H%M%S)
    
    # 备份数据库
    if docker exec vabhub-postgres pg_dump -U vabhub vabhub > "$BACKUP_DIR/db_backup_$DATE.sql" 2>/dev/null; then
        log "✓ 数据库备份完成"
    else
        warn "✗ 数据库备份失败"
    fi
    
    # 备份配置文件
    if cp -r "$CONFIG_DIR" "$BACKUP_DIR/config_$DATE" 2>/dev/null; then
        log "✓ 配置文件备份完成"
    else
        warn "✗ 配置文件备份失败"
    fi
    
    # 备份数据卷
    if docker run --rm -v vabhub_data:/data -v "$BACKUP_DIR:/backup" alpine tar -czf "/backup/data_backup_$DATE.tar.gz" /data 2>/dev/null; then
        log "✓ 数据卷备份完成"
    else
        warn "✗ 数据卷备份失败"
    fi
    
    log "备份完成: $BACKUP_DIR"
}

# 显示帮助信息
show_help() {
    echo "VabHub 多仓库部署脚本"
    echo ""
    echo "用法: $0 {init|build|start|stop|restart|status|backup|help}"
    echo ""
    echo "命令:"
    echo "  init     初始化部署环境"
    echo "  build    构建 Docker 镜像"
    echo "  start    启动所有服务"
    echo "  stop     停止所有服务"
    echo "  restart  重启所有服务"
    echo "  status   检查服务状态"
    echo "  backup   备份数据"
    echo "  help     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 init    # 初始化环境"
    echo "  $0 build   # 构建镜像"
    echo "  $0 start   # 启动服务"
}

# 主函数
main() {
    case "$1" in
        init)
            check_dependencies
            init_deploy
            ;;
        build)
            check_dependencies
            build_images
            ;;
        start)
            check_dependencies
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            check_dependencies
            restart_services
            ;;
        status)
            check_services
            ;;
        backup)
            backup_data
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"