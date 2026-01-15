# 贡献指南

感谢您对 Anki Assistant 项目的关注！我们欢迎任何形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了 Bug 或有功能建议：

1. 检查 [Issues](https://github.com/yourusername/anki-assistant/issues) 是否已有相同问题
2. 如果没有，创建新的 Issue，使用相应的模板：
   - Bug 反馈
   - 功能建议
   - 使用问题

### 提交代码

#### 开发环境设置

1. Fork 项目仓库
2. Clone 您的 Fork：
   ```bash
   git clone https://github.com/yourusername/anki-assistant.git
   cd anki-assistant
   ```

3. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows

   pip install -r requirements.txt
   ```

4. 创建功能分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### 代码规范

- **Python 版本**: Python 3.8+
- **代码风格**: 遵循 PEP 8
- **命名规范**:
  - 类名: `PascalCase` (如 `AnkiCardEnhancer`)
  - 函数/变量: `snake_case` (如 `enhance_card`)
  - 常量: `UPPER_SNAKE_CASE` (如 `MAX_RETRIES`)
- **文档字符串**: 使用 Google 风格的 docstrings

```python
def enhance_card(front_text: str, back_text: str) -> Dict[str, str]:
    """
    增强单个 Anki 卡片

    Args:
        front_text: 卡片正面文本
        back_text: 卡片背面原始文本

    Returns:
        包含增强后卡片的字典，键为 'front' 和 'back'

    Raises:
        ValueError: 当输入文本为空时
    """
    pass
```

#### 提交流程

1. 确保代码通过测试
2. 提交代码：
   ```bash
   git add .
   git commit -m "feat: 添加新的 XXX Profile"
   ```

   提交信息格式：
   - `feat:` 新功能
   - `fix:` Bug 修复
   - `docs:` 文档更新
   - `refactor:` 代码重构
   - `test:` 测试相关
   - `chore:` 构建/工具相关

3. 推送到您的 Fork：
   ```bash
   git push origin feature/your-feature-name
   ```

4. 创建 Pull Request：
   - 填写 PR 描述模板
   - 等待代码审查

## 📋 开发指南

### 添加新的 Profile

在 `config/config.json` 中添加新的 Profile 配置：

```json
{
  "profiles": {
    "your_new_profile": {
      "name": "您的场景名称",
      "description": "场景描述",
      "system_prompt": "系统提示词",
      "user_prompt_template": "用户提示词模板，使用 {front_text} 和 {back_text} 占位符"
    }
  }
}
```

### 添加新的 AI 服务商

1. 在 `src/anki_enhancer.py` 中创建新的 Provider 类：

```python
class YourProvider(AIProvider):
    """您的 AI 服务商"""

    def __init__(self, config: Dict):
        super().__init__(config)
        # 初始化代码

    def generate_content(self, prompt: str, system_prompt: str = "") -> str:
        # 生成内容代码
        pass
```

2. 在 `create_ai_provider` 工厂方法中添加对应分支

3. 更新配置文件和文档

### 测试

- 添加新功能时，请在 `tests/` 目录添加相应测试
- 使用测试数据验证功能：
  ```bash
  python src/anki_enhancer.py -c config/config.json -i tests/test_data/test_v4_vocab.txt -o tests/test_output/output.txt
  ```

## 📝 文档贡献

- 代码变更需要同步更新相关文档
- 新功能请在 `README.md` 或 `docs/` 中添加说明
- 使用清晰简洁的中文描述

## 🎯 优先事项

当前特别欢迎以下方向的贡献：

- [ ] 更多内置 Profile（历史、地理、化学等）
- [ ] 单元测试覆盖
- [ ] 性能优化
- [ ] Web UI 界面
- [ ] 多语言支持
- [ ] Docker 部署支持

## 📧 联系方式

- Issues: [GitHub Issues](https://github.com/yourusername/anki-assistant/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/anki-assistant/discussions)

## 📄 行为准则

请尊重所有贡献者，保持友好和专业的交流。我们承诺提供友好的欢迎和包容的环境。

---

再次感谢您的贡献！🎉
