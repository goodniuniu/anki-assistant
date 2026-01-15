# Anki Enhancer v4.0: 简化的卡片增强工具

> **从生成到增强** - 基于已有内容进行补充、完善、扩展

## 🎯 核心定位转变

### v3.0 vs v4.0 对比

**v3.0 (Anki-LLM-Forge)**:
```
Front (单一输入) → LLM生成完整卡片 → Front + Back + Note + ...
```

**v4.0 (Anki Enhancer)**:
```
Front + 原始Back (已有内容) → LLM增强Back → Front + 增强Back
```

### 核心理念

v4.0 的定位更加简洁和实用：
- **输入**: 你已经有了一些学习笔记（Front + Back）
- **增强**: LLM 阅读你的笔记，补充缺失的信息
- **输出**: 同样的两列格式，但背面内容更加丰富完整

### 为什么选择增强模式？

1. **保留你的原始思考**: 不会完全替换你的笔记，而是补充和完善
2. **减少幻觉风险**: LLM 基于已有内容扩展，不是从零生成
3. **更符合Anki结构**: 简单的两列格式，兼容所有Anki卡片类型
4. **更容易质量控制**: 你提供基础内容，LLM负责填充细节

## ✨ v4.0 特性

### 1. 简化的两列结构

**输入格式** (Tab分隔):
```
Front (正面)	Back (背面原始内容)
```

**输出格式** (Tab分隔):
```
Front (正面)	Enhanced Back (增强后的背面)
```

### 2. 6个内置增强场景

| Profile | 描述 | 适用场景 |
|---------|------|----------|
| `vocabulary_enhancement` | 词汇笔记增强 | 补充释义、例句、词源、同义词等 |
| `sentence_translation` | 句子翻译增强 | 添加背景、文化解读、语法要点 |
| `code_explanation` | 代码理解增强 | 添加详细解释、复杂度分析、优化建议 |
| `ancient_text_explanation` | 古文理解增强 | 添加注释、翻译、历史背景 |
| `concept_deepening` | 概念理解深化 | 添加定义、例子、对比、应用场景 |
| `qa_enhancement` | 问答卡片增强 | 扩展答案、添加解析、补充相关知识 |

### 3. 纯文本输出

- 不再使用 JSON 格式
- 避免了 JSON 解析错误
- LLM 直接输出增强后的文本内容
- 更稳定、更可靠

### 4. 完全配置驱动

- 6 个 Profile 可通过配置文件切换
- 无需修改代码即可调整增强策略
- 支持自定义 Profile

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas google-generativeai openai tqdm openpyxl
```

### 2. 配置系统

复制配置模板并填写API密钥：

```bash
cp config_v4.example.json config.json
```

编辑 `config.json`，填写你的 API KEY：

```json
{
  "global_settings": {
    "provider": "qiniu",  // 或 "gemini"
    "active_profile": "vocabulary_enhancement",  // 选择增强场景
    "input_file": "input.txt",
    "output_file": "anki_enhanced.txt"
  },
  "providers": {
    "qiniu": {
      "api_key": "你的七牛云_API_KEY"  // 填写实际密钥
    }
  }
}
```

### 3. 准备输入数据

创建一个 Tab 分隔的文本文件（如 `input.txt`）：

**示例 - 词汇增强**:
```
ephemeral	lasting for a very short time
serene	calm and peaceful
ubiquitous	very common and found everywhere
```

**示例 - 古文增强**:
```
学而时习之，不亦说乎	学习并且时常温习，不也很愉快吗
温故而知新，可以为师矣	温习旧知识从而获得新的理解和体会，就可以当老师了
```

### 4. 运行增强

**使用配置文件中指定的场景**:
```bash
python anki_enhancer.py
```

**临时切换场景**:
```bash
# 使用词汇增强
python anki_enhancer.py -p vocabulary_enhancement -i words.txt -o enhanced_words.txt

# 使用古文增强
python anki_enhancer.py -p ancient_text_explanation -i ancient.txt -o enhanced_ancient.txt

# 使用代码增强
python anki_enhancer.py -p code_explanation -i code.txt -o enhanced_code.txt
```

**列出所有可用场景**:
```bash
python anki_enhancer.py --list-profiles
```

**清除缓存重新生成**:
```bash
python anki_enhancer.py --clear-cache
```

### 5. 导入 Anki

1. 打开 Anki
2. 文件 → 导入
3. 选择生成的文件（如 `anki_enhanced.txt`）
4. 选择合适的模型类型
5. 确保字段映射为: Front → Front, Enhanced Back → Back

## 📖 增强场景详解

### 1. vocabulary_enhancement - 词汇增强

**输入示例**:
```
ephemeral	lasting for a very short time
```

**增强后输出**:
```
ephemeral

