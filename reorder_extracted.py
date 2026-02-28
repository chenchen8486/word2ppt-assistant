#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根据test_chunks.json的原始顺序，重构test_extracted.json的顺序
确保每个context后跟其相关的questions，而不是将所有context和question分离
"""

import json
import re

def reorder_extracted_by_chunks():
    # 读取chunks文件以获取正确的顺序
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    # 读取当前的extracted文件
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8-sig') as f:
        extracted_data = json.load(f)

    # 创建一个映射，将题目编号映射到具体的question对象
    question_map = {}
    for item in extracted_data:
        if item.get('type') == 'question':
            number = item.get('number')
            if number:
                question_map[number] = item

    # 创建一个映射，将context编号映射到context对象
    context_map = {}
    for item in extracted_data:
        if item.get('type') == 'context':
            number = item.get('number')
            if number:
                # 移除中文编号后的中文字符，比如"一、" -> "一"
                clean_number = number.replace('、', '')
                context_map[clean_number] = item

    # 重构数据：根据chunks的顺序，每个context后跟其相关的问题
    reordered_data = []

    for chunk in chunks_data:
        chunk_number = chunk.get('number', '').replace('、', '')  # 清理编号

        # 添加对应的context
        if chunk_number in context_map:
            context_item = context_map[chunk_number]
            reordered_data.append(context_item)

            # 根据chunk内容中的数字，找到相关的questions
            chunk_content = chunk.get('content', '')

            # 从chunk内容中找出可能包含的题目编号
            # 从当前的chunk编号开始，寻找接下来可能出现的题目
            possible_numbers = []

            # 找出chunk内容中包含的数字（表示题目编号）
            # 根据chunk中的信息，我们可以知道这个section应该包含哪些题目
            if chunk_number == "一":
                possible_numbers = ["1", "2", "3"]
            elif chunk_number == "二":
                possible_numbers = ["4", "5", "6"]
            elif chunk_number == "三":
                possible_numbers = ["7", "8", "9", "10", "11", "12", "13"]
            elif chunk_number == "四":
                possible_numbers = ["14", "15", "16"]
            elif chunk_number == "五":
                possible_numbers = ["17", "18", "19", "20", "21"]
            elif chunk_number == "六":
                possible_numbers = ["22（1）", "22（2）", "23"]
            elif chunk_number == "七":
                possible_numbers = ["24"]
            else:
                # 尝试从内容中提取可能的数字
                numbers_in_chunk = re.findall(r'\b\d+', chunk_content)
                for num in numbers_in_chunk:
                    # 检查是否是题目编号（通常在某个范围内）
                    if 1 <= int(num) <= 24:
                        possible_numbers.append(num)

            # 添加对应的questions
            for num in possible_numbers:
                # 也检查带括号的变体，如"22（1）"和"22（2）"
                bracket_variants = [num, f"{num}（1）", f"{num}（2）"]

                for variant in bracket_variants:
                    if variant in question_map:
                        question_item = question_map[variant]
                        reordered_data.append(question_item)

    # 保存重构后的数据
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8-sig') as f:
        json.dump(reordered_data, f, ensure_ascii=False, indent=2)

    print(f"Reordered test_extracted.json with {len(reordered_data)} items")
    print("Structure:")
    for i, item in enumerate(reordered_data[:20]):  # 显示前20个项目
        item_type = item.get('type', 'unknown')
        number = item.get('number', 'no_number')
        print(f"{i+1}. {item_type}: {number}")

    if len(reordered_data) > 20:
        print("...")

    return reordered_data

def verify_order(data):
    """验证数据顺序是否正确"""
    context_count = 0
    question_count = 0

    for item in data:
        if item.get('type') == 'context':
            context_count += 1
        elif item.get('type') == 'question':
            question_count += 1

    print(f"\nVerification:")
    print(f"Total contexts: {context_count}")
    print(f"Total questions: {question_count}")

    # 检查是否每个context后面跟着相关的问题
    prev_was_context = False
    valid_pairs = 0

    for item in data:
        if item.get('type') == 'context':
            prev_was_context = True
        elif item.get('type') == 'question' and prev_was_context:
            # 这是一个context后跟question的正确配对
            prev_was_context = False  # 重置标志，直到遇到下一个context
            valid_pairs += 1

    print(f"Context-question pairs: {valid_pairs}")

if __name__ == "__main__":
    print("Reordering test_extracted.json based on chunks structure...")
    reordered_data = reorder_extracted_by_chunks()
    print("\nDone!")

    # 验证结果
    verify_order(reordered_data)