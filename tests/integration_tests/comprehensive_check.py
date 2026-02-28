#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
综合校验脚本：检查test_extracted.json的数据完整性、错误处理和结构
"""

import json
import re

def comprehensive_check():
    """综合检查数据文件"""
    print("开始综合校验 test_extracted.json ...")

    # 读取文件
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f"总项目数: {len(data)}")

    # 1. 检查是否有错误条目
    error_items = []
    for i, item in enumerate(data):
        if isinstance(item, dict):
            if 'error' in item and item['error']:
                error_items.append((i, item))

    if error_items:
        print(f"\n[WARN] 发现 {len(error_items)} 个错误条目:")
        for idx, error_item in error_items:
            print(f"  - 位置 {idx}: {error_item.get('error', 'Unknown error')}")
    else:
        print("\n[OK] 未发现错误条目")

    # 2. 验证所有项目的基本结构
    invalid_items = []
    for i, item in enumerate(data):
        required_fields = ['type', 'number', 'content']
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            invalid_items.append((i, item, missing_fields))

    if invalid_items:
        print(f"\n[WARN] 发现 {len(invalid_items)} 个结构不完整的项目:")
        for idx, item, missing in invalid_items:
            print(f"  - 位置 {idx}: 缺少字段 {missing}, 项目类型: {item.get('type', 'unknown')}")
    else:
        print("[OK] 所有项目结构完整")

    # 3. 统计各类项目
    contexts = [item for item in data if item.get('type') == 'context']
    questions = [item for item in data if item.get('type') == 'question']
    print(f"\n[STAT] 项目统计: {len(contexts)} 个context, {len(questions)} 个question")

    # 4. 验证编号完整性
    context_numbers = set(item['number'] for item in contexts)
    expected_contexts = {"一", "二", "三", "四", "五", "六", "七"}
    missing_contexts = expected_contexts - context_numbers
    extra_contexts = context_numbers - expected_contexts

    if missing_contexts:
        print(f"\n[WARN] 缺少 context 编号: {missing_contexts}")
    if extra_contexts:
        print(f"[WARN] 额外的 context 编号: {extra_contexts}")
    if not missing_contexts and not extra_contexts:
        print("[OK] Context 编号完整")

    # 5. 验证 question 编号连续性
    question_numbers = []
    for item in questions:
        num_str = item['number']
        if '（' in num_str and '）' in num_str:
            # 处理带括号的编号如 "22（1）" -> 作为 22 的一部分
            main_num = re.search(r'(\d+)', num_str)
            if main_num:
                question_numbers.append(int(main_num.group(1)))
        elif num_str.isdigit():
            question_numbers.append(int(num_str))

    question_numbers = sorted(set(question_numbers))  # 去重并排序
    expected_question_range = list(range(min(question_numbers), max(question_numbers) + 1))
    missing_questions = [n for n in expected_question_range if n not in question_numbers]

    if missing_questions:
        print(f"\n[WARN] 缺少 question 编号: {missing_questions}")
    else:
        print("[OK] Question 编号连续完整")

    # 6. 检查数据顺序 (context 后面跟着相关的问题)
    print("\n[ORDER] 数据顺序检查:")
    prev_type = None
    pair_count = 0
    for i, item in enumerate(data):
        current_type = item.get('type')
        number = item.get('number')

        if prev_type == 'context' and current_type == 'question':
            print(f"  {i+1:2d}. [OK] Context后跟Question: {number}")
            pair_count += 1
        elif prev_type == 'question' and current_type == 'question':
            print(f"  {i+1:2d}. [OK] 同一Context下的连续Question: {number}")
        elif prev_type == 'question' and current_type == 'context':
            print(f"  {i+1:2d}. [OK] 新Context开始: {number}")
        elif prev_type == 'context' and current_type == 'context':
            print(f"  {i+1:2d}. [WARN] Context后直接跟Context: {number}")
        else:
            print(f"  {i+1:2d}. - {current_type}: {number}")

        prev_type = current_type

    print(f"\n总共有 {pair_count} 个 context-question 配对")

    # 7. 检查字段完整性
    print("\n[FIELD] 字段完整性检查:")
    all_good = True
    for i, item in enumerate(data):
        if item.get('type') == 'question':
            if not item.get('answer') or not item.get('analysis'):
                print(f"  {i+1:2d}. [WARN] Question 缺少 answer 或 analysis: {item.get('number')}")
                all_good = False

    if all_good:
        print("  [OK] 所有 Question 项目包含 answer 和 analysis")

    print(f"\n[SUCCESS] 综合校验完成")
    print(f"- 总项目数: {len(data)}")
    print(f"- Contexts: {len(contexts)}")
    print(f"- Questions: {len(questions)}")
    print(f"- 错误项目: {len(error_items)}")
    print(f"- 配对数: {pair_count}")

    return len(error_items) == 0 and len(missing_contexts) == 0 and len(missing_questions) == 0

if __name__ == "__main__":
    success = comprehensive_check()
    if success:
        print("\n[PASS] 所有校验通过！数据完整且结构正确。")
    else:
        print("\n[FAIL] 某些校验失败，请检查上述问题。")