【释义】
lasting for a very short time

【例句】
- Fashion trends are often ephemeral.
- The ephemeral beauty of cherry blossoms...

【词源】
From Greek "ephēmeros" meaning "lasting only one day"

【同义词】
transient, fleeting, short-lived, brief

【反义词】
permanent, lasting, enduring

【记忆技巧】
联想 "e-" (out) + "hemera" (day) → 一天就消逝的 → 短暂的
```

**增强内容**:
- 准确释义（如果原始释义不够详细）
- 实用例句
- 词源、词根词缀
- 同义词、反义词
- 记忆技巧
- 使用场景

### 2. ancient_text_explanation - 古文增强

**输入示例**:
```
学而时习之，不亦说乎	学习并且时常温习，不也很愉快吗
```

**增强后输出**:
```
【原文】
学而时习之，不亦说乎

【现代翻译】
学习并经常复习，不也是很快乐的吗？

【注释】
- 而：并且，连词
- 时：按时，时常
- 习：复习，练习
- 说（yuè）：通"悦"，高兴、快乐

【出处】
《论语·学而第一》

【背景解读】
这句话是孔子关于学习态度的名言，体现了儒家"学以致用"的教育理念...

【记忆提示】
- 相关名句："温故而知新"
- 核心思想：学习的快乐在于复习和实践
```

**增强内容**:
- 准确的现代翻译（改进原始翻译）
- 逐词注释
- 出处信息
- 历史背景和文化内涵
- 记忆技巧和相关名句

### 3. code_explanation - 代码增强

**输入示例**:
```
def binary_search(arr, target):
    # ... 代码 ...
	二分查找算法，用于在有序数组中快速查找目标值
```

**增强后输出**:
```
【代码说明】
这是一个二分查找算法实现...

【关键概念】
- 分治策略：每次将搜索范围减半
- 有序数组前提：要求数组必须预先排序

【复杂度分析】
- 时间复杂度: O(log n)
- 空间复杂度: O(1)

【使用场景】
- 在大型有序数据集中查找
- 游戏中的排行榜查询
- 字典查找优化

【改进建议】
- 添加输入验证
- 处理重复元素的情况
- 返回找到元素的索引

【相关代码】
- 线性查找: O(n)
- 插值查找
- 斐波那契查找
```

### 4. concept_deepening - 概念深化

**输入示例**:
```
Recursion	函数调用自身来解决问题的编程技巧
```

**增强后输出**:
```
【定义】
递归是一种编程技巧，函数直接或间接调用自身来解决问题。

【核心要点】
- 基准情况（Base Case）：终止递归的条件
- 递归步骤（Recursive Step）：将问题分解为更小的子问题
- 调用栈：每次递归调用都会在栈上创建新的栈帧

【具体例子】
1. 计算阶乘: n! = n * (n-1)!
2. 斐波那契数列
3. 二叉树遍历

【对比区分】
- vs 迭代：递归更简洁但可能有栈溢出风险
- vs 分治：递归是分治的一种实现方式

【实际应用】
- 树和图的遍历
- 分治算法（归并排序、快速排序）
- 回溯算法
- 动态规划

【延伸思考】
- 尾递归优化是什么？
- 如何避免递归导致的栈溢出？
```

### 5. sentence_translation - 句子翻译增强

**输入示例**:
```
To be, or not to be, that is the question.	生存还是毁灭，这是一个问题
```

**增强后输出**:
```
【翻译】
生存还是毁灭，这是一个问题。

【背景与解读】
- 作者: William Shakespeare (威廉·莎士比亚)
- 出处: 《哈姆雷特》第三幕第一场
- 背景: 哈姆雷特的独白，探讨生与死的哲学问题
- 含义: 面对人生困境时的挣扎和思考

【记忆要点】
- 这是最著名的英语台词之一
- 反映了文艺复兴时期的人文主义思想
- "to be" = "存在" = "活着"
- 常用于表达人生抉择时的矛盾心理

【文化影响】
- 成为英语文学的经典语句
- 被无数次引用、改编和模仿
- 体现了存在主义哲学的早期思考
```

### 6. qa_enhancement - 问答增强

**输入示例**:
```
什么是二分查找？
	在有序数组中通过比较中间元素来查找目标值
```

**增强后输出**:
```
【答案要点】
二分查找是一种在有序数组中查找特定元素的高效算法，通过反复将搜索范围减半来快速定位目标值。

