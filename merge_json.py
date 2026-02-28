import json

def merge_json_files(main_file, additional_file, output_file=None):
    """
    将additional_file中的数据合并到main_file中
    """
    # 读取主文件
    with open(main_file, 'r', encoding='utf-8-sig') as f:
        main_data = json.load(f)

    # 读取附加文件
    with open(additional_file, 'r', encoding='utf-8-sig') as f:
        additional_data = json.load(f)

    print(f'主文件数据长度: {len(main_data)}')
    print(f'附加文件数据长度: {len(additional_data)}')

    # 将附加数据添加到主数据中
    merged_data = main_data + additional_data

    # 按编号排序
    def sort_key(item):
        num_str = item.get('number', '')
        # 处理带括号的编号如 "22(1)", "22(2)"
        if '(' in num_str and ')' in num_str:
            main_num, sub_num = num_str.split('(')
            sub_num = sub_num.rstrip(')')
            # 将所有部分转换为字符串进行比较
            try:
                main_int = int(main_num) if main_num.isdigit() else 0
                sub_int = int(sub_num) if sub_num.isdigit() else 0
                return (main_int, sub_int)  # 返回整数元组
            except:
                return (0, 0)  # 默认返回整数元组
        else:
            try:
                # 对纯数字编号进行排序
                num_int = int(num_str) if num_str.isdigit() else 0
                return (num_int, 0)  # 返回整数元组
            except:
                # 如果不是数字，按字母顺序排序，使用ASCII值作为数字
                return (sum(ord(c) for c in num_str), 0)  # 返回整数元组

    merged_data.sort(key=sort_key)

    # 打印合并后的数据结构
    print('\n合并后的数据结构:')
    for i, item in enumerate(merged_data, 1):
        if item.get('type') == 'context':
            print(f' {i:2d}. context: {item.get("number")}')
        elif item.get('type') == 'question':
            print(f' {i:2d}. question: {item.get("number")}')
        else:
            print(f' {i:2d}. unknown: {item.get("number")}')

    print(f'\n总计: {len(merged_data)} 个项目')
    print(f'Contexts: {sum(1 for item in merged_data if item.get("type") == "context")}, '
          f'Questions: {sum(1 for item in merged_data if item.get("type") == "question")}')

    # 确定输出文件名
    if output_file is None:
        output_file = main_file.replace('.json', '_merged.json')

    # 保存合并后的数据
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    print(f'\n合并完成! 输出到: {output_file}')

    return merged_data

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        main_file = sys.argv[1]
        additional_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        main_file = 'data/02_temp_build/test_extracted.json'
        additional_file = 'data/02_temp_build/missing_parts_fixed_extracted_fixed.json'
        output_file = 'data/02_temp_build/test_extracted_merged.json'

    merge_json_files(main_file, additional_file, output_file)