# GitHub 发布检查清单

## ✅ 已完成项目

- [x] **LICENSE** - 添加 MIT License
- [x] **requirements.txt** - 添加 Python 依赖列表
- [x] **CONTRIBUTING.md** - 添加贡献指南
- [x] **README.md** - 完善项目说明文档
- [x] **.gitignore** - 完善 Git 忽略规则
- [x] **.github 模板** - 添加 Issue 和 PR 模板

## 📋 发布前检查

### 1. 更新仓库信息

- [ ] 将 README.md 中的 `yourusername` 替换为实际的 GitHub 用户名
- [ ] 将 CONTRIBUTING.md 中的 `yourusername` 替换为实际的 GitHub 用户名
- [ ] 更新仓库的 Description 和 Topics
- [ ] 设置仓库的可见性（Public/Private）

### 2. 配置仓库设置

在 GitHub 仓库设置中：

- [ ] **Features**:
  - [ ] Enable Issues
  - [ ] Enable Projects
  - [ ] Enable Discussions
  - [ ] Enable Wikis（可选）

- [ ] **Branches**:
  - [ ] 设置 main/master 为默认分支
  - [ ] 启用分支保护规则（推荐）
  - [ ] 配置 Pull Request 审查规则

- [ ] **Labels**: 设置 Issue 标签颜色
  - `bug`: 红色
  - `enhancement`: 蓝色
  - `question`: 绿色
  - `documentation`: 紫色
  - `good first issue`: 粉色

### 3. 初始 Commit

- [ ] 清理不必要的文件
- [ ] 确保没有敏感信息被提交
- [ ] 创建初始 commit
- [ ] 推送到 GitHub

### 4. 发布 Release

在 GitHub Releases 页面：

- [ ] 创建 v4.0.0 Release
- [ ] 填写 Release Notes（可参考 CHANGELOG.md）
- [ ] 上传示例文件（可选）

### 5. 文档完善

- [ ] 确保所有文档链接正确
- [ ] 检查代码示例是否可运行
- [ ] 更新版本号和日期
- [ ] 添加项目 Logo（可选）

### 6. 社区准备

- [ ] 在 GitHub 上添加 Topics 标签：
  - `anki`
  - `ai`
  - `llm`
  - `flashcards`
  - `learning`
  - `education`
  - `python`
  - `gemini`
  - `deepseek`

- [ ] 准备一条发布推文/社交媒体帖子
- [ ] 考虑在相关社区分享（Anki 论坛、Reddit 等）

## 📝 README.md 中的占位符

请搜索并替换以下内容：

```markdown
yourusername/anki-assistant
```

替换为您的实际 GitHub 用户名和仓库名。

## 🔐 安全检查

- [ ] 确认 `config.json` 在 .gitignore 中
- [ ] 确认没有 API Key 被提交
- [ ] 确认日志文件不会被提交
- [ ] 确认缓存文件不会被提交
- [ ] 检查代码中是否有硬编码的密钥

## 📊 项目统计

提交前可以运行以下命令检查项目状态：

```bash
# 检查文件结构
ls -R

# 检查 Git 状态
git status

# 检查将要提交的文件
git ls-files

# 检查是否有大文件
find . -size +1M -not -path "./venv/*" -not -path "./.git/*"
```

## 🎉 发布后

- [ ] 在社区分享项目
- [ ] 监控 Issues 和 PRs
- [ ] 收集用户反馈
- [ ] 根据反馈改进项目

---

**祝发布顺利！🚀**
