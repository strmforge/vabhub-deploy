# MediaRenamer Enhanced 部署指南

## 部署方式

### 1. Docker Compose 部署（推荐用于开发环境）

```bash
# 克隆项目
git clone <repository-url>
cd media-renamer

# 使用增强版配置
docker-compose -f docker-compose.enhanced.yml up -d

# 查看服务状态
docker-compose -f docker-compose.enhanced.yml ps

# 查看日志
docker-compose -f docker-compose.enhanced.yml logs -f media-renamer
```

### 2. Kubernetes 原生部署

```bash
# 创建命名空间
kubectl create namespace media-renamer

# 部署数据库
kubectl apply -f kubernetes/postgres.yaml

# 部署Redis
kubectl apply -f kubernetes/redis.yaml

# 部署配置
kubectl apply -f kubernetes/configmap.yaml

# 部署应用
kubectl apply -f kubernetes/deployment.yaml

# 查看部署状态
kubectl get all -n media-renamer
```

### 3. Helm 部署（推荐用于生产环境）

```bash
# 添加 Helm 仓库（如果使用私有仓库）
helm repo add media-renamer https://charts.example.com/media-renamer

# 更新仓库
helm repo update

# 安装应用
helm install media-renamer media-renamer/media-renamer \
  --namespace media-renamer \
  --create-namespace \
  --values deploy/helm/values.yaml

# 升级应用
helm upgrade media-renamer media-renamer/media-renamer \
  --namespace media-renamer \
  --values deploy/helm/values.yaml

# 卸载应用
helm uninstall media-renamer --namespace media-renamer
```

## 配置说明

### 环境变量配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| APP_ENV | 应用环境 | production |
| LOG_LEVEL | 日志级别 | INFO |
| DATABASE_URL | 数据库连接字符串 | postgresql://user:pass@db:5432/media_renamer |
| REDIS_URL | Redis连接字符串 | redis://redis:6379/0 |

### 配置文件

应用支持多种配置源：

1. **环境变量**：最高优先级
2. **ConfigMap**：Kubernetes环境
3. **配置文件**：本地文件系统
4. **数据库**：动态配置存储

## 监控和日志

### 内置监控

应用内置了以下监控指标：
- HTTP请求统计
- 数据库连接池状态
- 缓存命中率
- 任务队列状态
- 插件加载状态

### 日志配置

日志输出到标准输出和文件：
- 标准输出：容器日志
- 文件日志：/app/logs/app.log
- 错误日志：/app/logs/error.log

### Prometheus 监控

```yaml
# prometheus.yml 配置示例
scrape_configs:
  - job_name: 'media-renamer'
    static_configs:
      - targets: ['media-renamer-service:8000']
    metrics_path: /metrics
    scrape_interval: 30s
```

## 高可用配置

### 副本数量

```yaml
# 生产环境推荐配置
replicaCount: 3
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

### 自动扩缩容

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

## 安全配置

### 网络策略

```yaml
# 限制网络访问
networkPolicy:
  enabled: true
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx
      ports:
        - protocol: TCP
          port: 8000
```

### TLS 配置

```yaml
ingress:
  enabled: true
  tls:
    - hosts:
        - media-renamer.example.com
      secretName: media-renamer-tls
```

## 备份和恢复

### 数据库备份

```bash
# 创建数据库备份
kubectl exec -n media-renamer postgres-pod -- pg_dump -U user media_renamer > backup.sql

# 恢复数据库
kubectl exec -i -n media-renamer postgres-pod -- psql -U user media_renamer < backup.sql
```

### 持久化数据备份

```bash
# 备份数据卷
kubectl cp media-renamer-pod:/app/data ./backup-data

# 恢复数据卷
kubectl cp ./backup-data media-renamer-pod:/app/data
```

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查数据库连接
   - 检查Redis连接
   - 查看应用日志

2. **性能问题**
   - 调整资源限制
   - 优化数据库查询
   - 启用缓存

3. **网络问题**
   - 检查网络策略
   - 验证服务发现
   - 检查防火墙规则

### 日志分析

```bash
# 查看应用日志
kubectl logs -n media-renamer deployment/media-renamer

# 查看数据库日志
kubectl logs -n media-renamer deployment/postgres

# 查看Redis日志
kubectl logs -n media-renamer deployment/redis
```

## 升级指南

### 版本升级

```bash
# 备份当前配置和数据
kubectl get configmap media-renamer-config -n media-renamer -o yaml > config-backup.yaml

# 升级Helm版本
helm upgrade media-renamer media-renamer/media-renamer --version 2.0.0

# 验证升级
kubectl rollout status deployment/media-renamer -n media-renamer
```

### 数据库迁移

```bash
# 执行数据库迁移
kubectl exec -n media-renamer media-renamer-pod -- python manage.py migrate
```

## 性能优化

### 资源优化

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1000m"
    memory: "1Gi"
```

### 缓存优化

```yaml
redis:
  enabled: true
  master:
    persistence:
      enabled: true
      size: 10Gi
```

### 数据库优化

```yaml
postgresql:
  postgresqlExtendedConf:
    shared_buffers: 256MB
    effective_cache_size: 1GB
    work_mem: 16MB
```

## 监控告警

### 关键指标告警

- CPU使用率 > 80%
- 内存使用率 > 85%
- 磁盘使用率 > 90%
- 数据库连接数 > 80%
- 响应时间 > 2秒

### 告警配置

```yaml
alerting:
  enabled: true
  rules:
    - alert: HighCPUUsage
      expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage detected"
        description: "CPU usage is above 80% for more than 5 minutes"
```

## 支持联系方式

- 项目文档：https://docs.media-renamer.com
- 问题反馈：https://github.com/media-renamer/issues
- 社区支持：https://discord.gg/media-renamer