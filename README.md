# Anki 卡片自动生成工具

基于 Google Gemini AI 的 Anki 记忆卡片自动生成工具，可以为句子自动生成中文翻译和背景信息。

## 功能特性

- 自动生成中文翻译
- 智能推测句子出处、作者和背景
- 支持断点续传（中断后可继续）
- 自动重试机制（API 调用失败时）
- 多种输入格式支持（.txt, .csv, .xlsx）
- 完善的日志系统
- 定期保存进度，防止数据丢失

## 安装依赖

```bash
pip install pandas google-generativeai tqdm openpyxl
```

## 快速开始

### 1. 配置 API KEY

复制示例配置文件：
```bash
copy config.example.json config.json
```

编辑 `config.json`，填入你的 Google API KEY：
```json
{
  "api_key": "你的实际_API_KEY",
  "model": "gemini-pro",
  "request_delay": 1.0,
  "max_retries": 3,
  "save_interval": 10,
  "output_filename": "anki_cards.txt",
  "cache_filename": "progress_cache.csv",
  "log_file": "anki_process.log"
}
```

获取 Google API KEY：https://makersuite.google.com/app/apikey

### 2. 准备输入数据

**方式1：在代码中直接输入**
```python
# 编辑 anki_process.py 第 255-260 行
raw_data = [
    "To be, or not to be, that is the question.",
    "Stay hungry, stay foolish.",
    # 添加更多句子...
]
```

**方式2：从文件读取**
```python
# 编辑 anki_process.py 第 263 行，取消注释
raw_data = "input.txt"  # 或 input.csv, input.xlsx
```

支持的输入格式：
- `.txt` - 每行一个句子
- `.csv` - 第一列为句子
- `.xlsx` - 第一列为句子

### 3. 运行程序

```bash
python anki_process.py
```

### 4. 导入 Anki

1. 打开 Anki 桌面版
2. 点击 `文件` → `导入`
3. 选择生成的 `anki_cards.txt`
4. 确认导入设置（Tab 分隔，UTF-8 编码）
5. 点击 `导入`

## 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `api_key` | Google API KEY | 必填 |
| `model` | Gemini 模型名称 | `gemini-pro` |
| `request_delay` | API 请求间隔（秒） | `1.0` |
| `max_retries` | 失败重试次数 | `3` |
| `save_interval` | 进度保存间隔（条数） | `10` |
| `output_filename` | 输出文件名 | `anki_cards.txt` |
| `cache_filename` | 缓存文件名 | `progress_cache.csv` |
| `log_file` | 日志文件名 | `anki_process.log` |

## 高级功能

### 断点续传

程序会自动保存进度到 `progress_cache.csv`，如果中途中断：
- 下次运行会自动从断点继续
- 已处理的数据不会重复请求 API
- 节省时间和 API 配额

### 日志系统

所有操作都会记录到日志文件：
- 查看日志：`type anki_process.log`（Windows）
- 日志级别：INFO
- 记录内容：处理进度、成功/失败信息、错误详情

### 错误处理

程序具有完善的错误处理机制：
- API 调用失败：自动重试（指数退避）
- JSON 解析失败：标记为"需人工检查"
- 网络错误：重试并记录日志

## 输出格式

生成的 Anki 卡片包含三列（Tab 分隔）：
1. **Front**（正面）：原始句子
2. **Back**（背面）：中文翻译
3. **Note**（备注）：作者、出处、背景信息

示例：
```
To be, or not to be, that is the question.	生存还是毁灭，这是一个问题。	作者: Shakespeare <br> 出处: 《哈姆雷特》 <br> 背景: 哈姆雷特的独白，思考生死问题
```

## 注意事项

1. **API 配额**：Google Gemini 有免费配额限制，大量处理时注意控制请求速度
2. **速率限制**：建议 `request_delay` 设置为 1 秒以上，避免触发速率限制
3. **数据备份**：重要数据请提前备份，虽然程序有断点续传功能
4. **人工检查**：部分复杂句子可能需要人工检查翻译准确性

## 常见问题

### Q: 如何获取 Google API KEY？
A: 访问 https://makersuite.google.com/app/apikey 创建 API KEY

### Q: 程序中断了怎么办？
A: 重新运行即可，程序会自动从断点继续

### Q: 如何处理大量数据？
A:
- 调整 `save_interval` 更频繁保存进度（如 5）
- 增加 `request_delay` 避免速率限制（如 2.0）
- 分批处理，每批 100-200 条

### Q: 导入 Anki 后显示乱码？
A: 确保 Anki 导入时选择了 UTF-8 编码

### Q: 某些句子翻译不准确？
A: 查看日志文件定位问题句子，手动修改 `anki_cards.txt` 或直接在 Anki 中编辑

## 项目结构

```
anki-assistant/
├── anki_process.py          # 主程序
├── config.json              # 配置文件（需自己创建）
├── config.example.json      # 配置示例
├── input_example.txt        # 示例输入文件
├── README.md                # 使用文档
├── .gitignore               # Git 忽略文件
├── anki_cards.txt           # 生成的卡片（运行后）
├── progress_cache.csv       # 进度缓存（运行后）
└── anki_process.log         # 日志文件（运行后）
```

## 更新日志

### v2.0 (当前版本)
- 添加配置文件系统
- 实现断点续传功能
- 完善错误处理和重试机制
- 添加日志系统
- 支持多种输入格式（.txt, .csv, .xlsx）
- 优化进度显示和用户体验

### v1.0 (初始版本)
- 基础的 AI 卡片生成功能

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
