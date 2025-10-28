# VabHub 新建仓库流程指南

## 概述

VabHub 采用多仓库架构，每个仓库都有特定的职能分工。本指南详细说明如何创建新的 VabHub 仓库。

## 仓库类型

| 类型 | 前缀模式 | 描述 | 示例 |
|------|----------|------|------|
| **核心模块** | `VabHub-{name}` | 核心功能模块 | `VabHub-Core`, `VabHub-Auth` |
| **前端模块** | `VabHub-{name}` | 前端界面模块 | `VabHub-Frontend`, `VabHub-Admin` |
| **插件模块** | `VabHub-{name}-Plugin` | 插件系统模块 | `VabHub-Image-Plugin`, `VabHub-Video-Plugin` |
| **部署模块** | `VabHub-{name}-Deploy` | 部署配置模块 | `VabHub-Deploy`, `VabHub-K8s-Deploy` |
| **资源模块** | `VabHub-{name}-Resources` | 资源文件模块 | `VabHub-Resources`, `VabHub-Theme-Resources` |
| **服务模块** | `VabHub-{name}-Service` | 微服务模块 | `VabHub-User-Service`, `VabHub-Media-Service` |
| **工具模块** | `VabHub-{name}-Tool` | 开发工具模块 | `VabHub-CLI-Tool`, `VabHub-Migration-Tool` |

## 快速开始

### 方法一：使用自动化工具（推荐）

```bash
# 进入脚本目录
cd f:\VabHub\scripts

# 创建新的核心模块
python vabhub_repo_creator.py auth --type core --description "VabHub 认证授权模块" --init-git

# 创建新的插件模块
python vabhub_repo_creator.py image --type plugin --description "VabHub 图片处理插件" --init-git

# 创建新的服务模块并推送到 GitHub
python vabhub_repo_creator.py user --type service --description "VabHub 用户服务" --init-git --create-github --public
```

### 方法二：手动创建流程

#### 1. 确定仓库类型和名称

```bash
# 检查现有仓库结构
ls f:\VabHub\

# 验证新仓库名称是否可用
python scripts/vabhub_repo_creator.py check-name --name mymodule --type core
```

#### 2. 创建仓库目录结构

```bash
# 创建仓库目录
mkdir f:\VabHub\VabHub-MyModule

# 创建标准目录结构
mkdir -p VabHub-MyModule/{src,tests,config,docs,scripts}
```

#### 3. 初始化 Git 仓库

```bash
cd f:\VabHub\VabHub-MyModule

git init
git add .
git commit -m "Initial commit: VabHub MyModule"
```

#### 4. 关联到 GitHub

```bash
# 在 GitHub 上创建新仓库（通过网页或 CLI）
gh repo create VabHub/VabHub-MyModule --public --description "VabHub MyModule"

# 添加远程仓库
git remote add origin https://github.com/VabHub/VabHub-MyModule.git

# 推送代码
git push -u origin main
```

## 详细流程

### 第一步：规划仓库

1. **确定职能**：明确新仓库在 VabHub 架构中的角色
2. **选择类型**：根据功能选择合适的仓库类型
3. **命名规范**：遵循命名约定，确保名称清晰易懂
4. **依赖分析**：确定与其他仓库的依赖关系

### 第二步：创建仓库结构

每个仓库应包含以下标准文件：

```
VabHub-{Name}/
├── README.md              # 项目说明文档
├── VERSION                # 版本文件
├── requirements.txt       # Python 依赖（如适用）
├── package.json          # Node.js 依赖（如适用）
├── src/                   # 源代码目录
│   ├── __init__.py       # Python 包初始化
│   └── core.py           # 核心功能实现
├── tests/                 # 测试代码
│   ├── __init__.py
│   └── test_core.py
├── config/               # 配置文件
│   └── config.yaml
├── docs/                 # 文档
├── scripts/              # 脚本文件
├── .gitignore            # Git 忽略规则
└── .github/workflows/    # GitHub Actions
    └── ci.yml
```

### 第三步：配置开发环境

