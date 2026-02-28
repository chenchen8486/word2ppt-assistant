"""
数据修复工具模块
整合了原有的repair目录中的通用修复功能
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


def fix_extracted_structure(input_file, output_file=None):
    """
    修复extracted.json文件结构问题

    Args:
        input_file: 输入的JSON文件路径
        output_file: 输出文件路径（如果未指定，则覆盖原文件）
    """
    # 如果没有指定输出文件，则使用输入文件路径
    if output_file is None:
        output_file = input_file

    # 读取当前的损坏文件
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        raw_data = f.read()

    # 解析JSON（注意：由于数据格式混乱，我们需要先修复结构）
    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        print(f"原始JSON格式有误，需要修复: {input_file}")
        return

    # 过滤并修复数据
    fixed_data = []
    processed_numbers = set()  # 用于避免重复

    for item_idx, item in enumerate(data):
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
                        number = sub_item['number']
                        if number not in processed_numbers:
                            fixed_data.append(sub_item)
                            processed_numbers.add(number)
                        else:
                            print(f"跳过重复项目: {number}")
                    else:
                        print(f"跳过结构不完整的条目: {sub_item}")

        # 如果是字典对象
        elif isinstance(item, dict):
            # 检查是否是错误条目（只检查有具体内容的错误）
            if 'error' in item and item['error'] and "Failed to parse LLM response:" in item['error']:
                print(f"检测到解析错误，尝试从中提取有效数据...")
                # 从错误消息中提取有效的JSON部分
                error_msg = item['error']

                # 查找 JSON 数组的开始 '[\n' 和对应结束 ']'
                start_match = re.search(r'\[\s*\n\s*{', error_msg)
                if start_match:
                    # 从找到的开始位置向后查找匹配的结束括号
                    content = error_msg[start_match.start():]
                    brace_count = 0
                    pos = 0

                    # 找到匹配的数组结束位置
                    for i, char in enumerate(content):
                        if char == '[':
                            brace_count += 1
                        elif char == ']':
                            brace_count -= 1
                            if brace_count == 0:
                                extracted_json = content[:i+1]
                                break
                    else:
                        extracted_json = content  # fallback

                    try:
                        # 替换常见的转义字符问题
                        extracted_json = extracted_json.replace('\\n', '\n').replace('\\\\', '\\')

                        # 清理可能的问题字符
                        extracted_json = re.sub(r',\s*([}\]])', r'\1', extracted_json)  # 移除末尾多余的逗号

                        parsed_list = json.loads(extracted_json)

                        if isinstance(parsed_list, list):
                            for parsed_item in parsed_list:
                                if isinstance(parsed_item, dict) and 'type' in parsed_item and 'number' in parsed_item:
                                    number = parsed_item['number']
                                    if number not in processed_numbers:
                                        fixed_data.append(parsed_item)
                                        processed_numbers.add(number)
                                    else:
                                        print(f"跳过重复项目: {number}")
                            print(f"从解析错误中成功提取了 {len(parsed_list)} 个项目")
                        else:
                            print("提取的内容不是列表格式")
                    except json.JSONDecodeError as e:
                        print(f"无法解析提取的JSON部分: {e}")
                        # 尝试另一种方式提取JSON数据
                        # 使用正则表达式来查找 { "type": ..., "number": ... } 格式的对象
                        pattern = r'\{\s*"type"\s*:\s*"[^"]+"\s*,\s*"number"\s*:\s*"[^"]+"\s*(?:,\s*"[^"]+"\s*:\s*[^}]+)+\s*\}'
                        matches = re.findall(pattern, error_msg)

                        for match in matches:
                            try:
                                obj = json.loads(match)
                                if 'type' in obj and 'number' in obj:
                                    number = obj['number']
                                    if number not in processed_numbers:
                                        fixed_data.append(obj)
                                        processed_numbers.add(number)
                                        print(f"从错误消息中提取项目: {number}")
                            except json.JSONDecodeError:
                                continue
                continue
            elif 'error' in item and item['error']:
                print(f"跳过错误条目: {item['error']}")
                continue
            elif 'error' in item and not item['error']:
                # 空错误字符串，也是错误条目
                continue
            elif 'original_chunk' in item:
                # 这是一个包含原始块但解析失败的条目
                print(f"跳过解析失败的条目 (chunk: {item.get('original_chunk', {}).get('number', 'unknown')})")
                continue
            else:
                # 检查是否是有效数据
                if 'type' in item and 'number' in item:
                    number = item['number']
                    if number not in processed_numbers:
                        # 确保必需字段存在
                        item.setdefault('content', '')
                        item.setdefault('answer', '')
                        item.setdefault('analysis', '')
                        fixed_data.append(item)
                        processed_numbers.add(number)
                    else:
                        print(f"跳过重复项目: {number}")
                else:
                    print(f"跳过结构未知的条目 #{item_idx}: {item}")

    print(f"修复后数据项数量: {len(fixed_data)}")

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

    fixed_data.sort(key=sort_key)

    # 保存修复后的文件
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print(f"已保存修复后的文件到: {output_file}，包含 {len(fixed_data)} 个项目")

    # 打印修复后的结构概览
    print("\n修复后数据结构概览:")
    context_count = 0
    question_count = 0
    for i, item in enumerate(fixed_data):  # 显示所有项目
        item_type = item.get('type', 'unknown')
        number = item.get('number', 'no_number')
        print(f"{i+1:2d}. {item_type}: {number}")
        if item_type == 'context':
            context_count += 1
        elif item_type == 'question':
            question_count += 1

    print(f"\n总计: {len(fixed_data)} 个项目")
    print(f"Contexts: {context_count}, Questions: {question_count}")

    return fixed_data