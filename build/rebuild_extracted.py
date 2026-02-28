#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从test_chunks.json中提取并重构正确的test_extracted.json文件
"""

import json
import re

def extract_questions_from_chunk(chunk_content, chunk_number):
    """
    从chunk内容中提取问题
    """
    questions = []

    # 定义正则表达式模式来匹配题目
    # 匹配题目：数字 + 点号/句号 + 内容
    question_pattern = r'(\d+)\s*[.．]([^\n]+?)(?=\n\d+[.．]|\n【|$(?!\n))'

    # 为每种题型分别提取
    # 选择题：1. 2. 3. 这样的格式
    choices_pattern = r'(\d+)\s*[.．]\s*(.*?)\n(A\..*?D\..*?)\n.*?【答案】.*?([A-D])'
    choices_matches = re.findall(choices_pattern, chunk_content, re.DOTALL)

    for match in choices_matches:
        number, content, options, answer = match
        # 获取解析部分
        analysis_match = re.search(r'【解析】.*?(' + number + r'\..*?)\n(?:\d+[.．]|【|$)', chunk_content, re.DOTALL)
        analysis = analysis_match.group(1).strip() if analysis_match else ""

        question = {
            "type": "question",
            "number": number.strip(),
            "content": f"{content.strip()}\n\n{options.strip()}",
            "answer": answer.strip(),
            "analysis": analysis.strip()
        }
        questions.append(question)

    # 填空题、问答题等：其他数字编号的题目
    other_questions = re.findall(r'([一二三四五六七八九十\d]+[（\(]\d+[）\)]|\d+)[\s.．]\s*(.*?)(?=【答案】|【解析】|\n\d+\.|\n【|$)', chunk_content, re.DOTALL)

    for q_num, q_content in other_questions:
        # 尝试找到对应的答案和解析
        answer_match = re.search(r'【答案】.*?' + re.escape(q_num) + r'[.．\s]*(.*?)(?=【解析】|\n\d+[.．]|$)', chunk_content, re.DOTALL)
        analysis_match = re.search(r'【解析】.*?' + re.escape(q_num) + r'[.．\s]*(.*?)(?=\n\d+[.．]|$)', chunk_content, re.DOTALL)

        answer = answer_match.group(1).strip() if answer_match else ""
        analysis = analysis_match.group(1).strip() if analysis_match else ""

        # 清理答案和解析中的多余空白
        answer = re.sub(r'\n+', '\n', answer).strip()
        analysis = re.sub(r'\n+', '\n', analysis).strip()

        question = {
            "type": "question",
            "number": q_num.strip().replace('（', '(').replace('）', ')'),
            "content": q_content.strip(),
            "answer": answer,
            "analysis": analysis
        }
        questions.append(question)

    return questions

def convert_chunks_to_extracted():
    """
    从test_chunks.json转换为正确格式的test_extracted.json
    """
    # 读取chunks文件
    with open('data/02_temp_build/test_chunks.json', 'r', encoding='utf-8-sig') as f:
        chunks_data = json.load(f)

    extracted_data = []

    for i, chunk in enumerate(chunks_data):
        chunk_number = chunk.get('number', '')
        chunk_content = chunk.get('content', '')

        # 根据chunk的编号判断是context还是question
        if chunk_number and any(x in chunk_number for x in ['一、', '二、', '三、', '四、', '五、', '六、', '七、', '一', '二', '三', '四', '五', '六', '七']):
            # 这是一个context
            context_num = chunk_number.replace('、', '').strip()
            context = {
                "type": "context",
                "number": context_num,
                "content": chunk_content,
                "answer": "",
                "analysis": ""
            }
            extracted_data.append(context)

            # 从这个context中提取所有相关的问题
            questions = extract_questions_from_chunk(chunk_content, context_num)
            extracted_data.extend(questions)
        else:
            # 处理可能单独存在的问题
            questions = extract_questions_from_chunk(chunk_content, chunk_number)
            extracted_data.extend(questions)

    # 保存结果
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    print(f"成功转换，总共 {len(extracted_data)} 个项目")

    # 统计信息
    contexts = [item for item in extracted_data if item.get('type') == 'context']
    questions = [item for item in extracted_data if item.get('type') == 'question']
    print(f"Contexts: {len(contexts)}, Questions: {len(questions)}")

    return extracted_data

if __name__ == "__main__":
    print("开始从test_chunks.json重构test_extracted.json...")
    result = convert_chunks_to_extracted()
    print("转换完成!")