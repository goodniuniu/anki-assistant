import zipfile
import sqlite3
import os
import shutil
import argparse
import sys
from datetime import datetime

def extract_anki_apkg(apkg_path, output_folder=None, save_to_file=True):
    """
    提取Anki卡包文件内容

    参数:
        apkg_path: .apkg文件路径
        output_folder: 输出文件夹路径，如果为None则自动生成
        save_to_file: 是否将结果保存到文件
    """
    # 检查输入文件是否存在
    if not os.path.exists(apkg_path):
        print(f"[错误] 文件不存在 - {apkg_path}")
        return False

    # 自动生成输出文件夹名称（基于输入文件名）
    if output_folder is None:
        base_name = os.path.splitext(os.path.basename(apkg_path))[0]
        output_folder = f"extracted_{base_name}"

    # 1. 解压 .apkg 文件
    print(f"[解压] 正在解压: {apkg_path}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        with zipfile.ZipFile(apkg_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        print(f"[完成] 解压完成，文件位于: {output_folder}")
    except Exception as e:
        print(f"[错误] 解压失败: {e}")
        return False

    # 2. 连接到 SQLite 数据库 (collection.anki2)
    db_path = os.path.join(output_folder, "collection.anki2")

    if not os.path.exists(db_path):
        print("[错误] 未找到数据库文件 collection.anki2")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. 查询笔记内容 (Notes 表)
    try:
        cursor.execute("SELECT flds FROM notes")
        rows = cursor.fetchall()

        print(f"\n[笔记] 提取到 {len(rows)} 条笔记\n")

        # 准备输出内容
        output_lines = []
        output_lines.append(f"=" * 60)
        output_lines.append(f"Anki 卡包提取结果")
        output_lines.append(f"源文件: {apkg_path}")
        output_lines.append(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"卡片数量: {len(rows)}")
        output_lines.append(f"=" * 60)
        output_lines.append("")

        for idx, row in enumerate(rows):
            # 将分隔符替换为更容易阅读的符号
            content = row[0].replace('\x1f', ' | ')

            # 控制台输出（显示前10条和后5条）
            if idx < 10 or idx >= len(rows) - 5:
                print(f"卡片 {idx+1}: {content}")

            # 保存到输出列表
            output_lines.append(f"卡片 {idx+1}: {content}")

        if len(rows) > 15:
            print(f"\n... (省略中间 {len(rows) - 15} 条卡片) ...\n")

        # 4. 保存到文件
        if save_to_file:
            output_file = os.path.join(output_folder, "提取结果.txt")
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_lines))
                print(f"\n[保存] 结果已保存到: {output_file}")
            except Exception as e:
                print(f"[警告] 保存文件失败: {e}")

        print(f"\n[完成] 提取完成！")
        return True

    except sqlite3.Error as e:
        print(f"[错误] 读取数据库出错: {e}")
        return False
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(
        description='Anki卡包提取工具 - 从.apkg文件中提取学习卡片内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s anki_data/120.apkg                    # 使用默认输出文件夹
  %(prog)s anki_data/120.apkg -o my_output      # 指定输出文件夹
  %(prog)s anki_data/120.apkg --no-file         # 不保存到文件
  %(prog)s anki_data/*.apkg                     # 批量处理多个文件
        """
    )

    parser.add_argument(
        'input',
        help='输入的.apkg文件路径（支持通配符）'
    )
    parser.add_argument(
        '-o', '--output',
        help='输出文件夹路径（默认为 extracted_文件名）'
    )
    parser.add_argument(
        '--no-file',
        action='store_true',
        help='不保存结果到文件'
    )

    args = parser.parse_args()

    # 处理输入文件（支持通配符）
    import glob
    input_files = glob.glob(args.input)

    if not input_files:
        print(f"[错误] 未找到匹配的文件 - {args.input}")
        sys.exit(1)

    print(f"[搜索] 找到 {len(input_files)} 个文件\n")

    # 处理每个文件
    success_count = 0
    for i, apkg_file in enumerate(input_files, 1):
        print(f"\n{'='*60}")
        print(f"处理文件 [{i}/{len(input_files)}]: {apkg_file}")
        print(f"{'='*60}")

        # 如果指定了输出文件夹且只有一个文件，使用指定的文件夹
        output_folder = args.output if len(input_files) == 1 else None

        if extract_anki_apkg(apkg_file, output_folder, not args.no_file):
            success_count += 1

    # 总结
    print(f"\n{'='*60}")
    print(f"处理完成: 成功 {success_count}/{len(input_files)} 个文件")
    print(f"{'='*60}")

    sys.exit(0 if success_count == len(input_files) else 1)

if __name__ == "__main__":
    main()