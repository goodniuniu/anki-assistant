import pandas as pd
import google.generativeai as genai
import os
import time
import json
import logging
from pathlib import Path
from tqdm import tqdm
import re
from typing import Dict, Optional

# ================= AI 服务商接口 =================
class AIProvider:
    """AI 服务商基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate_content(self, prompt: str) -> str:
        """生成内容，子类必须实现"""
        raise NotImplementedError

class GeminiProvider(AIProvider):
    """Google Gemini 服务商"""

    def __init__(self, config: Dict):
        super().__init__(config)
        os.environ["GOOGLE_API_KEY"] = config["api_key"]
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(config['model'])
        self.logger.info(f"✅ 已初始化 Gemini 模型: {config['model']}")

    def generate_content(self, prompt: str) -> str:
        """使用 Gemini 生成内容"""
        response = self.model.generate_content(prompt)
        return response.text

class QiniuProvider(AIProvider):
    """七牛云 AI 服务商（DeepSeek）"""

    def __init__(self, config: Dict):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=config["base_url"],
                api_key=config["api_key"]
            )
            self.model = config['model']
            self.logger.info(f"✅ 已初始化七牛云 AI 模型: {config['model']}")
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")

    def generate_content(self, prompt: str) -> str:
        """使用七牛云 AI 生成内容"""
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            max_tokens=4096
        )
        return response.choices[0].message.content

def create_ai_provider(config: Dict) -> AIProvider:
    """
    工厂方法：根据配置创建对应的 AI 服务商实例
    """
    provider_name = config.get("provider", "gemini").lower()

    if provider_name == "gemini":
        if "gemini" not in config:
            raise ValueError("配置中缺少 gemini 配置项")
        return GeminiProvider(config["gemini"])

    elif provider_name in ["qiniu", "deepseek"]:
        if "qiniu" not in config:
            raise ValueError("配置中缺少 qiniu 配置项")
        return QiniuProvider(config["qiniu"])

    else:
        raise ValueError(f"不支持的服务商: {provider_name}，请选择 'gemini' 或 'qiniu'")

# ================= 配置加载 =================
def load_config(config_file='config.json'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"❌ 配置文件 {config_file} 未找到！")
        print(f"💡 请复制 config.example.json 为 config.json 并填写你的 API KEY")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        raise

# ================= 初始化日志系统 =================
def setup_logging(log_file):
    """设置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# ================= 数据准备 =================
