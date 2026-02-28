#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证修复后的test_extracted.json文件结构是否正确
"""

import json

def validate_structure():
    """验证数据结构是否正确"""
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f"总项目数: {len(data)}")

    contexts = [item for item in data if item.get('type') == 'context']
    questions = [item for item in data if item.get('type') == 'question']

    print(f"Contexts: {len(contexts)}")
    print(f"Questions: {len(questions)}")

    # 验证顺序
    print("\n数据顺序验证:")
    for i, item in enumerate(data):
        item_type = item.get('type', 'unknown')
        number = item.get('number', 'no_number')
        print(f"{i+1:2d}. {item_type}: {number}")

    # 验证题目连续性
    question_numbers = []
    for item in data:
        if item.get('type') == 'question':
            num_str = item.get('number', '')
            # 处理带括号的编号
            if '（' in num_str and '）' in num_str:
                main_num = num_str.split('（')[0]
                question_numbers.append(int(main_num))
            elif num_str.isdigit():
                question_numbers.append(int(num_str))

    question_numbers = sorted(set(question_numbers))  # 去重并排序

    print(f"\n发现的题目编号: {question_numbers}")
    print(f"题目编号范围: {min(question_numbers)} 到 {max(question_numbers)}")

    # 检查连续性
    expected_range = list(range(min(question_numbers), max(question_numbers) + 1))
    missing = [n for n in expected_range if n not in question_numbers]

    if missing:
        print(f"缺失的题目编号: {missing}")
        return False
    else:
        print("所有题目编号连续，无缺失")
        return True

if __name__ == "__main__":
    print("验证修复后的test_extracted.json文件结构...")
    success = validate_structure()
    if success:
        print("\n验证通过: 数据结构正确")
    else:
        print("\n验证失败: 数据结构有问题")