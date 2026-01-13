# Anki-LLM-Forge: 通用型 Anki 卡片增强工具

> **从单一工具到通用平台** - 一个配置驱动的、支持多场景的 Anki 卡片内容生成系统

## 🎯 项目定位

Anki-LLM-Forge 不再是单一用途的翻译工具，而是一个**通用的 Anki 卡片内容增强平台**。

**核心理念**:
```
原始数据 (Raw Data) + Prompt模板 (Profile) + LLM → 增强的完整卡片 (Enriched Card)
```

通过修改配置文件，无需改代码即可支持**任意学习场景**！

## ✨ 核心特性

### 1. **多场景支持 (Profiles)**
- ✅ **古文学习**: 翻译、出处、背景
- ✅ **英语句子**: 翻译、文化背景
- ✅ **英语词汇**: 音标、例句、同义词
- ✅ **编程代码**: 算法分析、时间复杂度
- ✅ **法律法条**: 法理、案例
- 🚀 **无限扩展**: 自定义你的 Profile

### 2. **完全配置驱动**
- 无需修改代码，通过 JSON 配置切换功能
- 每个场景独立的 Prompt 模板
- 动态字段映射系统

### 3. **架构优势**
- **面向对象设计**: 清晰的类结构，易于维护
- **Profile 系统**: 管理多个任务场景
- **Provider 抽象**: 统一的 AI 服务商接口
- **灵活扩展**: 轻松添加新的 Profile 或 Provider

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas google-generativeai openai tqdm openpyxl
```

### 2. 配置系统

复制配置模板：
```bash
copy config_v3.example.json config.json
```

编辑 `config.json`，填写你的 API KEY：
```json
{
  "global_settings": {
    "provider": "qiniu",  // 或 "gemini"
    "active_profile": "english_sentences",  // 选择你要使用的场景
    "input_file": "input.txt",
    "output_file": "anki_cards.txt"
  },
  "providers": {
    "qiniu": {
      "api_key": "你的七牛云_API_KEY"
    }
  }
}
```

### 3. 使用

**查看所有可用的场景**:
```bash
python anki_llm_forge.py --list-profiles
```

**使用指定场景生成卡片**:
```bash
# 使用配置文件中指定的场景
python anki_llm_forge.py

# 临时切换到其他场景
python anki_llm_forge.py -p ancient_chinese

# 指定输入输出文件
python anki_llm_forge.py -p english_vocab -i words.txt -o vocab_cards.txt
```

## 📖 内置场景 (Profiles)

### 1. `english_sentences` - 英语句子翻译

**用途**: 英语名言、电影台词翻译

**输出字段**: Front, Back, Note

**示例输入**:
```
To be, or not to be, that is the question.
```

**示例输出**:
- Front: To be, or not to be, that is the question.
- Back: 生存还是毁灭，这是一个问题。
- Note: 作者: Shakespeare <br> 出处: 《哈姆雷特》

### 2. `ancient_chinese` - 古文学习

**用途**: 古汉语、文言文学习

**输出字段**: Front, Translation, Source, Background

**示例输入**:
```
学而时习之，不亦说乎
```

**示例输出**:
- Front: 学而时习之，不亦说乎
- Translation: 学习并经常复习，不也是很快乐的吗？
- Source: 《论语·学而》
- Background: 孔子关于学习态度的名言...

### 3. `english_vocab` - 英语词汇

**用途**: 雅思/托福词汇学习

**输出字段**: Word, Definition, Pronunciation, Example, Synonyms, Word Family

**示例输入**:
```
ephemeral
```

**示例输出**:
- Word: ephemeral
- Definition: lasting for a very short time
- Pronunciation: /əˈfemərəl/
- Example: Fashion trends are often ephemeral.
- Synonyms: transient, fleeting, short-lived
- Word Family: ephemerally (adverb), ephemerality (noun)

### 4. `programming` - 编程代码

**用途**: 算法学习、代码分析

**输出字段**: Code, Explanation, Time, Space, Usage, Improvements

**示例输入**:
```python
def binary_search(arr, target):
    # ...
