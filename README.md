# Anki Assistant - Anki 卡片AI增强工具

> 🚀 **强大的 Anki 卡片内容生成和增强系统** - 支持多种学习场景，完全配置驱动

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.0-orange)](CHANGELOG.md)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/anki-assistant)](https://github.com/yourusername/anki-assistant/issues)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/anki-assistant)](https://github.com/yourusername/anki-assistant)

## 📖 项目简介

Anki Assistant 是一个通用的 Anki 卡片内容生成和增强平台，利用 AI（LLM）技术帮助用户创建高质量的 Anki 学习卡片。

### 核心特性

✅ **多场景支持** - 内置6种学习场景配置，覆盖古文、词汇、代码、概念等
✅ **完全配置驱动** - 无需修改代码，通过 JSON 配置切换功能
✅ **两种工作模式**:
  - **生成模式 (v3.0)**: Front → LLM 生成完整卡片 (Front + Back + Note...)
  - **增强模式 (v4.0)**: Front + 原始Back → LLM 增强Back → Front + 增强Back
✅ **多AI服务商支持** - Gemini、七牛云 (DeepSeek) 等
✅ **断点续传** - 支持大批量处理，自动保存进度
✅ **多格式输入** - 支持 .txt、.csv、.xlsx 格式

## 🎯 适用场景

| 场景 | 描述 | Profile |
|------|------|---------|
| 古文词语解释 | 增强古文中的词语解释，添加出处、用法、例句 | `ancient_word_enhancement` |
| 古文理解 | 增强古文句子，添加翻译、注释、背景 | `ancient_text_explanation` |
| 词汇学习 | 补充英语词汇的释义、例句、词源、同义词 | `vocabulary_enhancement` |
| 句子翻译 | 增强翻译卡片，添加背景、文化解读 | `sentence_translation` |
| 代码理解 | 增强代码解释，添加复杂度分析、优化建议 | `code_explanation` |
| 概念深化 | 深化概念理解，添加定义、例子、应用 | `concept_deepening` |
| 问答增强 | 扩展问答答案，添加解析、相关知识 | `qa_enhancement` |

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 requirements.txt（推荐）
pip install -r requirements.txt

# 或手动安装
pip install pandas google-generativeai openai tqdm openpyxl
```

### 2. 配置系统

复制配置模板并填写 API 密钥：

```bash
cp config/config_v4.example.json config/config.json
```

编辑 `config/config.json`，填写你的 API KEY。

### 3. 运行增强

```bash
# 使用配置文件中的设置
python src/anki_enhancer.py -c config/config.json

# 列出所有可用场景
python src/anki_enhancer.py -c config/config.json --list-profiles

# 临时切换场景
python src/anki_enhancer.py -c config/config.json -p ancient_word_enhancement
```

### 4. 导入 Anki

1. 打开 Anki
2. 文件 → 导入
3. 选择生成的文件（位于 `data/output/` 目录）
4. 设置字段映射: Column 1 → Front, Column 2 → Back
5. 编码: UTF-8
6. 导入 ✨

## 📁 项目结构

```
anki-assistant/
├── README.md                   # 主文档（本文件）
├── .gitignore                  # Git 忽略文件
│
├── src/                        # 📦 源代码目录
│   ├── anki_enhancer.py        # v4.0 主程序（推荐使用）
│   ├── anki_llm_forge.py       # v3.0 多场景生成
│   ├── anki_process.py         # v2.0 基础版本
│   ├── anki_extractor.py       # Anki 卡包提取工具
│   └── clean_extracted_data.py # 数据清洗脚本
│
├── config/                     # ⚙️  配置文件目录
│   ├── config.json             # 当前使用配置（含 API Key）
│   ├── config_v4.example.json  # v4.0 配置模板（推荐）
│   ├── config_v3.example.json  # v3.0 配置模板
│   └── config_v2_backup.json   # v2.0 配置备份
│
├── docs/                       # 📚 文档目录
│   ├── README_v4.md            # v4.0 详细文档
│   ├── README_v3.md            # v3.0 详细文档
│   ├── 古文卡片完成说明.md      # 古文卡片使用指南
│   ├── ancient_words_processing_guide.md  # 古文处理技术文档
│   └── README_古文卡片增强.md   # 古文卡片快速指南
│
├── data/                       # 📊 数据目录
│   ├── input/                  # 输入数据
│   │   ├── extracted_120/      # 提取的原始数据
│   │   │   └── 提取结果.txt
│   │   └── raw/                # 其他原始数据
│   ├── cleaned/                # 清洗后的数据
│   │   ├── cleaned_ancient_words.txt
│   │   └── cleaned_ancient_words.csv
│   └── output/                 # AI 增强后的输出
│       └── ancient_words_793_enhanced.txt  # 783张古文词语卡片
│
├── tests/                      # 🧪 测试目录
│   ├── test_data/              # 测试数据
│   │   ├── test_v4_vocab.txt    # 词汇测试数据
│   │   ├── test_v4_ancient.txt  # 古文测试数据
│   │   ├── test_v4_code.txt     # 代码测试数据
│   │   └── test_v4_concept.txt  # 概念测试数据
│   └── test_output/            # 测试输出
│
├── archive/                    # 📦 归档目录（旧版本临时文件）
└── logs/                       # 📝 日志目录
    ├── anki_process.log        # 运行日志
    └── progress_cache.csv      # 进度缓存（支持断点续传）
```

## 🎓 版本选择指南

### v4.0 - Anki Enhancer (推荐) ⭐

**定位**: 基于已有内容进行增强

**特点**:
- ✅ 简化的两列结构 (Front + Enhanced Back)
- ✅ 纯文本输出，无 JSON 解析错误
- ✅ 保留用户原始思考，AI 补充完善
- ✅ 更高的可靠性和稳定性

**适用场景**:
- 你已经有基础笔记，需要补充完善
- 需要高质量、可靠的内容增强
- 重视原始内容的保留

**使用**: `python src/anki_enhancer.py`

**文档**: [docs/README_v4.md](docs/README_v4.md)

### v3.0 - Anki LLM Forge

**定位**: 从零生成完整卡片

**特点**:
- ✅ 动态多列输出
- ✅ 支持复杂场景
- ✅ 灵活的字段映射

**适用场景**:
- 从零开始生成卡片
- 需要多字段输出
- 复杂的学习场景

**使用**: `python src/anki_llm_forge.py`

**文档**: [docs/README_v3.md](docs/README_v3.md)

## 💡 典型使用案例

### 案例1: 古文词语卡片增强（已完成）

**成果**: 783张高质量古文词语卡片

**输入**: 从 Anki 卡包提取的古文句子和简单释义
**输出**: 包含词语、句子、详细释义、出处、词性用法、例句、记忆要点的完整卡片

**详细文档**: [docs/古文卡片完成说明.md](docs/古文卡片完成说明.md)

**输出文件**: `data/output/ancient_words_793_enhanced.txt`

### 案例2: 英语词汇学习

**需求**: 创建雅思词汇学习卡片

**数据**:
```
ephemeral	lasting for a very short time
serene	calm and peaceful
```

**命令**:
```bash
python src/anki_enhancer.py \
  -p vocabulary_enhancement \
  -i data/input/raw/vocab.txt \
  -o data/output/vocab_cards.txt
```

## 📚 详细文档

- **v4.0 使用说明**: [docs/README_v4.md](docs/README_v4.md)
- **v3.0 使用说明**: [docs/README_v3.md](docs/README_v3.md)
- **古文卡片指南**: [docs/古文卡片完成说明.md](docs/古文卡片完成说明.md)
- **技术文档**: [docs/ancient_words_processing_guide.md](docs/ancient_words_processing_guide.md)

## 🔄 版本历史

详见 [CHANGELOG.md](CHANGELOG.md)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

- 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南
- 提交 [Issue](https://github.com/yourusername/anki-assistant/issues) 报告问题
- 创建 [Pull Request](https://github.com/yourusername/anki-assistant/pulls) 贡献代码

## ⭐ Star History

如果这个项目对你有帮助，请给我们一个 Star！

## 📮 联系方式

- Issues: [GitHub Issues](https://github.com/yourusername/anki-assistant/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/anki-assistant/discussions)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢所有为本项目做出贡献的开发者
- 感谢 Anki 社区提供的优秀学习工具
- 感谢各 AI 服务商提供的 API 支持

---

**🚀 让 Anki 学习更高效！**

*最后更新: 2026-01-15*
