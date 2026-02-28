#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通用JSON数据修复脚本
修复最常见的extracted.json数据质量问题
"""

import json
import re
import sys
from pathlib import Path

def repair_common_json_issues(input_file, output_file=None):
    """
    修复extracted.json中的常见问题

    Args:
        input_file: 输入的JSON文件路径
        output_file: 输出文件路径（如果未指定，则覆盖原文件）
    """
    if output_file is None:
        output_file = input_file

    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f'原始数据长度: {len(data)}')

    # 统计原始状态
    original_errors = sum(1 for item in data if 'error' in item)
    original_contexts = sum(1 for item in data if item.get('type') == 'context')
    original_questions = sum(1 for item in data if item.get('type') == 'question')

    print(f'原始数据统计: {original_errors} 错误, {original_contexts} contexts, {original_questions} questions')

    # 修复数据
    repaired_data = []

    for item in data:
        # 跳过真正的错误条目（保留有意义的错误）
        if isinstance(item, dict) and 'error' in item and item.get('error') and 'original_chunk' in item:
            # 这些是真正的处理失败项，保持原样
            repaired_data.append(item)
        elif isinstance(item, dict):
            # 修复正常的项目
            required_fields = ['type', 'number', 'content']

            # 确保必需字段存在
            for field in required_fields:
                if field not in item:
                    item[field] = ''

            # 对于question类型，确保answer和analysis字段存在
            if item.get('type', '').lower() == 'question':
                item.setdefault('answer', '')
                item.setdefault('analysis', '')

            # 对于context类型，也提供默认的answer和analysis
            if item.get('type', '').lower() == 'context':
                item.setdefault('answer', '')
                item.setdefault('analysis', '')

            # 修复可能存在的非法字符
            for field in ['content', 'answer', 'analysis']:
                if field in item and isinstance(item[field], str):
                    # 清理可能的非法转义字符
                    item[field] = item[field].replace('\\_', '_').replace('\\*', '*')

            repaired_data.append(item)
        elif isinstance(item, list):
            # 如果项目是列表，展开它
            for sub_item in item:
                if isinstance(sub_item, dict):
                    # 修复子项目
                    required_fields = ['type', 'number', 'content']

                    for field in required_fields:
                        if field not in sub_item:
                            sub_item[field] = ''

                    if sub_item.get('type', '').lower() == 'question':
                        sub_item.setdefault('answer', '')
                        sub_item.setdefault('analysis', '')

                    if sub_item.get('type', '').lower() == 'context':
                        sub_item.setdefault('answer', '')
                        sub_item.setdefault('analysis', '')

                    # 修复非法字符
                    for field in ['content', 'answer', 'analysis']:
                        if field in sub_item and isinstance(sub_item[field], str):
                            sub_item[field] = sub_item[field].replace('\\_', '_').replace('\\*', '*')

                    repaired_data.append(sub_item)

    # 按编号排序
    def sort_key(item):
        num_str = item.get('number', '')
        # 处理带括号的编号如 "22(1)", "22(2)"
        if '(' in num_str and ')' in num_str:
            main_num, sub_num = num_str.split('(')
            sub_num = sub_num.rstrip(')')
            try:
                return (float(main_num), float(sub_num))
            except:
                return (num_str, 0)
        elif '（' in num_str and '）' in num_str:
            # 处理中文括号
            main_num, sub_num = num_str.split('（')
            sub_num = sub_num.rstrip('）')
            try:
                return (float(main_num), float(sub_num))
            except:
                return (num_str, 0)
        else:
            try:
                # 处理中文数字
                chinese_nums = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
                if num_str in chinese_nums:
                    return (0, chinese_nums[num_str])  # 中文数字排在前面
                elif num_str.isdigit():
                    return (1, int(num_str))  # 阿拉伯数字排在后面
                else:
                    return (2, ord(num_str[0]) if num_str else 0)  # 其他字符最后
            except:
                return (2, 0)

    repaired_data.sort(key=sort_key)

    print(f'修复后数据长度: {len(repaired_data)}')

    # 统计修复后的状态
    repaired_errors = sum(1 for item in repaired_data if 'error' in item)
    repaired_contexts = sum(1 for item in repaired_data if item.get('type') == 'context')
    repaired_questions = sum(1 for item in repaired_data if item.get('type') == 'question')

    print(f'修复后数据统计: {repaired_errors} 错误, {repaired_contexts} contexts, {repaired_questions} questions')

    # 打印数据结构
    print('\n修复后的数据结构:')
    for i, item in enumerate(repaired_data[:20], 1):  # 只显示前20个项目
        item_type = item.get('type', 'unknown')
        number = item.get('number', 'no_number')
        print(f' {i:2d}. {item_type}: {number}')

    if len(repaired_data) > 20:
        print(' ...')
        for i, item in enumerate(repaired_data[-5:], len(repaired_data)-4):  # 显示最后5个项目
            item_type = item.get('type', 'unknown')
            number = item.get('number', 'no_number')
            print(f' {i:2d}. {item_type}: {number}')

    print(f'\n总计: {len(repaired_data)} 个项目')
    print(f'Contexts: {sum(1 for item in repaired_data if item.get("type") == "context")}, Questions: {sum(1 for item in repaired_data if item.get("type") == "question")}')

    # 保存修复后的数据
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(repaired_data, f, ensure_ascii=False, indent=2)

    print(f'修复完成! 输出到: {output_file}')

    return repaired_data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python generic_repair.py <input_file> [output_file]")
        print("示例: python generic_repair.py data/02_temp_build/my_doc_extracted.json")
        sys.exit(1)

    input_file = sys.argv[1]

    # 检查输入文件是否存在
    if not Path(input_file).exists():
        print(f"错误: 输入文件不存在: {input_file}")
        sys.exit(1)

    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"开始修复文件: {input_file}")
    repair_common_json_issues(input_file, output_file)