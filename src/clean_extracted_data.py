"""
数据清洗脚本：从提取的 Anki 卡片中提取古文词语和释义
"""
import re
import pandas as pd
from pathlib import Path

def clean_html_tags(text):
    """移除HTML标签"""
    # 移除 <b> 和 </b>
    text = text.replace('<b>', '').replace('</b>', '')
    # 移除 <div> 和 </div>
    text = text.replace('<div>', '').replace('</div>', '')
    # 移除 <br> 和 </br>
    text = text.replace('<br>', ' ').replace('</br>', ' ')
    text = text.replace('<br/>', ' ').replace('<br />', ' ')
    return text

def extract_cards(input_file, output_file):
    """提取并清洗卡片数据"""
    print(f"正在读取文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cards = []
    current_card = []

    for line in lines:
        line = line.strip()
        # 跳过空行和标题行
        if not line or line.startswith('=') or '提取结果' in line or '源文件' in line or '提取时间' in line or '卡片数量' in line:
            continue

        # 提取卡片内容
        if line.startswith('卡片 '):
            # 提取卡片编号和内容
            match = re.match(r'卡片\s+(\d+):\s*(.+)', line)
            if match:
                card_num = match.group(1)
                content = match.group(2)

                # 分隔句子和释义
                if ' | ' in content:
                    parts = content.split(' | ', 1)
                    sentence = parts[0].strip()
                    meaning = parts[1].strip() if len(parts) > 1 else ''
                else:
                    # 如果没有 | 分隔符，尝试其他分隔方式
                    if '|' in content:
                        parts = content.split('|', 1)
                        sentence = parts[0].strip()
                        meaning = parts[1].strip() if len(parts) > 1 else ''
                    else:
                        sentence = content
                        meaning = ''

                # 清洗HTML标签
                sentence = clean_html_tags(sentence)
                meaning = clean_html_tags(meaning)

                # 清理多余空格
                sentence = ' '.join(sentence.split())
                meaning = ' '.join(meaning.split())

                if sentence and meaning:
                    cards.append({
                        'card_num': card_num,
                        'front_text': sentence,  # 包含词语的句子
                        'back_text': meaning     # 词语释义
                    })

    print(f"共提取 {len(cards)} 张卡片")

    # 保存为CSV
    df = pd.DataFrame(cards)
    df = df[['front_text', 'back_text']]  # 只保留需要的两列
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"数据已保存到: {output_file}")

    # 保存为Tab分隔的txt（备用）
    txt_file = output_file.replace('.csv', '.txt')
    df.to_csv(txt_file, sep='\t', index=False, header=False, encoding='utf-8')
    print(f"Tab分隔格式已保存到: {txt_file}")

    return df

if __name__ == '__main__':
    input_file = r'C:\Users\user\WPSDrive\203612604\WPS云盘\申悦文档\高考准备-anki\Github\anki-assistant\extracted_120\提取结果.txt'
    output_file = r'C:\Users\user\WPSDrive\203612604\WPS云盘\申悦文档\高考准备-anki\Github\anki-assistant\cleaned_ancient_words.csv'

    df = extract_cards(input_file, output_file)

    # 显示前5条数据
    print("\n数据预览（前5条）:")
    print(df.head(10))
