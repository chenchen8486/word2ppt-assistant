#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版修复test_extracted.json文件，正确处理所有题目提取
"""

import json
import re

def advanced_rebuild_extracted():
    """
    从chunks文件中完整提取所有题目
    """
    # 读取chunks文件
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    full_data = []

    # 首先添加所有contexts
    for chunk in chunks_data:
        number = chunk.get('number', '').replace('、', '').strip()
        if number in ['一', '二', '三', '四', '五', '六', '七']:
            context = {
                "type": "context",
                "number": number,
                "content": chunk.get('content', ''),
                "answer": "",
                "analysis": ""
            }
            full_data.append(context)

    # 然后从每个chunk中提取问题
    for chunk in chunks_data:
        chunk_number = chunk.get('number', '').replace('、', '').strip()
        chunk_content = chunk.get('content', '')

        # 特殊处理第6部分（包含22和23题）
        if chunk_number == '六':
            # 提取22题（可能包含子题）
            # 查找 22(1) 和 22(2) 或 22（1）和 22（2）
            sub_q1_pattern = r'(22[（\(]1[）\)][^]*?)(?=22[（\(]2[）\)]|\d+[（\(]?\d+[）\)]|\n【答案】|\n【解析】|$)'
            sub_q2_pattern = r'(22[（\(]2[）\)][^]*?)(?=\d+[.．]|\n【答案】|\n【解析】|$)'

            sub_q1_match = re.search(sub_q1_pattern, chunk_content, re.DOTALL)
            sub_q2_match = re.search(sub_q2_pattern, chunk_content, re.DOTALL)

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
                full_data.append(question1)

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
                full_data.append(question2)

            # 提取第23题
            q23_pattern = r'(23\.[^]*?)(?=\d+[.．]|\n【答案】|\n【解析】|$)'
            q23_match = re.search(q23_pattern, chunk_content, re.DOTALL)
            if q23_match:
                q23_content = q23_match.group(1).strip()
                answer23 = extract_answer_for_question(chunk_content, "23")
                analysis23 = extract_analysis_for_question(chunk_content, "23")

                question23 = {
                    'type': 'question',
                    'number': '23',
                    'content': q23_content,
                    'answer': answer23,
                    'analysis': analysis23
                }
                full_data.append(question23)

        # 从每个chunk中提取常规问题（1-21, 24）
        for q_num in range(1, 25):  # 检查所有可能的问题编号
            if chunk_number == '六' and q_num in [22, 23]:  # 已经处理过了
                continue
            if q_num in [22, 23, 24]:  # 22, 23在六中处理，24在七中处理
                continue

            # 检查chunk内容中是否包含这个问题编号
            if f"{q_num}." in chunk_content or f"{q_num}．" in chunk_content:
                # 提取这个题目的内容
                # 使用更精确的模式来提取题目内容直到下一个题目或答案/解析部分
                next_num = q_num + 1
                # 模式: 当前题号 + 内容 + (下一个题号 或 【答案】 或 【解析】 或 结束)
                pattern = rf'({q_num}[.．\s][^]*?)(?={next_num}[.．]|\n【答案】|\n【解析】|$)'

                match = re.search(pattern, chunk_content, re.DOTALL)
                if match:
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
                    full_data.append(question)

    # 最后，从第七部分（写作题）提取第24题
    for chunk in chunks_data:
        if chunk.get('number', '').replace('、', '').strip() == '七':
            chunk_content = chunk.get('content', '')

            # 查找24题（写作题）
            if "24." in chunk_content or "24．" in chunk_content:
                q24_pattern = r'(24[.．\s][^]*?)(?=\n【答案】|\n【解析】|$)'
                q24_match = re.search(q24_pattern, chunk_content, re.DOTALL)

                if q24_match:
                    q24_content = q24_match.group(1).strip()
                    answer24 = extract_answer_for_question(chunk_content, "24")
                    analysis24 = extract_analysis_for_question(chunk_content, "24")

                    question24 = {
                        'type': 'question',
                        'number': '24',
                        'content': q24_content,
                        'answer': answer24,
                        'analysis': analysis24
                    }
                    full_data.append(question24)

    # 按照类型和编号排序
    def sort_key(item):
        if item['type'] == 'context':
            # 中文数字排序
            chinese_nums = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7}
            return chinese_nums.get(item['number'], 999)
        else:  # question
            number = item['number']
            if '(' in number:  # 如 22(1), 22(2)
                main_num, sub_num = number.split('(')
                sub_num = sub_num.rstrip(')')
                return int(main_num) + int(sub_num)/10.0
            elif number.isdigit():
                return int(number)
            else:
                return 9999

    full_data.sort(key=sort_key)

    # 保存结果
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"高级重建完成！共处理 {len(full_data)} 个项目")

    # 显示统计
    contexts = [item for item in full_data if item['type'] == 'context']
    questions = [item for item in full_data if item['type'] == 'question']
    print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

    question_nums = [q['number'] for q in questions]
    print(f"题目编号: {sorted(question_nums)}")

    return full_data

def extract_answer_for_question(content, main_num, sub_num=None):
    """从内容中提取特定问题的答案"""
    if sub_num:
        # 使用更安全的正则表达式，避免特殊字符问题
        escaped_main = re.escape(main_num)
        escaped_sub = re.escape(sub_num)
        pattern = rf'【答案】.*?{escaped_main}[（\(]\s*{escaped_sub}\s*[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)'
    else:
        escaped_num = re.escape(main_num)
        pattern = rf'【答案】.*?{escaped_num}[.．\s]([^【\n]*?)(?=\n|$|【)'

    match = re.search(pattern, content)
    return match.group(1).strip() if match else ""

def extract_analysis_for_question(content, main_num, sub_num=None):
    """从内容中提取特定问题的解析"""
    if sub_num:
        escaped_main = re.escape(main_num)
        escaped_sub = re.escape(sub_num)
        pattern = rf'【解析】.*?{escaped_main}[（\(]\s*{escaped_sub}\s*[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)'
    else:
        escaped_num = re.escape(main_num)
        pattern = rf'【解析】.*?{escaped_num}[.．\s]([^【]*?)(?=\n\d+[.．]|【|$)'

    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

if __name__ == "__main__":
    print("开始高级重建 test_extracted.json 文件...")
    result = advanced_rebuild_extracted()
    print("高级重建完成!")