"""
Anki-LLM-Forge: 通用型 Anki 卡片增强工具
一个配置驱动的、支持多场景的 Anki 卡片内容生成系统
"""

import pandas as pd
import google.generativeai as genai
import os
import time
import json
import logging
import argparse
from pathlib import Path
from tqdm import tqdm
import re
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


# ================= AI 服务商接口 =================
class AIProvider(ABC):
    """AI 服务商抽象基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def generate_content(self, prompt: str, system_prompt: str = "") -> str:
        """生成内容，子类必须实现"""
        pass


class GeminiProvider(AIProvider):
    """Google Gemini 服务商"""

    def __init__(self, config: Dict):
        super().__init__(config)
        os.environ["GOOGLE_API_KEY"] = config["api_key"]
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(config['model'])
        self.logger.info(f"已初始化 Gemini 模型: {config['model']}")

    def generate_content(self, prompt: str, system_prompt: str = "") -> str:
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
            self.logger.info(f"已初始化七牛云 AI 模型: {config['model']}")
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")

    def generate_content(self, prompt: str, system_prompt: str = "") -> str:
        """使用七牛云 AI 生成内容"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            max_tokens=4096
        )
        return response.choices[0].message.content


def create_ai_provider(config: Dict, provider_name: str) -> AIProvider:
    """
    工厂方法：根据配置创建对应的 AI 服务商实例
    """
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


# ================= Profile 管理 =================
class Profile:
    """任务场景配置类"""

    def __init__(self, profile_name: str, profile_config: Dict):
        self.name = profile_name
        self.description = profile_config.get("description", "")
        self.system_prompt = profile_config.get("system_prompt", "")
        self.user_prompt_template = profile_config.get("user_prompt_template", "")
        self.output_fields = profile_config.get("output_fields", [])
        self.anki_fields = profile_config.get("anki_fields", [])
        self.field_mapping = profile_config.get("field_mapping", {})

    def validate(self) -> bool:
        """验证 Profile 配置是否有效"""
        if not self.user_prompt_template:
            raise ValueError(f"Profile '{self.name}' 缺少 user_prompt_template")
        if not self.output_fields:
            raise ValueError(f"Profile '{self.name}' 缺少 output_fields")
        if not self.anki_fields:
            raise ValueError(f"Profile '{self.name}' 缺少 anki_fields")
        if not self.field_mapping:
            raise ValueError(f"Profile '{self.name}' 缺少 field_mapping")
        return True

    def format_prompt(self, front_text: str) -> str:
        """格式化用户提示词"""
        return self.user_prompt_template.format(front_text=front_text)


class ProfileManager:
    """Profile 管理器"""

    def __init__(self, profiles_config: Dict):
        self.profiles = {}
        for name, config in profiles_config.items():
            self.profiles[name] = Profile(name, config)

    def get_profile(self, profile_name: str) -> Profile:
        """获取指定的 Profile"""
        if profile_name not in self.profiles:
            available = list(self.profiles.keys())
            raise ValueError(
                f"Profile '{profile_name}' 不存在。"
                f"可用的 Profiles: {', '.join(available)}"
            )
        profile = self.profiles[profile_name]
        profile.validate()
        return profile

    def list_profiles(self) -> List[str]:
        """列出所有可用的 Profiles"""
        return list(self.profiles.keys())


