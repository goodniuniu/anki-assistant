"""
数据清洗脚本：处理高中英语词汇文件
将"单词+音标+词性释义+考查次数"格式转换为标准两列格式
"""
import pandas as pd
import re
from pathlib import Path

def clean_vocab_file(input_file, output_file):
    """清洗词汇文件"""
    print(f"正在读取文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    words = []
    in_data_section = False

    for line in lines:
        line = line.strip()

        # 跳过空行和说明文字
        if not line:
            continue
        if line.startswith('以下是'):
            in_data_section = True
            continue
        if line.startswith('```'):
            continue

        # 处理单词行
        if in_data_section or '\t' in line:
            # 分割字段
            parts = line.split('\t')

            if len(parts) >= 3:
                word = parts[0].strip()
                phonetic = parts[1].strip() if len(parts) > 1 else ''
                meaning = parts[2].strip() if len(parts) > 2 else ''
                frequency = parts[3].strip() if len(parts) > 3 else ''

                # 跳过标题行
                if word == '单词' or word == 'anxious':
                    in_data_section = True
                    continue

                # 组合 front_text (单词 + 音标)
                front_text = f"{word} {phonetic}".strip()

                # 组合 back_text (词性释义 + 考查次数)
                if meaning and meaning != '无':
                    back_text = meaning
                    if frequency and frequency != '无':
                        back_text += f" [考查{frequency}次]"
                else:
                    back_text = "待补充释义"

                words.append({
                    'front_text': front_text,
                    'back_text': back_text,
                    'word': word,
                    'phonetic': phonetic,
                    'meaning': meaning,
                    'frequency': frequency
                })

    print(f"共提取 {len(words)} 个单词")

    # 保存为CSV
    df = pd.DataFrame(words)
    df = df[['front_text', 'back_text']]  # 只保留标准两列
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"数据已保存到: {output_file}")

    # 保存为Tab分隔的txt（备用）
    txt_file = output_file.replace('.csv', '.txt')
    df.to_csv(txt_file, sep='\t', index=False, header=False, encoding='utf-8')
    print(f"Tab分隔格式已保存到: {txt_file}")

    return df

if __name__ == '__main__':
    input_file = r'data/input/raw/高一上学期期末-单词191.txt'
    output_file = r'data/cleaned/cleaned_exam_vocab_191.csv'

    df = clean_vocab_file(input_file, output_file)

    # 显示前5条数据
    print("\n数据预览（前5条）:")
    for idx in range(min(5, len(df))):
        print(f"\n单词 {idx + 1}:")
        print(f"  正面: {df.loc[idx, 'front_text']}")
        print(f"  背面: {df.loc[idx, 'back_text']}")
