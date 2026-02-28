#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接从test_chunks.json文件构建正确的test_extracted.json
"""

import json
import re

def build_from_chunks():
    """
    从chunks文件直接构建提取的文件
    """
    # 读取chunks文件
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    extracted_data = []

    # 首先添加所有contexts（第2-8个chunk，对应一到七）
    for i, chunk in enumerate(chunks_data):
        chunk_number = chunk.get('number', '').replace('、', '').strip()

        if chunk_number in ['一', '二', '三', '四', '五', '六', '七']:
            context = {
                "type": "context",
                "number": chunk_number,
                "content": chunk.get('content', ''),
                "answer": "",
                "analysis": ""
            }
            extracted_data.append(context)

    # 现在处理所有问题，从每个chunk的内容中提取
    question_pattern = r'(\d+)[.．\s](.*?)(?=\n\d+[.．]|\n【答案】|\n【解析】|$)'

    for chunk in chunks_data:
        chunk_number = chunk.get('number', '').replace('、', '').strip()
        chunk_content = chunk.get('content', '')

        # 提取所有问题
        questions_in_chunk = re.findall(question_pattern, chunk_content, re.DOTALL)

        for q_num, q_content in questions_in_chunk:
            # 特殊处理22题的子题（22(1), 22(2)）
            if q_num == '22':
                # 在22题的文本中查找子题
                subq1_pattern = r'(22[（\(]1[）\)][^]*?)(?=22[（\(]2[）\)]|\d+[（\(]?\d+[）\)]|\n【答案】|\n【解析】|$)'
                subq2_pattern = r'(22[（\(]2[）\)][^]*?)(?=\d+[.．]|\n【答案】|\n【解析】|$)'

                subq1_match = re.search(subq1_pattern, q_content, re.DOTALL)
                subq2_match = re.search(subq2_pattern, q_content, re.DOTALL)

                if subq1_match:
                    subq1_content = subq1_match.group(1).strip()

                    # 提取对应答案和解析
                    answer1_match = re.search(r'【答案】.*?22[（\(]1[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)', chunk_content)
                    analysis1_match = re.search(r'【解析】.*?22[（\(]1[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)', chunk_content, re.DOTALL)

                    answer1 = answer1_match.group(1).strip() if answer1_match else ""
                    analysis1 = analysis1_match.group(1).strip() if analysis1_match else ""

                    subq1 = {
                        "type": "question",
                        "number": "22(1)",
                        "content": subq1_content,
                        "answer": answer1,
                        "analysis": analysis1
                    }
                    extracted_data.append(subq1)

                if subq2_match:
                    subq2_content = subq2_match.group(1).strip()

                    answer2_match = re.search(r'【答案】.*?22[（\(]2[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)', chunk_content)
                    analysis2_match = re.search(r'【解析】.*?22[（\(]2[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)', chunk_content, re.DOTALL)

                    answer2 = answer2_match.group(1).strip() if answer2_match else ""
                    analysis2 = analysis2_match.group(1).strip() if analysis2_match else ""

                    subq2 = {
                        "type": "question",
                        "number": "22(2)",
                        "content": subq2_content,
                        "answer": answer2,
                        "analysis": analysis2
                    }
                    extracted_data.append(subq2)

            # 跳过已作为子题处理的22题主体部分
            elif q_num != '22':
                # 提取答案和解析
                answer_match = re.search(rf'【答案】.*?{q_num}[.．\s]([^【\n]*?)(?=\n|$|【)', chunk_content)
                analysis_match = re.search(rf'【解析】.*?{q_num}[.．\s]([^【]*?)(?=\n\d+[.．]|【|$)', chunk_content, re.DOTALL)

                answer = answer_match.group(1).strip() if answer_match else ""
                analysis = analysis_match.group(1).strip() if analysis_match else ""

                # 处理特殊情况，比如某些答案可能包含更多信息
                if not answer:
                    # 查找更宽松的答案格式
                    loose_answer_match = re.search(rf'{q_num}[.．].*?【答案】([^【]*)', chunk_content)
                    if loose_answer_match:
                        answer = loose_answer_match.group(1).strip()

                if not analysis:
                    # 查找解析可能在不同位置
                    loose_analysis_match = re.search(rf'{q_num}[.．].*?【解析】([^【]*)', chunk_content, re.DOTALL)
                    if loose_analysis_match:
                        analysis = loose_analysis_match.group(1).strip()

                question = {
                    "type": "question",
                    "number": q_num,
                    "content": q_content.strip(),
                    "answer": answer,
                    "analysis": analysis
                }
                extracted_data.append(question)

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

    extracted_data.sort(key=sort_key)

    # 保存结果
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    print(f"从chunks文件构建完成！共处理 {len(extracted_data)} 个项目")

    # 显示统计
    contexts = [item for item in extracted_data if item['type'] == 'context']
    questions = [item for item in extracted_data if item['type'] == 'question']
    print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

    question_nums = [q['number'] for q in questions]
    print(f"题目编号: {sorted(question_nums)}")

    return extracted_data

if __name__ == "__main__":
    print("开始从test_chunks.json构建test_extracted.json...")
    result = build_from_chunks()
    print("构建完成!")