def load_input_data(source):
    """
    从多种来源加载输入数据
    支持: list, .txt, .csv, .xlsx
    """
    logger = logging.getLogger(__name__)

    if isinstance(source, list):
        logger.info(f"从列表加载 {len(source)} 条数据")
        return pd.DataFrame(source, columns=['Front'])

    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source}")

    if source_path.suffix == '.txt':
        with open(source, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        logger.info(f"从 TXT 文件加载 {len(lines)} 条数据")
        return pd.DataFrame(lines, columns=['Front'])

    elif source_path.suffix == '.csv':
        df = pd.read_csv(source)
        if 'Front' not in df.columns:
            df = pd.DataFrame(df.iloc[:, 0], columns=['Front'])
        logger.info(f"从 CSV 文件加载 {len(df)} 条数据")
        return df

    elif source_path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(source)
        if 'Front' not in df.columns:
            df = pd.DataFrame(df.iloc[:, 0], columns=['Front'])
        logger.info(f"从 Excel 文件加载 {len(df)} 条数据")
        return df

    else:
        raise ValueError(f"不支持的文件格式: {source_path.suffix}")

def prepare_data(raw_data):
    """
    将原始数据转换为 DataFrame，预留三列结构
    """
    df = load_input_data(raw_data)
    if 'Back' not in df.columns:
        df['Back'] = ""
    if 'Note' not in df.columns:
        df['Note'] = ""
    return df

# ================= 大模型信息补充（带重试和断点续传） =================
def clean_json_response(response_text):
    """清理大模型返回的 JSON 字符串"""
    # 移除 markdown 代码块标记
    clean_text = response_text.replace('```json', '').replace('```', '').strip()
    # 移除可能的注释
    clean_text = re.sub(r'//.*?\n', '\n', clean_text)
    clean_text = re.sub(r'/\*.*?\*/', '', clean_text, flags=re.DOTALL)
    return clean_text

def call_ai_with_retry(ai_provider: AIProvider, prompt: str, max_retries: int = 3, delay: float = 2):
    """
    带重试机制的 AI 调用
    """
    logger = logging.getLogger(__name__)

    for attempt in range(max_retries):
        try:
            response_text = ai_provider.generate_content(prompt)
            return response_text
        except Exception as e:
            logger.warning(f"AI 调用失败（尝试 {attempt + 1}/{max_retries}）: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # 指数退避
            else:
                raise

def enrich_data_with_llm(df, config, logger):
    """
    遍历 DataFrame，让大模型为每一行补充信息
    支持断点续传
    """
    # 创建 AI 服务商实例
    try:
        ai_provider = create_ai_provider(config)
        provider_name = config.get("provider", "gemini")
        logger.info(f"使用 AI 服务商: {provider_name}")
    except Exception as e:
        logger.error(f"初始化 AI 服务商失败: {e}")
        raise

    # 检查是否有缓存
    cache_file = config.get('cache_filename', 'progress_cache.csv')
    start_index = 0

    if Path(cache_file).exists():
        logger.info(f"发现缓存文件，从断点继续...")
        cache_df = pd.read_csv(cache_file)
        start_index = len(cache_df)
        df = pd.concat([cache_df, df.iloc[start_index:]], ignore_index=True)
        logger.info(f"已完成 {start_index} 条，剩余 {len(df) - start_index} 条")

    logger.info(f"开始处理 {len(df)} 条数据（从第 {start_index + 1} 条开始）...")

    prompt_template = """
你是一个语言学习助手。请分析以下句子：
"{sentence}"

请完成以下任务并严格以 JSON 格式输出：
1. translate: 提供地道的中文翻译。
2. meta_info: 推测或查找该句子的作者、出处（书名/电影名）以及简短的背景。如果完全无法考证，请根据句子内容通过"AI解析"来解释其语境。

输出格式示例：
{{
    "translate": "这是中文翻译。",
    "meta_info": "作者: XXX <br> 出处: 《XXX》 <br> 背景: 这句话通常用于..."
}}
注意：meta_info 中的换行请使用 <br> 标签，因为这是为了导入 Anki。
"""

    save_interval = config.get('save_interval', 10)
    request_delay = config.get('request_delay', 1.0)
    max_retries = config.get('max_retries', 3)

    # 使用 tqdm 显示进度条
    for index in tqdm(range(start_index, len(df)), desc="处理进度"):
        if pd.notna(df.loc[index, 'Back']) and df.loc[index, 'Back'] != "":
            logger.info(f"跳过已处理的第 {index + 1} 条")
            continue

        sentence = df.loc[index, 'Front']

        try:
            # 1. 生成内容
            response_text = call_ai_with_retry(
                ai_provider,
                prompt_template.format(sentence=sentence),
                max_retries=max_retries
            )

            # 2. 清洗数据
            clean_json = clean_json_response(response_text)

            # 3. 解析 JSON
            data = json.loads(clean_json)

            # 4. 存入 DataFrame
            df.loc[index, 'Back'] = data.get("translate", "翻译失败")
            df.loc[index, 'Note'] = data.get("meta_info", "无额外信息")

            logger.info(f"✅ 第 {index + 1}/{len(df)} 条处理成功")

            # 5. 定期保存进度
            if (index + 1) % save_interval == 0:
                df.to_csv(cache_file, index=False)
                logger.info(f"💾 进度已保存（已完成 {index + 1} 条）")

            # 避免触发 API 速率限制
            time.sleep(request_delay)

        except json.JSONDecodeError as e:
            logger.error(f"❌ 第 {index + 1} 条 JSON 解析失败: {e}")
            df.loc[index, 'Back'] = "需人工检查"
            df.loc[index, 'Note'] = f"JSON 解析错误: {str(e)[:100]}"
        except Exception as e:
            logger.error(f"❌ 第 {index + 1} 条处理失败: {e}")
            df.loc[index, 'Back'] = "需人工检查"
            df.loc[index, 'Note'] = f"API Error: {str(e)[:100]}"

    # 最终保存
    df.to_csv(cache_file, index=False)
    logger.info("💾 最终进度已保存")

    return df

# ================= 导出为 Anki 格式 =================
def export_to_anki(df, filename):
    """
    将数据导出为 Anki 可识别的 TXT 文件
    """
    logger = logging.getLogger(__name__)

    # 创建副本，避免修改原数据
    export_df = df.copy()

    # 替换换行符，防止破坏 CSV 结构
    for col in ['Front', 'Back', 'Note']:
        export_df[col] = export_df[col].astype(str).str.replace('\n', '<br>', regex=False)
        export_df[col] = export_df[col].astype(str).str.replace('\r', '', regex=False)
        export_df[col] = export_df[col].astype(str).str.replace('\t', '    ', regex=False)

    # 导出
    export_df.to_csv(filename, sep='\t', index=False, header=False, encoding='utf-8')
    logger.info(f"✅ 文件已保存: {filename}")
    logger.info(f"📊 共 {len(df)} 张卡片")

    # 生成统计报告
    print("\n" + "="*50)
    print("处理完成！统计信息：")
    print(f"  总卡片数: {len(df)}")
    print(f"  成功处理: {len(df[df['Back'] != '需人工检查'])}")
    print(f"  需人工检查: {len(df[df['Back'] == '需人工检查'])}")
    print(f"  导出文件: {filename}")
    print("="*50)

# ================= 主程序 =================
def main():
    """主程序入口"""
    try:
        # 1. 加载配置
        config = load_config()

        # 2. 设置日志
        logger = setup_logging(config.get('log_file', 'anki_process.log'))
        logger.info("="*50)
        logger.info("Anki 卡片生成程序启动")
        logger.info(f"AI 服务商: {config.get('provider', 'gemini')}")
        logger.info("="*50)

        # 3. 准备数据（支持多种输入源）
        # 方式1: 从列表
        raw_data = [
            "To be, or not to be, that is the question.",
            "Stay hungry, stay foolish.",
            "It was the best of times, it was the worst of times.",
            "I'm gonna make him an offer he can't refuse."
        ]

        # 方式2: 从文件（取消注释使用）
        # raw_data = "input.txt"  # 支持 .txt, .csv, .xlsx

        logger.info("开始准备数据...")
        df = prepare_data(raw_data)
        logger.info(f"数据准备完成，共 {len(df)} 条")

        # 4. AI 补充
        logger.info("开始 AI 信息补充...")
        df_enriched = enrich_data_with_llm(df, config, logger)

        # 5. 打印预览
        print("\n--- 数据预览（前3条）---")
        print(df_enriched.head(3).to_string())

        # 6. 导出
        output_file = config.get('output_filename', 'anki_cards.txt')
        export_to_anki(df_enriched, output_file)

        logger.info("="*50)
        logger.info("程序执行完成！")
        logger.info("="*50)

    except Exception as e:
        logging.getLogger(__name__).error(f"程序执行失败: {e}")
        print(f"\n❌ 程序执行失败: {e}")
        raise

if __name__ == "__main__":
    main()
