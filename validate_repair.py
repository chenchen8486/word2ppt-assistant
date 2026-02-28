#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证test_extracted.json文件中的题目序列完整性
"""

import json
import re


def validate_questions_sequence():
    """
    验证题目序列是否完整
    """
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取所有的数字题目编号
    numbers = []
    for item in data:
        if 'number' in item:
            num_str = item['number']
            # 处理普通的数字题目（如 "1", "2", "7" 等）
            if num_str.isdigit():
                numbers.append(int(num_str))
            # 处理带括号的题目（如 "22（1）", "22（2）"）
            elif '（' in num_str and '）' in num_str:
                main_num = re.search(r'(\d+)（', num_str)
                if main_num:
                    numbers.append(int(main_num.group(1)))

    # 去重并排序
    unique_numbers = sorted(list(set(numbers)))

    print(f"Found {len(unique_numbers)} unique question numbers")
    print(f"Question numbers range: {min(unique_numbers)} to {max(unique_numbers)}")

    # 检查是否有缺失的题目
    expected_range = list(range(min(unique_numbers), max(unique_numbers) + 1))
    missing = [n for n in expected_range if n not in unique_numbers]

    if missing:
        print(f"Missing question numbers: {missing}")
        return False
    else:
        print("All question numbers present in sequence!")

        # 特别检查之前缺失的题目
        previously_missing = [8, 9, 10, 11, 12, 13, 16, 18, 19, 20, 21, 23]
        found_previously_missing = [n for n in previously_missing if n in unique_numbers]
        print(f"Previously missing questions now found: {found_previously_missing}")

        return True


def validate_content():
    """
    验证JSON内容的基本结构
    """
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计各种类型的项目
    contexts = 0
    questions = 0

    for item in data:
        if 'type' in item:
            if item['type'] == 'context':
                contexts += 1
            elif item['type'] == 'question':
                questions += 1

    print(f"Total items: {len(data)}")
    print(f"Context items: {contexts}")
    print(f"Question items: {questions}")

    return len(data) > 0 and questions > 0


if __name__ == "__main__":
    print("=== Validating test_extracted.json ===")

    print("\n1. Checking question sequence...")
    seq_valid = validate_questions_sequence()

    print("\n2. Checking content structure...")
    content_valid = validate_content()

    print(f"\n=== Validation Result ===")
    if seq_valid and content_valid:
        print("✓ SUCCESS: All validations passed!")
        print("✓ No missing questions detected")
        print("✓ Content structure is valid")
    else:
        print("✗ FAILED: Some validations failed")
        if not seq_valid:
            print("  - Sequence validation failed")
        if not content_valid:
            print("  - Content validation failed")