#### Python 项目配置

```python
# setup.py 示例
from setuptools import setup, find_packages

setup(
    name="vabhub-mymodule",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # 依赖包
    ],
)
```

#### Node.js 项目配置

```json
{
  "name": "@vabhub/mymodule",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
```

### 第四步：设置版本管理

#### 版本文件 (VERSION)

```
0.1.0
```

#### 版本兼容性检查

```bash
# 检查与其他仓库的版本兼容性
python scripts/vabhub_version_manager.py check
```

### 第五步：配置持续集成

#### GitHub Actions 配置

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest
```

### 第六步：文档编写

#### README.md 模板

```markdown
# VabHub-{Name}

{描述}

## 功能特性

- 特性1
- 特性2

## 快速开始

### 安装

```bash
pip install vabhub-{name}
```

### 使用示例

```python
from vabhub_{name} import {Name}Core

core = {Name}Core()
result = core.hello()
print(result)
```

## API 文档

{详细API文档}
```

## 最佳实践

### 命名规范

1. **仓库名称**：使用帕斯卡命名法，如 `VabHub-UserService`
2. **包名称**：使用蛇形命名法，如 `vabhub_user_service`
3. **类名称**：使用帕斯卡命名法，如 `UserService`
4. **函数/方法**：使用蛇形命名法，如 `get_user_by_id`

### 代码规范

1. **Python**：遵循 PEP 8，使用类型注解
2. **JavaScript**：使用 ESLint，遵循 Airbnb 规范
3. **文档**：为所有公共 API 编写文档字符串
4. **测试**：测试覆盖率不低于 80%

### 依赖管理

1. **明确依赖**：在 `requirements.txt` 或 `package.json` 中明确声明
2. **版本锁定**：使用精确版本号，避免自动升级
3. **安全扫描**：定期进行依赖安全扫描

### 版本发布

1. **语义化版本**：遵循 `主版本.次版本.修订版本` 格式
2. **发布分支**：使用 `release/v1.0.0` 格式的分支
3. **变更日志**：维护 `CHANGELOG.md` 文件

## 常见问题

### Q: 如何确定新仓库的类型？
A: 根据功能职责选择：
- 核心业务逻辑 → 核心模块
- 用户界面 → 前端模块  
- 可扩展功能 → 插件模块
- 部署配置 → 部署模块

### Q: 新仓库应该放在哪个目录？
A: 所有 VabHub 仓库都应放在 `f:\VabHub\` 根目录下

### Q: 如何确保版本兼容性？
A: 使用版本管理器工具：
```bash
python scripts/vabhub_version_manager.py status
python scripts/vabhub_version_manager.py check
```

### Q: 新仓库需要哪些基本配置？
A: 至少需要：
- README.md
- VERSION 文件
- .gitignore
- 合适的许可证文件
- 基础测试框架

## 工具命令参考

### 仓库创建工具

```bash
# 查看帮助
python scripts/vabhub_repo_creator.py --help

# 验证仓库名称
python scripts/vabhub_repo_creator.py check-name --name auth --type core

# 创建完整仓库（包含Git初始化）
python scripts/vabhub_repo_creator.py media --type service --description "媒体处理服务" --init-git --create-github
```

### 版本管理工具

```bash
# 查看所有仓库版本状态
python scripts/vabhub_version_manager.py status

# 检查版本兼容性
python scripts/vabhub_version_manager.py check

# 递增版本号
python scripts/vabhub_version_manager.py bump --repo core --type minor

# 执行发布流程
python scripts/vabhub_version_manager.py release --type patch
```

## 后续步骤

1. **代码实现**：完成核心功能开发
2. **测试编写**：确保代码质量
3. **文档完善**：提供完整的使用文档
4. **集成测试**：验证与其他仓库的集成
5. **发布准备**：准备首次发布

## 支持与帮助

- 📖 查看现有仓库示例
- 🔧 使用提供的自动化工具
- 📚 参考 VabHub 开发文档
- 💬 在团队讨论中寻求帮助

---

*最后更新: 2025-10-27*