【详细解析】
1. 初始状态：整个数组都是搜索范围
2. 每次迭代：检查中间元素
   - 如果等于目标值，返回索引
   - 如果目标值小于中间值，搜索左半部分
   - 如果目标值大于中间值，搜索右半部分
3. 终止条件：找到目标值或搜索范围为空

【举例说明】
在数组 [1, 3, 5, 7, 9, 11, 13] 中查找 7：
- 第1次: mid=3, arr[3]=7 → 找到！

【常见误区】
- 忘记检查数组是否已排序
- 循环条件写成 `left < right` 而不是 `left <= right`
- 计算mid时使用 `(left + right) // 2` 可能溢出（在大数组中）

【相关知识】
- 前置知识：数组、循环、条件判断
- 相关算法：线性查找 O(n)、插值查找
- 数据结构：有序数组、二叉搜索树

【思考拓展】
- 如何用递归实现二分查找？
- 如果数组中有重复元素，应该返回哪个索引？
- 如何在二维矩阵中进行二分查找？
```

## 🔧 自定义 Profile

创建自己的增强场景非常简单：

### 步骤 1: 编辑配置文件

在 `config.json` 的 `profiles` 部分添加新配置：

```json
{
  "profiles": {
    "my_custom_profile": {
      "description": "我的自定义增强场景",
      "system_prompt": "你是一个...专家。",
      "user_prompt_template": "请阅读并增强以下卡片：\n\n【正面】:\n{front_text}\n\n【背面原始内容】:\n{back_text}\n\n请基于原始内容进行增强，添加...\n\n请直接输出增强后的完整背面内容（纯文本，不要JSON，不要markdown代码块）。",
      "output_format": "text",
      "input_fields": ["front_text", "back_text"],
      "output_fields": ["front_text", "enhanced_back"]
    }
  }
}
```

### 步骤 2: 使用自定义 Profile

```bash
python anki_enhancer.py -p my_custom_profile -i input.txt -o output.txt
```

## 📋 配置文件详解

### global_settings - 全局设置

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `provider` | AI 服务商 (gemini/qiniu) | `"qiniu"` |
| `active_profile` | 当前激活的增强场景 | 必填 |
| `input_file` | 输入文件路径 | 必填 |
| `output_file` | 输出文件路径 | `"anki_enhanced.txt"` |
| `cache_file` | 缓存文件路径 | `"progress_cache.csv"` |
| `log_file` | 日志文件路径 | `"anki_process.log"` |
| `request_delay` | API 请求间隔（秒） | `1.0` |
| `max_retries` | 失败重试次数 | `3` |
| `save_interval` | 进度保存间隔 | `10` |
| `input_encoding` | 输入文件编码 | `"utf-8"` |
| `output_encoding` | 输出文件编码 | `"utf-8"` |

### Profile 配置

每个 Profile 包含：

- **`description`**: 场景描述
- **`system_prompt`**: 系统提示词（设定 AI 角色）
- **`user_prompt_template`**: 用户提示词模板
  - 使用 `{front_text}` 占位符表示正面内容
  - 使用 `{back_text}` 占位符表示背面原始内容
- **`output_format`**: 输出格式（固定为 "text"）
- **`input_fields`**: 输入字段（固定为 ["front_text", "back_text"]）
- **`output_fields`**: 输出字段（固定为 ["front_text", "enhanced_back"]）

## 🏗️ 架构设计

### 核心类

1. **`AIProvider`**: AI 服务商抽象基类
   - `GeminiProvider`: Google Gemini 实现
   - `QiniuProvider`: 七牛云 AI 实现（DeepSeek）

2. **`EnhancementProfile`**: 增强场景配置类
   - 管理单个场景的配置
   - 验证配置完整性
   - 格式化提示词

3. **`ProfileManager`**: 场景管理器
   - 管理多个 Profile
   - 获取指定 Profile
   - 列出所有可用 Profile

4. **`AnkiCardEnhancer`**: 核心增强器
   - 加载配置
   - 增强卡片
   - 管理缓存
   - 导出结果

### 工作流程

```
1. 加载配置 (config.json)
   ↓
2. 初始化 AI Provider (根据 provider 设置)
   ↓
3. 获取 Active Profile (根据 active_profile 设置)
   ↓
4. 加载输入数据 (Front + Back)
   ↓
5. 对每条数据:
   - 使用 Profile 格式化提示词
   - 调用 LLM 进行增强
   - 清洗响应结果
   - 保存进度
   ↓
6. 导出为 Tab 分隔的两列格式
   ↓
