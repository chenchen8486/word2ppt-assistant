import json
import re
from typing import List, Dict, Any

def validate_extracted_json(file_path: str = 'data/02_temp_build/test_extracted_merged.json'):
    """
    验证提取的JSON文件的完整性和正确性
    """
    print(f"开始综合验证 {file_path} ...")

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f"总项目数: {len(data)}")

    # 检查是否有错误条目
    error_items = [item for item in data if 'error' in item]
    if not error_items:
        print("[OK] 无错误条目")
    else:
        print(f"[ERROR] 发现 {len(error_items)} 个错误条目")
        for item in error_items:
            print(f"  - 错误条目: {item}")

    # 检查项目结构
    structurally_correct = True
    for i, item in enumerate(data):
        required_fields = ['type', 'number', 'content']
        missing_fields = [field for field in required_fields if field not in item]

        if missing_fields:
            print(f"[ERROR] 第{i+1}项缺少字段: {missing_fields}")
            structurally_correct = False

    if structurally_correct:
        print("[OK] 所有项目结构正确")

    # 统计各类项目
    contexts = [item for item in data if item.get('type') == 'context']
    questions = [item for item in data if item.get('type') == 'question']

    print(f"\n[STAT] 项目统计: {len(contexts)} 个context, {len(questions)} 个question")

    # 检查是否包含所有预期的context
    expected_contexts = {'一', '二', '三', '四', '五', '六', '七'}
    actual_contexts = {item.get('number', '').strip('、') for item in contexts}
    missing_contexts = expected_contexts.intersection({'三', '五'}) - actual_contexts

    if missing_contexts:
        print(f"[WARN] 缺少 context 编号: {missing_contexts}")
    else:
        print(f"[OK] 所有预期的 context 都存在: {actual_contexts}")

    # 获取所有question编号
    question_numbers = []
    for q in questions:
        num = q.get('number', '')
        # 处理带括号的编号如 "22(1)"
        if '(' in num and ')' in num:
            main_num, sub_num = num.split('(')
            sub_num = sub_num.rstrip(')')
            # 创建复合编号表示法
            question_numbers.append(f"{main_num}({sub_num})")
        else:
            question_numbers.append(num)

    # 期望的题目编号（1-24题，但有些可能缺失）
    expected_questions = set(range(1, 25))
    actual_questions_set = set()

    for num in question_numbers:
        if '(' in num:  # 处理子题如 "22(1)"
            main_num = num.split('(')[0]
            try:
                actual_questions_set.add(int(main_num))
            except:
                continue
        else:
            try:
                actual_questions_set.add(int(num))
            except:
                continue

    # 查找缺失的题目
    missing_questions = expected_questions - actual_questions_set
    if missing_questions:
        print(f"[WARN] 缺少 question 编号: {sorted(list(missing_questions))}")
    else:
        print("[OK] 所有预期的 question 都存在")

    # 检查数据顺序
    print("\n[ORDER] 数据顺序:")
    context_order_ok = True
    for i, item in enumerate(data):
        if item.get('type') == 'context':
            # 检查下一个项目是否为question或另一个context
            if i + 1 < len(data):
                next_item = data[i + 1]
                if next_item.get('type') == 'context':
                    print(f"  {i+1:2d}. [WARN] Context直接跟Context: {item.get('number')} -> {next_item.get('number')}")
                else:
                    print(f"  {i+1:2d}. [OK] Context后跟{next_item.get('type')}: {item.get('number')}")
            else:
                print(f"  {i+1:2d}. [INFO] 最后一个项目: {item.get('number')}")
        elif item.get('type') == 'question':
            print(f"  {i+1:2d}. [INFO] Question: {item.get('number')}")

    # 检查question字段完整性
    print("\n[FIELD] 字段完整性检查:")
    questions_without_answer_or_analysis = []
    for q in questions:
        if not q.get('answer') or not q.get('analysis'):
            questions_without_answer_or_analysis.append(q.get('number'))

    if not questions_without_answer_or_analysis:
        print("  [OK] 所有 Question 项目都包含 answer 和 analysis")
    else:
        print(f"  [WARN] {len(questions_without_answer_or_analysis)} 个Question缺少answer或analysis字段: {questions_without_answer_or_analysis}")

    # 总结
    print(f"\n[SUCCESS] 验证完成")
    print(f"- 总项目数: {len(data)}")
    print(f"- Contexts: {len(contexts)}")
    print(f"- Questions: {len(questions)}")
    print(f"- 错误项目: {len(error_items)}")
    print(f"- 数据组数: {len([item for item in data if item.get('type') == 'context'])}")

    success = len(error_items) == 0 and structurally_correct

    if success:
        print("\n[SUCCESS] 所有验证通过!")
        return True
    else:
        print(f"\n[FAIL] 某些验证失败，请检查以上警告和错误信息。")
        return False

if __name__ == '__main__':
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'data/02_temp_build/test_extracted_merged.json'
    validate_extracted_json(file_path)