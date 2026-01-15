"""
Anki Card Enhancer: Anki 卡片内容增强工具
基于已有内容进行补充、完善、扩展
核心定位: Front + 原始Back → LLM增强 → Front + 增强Back
"""

import pandas as pd
import google.generativeai as genai
import os
import re
import time
import json
import logging
import argparse
from pathlib import Path
from tqdm import tqdm
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
    """工厂方法：根据配置创建对应的 AI 服务商实例"""
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
class EnhancementProfile:
    """增强场景配置类"""

    def __init__(self, profile_name: str, profile_config: Dict):
        self.name = profile_name
        self.description = profile_config.get("description", "")
        self.system_prompt = profile_config.get("system_prompt", "")
        self.user_prompt_template = profile_config.get("user_prompt_template", "")
        self.output_format = profile_config.get("output_format", "text")
        self.input_fields = profile_config.get("input_fields", ["front_text", "back_text"])
        self.output_fields = profile_config.get("output_fields", ["front_text", "enhanced_back"])

    def validate(self) -> bool:
        """验证 Profile 配置是否有效"""
        if not self.user_prompt_template:
            raise ValueError(f"Profile '{self.name}' 缺少 user_prompt_template")
        if not self.output_format:
            raise ValueError(f"Profile '{self.name}' 缺少 output_format")
        return True

    def format_prompt(self, front_text: str, back_text: str) -> str:
        """格式化增强提示词"""
        return self.user_prompt_template.format(
            front_text=front_text,
            back_text=back_text
        )


class ProfileManager:
    """Profile 管理器"""

    def __init__(self, profiles_config: Dict):
        self.profiles = {}
        for name, config in profiles_config.items():
            self.profiles[name] = EnhancementProfile(name, config)

    def get_profile(self, profile_name: str) -> EnhancementProfile:
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


