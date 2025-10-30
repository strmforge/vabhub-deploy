# VabHub Deploy — One-Click Install

[![Release](https://img.shields.io/github/v/release/strmforge/vabhub-deploy?label=Release)](https://github.com/strmforge/vabhub-deploy/releases)
[![Bump Workflow](https://img.shields.io/github/actions/workflow/status/strmforge/vabhub-deploy/bump-versions.yml?branch=main&label=versions.json)](https://github.com/strmforge/vabhub-deploy/actions)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

分发主仓：包含 `docker-compose.yml` / Helm / 云函数模板，以及**唯一的兼容清单** `versions.json`。

## 快速开始（Compose）
```bash
# 1) 准备 .env（后端-only 密钥，示例见 Core/Docs）
# 2) 拉取镜像 & 启动
docker compose up -d
# 访问：前端 http://localhost:8090 ；后端 http://localhost:8080
```

## 版本兼容（versions.json）
本仓根目录的 `versions.json` 指定：
```json
{
  "release": "1.3.0",
  "core": "1.8.2",
  "frontend": "1.7.0",
  "plugins": {
    "115-open": "1.3.1",
    "123-open": "1.2.4"
  }
}
```
- **发版** = 更新 `versions.json` + 生成安装清单
- `bump-versions` 工作流会根据 Core/Frontend 最新 Release 自动 PR 更新

## 手动触发自动 Bump
在 Actions 里手点 `Run workflow` 即可；也支持 `repository_dispatch` 触发。

## License
MIT
