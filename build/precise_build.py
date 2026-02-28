#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
精确构建test_extracted.json文件，避免重复和错误提取
"""

import json
import re

def precise_build_from_chunks():
    """
    精确从chunks文件构建提取的文件
    """
    # 读取chunks文件
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    extracted_data = []

    # 首先添加所有contexts
    for chunk in chunks_data:
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

    # 定义所有期望的题目编号
    expected_questions = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
                        '14', '15', '16', '17', '18', '19', '20', '21', '22(1)', '22(2)', '23', '24']

    # 创建一个字典存储找到的题目，避免重复
    found_questions = {}

    for chunk in chunks_data:
        chunk_content = chunk.get('content', '')

        # 为每个可能的题目编号查找
        for q_num in range(1, 25):
            str_qnum = str(q_num)

            # 跳过特殊的子题（22(1), 22(2)） - 这些需要特殊处理
            if q_num == 22:
                # 特殊处理22题及其子题
                # 查找22(1)和22(2)
                subq1_pattern = r'(22[（\(]1[）\)][^]*?)(?=22[（\(]2[）\)]|\d+[（\(]?\d+[）\)]|\n【答案】|\n【解析】|$)'
                subq2_pattern = r'(22[（\(]2[）\)][^]*?)(?=\d+[.．]|\n【答案】|\n【解析】|$)'

                subq1_match = re.search(subq1_pattern, chunk_content, re.DOTALL)
                subq2_match = re.search(subq2_pattern, chunk_content, re.DOTALL)

                if subq1_match and '22(1)' not in found_questions:
                    q1_content = subq1_match.group(1).strip()

                    # 提取答案和解析
                    answer1_match = re.search(r'【答案】.*?22[（\(]1[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)', chunk_content)
                    analysis1_match = re.search(r'【解析】.*?22[（\(]1[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)', chunk_content, re.DOTALL)

                    answer1 = answer1_match.group(1).strip() if answer1_match else ""
                    analysis1 = analysis1_match.group(1).strip() if analysis1_match else ""

                    found_questions['22(1)'] = {
                        "type": "question",
                        "number": "22(1)",
                        "content": q1_content,
                        "answer": answer1,
                        "analysis": analysis1
                    }

                if subq2_match and '22(2)' not in found_questions:
                    q2_content = subq2_match.group(1).strip()

                    answer2_match = re.search(r'【答案】.*?22[（\(]2[）\)][.．\s]*([^【\n]*?)(?=\n|$|【)', chunk_content)
                    analysis2_match = re.search(r'【解析】.*?22[（\(]2[）\)][.．\s]*([^【]*?)(?=\n\d+[.．]|【|$)', chunk_content, re.DOTALL)

                    answer2 = answer2_match.group(1).strip() if answer2_match else ""
                    analysis2 = analysis2_match.group(1).strip() if analysis2_match else ""

                    found_questions['22(2)'] = {
                        "type": "question",
                        "number": "22(2)",
                        "content": q2_content,
                        "answer": answer2,
                        "analysis": analysis2
                    }

                # 对于22题整体，如果我们找到子题之一，就不需要整体题目
                continue

            # 使用精确模式查找题目
            # 模式：题号. + 内容 + (下一个题号 或 【答案】 或 【解析】 或 $)
            # 使用非贪婪匹配，并确保正确界定
            pattern = rf'({str_qnum}[.．]\s*.*?)(?=\n\d+[.．]|\n【答案】|\n【解析】|$)'

            matches = re.findall(pattern, chunk_content, re.DOTALL)

            # 只取最合适的匹配（通常是最长的那个）
            if matches:
                # 找到最相关的匹配
                best_match = max(matches, key=len)  # 选择最长的匹配

                if str_qnum not in found_questions:
                    # 提取对应答案和解析
                    answer_match = re.search(rf'【答案】.*?{str_qnum}[.．\s]([^【\n]*?)(?=\n|$|【)', chunk_content)
                    analysis_match = re.search(rf'【解析】.*?{str_qnum}[.．\s]([^【]*?)(?=\n\d+[.．]|【|$)', chunk_content, re.DOTALL)

                    answer = answer_match.group(1).strip() if answer_match else ""
                    analysis = analysis_match.group(1).strip() if analysis_match else ""

                    # 遵循一些特殊情况
                    if str_qnum == '24':  # 作文题通常较长，我们取主要部分
                        if len(best_match) > 1000:
                            best_match = best_match[:500] + "..."

                    found_questions[str_qnum] = {
                        "type": "question",
                        "number": str_qnum,
                        "content": best_match.strip(),
                        "answer": answer,
                        "analysis": analysis
                    }

    # 将找到的题目添加到结果中
    for q_num in sorted(found_questions.keys(), key=lambda x: (int(x.split('(')[0]) if '(' not in x else int(x.split('(')[0]),
                                                              int(x.split('(')[1].rstrip(')')) if '(' in x else 0)):
        extracted_data.append(found_questions[q_num])

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

    print(f"精确构建完成！共处理 {len(extracted_data)} 个项目")

    # 显示统计
    contexts = [item for item in extracted_data if item['type'] == 'context']
    questions = [item for item in extracted_data if item['type'] == 'question']
    print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

    question_nums = [q['number'] for q in questions]
    print(f"题目编号: {sorted(question_nums)}")

    return extracted_data

if __name__ == "__main__":
    print("开始精确构建test_extracted.json...")
    result = precise_build_from_chunks()
    print("精确构建完成!")