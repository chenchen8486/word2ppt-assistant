#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重构test_extracted.json文件，正确组织context-question结构
"""

import json
import re

def extract_questions_and_contexts_from_chunks():
    """
    从chunks文件中精确提取contexts和questions
    """
    # 读取chunks文件
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    all_data = []

    # 逐个处理每个chunk
    for chunk in chunks_data:
        chunk_number = chunk.get('number', '').replace('、', '').strip()
        chunk_content = chunk.get('content', '')

        if chunk_number in ['一', '二', '三', '四', '五', '六', '七']:
            # 创建context
            context = {
                "type": "context",
                "number": chunk_number,
                "content": chunk_content,
                "answer": "",
                "analysis": ""
            }
            all_data.append(context)

    # 现在从内容中提取所有题目
    # 根据预期的题目编号来提取
    expected_questions = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
        '21', '22', '22(1)', '22(2)', '23', '24'
    ]

    # 将所有chunk内容合并，便于全局搜索
    full_content = ""
    for chunk in chunks_data:
        full_content += chunk.get('content', '') + "\n===END_CHUNK===\n"

    # 提取每个问题
    for q_num in expected_questions:
        if q_num in ['22(1)', '22(2)']:
            continue  # 这些是22题的子题，我们单独处理

        # 处理题目编号，如果是带括号的需要特殊处理
        if '(' in q_num:
            main_num, sub_num = q_num.split('(')
            sub_num = sub_num.rstrip(')')

            # 在内容中查找子题
            pattern = rf'({main_num}\s*[（\(]\s*{sub_num}\s*[）\)]\s*.*?)(?=\n\d+\s*[.．]|【答案】|【解析】|$)'
            matches = re.findall(pattern, full_content, re.DOTALL)
            if matches:
                question_content = matches[0].strip()

                # 提取对应答案和解析
                answer = ""
                analysis = ""

                # 找答案
                answer_pattern = rf'【答案】.*?{main_num}\s*[（\(]\s*{sub_num}\s*[）\)]\s*([^【\n]*?)(?=\n|$|【)'
                answer_match = re.search(answer_pattern, full_content)
                if answer_match:
                    answer = answer_match.group(1).strip()

                # 找解析
                analysis_pattern = rf'【解析】.*?{main_num}\s*[（\(]\s*{sub_num}\s*[）\)]\s*([^【]*?)(?=\n\d+\s*[.．]|【|$)'
                analysis_match = re.search(analysis_pattern, full_content, re.DOTALL)
                if analysis_match:
                    analysis = analysis_match.group(1).strip()

                question = {
                    "type": "question",
                    "number": q_num,
                    "content": question_content,
                    "answer": answer,
                    "analysis": analysis
                }
                all_data.append(question)
        else:
            # 处理普通题目编号
            pattern = rf'({q_num}\s*[.．]\s*.*?)(?=\n\d+\s*[.．]|【答案】|【解析】|$)'
            matches = re.findall(pattern, full_content, re.DOTALL)
            if matches:
                question_content = matches[0].strip()

                # 提取对应答案和解析
                answer = ""
                analysis = ""

                # 找答案
                answer_pattern = rf'【答案】.*?{q_num}\s*[.．\s]([^【\n]*?)(?=\n|$|【)'
                answer_match = re.search(answer_pattern, full_content)
                if answer_match:
                    answer = answer_match.group(1).strip()

                # 找解析
                analysis_pattern = rf'【解析】.*?{q_num}\s*[.．\s]([^【]*?)(?=\n\d+\s*[.．]|【|$)'
                analysis_match = re.search(analysis_pattern, full_content, re.DOTALL)
                if analysis_match:
                    analysis = analysis_match.group(1).strip()

                question = {
                    "type": "question",
                    "number": q_num,
                    "content": question_content,
                    "answer": answer,
                    "analysis": analysis
                }
                all_data.append(question)

    # 特别处理22题的子题，因为我们知道它在第六个chunk中
    sixth_chunk = chunks_data[5]['content']  # 第六个chunk（索引5）对应第六部分

    # 提取22(1)和22(2)
    subq1_pattern = r'(22[（\(]1[）\)].*?)(?=\n22[（\(]2[）\)]|\n【答案】|\n【解析】|$)'
    subq2_pattern = r'(22[（\(]2[）\)].*?)(?=\n\d+[.．]|\n【答案】|\n【解析】|$)'

    subq1_match = re.search(subq1_pattern, sixth_chunk, re.DOTALL)
    subq2_match = re.search(subq2_pattern, sixth_chunk, re.DOTALL)

    if subq1_match:
        # 提取22(1)的答案和解析
        answer1_match = re.search(r'【答案】.*?22[（\(]1[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)', sixth_chunk)
        analysis1_match = re.search(r'【解析】.*?22[（\(]1[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)', sixth_chunk, re.DOTALL)

        answer1 = answer1_match.group(1).strip() if answer1_match else ""
        analysis1 = analysis1_match.group(1).strip() if analysis1_match else ""

        question1 = {
            "type": "question",
            "number": "22(1)",
            "content": subq1_match.group(1).strip(),
            "answer": answer1,
            "analysis": analysis1
        }
        all_data.append(question1)

    if subq2_match:
        # 提取22(2)的答案和解析
        answer2_match = re.search(r'【答案】.*?22[（\(]2[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)', sixth_chunk)
        analysis2_match = re.search(r'【解析】.*?22[（\(]2[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)', sixth_chunk, re.DOTALL)

        answer2 = answer2_match.group(1).strip() if answer2_match else ""
        analysis2 = analysis2_match.group(1).strip() if analysis2_match else ""

        question2 = {
            "type": "question",
            "number": "22(2)",
            "content": subq2_match.group(1).strip(),
            "answer": answer2,
            "analysis": analysis2
        }
        all_data.append(question2)

    # 按照类型和编号排序：先context，然后是有序的问题
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

    all_data.sort(key=sort_key)

    # 保存结果
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"重构完成，总共 {len(all_data)} 个项目")

    # 统计信息
    contexts = [item for item in all_data if item.get('type') == 'context']
    questions = [item for item in all_data if item.get('type') == 'question']
    print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

    # 显示题目编号
    question_nums = [q['number'] for q in questions]
    print(f"题目编号: {sorted(question_nums)}")

    return all_data

if __name__ == "__main__":
    print("开始重构test_extracted.json文件...")
    result = extract_questions_and_contexts_from_chunks()
    print("重构完成!")