import json
import re
from typing import List, Dict, Any

def clean_json_content(text: str) -> str:
    """Clean illegal escape characters from text"""
    if not isinstance(text, str):
        return text

    # Clean illegal escapes like \_ and \*
    text = re.sub(r'\\\\([_*])', r'\1', text)  # Replace \\_ with _, \\* with *
    text = re.sub(r'\\([_*])', r'\1', text)    # Replace \_ with _, \* with *

    return text

def fix_extracted_structure(input_file: str = 'data/02_temp_build/test_extracted.json'):
    """
    修复提取文件的结构，确保所有项目都有正确的格式
    """
    print(f"开始修复{input_file}文件结构...")

    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f'原始数据长度: {len(data)}')

    # 统计修复前的信息
    original_errors = sum(1 for item in data if 'error' in item)
    original_contexts = sum(1 for item in data if item.get('type') == 'context')
    original_questions = sum(1 for item in data if item.get('type') == 'question')

    print(f'原始数据统计: {original_errors} 错误, {original_contexts} contexts, {original_questions} questions')

    # 修复数据
    fixed_data = []
    for i, item in enumerate(data):
        # 如果是错误条目，跳过
        if 'error' in item:
            error_msg = item.get('error', '')
            original_chunk = item.get('original_chunk', {})

            # 如果original_chunk中有有效数据，尝试从中恢复
            if original_chunk and isinstance(original_chunk, dict):
                number = original_chunk.get('number', '').strip()
                content = original_chunk.get('content', '')

                if number and content:
                    # 根据编号判断类型
                    if any(keyword in number for keyword in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']):
                        # 这是一个context
                        restored_item = {
                            'type': 'context',
                            'number': number,
                            'content': clean_json_content(content),
                            'answer': '',
                            'analysis': ''
                        }
                        fixed_data.append(restored_item)
                        print(f'  修复并恢复context: {number}')
                    elif re.match(r'^\d+|[（\(]?\d+[）\)]?$', number):
                        # 这是一个question
                        # 从内容中尝试提取答案和解析
                        answer_match = re.search(r'【答案】([^\n]+)', content)
                        analysis_match = re.search(r'【解析】(.+?)(?=【|$)', content, re.DOTALL)

                        restored_item = {
                            'type': 'question',
                            'number': number,
                            'content': clean_json_content(content.split('【答案】')[0]),
                            'answer': clean_json_content(answer_match.group(1)).strip() if answer_match else '',
                            'analysis': clean_json_content(analysis_match.group(1)).strip() if analysis_match else ''
                        }
                        fixed_data.append(restored_item)
                        print(f'  修复并恢复question: {number}')
                    else:
                        print(f'  无法识别条目类型，跳过: {number}')
                else:
                    print(f'  跳过无用错误条目: {i}')
            else:
                print(f'  跳过纯错误条目: {i}')
        else:
            # 检查正常条目是否有缺失字段
            required_fields = ['type', 'number', 'content']
            for field in required_fields:
                if field not in item:
                    item[field] = ''

            # 添加缺失的answer和analysis字段（对于question）
            if item.get('type') == 'question':
                if 'answer' not in item:
                    item['answer'] = ''
                if 'analysis' not in item:
                    item['analysis'] = ''

            # 添加缺失的answer和analysis字段（对于context，默认为空）
            if item.get('type') == 'context':
                if 'answer' not in item:
                    item['answer'] = ''
                if 'analysis' not in item:
                    item['analysis'] = ''

            # 清理内容
            if 'content' in item and isinstance(item['content'], str):
                item['content'] = clean_json_content(item['content'])
            if 'answer' in item and isinstance(item['answer'], str):
                item['answer'] = clean_json_content(item['answer'])
            if 'analysis' in item and isinstance(item['analysis'], str):
                item['analysis'] = clean_json_content(item['analysis'])

            fixed_data.append(item)

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
        else:
            try:
                return (float(num_str), 0)
            except:
                # 如果不是数字，使用字符顺序
                return (ord(num_str[0]) if num_str else 0, 0)

    fixed_data.sort(key=sort_key)

    print(f'修复后数据长度: {len(fixed_data)}')

    # 统计修复后的信息
    fixed_errors = sum(1 for item in fixed_data if 'error' in item)
    fixed_contexts = sum(1 for item in fixed_data if item.get('type') == 'context')
    fixed_questions = sum(1 for item in fixed_data if item.get('type') == 'question')

    print(f'修复后数据统计: {fixed_errors} 错误, {fixed_contexts} contexts, {fixed_questions} questions')

    # 打印数据结构
    print('\n修复后的数据结构:')
    for i, item in enumerate(fixed_data, 1):
        if item.get('type') == 'context':
            print(f' {i:2d}. context: {item.get("number")}')
        elif item.get('type') == 'question':
            print(f' {i:2d}. question: {item.get("number")}')
        else:
            print(f' {i:2d}. unknown: {item.get("number")}')

    print(f'\n总计: {len(fixed_data)} 个项目')
    print(f'Contexts: {sum(1 for item in fixed_data if item.get("type") == "context")}, Questions: {sum(1 for item in fixed_data if item.get("type") == "question")}')

    # 保存修复后的数据
    output_file = input_file.replace('.json', '_fixed.json')
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print(f'修复完成! 输出到: {output_file}')

    return fixed_data

if __name__ == '__main__':
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/02_temp_build/test_extracted.json'
    fix_extracted_structure(input_file)