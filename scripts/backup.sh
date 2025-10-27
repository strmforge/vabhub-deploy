#!/bin/bash

# VabHub 数据备份脚本
# 支持数据库、配置文件和数据的完整备份

set -e

# 配置变量
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# 检查 Docker 服务
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker 服务未运行"
    fi
}

# 创建备份目录
create_backup_dir() {
    mkdir -p "$BACKUP_DIR/$DATE"
    log "创建备份目录: $BACKUP_DIR/$DATE"
}

# 备份数据库
backup_database() {
    log "备份 PostgreSQL 数据库..."
    
    if docker exec vabhub-postgres pg_dump -U vabhub vabhub > "$BACKUP_DIR/$DATE/database.sql" 2>/dev/null; then
        log "✓ 数据库备份完成"
        
        # 压缩数据库备份
        gzip "$BACKUP_DIR/$DATE/database.sql"
        log "✓ 数据库备份已压缩"
    else
        warn "✗ 数据库备份失败"
    fi
}

# 备份 Redis 数据
backup_redis() {
    log "备份 Redis 数据..."
    
    # 创建 Redis 备份
    if docker exec vabhub-redis redis-cli SAVE > /dev/null 2>&1; then
        # 复制 RDB 文件
        docker cp vabhub-redis:/data/dump.rdb "$BACKUP_DIR/$DATE/redis.rdb" 2>/dev/null || true
        
        if [ -f "$BACKUP_DIR/$DATE/redis.rdb" ]; then
            log "✓ Redis 数据备份完成"
            gzip "$BACKUP_DIR/$DATE/redis.rdb"
        else
            warn "✗ Redis 数据备份失败"
        fi
    else
        warn "✗ Redis 备份命令执行失败"
    fi
}

# 备份配置文件
backup_config() {
    log "备份配置文件..."
    
    # 备份 Docker Compose 配置
    if [ -f "docker-compose.yml" ]; then
        cp docker-compose.yml "$BACKUP_DIR/$DATE/"
    fi
    
    if [ -f "docker-compose.multi-repo.yml" ]; then
        cp docker-compose.multi-repo.yml "$BACKUP_DIR/$DATE/"
    fi
    
    # 备份环境变量
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/$DATE/"
    fi
    
    # 备份配置目录
    if [ -d "config" ]; then
        cp -r config "$BACKUP_DIR/$DATE/"
    fi
    
    # 备份脚本
    if [ -d "scripts" ]; then
        cp -r scripts "$BACKUP_DIR/$DATE/"
    fi
    
    log "✓ 配置文件备份完成"
}

# 备份数据卷
backup_volumes() {
    log "备份数据卷..."
    
    # 备份核心数据卷
    if docker volume inspect vabhub_data > /dev/null 2>&1; then
        docker run --rm -v vabhub_data:/data -v "$BACKUP_DIR/$DATE:/backup" alpine tar -czf "/backup/vabhub_data.tar.gz" /data 2>/dev/null || true
        if [ -f "$BACKUP_DIR/$DATE/vabhub_data.tar.gz" ]; then
            log "✓ VabHub 数据卷备份完成"
        else
            warn "✗ VabHub 数据卷备份失败"
        fi
    fi
    
    # 备份配置卷
    if docker volume inspect vabhub_config > /dev/null 2>&1; then
        docker run --rm -v vabhub_config:/config -v "$BACKUP_DIR/$DATE:/backup" alpine tar -czf "/backup/vabhub_config.tar.gz" /config 2>/dev/null || true
        if [ -f "$BACKUP_DIR/$DATE/vabhub_config.tar.gz" ]; then
            log "✓ VabHub 配置卷备份完成"
        else
            warn "✗ VabHub 配置卷备份失败"
        fi
    fi
    
    # 备份日志卷
    if docker volume inspect vabhub_logs > /dev/null 2>&1; then
        docker run --rm -v vabhub_logs:/logs -v "$BACKUP_DIR/$DATE:/backup" alpine tar -czf "/backup/vabhub_logs.tar.gz" /logs 2>/dev/null || true
        if [ -f "$BACKUP_DIR/$DATE/vabhub_logs.tar.gz" ]; then
            log "✓ VabHub 日志卷备份完成"
        else
            warn "✗ VabHub 日志卷备份失败"
        fi
    fi
}

# 创建备份清单
create_backup_manifest() {
    log "创建备份清单..."
    
    cat > "$BACKUP_DIR/$DATE/manifest.json" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "backup_version": "1.0.0",
    "components": [
        {
            "name": "database",
            "file": "database.sql.gz",
            "size": "$(stat -c%s "$BACKUP_DIR/$DATE/database.sql.gz" 2>/dev/null || echo 0)"
        },
        {
            "name": "redis",
            "file": "redis.rdb.gz", 
            "size": "$(stat -c%s "$BACKUP_DIR/$DATE/redis.rdb.gz" 2>/dev/null || echo 0)"
        },
        {
            "name": "config",
            "files": ["docker-compose.yml", "docker-compose.multi-repo.yml", ".env", "config/", "scripts/"],
            "size": "$(du -sb "$BACKUP_DIR/$DATE/config" "$BACKUP_DIR/$DATE/scripts" 2>/dev/null | awk '{sum += $1} END {print sum}')"
        },
        {
            "name": "volumes",
            "files": ["vabhub_data.tar.gz", "vabhub_config.tar.gz", "vabhub_logs.tar.gz"],
            "size": "$(stat -c%s "$BACKUP_DIR/$DATE/vabhub_data.tar.gz" 2>/dev/null || echo 0)"
        }
    ],
    "total_size": "$(du -sb "$BACKUP_DIR/$DATE" | cut -f1)"
}
EOF
    
    log "✓ 备份清单创建完成"
}

# 清理旧备份
cleanup_old_backups() {
    log "清理超过 ${RETENTION_DAYS} 天的旧备份..."
    
    find "$BACKUP_DIR" -maxdepth 1 -type d -name "*_*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    log "✓ 旧备份清理完成"
}

# 验证备份完整性
verify_backup() {
    log "验证备份完整性..."
    
    # 检查关键文件是否存在
    local critical_files=("database.sql.gz" "manifest.json")
    
    for file in "${critical_files[@]}"; do
        if [ ! -f "$BACKUP_DIR/$DATE/$file" ]; then
            warn "✗ 关键备份文件缺失: $file"
            return 1
        fi
    done
    
    log "✓ 备份完整性验证通过"
    return 0
}

# 主备份函数
main_backup() {
    log "开始 VabHub 数据备份..."
    
    check_docker
    create_backup_dir
    backup_database
    backup_redis
    backup_config
    backup_volumes
    create_backup_manifest
    
    if verify_backup; then
        log "✅ 备份成功完成: $BACKUP_DIR/$DATE"
        
        # 显示备份统计
        echo ""
        echo "备份统计:"
        echo "- 备份时间: $(date)"
        echo "- 备份目录: $BACKUP_DIR/$DATE"
        echo "- 总大小: $(du -sh "$BACKUP_DIR/$DATE" | cut -f1)"
        echo ""
    else
        error "❌ 备份验证失败"
    fi
    
    cleanup_old_backups
}

# 显示帮助信息
show_help() {
    echo "VabHub 数据备份脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --dir DIR     指定备份目录 (默认: ./backups)"
    echo "  -r, --retention N 保留天数 (默认: 7)"
    echo "  -h, --help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 执行默认备份"
    echo "  $0 -d /mnt/backup    # 指定备份目录"
    echo "  $0 -r 30             # 保留30天备份"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 执行备份
main_backup