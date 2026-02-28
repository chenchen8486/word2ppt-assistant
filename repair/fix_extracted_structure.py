#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复test_extracted.json文件中的错误数据和结构问题
"""

import json
import re

def fix_extracted_json_structure():
    """修复extracted.json文件结构问题"""
    # 读取当前的损坏文件
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8-sig') as f:
        raw_data = f.read()

    # 解析JSON（注意：由于数据格式混乱，我们需要先修复结构）
    # 我们先直接加载来查看当前结构
    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        print("原始JSON格式有误，需要修复")
        return

    # 过滤并修复数据
    fixed_data = []

    for item in data:
        # 跳过空数组
        if isinstance(item, list) and len(item) == 0:
            continue

        # 如果是数组（包含多个项目的结构），展开它
        if isinstance(item, list):
            for sub_item in item:
                # 检查是否是错误条目
                if isinstance(sub_item, dict) and 'error' in sub_item and sub_item['error']:
                    print(f"跳过错误条目: {sub_item.get('error', 'Unknown error')}")
                    continue
                elif isinstance(sub_item, dict) and 'error' in sub_item and not sub_item['error']:
                    # 空错误字符串，也是错误条目
                    continue
                else:
                    # 验证项目是否具有基本结构
                    if isinstance(sub_item, dict) and 'type' in sub_item and 'number' in sub_item:
                        fixed_data.append(sub_item)
                    else:
                        print(f"跳过结构不完整的条目: {sub_item}")

        # 如果是字典对象
        elif isinstance(item, dict):
            # 检查是否是错误条目
            if 'error' in item and item['error']:
                print(f"跳过错误条目: {item['error']}")
                continue
            elif 'error' in item and not item['error']:
                # 空错误字符串，也是错误条目
                continue
            else:
                # 检查是否是包含解析结果的对象
                if 'type' in item and 'number' in item:
                    fixed_data.append(item)
                else:
                    # 检查是否有解析后的响应数据
                    if 'error' not in item and 'original_chunk' not in item:
                        # 尝试解析可能存在的嵌套响应
                        parsed_successfully = False
                        if 'response' in item:
                            # 如果有response字段，尝试解析
                            response_data = item['response']
                            if isinstance(response_data, str):
                                try:
                                    # 尝试解析字符串为JSON
                                    import ast
                                    try:
                                        parsed_response = ast.literal_eval(response_data)
                                    except:
                                        parsed_response = json.loads(response_data.replace('\\n', '\n'))

                                    if isinstance(parsed_response, list):
                                        for sub_item in parsed_response:
                                            if isinstance(sub_item, dict) and 'type' in sub_item and 'number' in sub_item:
                                                fixed_data.append(sub_item)
                                            else:
                                                print(f"跳过无效子项目: {sub_item}")
                                        parsed_successfully = True
                                except Exception as e:
                                    print(f"无法解析响应数据: {e}")
                                    print(f"响应内容: {response_data[:200]}...")
                            elif isinstance(response_data, list):
                                for sub_item in response_data:
                                    if isinstance(sub_item, dict) and 'type' in sub_item and 'number' in sub_item:
                                        fixed_data.append(sub_item)
                                    else:
                                        print(f"跳过无效子项目: {sub_item}")
                                parsed_successfully = True
                        if not parsed_successfully:
                            print(f"跳过结构未知的条目: {item}")

    # 再次验证和清理数据
    final_data = []
    for item in fixed_data:
        if isinstance(item, dict) and 'type' in item and 'number' in item:
            # 确保必需字段存在
            item.setdefault('content', '')
            item.setdefault('answer', '')
            item.setdefault('analysis', '')
            final_data.append(item)

    print(f"修复后数据项数量: {len(final_data)}")

    # 按照题目编号排序
    def sort_key(item):
        if 'number' not in item:
            return float('inf')  # 将没有number的项放到最后

        num_str = item['number']
        # 处理带括号的编号，如 "22（1）"
        if '（' in num_str:
            # 提取数字部分，如从 "22（1）" 中提取 22.1
            parts = re.match(r'(\d+)（(\d+)）', num_str)
            if parts:
                main_num, sub_num = parts.groups()
                return int(main_num) + int(sub_num)/10.0
        elif num_str.isdigit():
            # 纯数字
            return int(num_str)
        else:
            # 非数字编号，如 "一" "二" "三" 等，放到前面
            if num_str in ["一", "二", "三", "四", "五", "六", "七"]:
                return {"一": 0.1, "二": 0.2, "三": 0.3, "四": 0.4, "五": 0.5, "六": 0.6, "七": 0.7}[num_str]
            else:
                # 将字母或特殊字符编号放在最后
                return ord(num_str[0]) * 1000 if num_str else 9999

    final_data.sort(key=sort_key)

    # 保存修复后的文件
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8-sig') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"已保存修复后的文件，包含 {len(final_data)} 个项目")

    # 打印修复后的结构概览
    print("\n修复后数据结构概览:")
    context_count = 0
    question_count = 0
    for i, item in enumerate(final_data[:20]):  # 显示前20个项目
        item_type = item.get('type', 'unknown')
        number = item.get('number', 'no_number')
        print(f"{i+1:2d}. {item_type}: {number}")
        if item_type == 'context':
            context_count += 1
        elif item_type == 'question':
            question_count += 1

    if len(final_data) > 20:
        print("...")
        for i, item in enumerate(final_data[-5:], len(final_data)-4):  # 显示最后5个项目
            item_type = item.get('type', 'unknown')
            number = item.get('number', 'no_number')
            print(f"{i:2d}. {item_type}: {number}")

    print(f"\n总计: {len(final_data)} 个项目")
    print(f"Contexts: {context_count}, Questions: {question_count}")

    return final_data

if __name__ == "__main__":
    print("开始修复test_extracted.json文件结构...")
    fixed_data = fix_extracted_json_structure()
    print("修复完成!")