7. 导入 Anki
```

## 📊 测试结果

所有内置场景已测试通过：

- ✅ `vocabulary_enhancement`: 4条词汇测试成功
- ✅ `ancient_text_explanation`: 3条古文测试成功

**测试示例输出**:

词汇增强：
- Front: `ephemeral`
- Enhanced Back: 包含释义、例句、词源、同义词、反义词、记忆技巧等

古文增强：
- Front: `学而时习之，不亦说乎`
- Enhanced Back: 包含原文、翻译、注释、出处、背景解读、记忆提示等

## 💡 使用建议

### 1. 选择合适的增强场景

```bash
# 先查看所有可用场景
python anki_enhancer.py --list-profiles

# 选择最适合你数据的场景
python anki_enhancer.py -p ancient_text_explanation -i ancient.txt
```

### 2. 准备高质量的输入

- **Front**: 简洁明确的问题或关键词
- **Back**: 基础的答案或解释（哪怕很简单也可以）
- LLM 会基于你的输入进行补充和扩展

### 3. 优化增强效果

如果 AI 输出不符合预期：

1. **修改 Prompt**: 在配置文件中调整对应 Profile 的 `user_prompt_template`
2. **添加更具体的指令**: 告诉 LLM 需要补充哪些内容
3. **提供输出示例**: 在 Prompt 中给出期望的格式示例

### 4. 批量处理

对于大量数据：

- 设置较小的 `save_interval` (如 5)，避免意外丢失进度
- 启用断点续传功能（缓存文件自动支持）
- 分批处理，每批 50-100 条
- 根据 API 速率限制调整 `request_delay`

### 5. 质量检查

生成后建议检查：

- 翻译是否准确
- 例句是否恰当
- 是否有重复内容
- 格式是否统一

## 🐛 常见问题

### Q1: 如何添加新的 AI 服务商？

A: 继承 `AIProvider` 类，实现 `generate_content()` 方法，在 `create_ai_provider()` 中添加分支。

### Q2: 增强后的内容太长怎么办？

A: 在 Profile 的 `user_prompt_template` 中添加字数限制，例如："控制在 300 字以内"。

### Q3: 如何自定义输出格式？

A: 修改 `user_prompt_template`，指定你希望的格式和结构。

### Q4: 缓存文件如何管理？

A: 使用 `--clear-cache` 清除缓存，或手动删除 `progress_cache.csv`。

### Q5: 导入 Anki 后显示乱码？

A: 确保以下几点：
- 配置文件中设置 `"output_encoding": "utf-8"`
- Anki 导入时选择 UTF-8 编码
- 文本编辑器保存为 UTF-8 格式

### Q6: 不同场景间如何切换？

A: 使用 `-p` 参数或修改配置文件中的 `active_profile`。

### Q7: 能否只增强部分内容？

A: 可以在输入文件中只放入需要增强的条目，或分批处理不同类型的内容。

## 📦 项目文件

```
anki-assistant/
├── anki_enhancer.py          # 主程序 (v4.0)
├── anki_llm_forge.py         # 旧版本 (v3.0，保留兼容)
├── anki_process.py           # 更早版本 (v2.0，保留兼容)
├── config_v4.example.json    # v4.0 配置模板
├── config.json               # 实际配置文件
├── test_v4_vocab.txt         # 词汇测试数据
├── test_v4_ancient.txt       # 古文测试数据
├── test_v4_concept.txt       # 概念测试数据
├── test_v4_code.txt          # 代码测试数据
├── README_v4.md              # 本文档
├── README_v3.md              # v3.0 文档
└── README.md                 # 通用文档
```

## 🎓 版本对比总结

| 特性 | v3.0 | v4.0 |
|------|------|------|
| **输入** | 单列 (Front) | 双列 (Front + Back) |
| **输出** | 多列 (动态字段) | 双列 (Front + Enhanced Back) |
| **输出格式** | JSON | 纯文本 |
| **定位** | 从零生成卡片 | 增强已有笔记 |
| **复杂度** | 高 (需要解析JSON) | 低 (直接文本) |
| **可靠性** | 中等 (可能有JSON错误) | 高 (无解析错误) |
| **适用场景** | 快速批量生成 | 质量优先的补充 |
| **控制粒度** | 粗放 | 精细 |

## 🚀 未来计划

- [ ] 添加更多内置 Profile
- [ ] 支持批量文件处理
- [ ] 增强 Web UI 界面
- [ ] Profile 共享市场
- [ ] AI 输出质量评分
- [ ] 支持交互式调整

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 PR 和 Issue！

---

**v4.0 架构完成！** ✨

从复杂的多列生成到简洁的两列增强，Anki Enhancer v4.0 让 Anki 卡片制作变得更加实用和可靠。
