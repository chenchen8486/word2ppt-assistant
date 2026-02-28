#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
精确解析test_chunks.json内容并生成正确的test_extracted.json文件
"""

import json
import re

def parse_questions_from_content(content):
    """
    从文本内容中解析题目
    """
    questions = []

    # 匹配选择题：数字. 选项内容 (A. B. C. D.)
    choice_pattern = r'(\d+)\s*[.．]\s*([^.]*?\n(?:\s*[A-D]\..*?\n?)+)'
    choice_matches = re.findall(choice_pattern, content)

    for number, full_content in choice_matches:
        # 提取题目内容和选项
        lines = full_content.split('\n')
        question_text = ""
        options = []

        for line in lines:
            line = line.strip()
            if line.startswith(('A.', 'B.', 'C.', 'D.')):
                options.append(line)
            elif line:
                if not options:  # 如果还没遇到选项，则是题目文本
                    question_text += line + " "
                else:  # 如果已遇到选项，可能是续行
                    break

        question_content = question_text.strip()
        if options:
            question_content += "\n" + "\n".join(options)

        # 查找对应的答案和解析
        answer_match = re.search(r'【答案】.*?' + number + r'\s*[.．\s]*([A-D])', content)
        analysis_match = re.search(r'【解析】.*?' + number + r'\s*[.．\s]*(.*?)(?=\n\d+[.．]|\n【|$)', content, re.DOTALL)

        answer = answer_match.group(1) if answer_match else ""
        analysis = analysis_match.group(1).strip() if analysis_match else ""

        if question_content:
            question = {
                "type": "question",
                "number": number.strip(),
                "content": question_content,
                "answer": answer,
                "analysis": analysis
            }
            questions.append(question)

    # 匹配问答题：如 17. 下列对文章的理解与分析，不恰当的两项是（ ）
    essay_pattern = r'([一二三四五六七八九十\d]+[（\(]\d+[）\)]|\d+)\s*[.．]\s*(.*?)(?=\n\d+[.．]|\n【答案】|\n【解析】|\Z)'
    essay_matches = re.findall(essay_pattern, content, re.DOTALL)

    for number, question_content in essay_matches:
        # 处理复合编号，如 "22（1）", "22（2）"
        clean_number = number.replace('（', '(').replace('）', ')').strip()

        # 查找答案和解析
        answer_start = content.find('【答案】')
        if answer_start != -1:
            # 查找特定题号的答案
            answer_match = re.search(r'【答案】.*?' + re.escape(number) + r'\s*[.．\s]*([^【\n]+?)(?=\n|$)', content)
            answer = answer_match.group(1).strip() if answer_match else ""

            # 查找特定题号的解析
            analysis_match = re.search(r'【解析】.*?' + re.escape(number) + r'\s*[.．\s]*([^【\n]+?)(?=\n\d+[.．]|【|$)', content, re.DOTALL)
            analysis = analysis_match.group(1).strip() if analysis_match else ""
        else:
            answer = ""
            analysis = ""

        question = {
            "type": "question",
            "number": clean_number,
            "content": question_content.strip(),
            "answer": answer,
            "analysis": analysis
        }
        questions.append(question)

    return questions

def process_chunks_to_extracted():
    """
    处理chunks文件并生成extracted文件
    """
    # 读取chunks文件
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    extracted_data = []
    expected_questions = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22(1)', '22(2)', '23', '24'])

    for chunk in chunks_data:
        chunk_number = chunk.get('number', '').replace('、', '').strip()
        chunk_content = chunk.get('content', '')

        if chunk_number in ['一', '二', '三', '四', '五', '六', '七']:
            # 创建context条目
            context = {
                "type": "context",
                "number": chunk_number,
                "content": chunk_content,
                "answer": "",
                "analysis": ""
            }
            extracted_data.append(context)

        # 从chunk_content中提取问题
        questions = parse_questions_from_content(chunk_content)

        # 过滤和处理问题
        for question in questions:
            number = question['number']

            # 处理子题编号，如 "22（1）" -> "22(1)", "22（2）" -> "22(2)"
            if '（' in number and '）' in number:
                number = number.replace('（', '(').replace('）', ')')
                question['number'] = number

            # 检查是否是需要的题目编号
            extracted_data.append(question)

    # 移除重复的题目，保留第一个
    seen_numbers = set()
    unique_data = []
    for item in extracted_data:
        if item.get('type') == 'question':
            number = item['number']
            if number not in seen_numbers:
                seen_numbers.add(number)
                unique_data.append(item)
        elif item.get('type') == 'context':
            unique_data.append(item)

    # 重新组织数据：按context-question模式
    organized_data = []
    contexts = [item for item in unique_data if item.get('type') == 'context']
    questions = [item for item in unique_data if item.get('type') == 'question']

    # 按context排序
    context_order = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7}
    contexts.sort(key=lambda x: context_order.get(x['number'], 999))

    # 按数字排序问题
    def question_sort_key(q):
        number = q['number']
        if '(' in number and ')' in number:
            # 处理子题如 "22(1)" -> 22.1
            main_part, sub_part = number.split('(')
            sub_part = sub_part.rstrip(')')
            try:
                return float(main_part) + float(sub_part)/10.0
            except ValueError:
                return float(main_part) if main_part.isdigit() else 9999
        else:
            return int(number) if number.isdigit() else 9999

    questions.sort(key=question_sort_key)

    # 按逻辑组织：context后跟相关questions
    for context in contexts:
        organized_data.append(context)
        # 添加该context范围内的问题（这需要根据实际内容判断）

        # 这里我们采用简单的策略：按题目编号范围分配到相应的context
        # 通常：1-3 -> 一, 4-6 -> 二, 7-13 -> 三, 14-16 -> 四, 17-21 -> 五, 22-23 -> 六, 24 -> 七

    # 添加所有问题
    organized_data.extend(questions)

    # 最后按逻辑重新排序：保持context-question的配对
    final_data = []
    for context in contexts:
        final_data.append(context)
        # 找到属于这个context的问题
        context_start, context_end = get_context_question_range(context['number'])
        for q in questions:
            q_num = q['number']
            if is_question_in_context_range(q_num, context_start, context_end):
                final_data.append(q)

    # 如果上面的方法过于复杂，我们简化处理，先只添加context，然后添加所有问题
    final_simple = contexts.copy()
    final_simple.extend(questions)

    # 保存结果
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(final_simple, f, ensure_ascii=False, indent=2)

    print(f"成功处理，总共 {len(final_simple)} 个项目")
    contexts_count = len([item for item in final_simple if item.get('type') == 'context'])
    questions_count = len([item for item in final_simple if item.get('type') == 'question'])
    print(f"Contexts: {contexts_count}, Questions: {questions_count}")

    return final_simple

def get_context_question_range(context_num):
    """获取context对应的问题范围"""
    ranges = {
        '一': (1, 3),
        '二': (4, 6),
        '三': (7, 13),
        '四': (14, 16),
        '五': (17, 21),
        '六': (22, 23),  # 22(1), 22(2), 23
        '七': (24, 24)
    }
    return ranges.get(context_num, (0, 0))

def is_question_in_context_range(q_num, start, end):
    """检查问题编号是否在context范围内"""
    if '(' in q_num:  # 如 "22(1)"
        main_num = int(q_num.split('(')[0])
    else:
        main_num = int(q_num) if q_num.isdigit() else 0

    return start <= main_num <= end

if __name__ == "__main__":
    print("开始精确解析chunks文件...")
    result = process_chunks_to_extracted()
    print("解析完成!")