# VabHub-Deploy

VabHub 部署配置和脚本，支持 Docker 容器化部署。

## 🚀 快速开始

### Docker 部署（推荐）
```bash
# 一键部署所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 多仓库部署
```bash
# 部署多仓库版本
./scripts/deploy_multi_repo.sh init
./scripts/deploy_multi_repo.sh start
```

### 手动部署
```bash
# 部署后端服务
cd ../VabHub-Core
pip install -r requirements.txt
python start.py

# 部署前端服务
cd ../VabHub-Frontend
npm install
npm run build
npm run preview
```

## 📁 项目结构

```
VabHub-Deploy/
├── docker/                 # Docker 配置
│   ├── Dockerfile.core    # 后端镜像
│   ├── Dockerfile.frontend # 前端镜像
│   └── nginx.conf        # Nginx 配置
├── scripts/               # 部署脚本
│   ├── deploy_multi_repo.sh
│   ├── deploy_single.sh
│   └── backup.sh
├── config/                # 配置文件模板
│   ├── config.example.yaml
│   └── nginx.conf.example
├── docker-compose.yml     # 单仓库部署
├── docker-compose.multi-repo.yml # 多仓库部署
└── README.md
```

## 🔧 部署配置

### Docker Compose 配置

**单仓库部署（开发环境）**
```yaml
# docker-compose.yml
version: '3.8'
services:
  vabhub-core:
    build: .
    ports:
      - "8090:8090"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - VABHUB_ENV=production

  vabhub-frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - vabhub-core
```

**多仓库部署（生产环境）**
```yaml
# docker-compose.multi-repo.yml
version: '3.8'
services:
  vabhub-core:
    image: vabhub/vabhub-core:latest
    ports:
      - "8090:8090"
    volumes:
      - vabhub-config:/app/config
      - vabhub-data:/app/data

  vabhub-frontend:
    image: vabhub/vabhub-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - vabhub-core
```

### 环境变量配置

创建 `.env` 文件：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vabhub
DB_USER=vabhub
DB_PASSWORD=your_password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# 应用配置
VABHUB_ENV=production
SECRET_KEY=your_secret_key
API_BASE_URL=http://localhost:8090
```

## 🚀 部署脚本

### 多仓库部署脚本
```bash
#!/bin/bash
# scripts/deploy_multi_repo.sh

case "$1" in
  init)
    echo "初始化多仓库部署..."
    # 克隆所有仓库
    git clone https://github.com/vabhub/vabhub-core.git
    git clone https://github.com/vabhub/vabhub-frontend.git
    git clone https://github.com/vabhub/vabhub-plugins.git
    ;;
  start)
    echo "启动多仓库服务..."
    docker-compose -f docker-compose.multi-repo.yml up -d
    ;;
  stop)
    echo "停止多仓库服务..."
    docker-compose -f docker-compose.multi-repo.yml down
    ;;
  *)
    echo "用法: $0 {init|start|stop|restart|status}"
    ;;
esac
```

### 备份脚本
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# 备份数据库
docker exec vabhub-db pg_dump -U vabhub vabhub > "$BACKUP_DIR/db_backup_$DATE.sql"

# 备份配置文件
cp -r config "$BACKUP_DIR/config_$DATE"

# 备份数据文件
tar -czf "$BACKUP_DIR/data_backup_$DATE.tar.gz" data/

echo "备份完成: $BACKUP_DIR"
```

## 🔌 网络配置

### 端口映射
- **后端 API**: 8090
- **前端界面**: 3000 (开发) / 80 (生产)
- **数据库**: 5432
- **Redis**: 6379

### 反向代理配置（Nginx）
```nginx
# config/nginx.conf
server {
    listen 80;
    server_name vabhub.example.com;

    # 前端静态文件
    location / {
        proxy_pass http://vabhub-frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://vabhub-core:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 监控和日志

### 服务监控
```bash
# 查看容器状态
docker-compose ps

# 查看资源使用情况
docker stats

# 查看服务日志
docker-compose logs -f vabhub-core
```

### 健康检查
```yaml
# docker-compose.yml 中的健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8090/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 🔒 安全配置

### SSL/TLS 配置
```nginx
# SSL 配置
server {
    listen 443 ssl;
    server_name vabhub.example.com;

    ssl_certificate /etc/ssl/certs/vabhub.crt;
    ssl_certificate_key /etc/ssl/private/vabhub.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 其他配置...
}
```

### 防火墙规则
```bash
# 开放必要端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8090/tcp

# 限制访问来源
ufw allow from 192.168.1.0/24 to any port 22
```

## 🔗 相关仓库

- [VabHub-Core](https://github.com/vabhub/vabhub-core) - 后端核心服务
- [VabHub-Frontend](https://github.com/vabhub/vabhub-frontend) - 前端界面
- [VabHub-Plugins](https://github.com/vabhub/vabhub-plugins) - 插件系统
- [VabHub-Resources](https://github.com/vabhub/vabhub-resources) - 资源文件

## 🤝 贡献指南

欢迎提交部署配置和改进！

### 开发环境设置
```bash
# 1. Fork 仓库
# 2. 克隆到本地
git clone https://github.com/your-username/vabhub-deploy.git

# 3. 创建开发分支
git checkout -b feature/your-feature

# 4. 测试部署配置
./scripts/deploy_multi_repo.sh test

# 5. 提交更改
git commit -m "feat: add your feature"

# 6. 推送到远程
git push origin feature/your-feature

# 7. 创建 Pull Request
```

### 部署规范
- 使用 Docker 容器化部署
- 提供开发和生产环境配置
- 支持多仓库协作部署
- 包含备份和恢复脚本

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 支持

- 文档: [VabHub Wiki](https://github.com/vabhub/vabhub-wiki)
- 问题: [GitHub Issues](https://github.com/vabhub/vabhub-deploy/issues)
- 讨论: [GitHub Discussions](https://github.com/vabhub/vabhub-deploy/discussions)