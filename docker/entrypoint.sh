#!/bin/bash

# VabHub 核心容器启动脚本
# 支持快速启动和组件按需安装

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 显示横幅
show_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   VabHub 核心快速启动容器                    ║"
    echo "║                基于 MoviePilot 部署模式                    ║"
    echo "║                    版本: ${VABHUB_VERSION}                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# 检测系统环境
check_system() {
    log_info "🔍 检测系统环境..."
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python 版本: $PYTHON_VERSION"
    else
        log_error "未找到 Python3"
        exit 1
    fi
    
    # 检查必要服务
    services=("nginx" "supervisord")
    for service in "${services[@]}"; do
        if command -v $service &> /dev/null; then
            log_success "$service 服务可用"
        else
            log_error "$service 服务不可用"
            exit 1
        fi
    done
    
    # 检查目录权限
    directories=("/app" "/app/logs" "/app/data")
    for dir in "${directories[@]}"; do
        if [ -w "$dir" ]; then
            log_success "目录可写: $dir"
        else
            log_error "目录不可写: $dir"
            exit 1
        fi
    done
}

# 检测后端状态
check_backend() {
    log_info "⚙️ 检测后端状态..."
    
    # 检查核心文件
    core_files=("app/main.py" "app/core/config.py" "requirements.txt")
    for file in "${core_files[@]}"; do
        if [ -f "/app/$file" ]; then
            log_success "核心文件存在: $file"
        else
            log_error "核心文件缺失: $file"
            return 1
        fi
    done
    
    # 检查 Python 依赖
    if python3 -c "import fastapi, uvicorn, pydantic" &> /dev/null; then
        log_success "Python 依赖正常"
    else
        log_warning "Python 依赖异常，尝试重新安装..."
        pip install -r /app/requirements.txt
    fi
    
    return 0
}

# 检测前端状态
check_frontend() {
    log_info "🎨 检测前端状态..."
    
    # 检查前端构建文件
    if [ -d "/app/public" ] && [ -f "/app/public/index.html" ]; then
        log_success "前端构建文件存在"
        return 0
    else
        log_warning "前端构建文件缺失"
        return 1
    fi
}

# 安装或更新前端
install_frontend() {
    log_info "📥 安装/更新前端..."
    
    # 检查前端仓库是否存在
    if [ ! -d "/app/frontend" ]; then
        log_info "克隆前端仓库..."
        git clone https://github.com/vabhub/vabhub-frontend.git /app/frontend || {
            log_error "前端仓库克隆失败"
            return 1
        }
    else
        log_info "更新前端仓库..."
        cd /app/frontend && git pull
    fi
    
    # 检查 Node.js 环境
    if command -v npm &> /dev/null; then
        log_success "Node.js 环境可用"
    else
        log_info "安装 Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
            && apt-get install -y nodejs
    fi
    
    # 构建前端
    cd /app/frontend
    log_info "安装前端依赖..."
    npm install || {
        log_error "前端依赖安装失败"
        return 1
    }
    
    log_info "构建前端..."
    npm run build || {
        log_error "前端构建失败"
        return 1
    }
    
    # 复制构建文件
    rm -rf /app/public
    cp -r dist /app/public
    log_success "前端安装完成"
    return 0
}

# 检测插件库
check_plugins() {
    log_info "🔌 检测插件库..."
    
    # 检查插件目录
    if [ ! -d "/app/plugins" ]; then
        mkdir -p /app/plugins
        log_info "创建插件目录"
    fi
    
    # 检查插件仓库
    if [ ! -d "/app/plugins/.git" ]; then
        log_info "初始化插件仓库..."
        git clone https://github.com/vabhub/vabhub-plugins.git /app/plugins || {
            log_warning "插件仓库初始化失败，使用空插件目录"
            return 1
        }
    else
        log_info "更新插件仓库..."
        cd /app/plugins && git pull
    fi
    
    # 检测可用插件
    plugin_count=$(find /app/plugins -name "*.py" | wc -l)
    log_success "检测到 $plugin_count 个插件"
    
    return 0
}

# 检测资源文件
check_resources() {
    log_info "📚 检测资源文件..."
    
    # 检查资源目录
    if [ ! -d "/app/resources" ]; then
        mkdir -p /app/resources
        log_info "创建资源目录"
    fi
    
    # 检查资源仓库
    if [ ! -d "/app/resources/.git" ]; then
        log_info "初始化资源仓库..."
        git clone https://github.com/vabhub/vabhub-resources.git /app/resources || {
            log_warning "资源仓库初始化失败，使用默认资源"
            return 1
        }
    else
        log_info "更新资源仓库..."
        cd /app/resources && git pull
    fi
    
    return 0
}

# 启动服务
start_services() {
    log_info "🚀 启动服务..."
    
    # 启动 Supervisor
    supervisord -c /etc/supervisor/conf.d/supervisor.conf
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if supervisorctl status | grep -q RUNNING; then
        log_success "服务启动成功"
        
        # 显示服务状态
        echo ""
        echo "📊 服务状态:"
        supervisorctl status
        echo ""
        
        # 显示访问信息
        echo "🌐 访问信息:"
        echo "   前端界面: http://localhost:8090"
        echo "   API 文档: http://localhost:8090/docs"
        echo "   健康检查: http://localhost:8090/health"
        echo ""
        
    else
        log_error "服务启动失败"
        supervisorctl status
        exit 1
    fi
}

# 主启动函数
main() {
    show_banner
    
    # 检测系统环境
    check_system
    
    # 检测后端状态
    if ! check_backend; then
        log_error "后端检测失败，无法启动"
        exit 1
    fi
    
    # 检测前端状态，如果缺失则安装
    if ! check_frontend; then
        log_warning "前端文件缺失，尝试安装..."
        if install_frontend; then
            log_success "前端安装成功"
        else
            log_warning "前端安装失败，将以 API 模式运行"
        fi
    fi
    
    # 检测插件库
    check_plugins
    
    # 检测资源文件
    check_resources
    
    # 启动服务
    start_services
    
    # 保持容器运行
    log_info "🔄 容器运行中..."
    tail -f /app/logs/app.log
}

# 执行主函数
main "$@"