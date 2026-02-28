import json
import re

def extract_questions_from_context(content):
    """
    从context内容中提取独立的题目
    """
    questions = []

    # 按行分割内容
    lines = content.split('\n')

    # 定义识别题目、答案、解析部分的模式
    question_start = False
    current_question = None
    answers_started = False
    analysis_started = False

    question_text = ""
    current_number = ""

    for line in lines:
        # 检查是否是题目开始 (数字加点号)
        question_match = re.match(r'^(\d+(?:\(\d+\))?)\s*[.．、]\s*(.+)$', line.strip())

        if question_match:
            # 如果之前已经有题目在构建，保存它
            if current_question and question_text:
                current_question["content"] = question_text.strip()
                questions.append(current_question)

            # 开始新题目
            current_number = question_match.group(1)
            question_text = question_match.group(2) + "\n"
            current_question = {
                "type": "question",
                "number": current_number,
                "content": "",
                "answer": "",
                "analysis": ""
            }
        elif line.strip().startswith('A.') or line.strip().startswith('B.') or \
             line.strip().startswith('C.') or line.strip().startswith('D.'):
            # 添加选项到题目
            if current_question:
                question_text += line + "\n"
        elif '【答案】' in line or '[答案]' in line:
            # 答案部分
            answers_started = True
            answer_text = line.replace('【答案】', '').replace('[答案]', '').strip()
            if current_question:
                current_question["answer"] = answer_text
        elif '【解析】' in line or '[解析]' in line:
            # 解析部分开始
            analysis_started = True
            analysis_text = line.replace('【解析】', '').replace('[解析]', '').strip()
            if current_question:
                current_question["analysis"] = analysis_text
        elif answers_started and not analysis_started:
            # 在答案部分但不在解析部分
            if current_question:
                current_question["answer"] += " " + line.strip()
        elif analysis_started:
            # 在解析部分
            if current_question:
                current_question["analysis"] += " " + line.strip()
        elif current_question and not answers_started and not analysis_started:
            # 题目内容部分
            question_text += line + "\n"

    # 保存最后一个题目
    if current_question and question_text:
        current_question["content"] = question_text.strip()
        questions.append(current_question)

    return questions

def fix_section_three_extracted(input_file, output_file=None):
    """
    修复第三部分提取结果，将合并的题目拆分成独立题目
    """
    if output_file is None:
        output_file = input_file.replace('_extracted.json', '_fixed.json')

    # 读取文件
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f'原始数据长度: {len(data)}')

    fixed_data = []
    for item in data:
        if isinstance(item, dict) and 'error' in item and item.get('error') == "":
            # 这是一个原始错误格式，尝试从original_chunk恢复
            original_chunk = item.get('original_chunk', {})
            if original_chunk and 'content' in original_chunk:
                content = original_chunk['content']

                # 检查是否包含多个题目
                if re.search(r'\d+\s*[.．、]\s*', content):
                    print("发现包含多个题目的内容，正在拆分...")

                    # 尝试提取题目
                    extracted_questions = extract_questions_from_context(content)

                    if extracted_questions:
                        print(f"成功提取 {len(extracted_questions)} 个题目")
                        fixed_data.extend(extracted_questions)

                        # 也要保留材料部分作为context
                        # 截取到第一个题目前的内容作为context
                        first_q_pos = re.search(r'\d+\s*[.．、]\s*', content)
                        if first_q_pos:
                            context_content = content[:first_q_pos.start()].strip()
                            if context_content:
                                context_item = {
                                    "type": "context",
                                    "number": original_chunk.get('number', ''),
                                    "content": context_content,
                                    "answer": "",
                                    "analysis": ""
                                }
                                # 插入到题目之前
                                fixed_data.insert(0, context_item)
                    else:
                        # 如果无法拆分，至少创建一个context
                        context_item = {
                            "type": "context",
                            "number": original_chunk.get('number', ''),
                            "content": content,
                            "answer": "",
                            "analysis": ""
                        }
                        fixed_data.append(context_item)
                else:
                    # 如果不包含多个题目，创建context
                    context_item = {
                        "type": "context",
                        "number": original_chunk.get('number', ''),
                        "content": content,
                        "answer": "",
                        "analysis": ""
                    }
                    fixed_data.append(context_item)
        else:
            # 处理正常项目
            fixed_data.append(item)

    # 保存修复后的数据
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print(f'修复完成，保存到: {output_file}')
    print(f'修复后数据长度: {len(fixed_data)}')

    # 打印结果摘要
    contexts = [item for item in fixed_data if item.get('type') == 'context']
    questions = [item for item in fixed_data if item.get('type') == 'question']

    print(f'Contexts: {len(contexts)}, Questions: {len(questions)}')

    if questions:
        print('提取的题目编号:', [q.get('number') for q in questions])

    return fixed_data

if __name__ == '__main__':
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/02_temp_build/section_three_only_extracted.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_section_three_extracted(input_file, output_file)