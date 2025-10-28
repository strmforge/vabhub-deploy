# VabHub-Deploy

VabHub-Deploy 是 VabHub 媒体管理系统的专业部署解决方案，提供完整的容器化部署、监控和运维支持。

## 🎉 最新版本: 1.3.0

**VabHub-Deploy 1.3.0** 是一个重大版本更新，带来了企业级的部署和运维能力。

### 🚀 1.3.0 版本亮点
- **多服务架构**: 后端、前端、数据库、缓存、监控分离部署
- **健康检查**: 自动服务健康监控和重启
- **监控告警**: Prometheus + Grafana 集成
- **备份恢复**: 完整的备份和恢复机制

## 🏗️ 部署架构

### 📦 容器化部署
- **Docker Compose**: 多服务编排管理
- **多环境支持**: 开发、测试、生产环境
- **资源管理**: CPU、内存资源限制
- **网络配置**: 安全的网络隔离

### 📊 监控系统
- **Prometheus**: 系统指标收集和存储
- **Grafana**: 可视化监控界面
- **健康检查**: 服务健康状态监控
- **告警规则**: 关键指标异常告警

### 🔒 安全特性
- **网络安全**: 网络隔离和防火墙规则
- **访问控制**: 基于角色的访问控制
- **数据加密**: 敏感数据加密存储
- **漏洞扫描**: 定期安全扫描

## 🚀 快速部署

### 生产环境部署
```bash
# 1. 克隆部署仓库
git clone https://github.com/vabhub/vabhub-deploy.git
cd vabhub-deploy

# 2. 配置环境
cp .env.production .env
# 编辑环境变量

# 3. 启动服务
docker-compose -f docker-compose.enhanced.yml up -d

# 4. 验证部署
docker-compose ps
curl http://localhost:8090/api/health
```

### 监控系统访问
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **前端界面**: http://localhost:8080
- **API文档**: http://localhost:8090/docs

## 📁 项目结构

```
VabHub-Deploy/
├── docker-compose.enhanced.yml    # 增强版部署配置
├── docker-compose.yml            # 基础部署配置
├── docker/                        # Docker配置
│   ├── Dockerfile.core           # 后端镜像
│   └── Dockerfile.frontend      # 前端镜像
├── scripts/                      # 部署脚本
│   ├── deploy.sh                # 部署脚本
│   └── backup.sh                # 备份脚本
├── config/                       # 配置文件
│   ├── prometheus.yml           # Prometheus配置
│   └── grafana.ini              # Grafana配置
└── .env.production              # 生产环境配置
```

## 🔧 部署配置

### 环境变量配置
```bash
# 数据库配置
POSTGRES_DB=vabhub
POSTGRES_USER=vabhub
POSTGRES_PASSWORD=your_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 服务端口
VABHUB_PORT=8090
FRONTEND_PORT=8080
GRAFANA_PORT=3000
```

### 资源限制
```yaml
services:
  vabhub-core:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

## 📈 运维管理

### 备份和恢复
```bash
# 数据备份
./scripts/backup.sh

# 数据恢复
./scripts/restore.sh backup_file.sql
```

### 监控和告警
- **系统指标**: CPU、内存、磁盘、网络使用率
- **服务状态**: 各服务运行状态和健康检查
- **性能指标**: API响应时间、数据库查询性能
- **告警通知**: 邮件、Slack、Webhook通知

### 日志管理
- **集中日志**: 所有服务的日志收集
- **日志轮转**: 自动日志轮转和清理
- **日志查询**: 支持关键词搜索和时间范围查询

## 🔗 相关仓库

- **后端服务**: [vabhub-core](https://github.com/vabhub/vabhub-core)
- **前端界面**: [vabhub-frontend](https://github.com/vabhub/vabhub-frontend)
- **插件系统**: [vabhub-plugins](https://github.com/vabhub/vabhub-plugins)

## 🤝 贡献指南

欢迎参与 VabHub-Deploy 项目的开发！

### 开发流程
1. Fork 仓库
2. 创建功能分支
3. 提交代码更改
4. 创建 Pull Request

### 部署测试
- 测试多环境部署
- 验证监控系统功能
- 测试备份恢复流程
- 性能压力测试

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 支持与交流

- **文档**: [VabHub Wiki](https://github.com/vabhub/vabhub-wiki)
- **问题**: [GitHub Issues](https://github.com/vabhub/vabhub-deploy/issues)
- **讨论**: [GitHub Discussions](https://github.com/vabhub/vabhub-deploy/discussions)

---

**VabHub Deploy Team**  
*专业级部署解决方案*  
2025年10月28日