# ================= Anki 卡片生成器 =================
class AnkiCardGenerator:
    """Anki 卡片生成器 - 核心业务逻辑"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # 初始化全局设置
        self.global_settings = config.get("global_settings", {})
        self.provider_name = self.global_settings.get("provider", "gemini")

        # 初始化 AI 服务商
        providers_config = config.get("providers", {})
        self.ai_provider = create_ai_provider(providers_config, self.provider_name)

        # 初始化 Profile 管理器
        profiles_config = config.get("profiles", {})
        self.profile_manager = ProfileManager(profiles_config)

        # 获取当前激活的 Profile
        active_profile_name = self.global_settings.get("active_profile")
        if not active_profile_name:
            raise ValueError("配置中缺少 active_profile，请指定要使用的 Profile")

        self.profile = self.profile_manager.get_profile(active_profile_name)
        self.logger.info(f"使用 Profile: {self.profile.name}")
        self.logger.info(f"Profile 描述: {self.profile.description}")

    def clean_json_response(self, response_text: str) -> str:
        """清理 LLM 返回的 JSON 字符串"""
        # 移除 markdown 代码块标记
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        # 移除可能的注释
        clean_text = re.sub(r'//.*?\n', '\n', clean_text)
        clean_text = re.sub(r'/\*.*?\*/', '', clean_text, flags=re.DOTALL)
        return clean_text

    def call_ai_with_retry(self, prompt: str, max_retries: int = 3, delay: float = 2) -> str:
        """带重试机制的 AI 调用"""
        for attempt in range(max_retries):
            try:
                response_text = self.ai_provider.generate_content(
                    prompt,
                    self.profile.system_prompt
                )
                return response_text
            except Exception as e:
                self.logger.warning(f"AI 调用失败（尝试 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
                else:
                    raise

    def generate_card(self, front_text: str) -> Dict[str, str]:
        """
        为单个 front_text 生成完整的 Anki 卡片

        返回: dict，包含所有 Anki 字段
        """
        # 1. 格式化提示词
        prompt = self.profile.format_prompt(front_text)

        # 2. 调用 AI
        response_text = self.call_ai_with_retry(prompt)

        # 3. 清洗和解析 JSON
        clean_json = self.clean_json_response(response_text)
        llm_output = json.loads(clean_json)

        # 4. 映射到 Anki 字段
        card = {"front_text": front_text}

        for llm_field in self.profile.output_fields:
            if llm_field in llm_output:
                # 根据 field_mapping 映射到 Anki 字段
                anki_field = self.profile.field_mapping.get(llm_field)
                if anki_field:
                    card[anki_field] = llm_output[llm_field]
                else:
                    card[llm_field] = llm_output[llm_field]
            else:
                self.logger.warning(f"LLM 返回缺少字段: {llm_field}")
                card[llm_field] = "[字段缺失]"

        return card

    def generate_cards(
        self,
        input_data: List[str],
        cache_file: Optional[str] = None,
        progress_callback=None
    ) -> pd.DataFrame:
        """
        批量生成 Anki 卡片

        Args:
            input_data: 输入数据列表
            cache_file: 缓存文件路径（支持断点续传）
            progress_callback: 进度回调函数

        Returns:
            pd.DataFrame: 包含所有生成的卡片
        """
        # 检查是否有缓存
        start_index = 0
        if cache_file and Path(cache_file).exists():
            self.logger.info(f"发现缓存文件，从断点继续...")
            cache_df = pd.read_csv(cache_file)
            start_index = len(cache_df)

            # 确保列一致
            expected_columns = list(self.profile.field_mapping.values())
            if set(cache_df.columns) != set(expected_columns):
                self.logger.warning("缓存文件的列与当前 Profile 不匹配，将重新生成")
                start_index = 0
                cache_df = pd.DataFrame(columns=expected_columns)

            self.logger.info(f"已完成 {start_index} 条，剩余 {len(input_data) - start_index} 条")

        # 初始化结果
        results = []
        if start_index > 0:
            cache_df_rows = cache_df.to_dict('records')
            results = cache_df_rows[:start_index]

        # 生成卡片
        request_delay = self.global_settings.get("request_delay", 1.0)
        max_retries = self.global_settings.get("max_retries", 3)
        save_interval = self.global_settings.get("save_interval", 10)

        for index in tqdm(range(start_index, len(input_data)), desc="生成卡片"):
            front_text = input_data[index]

            try:
                # 生成卡片
                card = self.generate_card(front_text)
                results.append(card)

                self.logger.info(f"✅ 第 {index + 1}/{len(input_data)} 条生成成功")

                # 定期保存进度
                if cache_file and (index + 1) % save_interval == 0:
                    df = pd.DataFrame(results)
                    df.to_csv(cache_file, index=False)
                    self.logger.info(f"💾 进度已保存（已完成 {index + 1} 条）")

                # 避免触发 API 速率限制
                time.sleep(request_delay)

            except json.JSONDecodeError as e:
                self.logger.error(f"❌ 第 {index + 1} 条 JSON 解析失败: {e}")
                # 创建一个部分填充的卡片
                card = {"front_text": front_text}
                for anki_field in self.profile.anki_fields:
                    if anki_field != "front_text":
                        card[anki_field] = f"[JSON 解析错误: {str(e)[:50]}]"
                results.append(card)

            except Exception as e:
                self.logger.error(f"❌ 第 {index + 1} 条处理失败: {e}")
                # 创建一个部分填充的卡片
                card = {"front_text": front_text}
                for anki_field in self.profile.anki_fields:
                    if anki_field != "front_text":
                        card[anki_field] = f"[处理错误: {str(e)[:50]}]"
                results.append(card)

        # 最终保存
        if cache_file:
            df = pd.DataFrame(results)
            df.to_csv(cache_file, index=False)
            self.logger.info("💾 最终进度已保存")

        return pd.DataFrame(results)


# ================= 工具函数 =================
def load_config(config_file: str) -> Dict:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"❌ 配置文件 {config_file} 未找到！")
        print(f"💡 请复制 config_v3.example.json 为 {config_file} 并填写配置")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        raise


def setup_logging(log_file: str):
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


def load_input_data(source: str) -> List[str]:
    """
    从多种来源加载输入数据
    支持: list, .txt, .csv, .xlsx
    """
    logger = logging.getLogger(__name__)

    if isinstance(source, list):
        logger.info(f"从列表加载 {len(source)} 条数据")
        return source

    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source}")

    if source_path.suffix == '.txt':
        with open(source, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        logger.info(f"从 TXT 文件加载 {len(lines)} 条数据")
        return lines

    elif source_path.suffix == '.csv':
        df = pd.read_csv(source)
        logger.info(f"从 CSV 文件加载 {len(df)} 条数据")
        return df.iloc[:, 0].tolist()

    elif source_path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(source)
        logger.info(f"从 Excel 文件加载 {len(df)} 条数据")
        return df.iloc[:, 0].tolist()

    else:
        raise ValueError(f"不支持的文件格式: {source_path.suffix}")


def export_to_anki(df: pd.DataFrame, filename: str, encoding: str = 'utf-8'):
    """导出为 Anki 可识别的格式"""
    logger = logging.getLogger(__name__)

    # 创建副本，避免修改原数据
    export_df = df.copy()

    # 替换换行符和制表符
    for col in export_df.columns:
        export_df[col] = export_df[col].astype(str).str.replace('\n', '<br>', regex=False)
        export_df[col] = export_df[col].astype(str).str.replace('\r', '', regex=False)
        export_df[col] = export_df[col].astype(str).str.replace('\t', '    ', regex=False)

    # 导出
    export_df.to_csv(filename, sep='\t', index=False, header=False, encoding=encoding)
    logger.info(f"✅ 文件已保存: {filename}")
    logger.info(f"📊 共 {len(df)} 张卡片")

    # 生成统计报告
    print("\n" + "="*50)
    print("处理完成！统计信息：")
    print(f"  总卡片数: {len(df)}")
    print(f"  字段数: {len(df.columns)}")
    print(f"  字段列表: {', '.join(df.columns)}")
    print(f"  导出文件: {filename}")
    print("="*50)


# ================= 主程序 =================
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Anki-LLM-Forge: 通用型 Anki 卡片增强工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用配置文件中指定的 input_file
  python anki_llm_forge.py -c config.json

  # 指定输入文件
  python anki_llm_forge.py -c config.json -i my_data.txt

  # 指定输出文件
  python anki_llm_forge.py -c config.json -i input.txt -o output.txt

  # 列出所有可用的 Profiles
  python anki_llm_forge.py -c config.json --list-profiles

  # 临时切换 Profile
  python anki_llm_forge.py -c config.json -p english_vocab

  # 清除缓存重新生成
  python anki_llm_forge.py -c config.json --clear-cache
        """
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        help='输入文件路径（覆盖配置文件）'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='输出文件路径（覆盖配置文件）'
    )

    parser.add_argument(
        '-p', '--profile',
        type=str,
        help='临时切换 Profile（覆盖配置文件）'
    )

    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='列出所有可用的 Profiles'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='清除缓存文件，重新生成所有内容'
    )

    return parser.parse_args()