```

**示例输出**:
- Code: [原始代码]
- Explanation: 这是一个二分查找算法...
- Time: O(log n)
- Space: O(1)
- Usage: 用于在有序数组中快速查找...
- Improvements: 可以添加输入验证...

### 5. `law` - 法律条文

**用途**: 法律学习、法条理解

**输出字段**: Article, Interpretation, Application, Cases, Key Points

## 🔧 自定义 Profile

创建你自己的学习场景只需3步：

### 步骤1: 定义 Profile

在 `config.json` 的 `profiles` 部分添加：

```json
{
  "profiles": {
    "my_custom_profile": {
      "description": "我的自定义学习场景",
      "system_prompt": "你是一个...专家",
      "user_prompt_template": "请分析：\"{front_text}\"\n\n返回 JSON 格式，包含：field1, field2, field3",
      "output_fields": ["field1", "field2", "field3"],
      "anki_fields": ["Front", "Field1", "Field2", "Field3"],
      "field_mapping": {
        "front_text": "Front",
        "field1": "Field1",
        "field2": "Field2",
        "field3": "Field3"
      }
    }
  }
}
```

### 步骤2: 切换并使用

```bash
python anki_llm_forge.py -p my_custom_profile -i your_data.txt
```

### 步骤3: 导入 Anki

打开 Anki → 文件 → 导入 → 选择生成的文件

## 📋 配置文件详解

### 全局设置 (`global_settings`)

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `provider` | AI 服务商 (gemini/qiniu) | `"gemini"` |
| `active_profile` | 当前激活的场景 | 必填 |
| `input_file` | 输入文件路径 | 必填 |
| `output_file` | 输出文件路径 | `"anki_cards.txt"` |
| `cache_file` | 缓存文件路径 | `"progress_cache.csv"` |
| `request_delay` | API 请求间隔（秒） | `1.0` |
| `max_retries` | 失败重试次数 | `3` |
| `save_interval` | 进度保存间隔 | `10` |

### Profile 配置

每个 Profile 包含：

- **`description`**: 场景描述
- **`system_prompt`**: 系统提示词（设定 AI 角色）
- **`user_prompt_template`**: 用户提示词模板
  - 使用 `{front_text}` 作为占位符
- **`output_fields`**: LLM 返回的 JSON 字段列表
- **`anki_fields`**: Anki 卡片的列名列表
- **`field_mapping`**: 字段映射关系
  - Key: LLM 返回字段
  - Value: Anki 列名

## 🏗️ 架构设计

### 核心类

1. **`AIProvider`**: AI 服务商抽象基类
   - `GeminiProvider`: Google Gemini 实现
   - `QiniuProvider`: 七牛云 AI 实现

2. **`Profile`**: 场景配置类
   - 管理单个场景的配置
   - 验证配置完整性
   - 格式化提示词

3. **`ProfileManager`**: 场景管理器
   - 管理多个 Profile
   - 获取指定 Profile
   - 列出所有可用 Profile

4. **`AnkiCardGenerator`**: 核心生成器
   - 加载配置
   - 生成卡片
   - 管理缓存
   - 导出结果

### 设计优势

- **开闭原则**: 对扩展开放，对修改关闭
- **单一职责**: 每个类职责明确
- **依赖注入**: Provider 通过工厂方法注入
- **配置驱动**: 行为由配置文件决定

## 🔄 版本对比

### v2.0 (旧版)
- ❌ 硬编码字段 (translate, meta_info)
- ❌ 单一场景
- ❌ 修改功能需要改代码

### v3.0 (Anki-LLM-Forge)
- ✅ 动态字段映射
- ✅ 多场景支持 (无限扩展)
- ✅ 完全配置驱动
- ✅ 面向对象架构
- ✅ Profile 管理系统

## 📊 测试结果

所有内置场景已测试通过：

- ✅ `english_sentences`: 古文测试成功 (4条)
- ✅ `ancient_chinese`: 古文测试成功 (4条)
- ✅ `programming`: 代码测试成功 (11条，9条成功，2条JSON错误)

## 💡 使用建议

### 1. 选择合适的场景

```bash
# 先查看所有可用场景
python anki_llm_forge.py --list-profiles

# 选择最适合你数据的场景
python anki_llm_forge.py -p ancient_chinese -i ancient_poems.txt
```

### 2. 优化 Prompt

如果 AI 输出不符合预期：
1. 修改对应 Profile 的 `user_prompt_template`
2. 添加更具体的指令
3. 提供输出示例

### 3. 处理 JSON 解析错误

某些输入（如代码、复杂文本）可能导致 JSON 解析失败：
- 程序会自动标记为 `[字段错误]`
- 可以查看日志定位问题
- 可以手动编辑生成的输出文件

### 4. 批量处理

对于大量数据：
- 设置较小的 `save_interval` (如 5)
- 启用断点续传功能
- 分批处理，每批 50-100 条

## 🐛 常见问题

### Q: 如何添加新的 AI 服务商？
A: 继承 `AIProvider` 类，实现 `generate_content()` 方法，在 `create_ai_provider()` 中添加分支。

### Q: 如何自定义字段映射？
A: 修改 Profile 的 `field_mapping`，将 LLM 返回字段映射到 Anki 列名。

### Q: 缓存文件如何管理？
A: 使用 `--clear-cache` 清除缓存，或手动删除 `progress_cache.csv`。

### Q: 导入 Anki 后显示乱码？
A: 确保 Anki 导入时选择了 UTF-8 编码。

### Q: 不同场景间切换？
A: 使用 `-p` 参数或修改配置文件中的 `active_profile`。

## 📦 项目文件

```
anki-assistant/
├── anki_llm_forge.py         # 主程序 (v3.0 新架构)
├── anki_process.py           # 旧版本 (v2.0，保留兼容)
├── config_v3.example.json     # v3.0 配置模板
├── config.json               # 实际配置文件
├── test_data_ancient.txt     # 古文测试数据
├── test_data_vocab.txt       # 词汇测试数据
├── test_data_code.txt        # 代码测试数据
└── README_v3.md              # 本文档
```

## 🎓 学习资源

- **Profile 设计**: 如何编写有效的 Prompt 模板
- **字段映射**: 理解 LLM 输出与 Anki 字段的对应关系
- **Anki 导入**: Tab 分隔文件导入指南

## 🚀 未来计划

- [ ] Web UI 界面
- [ ] Profile 共享市场
- [ ] 更多内置 Profile
- [ ] 支持批量文件处理
- [ ] AI 输出质量评分

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 PR 和 Issue！

**项目重构完成！** ✨

从单一工具到通用平台，Anki-LLM-Forge 让 Anki 卡片制作变得前所未有的灵活。
