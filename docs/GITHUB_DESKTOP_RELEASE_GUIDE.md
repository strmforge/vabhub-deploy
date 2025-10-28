# GitHub Desktop 发布版本指南

## 📋 概述

本指南详细说明如何使用 GitHub Desktop 客户端为 VabHub 多仓库项目创建和管理发布版本。

## 🚀 准备工作

### 1. 安装 GitHub Desktop
- 下载地址：https://desktop.github.com/
- 安装并登录您的 GitHub 账户

### 2. 配置仓库
确保所有 VabHub 仓库都已添加到 GitHub Desktop：

| 仓库名称 | 本地路径 | GitHub 地址 |
|---------|---------|-------------|
| VabHub-Core | `f:\VabHub\VabHub-Core` | https://github.com/strmforge/vabhub-core |
| VabHub-Frontend | `f:\VabHub\VabHub-Frontend` | https://github.com/strmforge/vabhub-frontend |
| VabHub-Plugins | `f:\VabHub\VabHub-Plugins` | https://github.com/strmforge/vabhub-plugins |
| VabHub-Deploy | `f:\VabHub\VabHub-Deploy` | https://github.com/strmforge/vabhub-deploy |
| VabHub-Resources | `f:\VabHub\VabHub-Resources` | https://github.com/strmforge/vabhub-resources |

## 📦 发布流程

### 步骤 1: 检查当前状态

在发布前，确保所有仓库都处于干净状态：

```bash
# 检查所有仓库状态
cd "f:\VabHub"
python scripts\vabhub_release_manager.py status
```

### 步骤 2: 创建发布分支

使用 GitHub Desktop 为每个仓库创建发布分支：

1. **打开 GitHub Desktop**
2. **选择第一个仓库** (VabHub-Core)
3. **创建新分支**：
   - 点击当前分支名称
   - 输入分支名称：`v1.2.0`
   - 点击 "Create branch"
4. **重复以上步骤**为其他仓库创建分支

### 步骤 3: 提交版本变更

为每个仓库提交版本变更：

1. **切换到发布分支**
2. **检查变更文件**：
   - `setup.py` (Core, Plugins)
   - `package.json` (Frontend)
   - `VERSION` (Deploy, Resources)
   - `CHANGELOG.md` (所有仓库)
3. **提交变更**：
   - 填写提交信息：`Release v1.2.0`
   - 点击 "Commit to v1.2.0"

### 步骤 4: 推送分支到远程

推送所有发布分支到 GitHub：

1. **发布分支**：
   - 点击 "Publish branch"
   - 确保选中 "Push to origin"
2. **重复**为所有仓库执行此操作

### 步骤 5: 创建发布标签

为每个仓库创建发布标签：

#### 方法一：使用 GitHub Desktop

1. **切换到发布分支**
2. **创建标签**：
   - Repository → Create Tag
   - 标签名称：`v1.2.0`
   - 描述：`VabHub v1.2.0 Release`
3. **推送标签**：
   - Repository → Push Tags

#### 方法二：使用命令行

```bash
# 为每个仓库创建标签
cd "f:\VabHub\VabHub-Core"
git tag -a v1.2.0 -m "VabHub Core v1.2.0 Release"
git push origin v1.2.0

cd "f:\VabHub\VabHub-Frontend"
git tag -a v1.2.0 -m "VabHub Frontend v1.2.0 Release"
git push origin v1.2.0

# 重复其他仓库...
```

### 步骤 6: 创建 GitHub 发布版本

在 GitHub 网站上为每个仓库创建正式发布：

1. **访问仓库页面**：
   - https://github.com/strmforge/vabhub-core
   - https://github.com/strmforge/vabhub-frontend
   - https://github.com/strmforge/vabhub-plugins
   - https://github.com/strmforge/vabhub-deploy
   - https://github.com/strmforge/vabhub-resources

2. **创建发布**：
   - 点击右侧 "Releases"
   - 点击 "Create a new release"
   - 选择标签：`v1.2.0`
   - 标题：`VabHub v1.2.0`
   - 描述：复制对应仓库的 `RELEASE_v1.2.0.md` 内容
   - 勾选 "Set as latest release"
   - 点击 "Publish release"

### 步骤 7: 合并发布分支

发布完成后，将发布分支合并到 main 分支：

1. **创建 Pull Request**：
   - 在 GitHub 网站上创建 PR
   - 源分支：`v1.2.0`
   - 目标分支：`main`
   - 标题：`Release v1.2.0`

2. **合并 PR**：
   - 审核代码变更
   - 点击 "Merge pull request"
   - 删除发布分支（可选）

## 🔧 自动化脚本

### 使用发布管理器脚本

我们提供了自动化发布脚本：

```bash
# 检查版本状态
python scripts\vabhub_release_manager.py status

# 递增版本号
python scripts\vabhub_release_manager.py bump --repo core --type minor

# 执行完整发布流程
python scripts\vabhub_release_manager.py release --type minor
```

### 手动发布脚本

如果自动化脚本遇到问题，可以使用手动脚本：

```bash
# 运行手动发布脚本
cd "f:\VabHub"
.\scripts\manual_release.ps1
```

## 🐛 常见问题

### Q: 发布分支已存在怎么办？
A: 删除现有分支后重新创建：
```bash
git branch -D v1.2.0
git push origin --delete v1.2.0
```

### Q: 标签已存在怎么办？
A: 删除现有标签后重新创建：
```bash
git tag -d v1.2.0
git push origin --delete v1.2.0
```

### Q: 发布失败如何回滚？
A: 回滚到上一个版本：
```bash
git reset --hard HEAD~1
git push --force origin v1.2.0
```

### Q: 如何验证发布成功？
A: 检查以下内容：
- GitHub Releases 页面显示新版本
- 标签正确创建
- 发布说明完整
- 下载链接有效

## 📊 发布检查清单

### 发布前检查
- [ ] 所有版本文件已更新
- [ ] 更新日志已填写
- [ ] 代码已通过测试
- [ ] 文档已更新

### 发布时操作
- [ ] 创建发布分支
- [ ] 提交版本变更
- [ ] 创建发布标签
- [ ] 创建GitHub发布

### 发布后验证
- [ ] 验证下载链接
- [ ] 更新项目文档
- [ ] 通知团队成员
- [ ] 备份发布文件

## 🔗 相关资源

- [GitHub Desktop 文档](https://docs.github.com/en/desktop)
- [Git 标签管理](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)

---

**完成以上步骤后，VabHub v1.2.0 版本就成功发布了！**