def main():
    """主程序入口"""
    args = parse_arguments()

    try:
        # 1. 加载配置
        config = load_config(args.config)

        # 2. 设置日志
        global_settings = config.get("global_settings", {})
        log_file = global_settings.get("log_file", "anki_process.log")
        logger = setup_logging(log_file)

        logger.info("="*50)
        logger.info("Anki-LLM-Forge 启动")
        logger.info(f"配置文件: {args.config}")
        logger.info("="*50)

        # 3. 处理 --list-profiles 参数
        if args.list_profiles:
            profile_manager = ProfileManager(config.get("profiles", {}))
            profiles = profile_manager.list_profiles()
            print("\n可用的 Profiles:")
            print("="*50)
            for name in profiles:
                profile = profile_manager.get_profile(name)
                print(f"\n[{name}]")
                print(f"  描述: {profile.description}")
                print(f"  Anki 字段: {', '.join(profile.anki_fields)}")
            print("\n" + "="*50)
            return 0

        # 4. 命令行参数覆盖配置文件
        if args.profile:
            global_settings["active_profile"] = args.profile
        if args.input:
            global_settings["input_file"] = args.input
        if args.output:
            global_settings["output_file"] = args.output

        # 5. 初始化卡片生成器
        generator = AnkiCardGenerator(config)

        # 6. 清除缓存（如果指定）
        cache_file = global_settings.get("cache_file")
        if args.clear_cache and cache_file and Path(cache_file).exists():
            logger.info(f"清除缓存文件: {cache_file}")
            os.remove(cache_file)

        # 7. 加载输入数据
        input_file = global_settings.get("input_file")
        if not input_file:
            print("错误: 配置文件中未指定 input_file")
            print("请通过命令行参数 -i 指定，或在配置文件中设置 input_file")
            return 1

        logger.info("开始加载数据...")
        input_data = load_input_data(input_file)
        logger.info(f"数据加载完成，共 {len(input_data)} 条")

        # 8. 生成卡片
        logger.info("开始生成 Anki 卡片...")
        df_cards = generator.generate_cards(
            input_data,
            cache_file=cache_file
        )

        # 9. 打印预览
        print("\n--- 数据预览（前3条）---")
        print(df_cards.head(3).to_string())

        # 10. 导出
        output_file = global_settings.get("output_file", "anki_cards.txt")
        output_encoding = global_settings.get("output_encoding", "utf-8")
        export_to_anki(df_cards, output_file, encoding=output_encoding)

        logger.info("="*50)
        logger.info("程序执行完成！")
        logger.info("="*50)

        return 0

    except FileNotFoundError as e:
        logging.getLogger(__name__).error(f"文件未找到: {e}")
        print(f"\n[错误] 文件未找到: {e}")
        return 1
    except ValueError as e:
        logging.getLogger(__name__).error(f"配置错误: {e}")
        print(f"\n[错误] 配置错误: {e}")
        return 1
    except Exception as e:
        logging.getLogger(__name__).error(f"程序执行失败: {e}")
        print(f"\n[错误] 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
