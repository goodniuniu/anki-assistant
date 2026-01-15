# 快速开始指南

本指南将帮助您在 5 分钟内开始使用 Anki Assistant。

## 前提条件

- Python 3.8 或更高版本
- Anki 桌面应用程序（用于导入生成的卡片）
- 一个 AI 服务商的 API Key：
  - Google Gemini（[获取 API Key](https://ai.google.dev/)）
  - 或七牛云 AI DeepSeek（[获取 API Key](https://www.qiniu.com/)）

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone https://github.com/yourusername/anki-assistant.git
cd anki-assistant
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key

```bash
# 复制配置模板
cp config/config_v4.example.json config/config.json

# 编辑配置文件，填写您的 API Key
# Windows: notepad config/config.json
# macOS/Linux: nano config/config.json
```

配置文件示例：

```json
{
  "provider": "gemini",
  "gemini": {
    "api_key": "您的_Gemini_API_Key",
    "model": "gemini-pro"
  }
}
```

或使用七牛云：

```json
{
  "provider": "qiniu",
  "qiniu": {
    "api_key": "您的_七牛云_API_Key",
    "base_url": "https://ai.qiniuapi.com/v1",
    "model": "deepseek-chat"
  }
}
```

## 使用示例

### 示例 1：增强古文词语卡片

创建输入文件 `ancient_words.txt`：

```
秦爱纷奢，人亦念其家	喜欢，爱好
师道之不传也久矣	从师学习的风尚
```

运行增强：

```bash
python src/anki_enhancer.py \
  -c config/config.json \
  -p ancient_word_enhancement \
  -i ancient_words.txt \
  -o enhanced_ancient_words.txt
```

### 示例 2：增强英语词汇卡片

创建输入文件 `vocab.txt`：

```
ephemeral	lasting for a very short time
serene	calm and peaceful
```

运行增强：

```bash
python src/anki_enhancer.py \
  -c config/config.json \
  -p vocabulary_enhancement \
  -i vocab.txt \
  -o enhanced_vocab.txt
```

## 导入到 Anki

1. 打开 Anki 桌面应用程序
2. 点击 `文件` → `导入`
3. 选择生成的文件（如 `enhanced_ancient_words.txt`）
4. 设置导入选项：
   - 字段映射: Column 1 → Front, Column 2 → Back
   - 编码: UTF-8
5. 点击 `导入`

## 查看所有可用场景

```bash
python src/anki_enhancer.py -c config/config.json --list-profiles
```

## 常见问题

### Q: 提示 "API Key 无效"

A: 请检查：
- API Key 是否正确复制
- 是否选择了正确的 provider
- API Key 是否有足够的额度

### Q: 处理速度很慢

A: 这是正常的，因为需要调用 AI API。一张卡片大约需要 8-10 秒。

### Q: 中断后如何继续？

A: 程序会自动保存进度，重新运行相同的命令即可继续。

### Q: 支持哪些输入格式？

A: 支持 .txt、.csv、.xlsx 格式。默认使用 Tab 分隔的两列格式（Front 和 Back）。

## 下一步

- 阅读 [README.md](README.md) 了解所有功能
- 查看 [docs/README_v4.md](docs/README_v4.md) 了解详细文档
- 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何贡献代码

## 获取帮助

- 提交 [Issue](https://github.com/yourusername/anki-assistant/issues)
- 查看 [文档](docs/)
- 加入 [Discussions](https://github.com/yourusername/anki-assistant/discussions)

---

**开始享受高效的 Anki 学习之旅吧！🚀**
