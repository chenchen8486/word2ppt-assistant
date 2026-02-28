#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整修复extracted.json文件，从原始混乱结构中提取所有有效数据
支持任意文档名称（包括中文命名）
"""

import json
import re
import sys
from pathlib import Path

def extract_data_from_error_string(error_str):
    """从错误字符串中提取JSON数据"""
    # 查找JSON数组的开始和结束
    start_pos = error_str.find('[\n')
    if start_pos == -1:
        start_pos = error_str.find('[{')

    if start_pos != -1:
        # 计算括号匹配来找结束位置
        brace_level = 0
        start_brace = 0

        # 从找到的开始位置往后扫描
        for i, char in enumerate(error_str[start_pos:], start_pos):
            if char == '[':
                start_brace += 1
            elif char == ']':
                start_brace -= 1
                if start_brace == 0:
                    # 找到匹配的结束
                    json_str = error_str[start_pos:i+1]

                    # 修复常见问题
                    json_str = json_str.replace('\\n', '\n').replace('\\_', '_')

                    # 移除可能的拖尾逗号
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                    try:
                        data = json.loads(json_str)
                        if isinstance(data, list):
                            return data
                    except json.JSONDecodeError:
                        # 尝试更积极的修复
                        try:
                            # 用正则表达式提取所有可能的对象
                            obj_pattern = r'\{\s*"type"[^}\]]+\}'
                            matches = re.findall(obj_pattern, json_str)

                            recovered_data = []
                            for match in matches:
                                try:
                                    obj = json.loads(match)
                                    if 'type' in obj and 'number' in obj:
                                        recovered_data.append(obj)
                                except:
                                    continue

                            if recovered_data:
                                return recovered_data
                        except:
                            pass

    return None

def full_repair_extracted_json(input_file, output_file=None):
    """
    完全修复extracted.json文件

    Args:
        input_file: 输入的JSON文件路径
        output_file: 输出文件路径（如果未指定，则覆盖原文件）
    """
    # 如果没有指定输出文件，则使用输入文件路径
    if output_file is None:
        output_file = input_file

    # 读取原始文件
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        raw_content = f.read()

    # 解析原始数据结构
    try:
        original_data = json.loads(raw_content)
    except json.JSONDecodeError:
        print(f"原始文件JSON格式错误，无法修复: {input_file}")
        return

    all_items = []
    processed_numbers = set()  # 追踪已处理的号码，避免重复

    for item in original_data:
        if isinstance(item, list):
            # 处理列表项
            for sub_item in item:
                if isinstance(sub_item, dict):
                    if 'type' in sub_item and 'number' in sub_item:
                        number = sub_item['number']
                        if number not in processed_numbers:
                            # 确保必要字段存在
                            sub_item.setdefault('content', '')
                            sub_item.setdefault('answer', '')
                            sub_item.setdefault('analysis', '')
                            all_items.append(sub_item)
                            processed_numbers.add(number)
                        else:
                            print(f"跳过重复项目: {number}")
        elif isinstance(item, dict):
            if 'error' in item and item['error'] and "Failed to parse LLM response:" in item['error']:
                # 从错误信息中提取数据
                recovered_data = extract_data_from_error_string(item['error'])
                if recovered_data and isinstance(recovered_data, list):
                    for recovered_item in recovered_data:
                        if isinstance(recovered_item, dict) and 'type' in recovered_item and 'number' in recovered_item:
                            number = recovered_item['number']
                            if number not in processed_numbers:
                                recovered_item.setdefault('content', '')
                                recovered_item.setdefault('answer', '')
                                recovered_item.setdefault('analysis', '')
                                all_items.append(recovered_item)
                                processed_numbers.add(number)
                            else:
                                print(f"跳过从错误中恢复的重复项目: {number}")
            elif 'type' in item and 'number' in item:
                # 正常的数据项
                number = item['number']
                if number not in processed_numbers:
                    item.setdefault('content', '')
                    item.setdefault('answer', '')
                    item.setdefault('analysis', '')
                    all_items.append(item)
                    processed_numbers.add(number)
                else:
                    print(f"跳过重复项目: {number}")

    # 按照数字顺序排序
    def sort_key(item):
        number = item.get('number', '')

        # 处理带括号的编号，如 "22（1）"
        if '（' in number and '）' in number:
            match = re.match(r'(\d+)（(\d+)）', number)
            if match:
                main_num, sub_num = match.groups()
                return int(main_num) + int(sub_num)/10.0

        # 处理纯数字
        if number.isdigit():
            return int(number)

        # 处理中文数字
        chinese_nums = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7}
        if number in chinese_nums:
            return chinese_nums[number] * 0.1  # 中文数字排在前面

        # 其他情况，按字符排序
        return ord(number[0]) * 1000 if number else 9999

    all_items.sort(key=sort_key)

    # 保存修复后的文件
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"修复完成！总共 {len(all_items)} 个项目，保存到: {output_file}")

    # 显示统计信息
    contexts = [item for item in all_items if item.get('type') == 'context']
    questions = [item for item in all_items if item.get('type') == 'question']

    print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

    # 显示结构
    print("\n数据结构:")
    for i, item in enumerate(all_items):
        item_type = item.get('type', 'unknown')
        number = item.get('number', 'no_number')
        print(f"{i+1:2d}. {item_type}: {number}")

    return all_items

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python full_repair_extracted.py <input_file> [output_file]")
        print("示例: python full_repair_extracted.py data/02_temp_build/my_chinese_doc_extracted.json")
        sys.exit(1)

    input_file = sys.argv[1]

    # 检查输入文件是否存在
    if not Path(input_file).exists():
        print(f"错误: 输入文件不存在: {input_file}")
        sys.exit(1)

    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    print(f"开始完全修复文件: {input_file}")
    result = full_repair_extracted_json(input_file, output_file)
    print("修复完成!")