# ================= Anki 卡片增强器 =================
class AnkiCardEnhancer:
    """Anki 卡片增强器 - 基于已有内容进行补充完善"""

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
        self.logger.info(f"使用增强 Profile: {self.profile.name}")
        self.logger.info(f"Profile 描述: {self.profile.description}")

    def clean_response(self, response_text: str) -> str:
        """清理 AI 返回的内容"""
        # 移除 markdown 代码块标记
        clean_text = response_text.replace('```text', '').replace('```', '').strip()
        # 移除可能的代码块语言标识
        clean_text = re.sub(r'^```\w*\n', '', clean_text, flags=re.MULTILINE)
        return clean_text.strip()

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

    def enhance_card(self, front_text: str, back_text: str) -> Dict[str, str]:
        """
        增强单个卡片
        输入: front_text, back_text (原始内容)
        输出: dict 包含 front_text, enhanced_back
        """
        # 1. 格式化提示词
        prompt = self.profile.format_prompt(front_text, back_text)

        # 2. 调用 AI
        response_text = self.call_ai_with_retry(prompt)

        # 3. 清洗响应
        enhanced_back = self.clean_response(response_text)

        # 4. 构建结果
        return {
            "front_text": front_text,
            "enhanced_back": enhanced_back
        }

    def enhance_cards(
        self,
        input_df: pd.DataFrame,
        cache_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        批量增强卡片

        Args:
            input_df: 输入 DataFrame，必须包含 front_text 和 back_text 列
            cache_file: 缓存文件路径（支持断点续传）

        Returns:
            pd.DataFrame: 包含增强后卡片的 DataFrame
        """
        # 检查输入列
        required_columns = ["front_text", "back_text"]
        if not all(col in input_df.columns for col in required_columns):
            raise ValueError(f"输入数据缺少必需的列: {required_columns}")

        # 检查是否有缓存
        start_index = 0
        if cache_file and Path(cache_file).exists():
            self.logger.info(f"发现缓存文件，从断点继续...")
            cache_df = pd.read_csv(cache_file)

            # 验证缓存列匹配
            required_cache_columns = ["front_text", "enhanced_back"]
            if all(col in cache_df.columns for col in required_cache_columns):
                start_index = len(cache_df)
                self.logger.info(f"已完成 {start_index} 条，剩余 {len(input_df) - start_index} 条")
            else:
                self.logger.warning("缓存文件的列与当前 Profile 不匹配，将重新生成")
                start_index = 0

        # 初始化结果
        results = []

        # 增强卡片
        request_delay = self.global_settings.get("request_delay", 1.0)
        max_retries = self.global_settings.get("max_retries", 3)
        save_interval = self.global_settings.get("save_interval", 10)

        for index in tqdm(range(start_index, len(input_df)), desc="增强卡片"):
            front_text = input_df.loc[index, "front_text"]
            back_text = input_df.loc[index, "back_text"]

            try:
                # 增强卡片
                enhanced_card = self.enhance_card(front_text, back_text)
                results.append(enhanced_card)

                self.logger.info(f"✅ 第 {index + 1}/{len(input_df)} 条增强成功")

                # 定期保存进度
                if cache_file and (index + 1) % save_interval == 0:
                    df = pd.DataFrame(results)
                    df.to_csv(cache_file, index=False)
                    self.logger.info(f"💾 进度已保存（已完成 {index + 1} 条）")

                # 避免触发 API 速率限制
                time.sleep(request_delay)

            except Exception as e:
                self.logger.error(f"❌ 第 {index + 1} 条处理失败: {e}")
                # 创建一个部分填充的卡片
                results.append({
                    "front_text": front_text,
                    "enhanced_back": f"[增强失败: {str(e)[:100]}...]\n\n原始内容:\n{back_text}"
                })

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
        print(f"💡 请复制 config_v4.example.json 为 {config_file} 并填写配置")
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


def load_input_data(source: str) -> pd.DataFrame:
    """
    从多种来源加载输入数据
    要求: 数据必须包含至少两列（Front, Back）
    支持: .txt (Tab分隔), .csv, .xlsx
    """
    logger = logging.getLogger(__name__)
    source_path = Path(source)

    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source}")

    if source_path.suffix == '.txt':
        # 读取 Tab 分隔的文本文件
        df = pd.read_csv(source, sep='\t', encoding='utf-8')
        # 如果没有列名，默认第一列是 Front，第二列是 Back
        if df.columns[0].startswith('Unnamed'):
            df = pd.read_csv(source, sep='\t', header=None, encoding='utf-8', names=['Front', 'Back'])
        logger.info(f"从 TXT 文件加载 {len(df)} 条数据")
        # 重命名列为 front_text 和 back_text
        df.columns = ['front_text', 'back_text']
        return df

    elif source_path.suffix == '.csv':
        df = pd.read_csv(source, encoding='utf-8')
        # 确保有至少两列
        if len(df.columns) < 2:
            raise ValueError("CSV 文件至少需要两列数据")
        # 取前两列
        df = df.iloc[:, :2]
        df.columns = ['front_text', 'back_text']
        logger.info(f"从 CSV 文件加载 {len(df)} 条数据")
        return df

    elif source_path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(source)
        # 确保有至少两列
        if len(df.columns) < 2:
            raise ValueError("Excel 文件至少需要两列数据")
        # 取前两列
        df = df.iloc[:, :2]
        df.columns = ['front_text', 'back_text']
        logger.info(f"从 Excel 文件加载 {len(df)} 条数据")
        return df

    else:
        raise ValueError(f"不支持的文件格式: {source_path.suffix}")


def export_to_anki(df: pd.DataFrame, filename: str, encoding: str = 'utf-8'):
    """导出为 Anki 可识别的格式 (Tab 分隔，两列)"""
    logger = logging.getLogger(__name__)

    # 创建副本，避免修改原数据
    export_df = df.copy()

    # 只导出 Front 和 Enhanced Back 两列
    output_df = pd.DataFrame({
        'Front': export_df['front_text'],
        'Back': export_df['enhanced_back']
    })

    # 替换换行符（但在 Anki 中可以使用 <br> 或 <br/>）
    for col in output_df.columns:
        output_df[col] = output_df[col].astype(str).str.replace('\r\n', '<br>', regex=False)
        output_df[col] = output_df[col].astype(str).str.replace('\n', '<br>', regex=False)
        output_df[col] = output_df[col].astype(str).str.replace('\t', '    ', regex=False)

    # 导出
    output_df.to_csv(filename, sep='\t', index=False, header=False, encoding=encoding)
    logger.info(f"✅ 文件已保存: {filename}")
    logger.info(f"📊 共 {len(df)} 张卡片")

    # 生成统计报告
    print("\n" + "="*50)
    print("增强完成！统计信息：")
    print(f"  总卡片数: {len(df)}")
    print(f"  字段数: 2 (Front + Enhanced Back)")
    print(f"  导出文件: {filename}")
    print("="*50)


# ================= 主程序 =================
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Anki Card Enhancer: 基于已有内容增强 Anki 卡片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用配置文件中指定的 Profile
  python anki_enhancer.py -c config.json

  # 指定输入文件
  python anki_enhancer.py -c config.json -i notes.txt

  # 指定输出文件
  python anki_enhancer.py -c config.json -i notes.txt -o enhanced.txt

  # 列出所有可用的 Profiles
  python anki_enhancer.py -c config.json --list-profiles

  # 临时切换 Profile
  python anki_enhancer.py -c config.json -p vocabulary_enhancement

  # 清除缓存重新生成
  python anki_enhancer.py -c config.json --clear-cache

数据格式要求:
  输入文件必须包含两列（Tab 或逗号分隔）:
  - 第一列: Front (正面 - 需要记忆的内容)
  - 第二列: Back (背面 - 原始内容)

  输出文件包含两列:
  - 第一列: Front (正面)
  - 第二列: Enhanced Back (增强后的背面)
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
        logger.info("Anki Card Enhancer 启动")
        logger.info(f"配置文件: {args.config}")
        logger.info("="*50)

        # 3. 处理 --list-profiles 参数
        if args.list_profiles:
            profile_manager = ProfileManager(config.get("profiles", {}))
            profiles = profile_manager.list_profiles()
            print("\n可用的增强 Profiles:")
            print("="*50)
            for name in profiles:
                profile = profile_manager.get_profile(name)
                print(f"\n[{name}]")
                print(f"  描述: {profile.description}")
            print("\n" + "="*50)
            return 0

        # 4. 命令行参数覆盖配置文件
        if args.profile:
            global_settings["active_profile"] = args.profile
        if args.input:
            global_settings["input_file"] = args.input
        if args.output:
            global_settings["output_file"] = args.output

        # 5. 初始化增强器
        enhancer = AnkiCardEnhancer(config)

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
        input_df = load_input_data(input_file)
        logger.info(f"数据加载完成，共 {len(input_df)} 条")

        # 8. 增强卡片
        logger.info("开始增强 Anki 卡片...")
        enhanced_df = enhancer.enhance_cards(
            input_df,
            cache_file=cache_file
        )

        # 9. 打印预览
        print("\n--- 数据预览（前3条）---")
        try:
            for idx in range(min(3, len(enhanced_df))):
                print(f"\n【卡片 {idx + 1}】")
                print(f"正面:\n{enhanced_df.loc[idx, 'front_text']}")
                print(f"\n背面（前200字符）:\n{enhanced_df.loc[idx, 'enhanced_back'][:200]}...")
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            print(f"[预览显示错误: {e}]")
            print("数据已成功处理，文件将正常保存。")

        # 10. 导出
        output_file = global_settings.get("output_file", "anki_enhanced.txt")
        output_encoding = global_settings.get("output_encoding", "utf-8")
        export_to_anki(enhanced_df, output_file, encoding=output_encoding)

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
