#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完全修复test_extracted.json文件，正确处理混合格式、错误数据和结构问题
"""

import json
import re

def full_rebuild_extracted():
    """
    完全重新构建extracted.json文件，处理错误数据和混合格式
    """
    # 读取文件内容
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # 解析内容
    try:
        raw_data = json.loads(content)
    except json.JSONDecodeError:
        print("原始文件JSON格式错误，尝试修复...")
        return

    # 解析数据，处理混合格式（数组和对象混合）
    parsed_items = []

    def process_item(item):
        """处理单个项目，提取有效的题目数据"""
        if isinstance(item, list):
            # 如果是数组，递归处理每个元素
            for sub_item in item:
                process_item(sub_item)
        elif isinstance(item, dict):
            # 如果是字典，检查是否包含错误信息
            if 'error' in item and item['error']:
                # 这是错误条目，尝试从中提取有效数据
                error_str = item['error']

                # 尝试从错误信息中提取JSON数组
                start_idx = error_str.find('[')
                end_idx = error_str.rfind(']') + 1

                if start_idx != -1 and end_idx != 0:
                    try:
                        json_part = error_str[start_idx:end_idx]
                        # 尝试解析JSON部分
                        extracted_data = json.loads(json_part)

                        if isinstance(extracted_data, list):
                            for extracted_item in extracted_data:
                                if isinstance(extracted_item, dict) and 'type' in extracted_item:
                                    # 清理数据并添加
                                    clean_item = clean_dict(extracted_item)
                                    parsed_items.append(clean_item)
                    except json.JSONDecodeError:
                        pass  # 如果解析失败，跳过

            elif 'original_chunk' in item:
                # 这是包含原始块的错误条目，尝试解析内容
                original_chunk = item['original_chunk']
                if isinstance(original_chunk, dict) and 'content' in original_chunk:
                    # 从内容中提取题目
                    extract_questions_from_content(original_chunk['content'], parsed_items)

            elif 'type' in item and item.get('type') in ['context', 'question']:
                # 这是有效的题目条目
                clean_item = clean_dict(item)
                parsed_items.append(clean_item)

    def clean_dict(d):
        """清理字典，确保必需字段存在"""
        required_fields = ['type', 'number', 'content', 'answer', 'analysis']
        cleaned = {}

        for field in required_fields:
            if field in d:
                value = d[field]
                # 确保字符串值不是None
                if value is None:
                    value = ""
                cleaned[field] = value
            else:
                cleaned[field] = ""

        return cleaned

    def extract_questions_from_content(content, target_list):
        """从内容中提取问题"""
        # 提取context
        context_pattern = r'([一二三四五六七])\s*[、.．]?\s*[（(]?[一二三四五六七八九十\d]*[）)?]?.*?阅读.*?(?=\d+[.．]|\Z|【答案】|【解析】)'

        # 简单的提取逻辑
        if '一、' in content or '一、' in content or '（9分）' in content:
            # 尝试识别上下文部分
            context_num = ''
            if '一、' in content:
                context_num = '一'
            elif '二、' in content:
                context_num = '二'
            elif '三、' in content:
                context_num = '三'
            elif '四、' in content:
                context_num = '四'
            elif '五、' in content:
                context_num = '五'
            elif '六、' in content:
                context_num = '六'
            elif '七、' in content:
                context_num = '七'

            if context_num:
                context = {
                    'type': 'context',
                    'number': context_num,
                    'content': content[:min(len(content), 500)] + "...",
                    'answer': '',
                    'analysis': ''
                }
                target_list.append(context)

    # 处理顶层数据
    for item in raw_data:
        process_item(item)

    # 现在从原始chunks文件重新构建正确的结构
    try:
        with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
            chunks_data = json.load(f)
    except:
        print("无法读取chunks文件，使用现有解析数据")
        chunks_data = []

    if chunks_data:
        # 重新构建正确的数据结构
        rebuilt_data = []

        # 添加contexts
        for chunk in chunks_data:
            number = chunk.get('number', '').replace('、', '').strip()
            if number in ['一', '二', '三', '四', '五', '六', '七']:
                context = {
                    'type': 'context',
                    'number': number,
                    'content': chunk.get('content', ''),
                    'answer': '',
                    'analysis': ''
                }
                rebuilt_data.append(context)

        # 现在从chunks内容中提取问题
        question_map = {
            '一': [1, 2, 3],
            '二': [4, 5, 6],
            '三': [7, 8, 9, 10, 11, 12, 13],
            '四': [14, 15, 16],
            '五': [17, 18, 19, 20, 21],
            '六': [22, 23],  # 包括22(1), 22(2)
            '七': [24]
        }

        for chunk in chunks_data:
            chunk_num = chunk.get('number', '').replace('、', '').strip()
            chunk_content = chunk.get('content', '')

            if chunk_num in question_map:
                questions_for_this_context = question_map[chunk_num]

                for q_num in questions_for_this_context:
                    # 为每个预期的问题编号提取内容

                    # 处理子题，如 22(1), 22(2)
                    if chunk_num == '六' and q_num == 22:
                        # 特殊处理第6部分，可能包含子题

                        # 查找 22(1) 和 22(2) 或 22（1）和 22（2）
                        sub_q1_pattern = r'(22[（\(]1[）\)][^]*?)(?=22[（\(]2[）\)]|\d+[（\(]?\d+[）\)]|\n【答案】|\n【解析】|$)'
                        sub_q2_pattern = r'(22[（\(]2[）\)][^]*?)(?=\d+[.．]|\n【答案】|\n【解析】|$)'

                        sub_q1_match = re.search(sub_q1_pattern, chunk_content)
                        sub_q2_match = re.search(sub_q2_pattern, chunk_content)

                        if sub_q1_match:
                            q1_content = sub_q1_match.group(1).strip()
                            # 尝试找到对应的答案和解析
                            answer1 = extract_answer_for_question(chunk_content, "22", "1")
                            analysis1 = extract_analysis_for_question(chunk_content, "22", "1")

                            question1 = {
                                'type': 'question',
                                'number': '22(1)',
                                'content': q1_content,
                                'answer': answer1,
                                'analysis': analysis1
                            }
                            rebuilt_data.append(question1)

                        if sub_q2_match:
                            q2_content = sub_q2_match.group(1).strip()
                            answer2 = extract_answer_for_question(chunk_content, "22", "2")
                            analysis2 = extract_analysis_for_question(chunk_content, "22", "2")

                            question2 = {
                                'type': 'question',
                                'number': '22(2)',
                                'content': q2_content,
                                'answer': answer2,
                                'analysis': analysis2
                            }
                            rebuilt_data.append(question2)

                    # 提取普通问题
                    q_pattern = rf'({q_num}[.．]\s*.*?)(?=\n\d+[.．]|\n【答案】|\n【解析】|$)'
                    match = re.search(q_pattern, chunk_content)

                    if match and str(q_num) != '22':  # 避免重复添加22题
                        q_content = match.group(1).strip()
                        answer = extract_answer_for_question(chunk_content, str(q_num))
                        analysis = extract_analysis_for_question(chunk_content, str(q_num))

                        question = {
                            'type': 'question',
                            'number': str(q_num),
                            'content': q_content,
                            'answer': answer,
                            'analysis': analysis
                        }
                        rebuilt_data.append(question)

        # 保存重建的数据
        with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(rebuilt_data, f, ensure_ascii=False, indent=2)

        print(f"重建完成！共处理 {len(rebuilt_data)} 个项目")

        # 显示统计
        contexts = [item for item in rebuilt_data if item['type'] == 'context']
        questions = [item for item in rebuilt_data if item['type'] == 'question']
        print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

        question_nums = [q['number'] for q in questions]
        print(f"题目编号: {sorted(question_nums)}")

        return rebuilt_data

    else:
        # 如果无法获取chunks数据，使用现有的解析数据
        with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(parsed_items, f, ensure_ascii=False, indent=2)

        print(f"使用解析数据，共处理 {len(parsed_items)} 个项目")
        return parsed_items

def extract_answer_for_question(content, main_num, sub_num=None):
    """从内容中提取特定问题的答案"""
    if sub_num:
        pattern = rf'【答案】.*?{main_num}[（\(]\s*{sub_num}\s*[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)'
    else:
        pattern = rf'【答案】.*?{main_num}[.．\s]([^【\n]*?)(?=\n|$|【)'

    match = re.search(pattern, content)
    return match.group(1).strip() if match else ""

def extract_analysis_for_question(content, main_num, sub_num=None):
    """从内容中提取特定问题的解析"""
    if sub_num:
        pattern = rf'【解析】.*?{main_num}[（\(]\s*{sub_num}\s*[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)'
    else:
        pattern = rf'【解析】.*?{main_num}[.．\s]([^【]*?)(?=\n\d+[.．]|【|$)'

    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

if __name__ == "__main__":
    print("开始完全重建 test_extracted.json 文件...")
    result = full_rebuild_extracted()
    print("重建完成!")