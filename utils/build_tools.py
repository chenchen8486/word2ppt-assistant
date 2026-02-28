"""
构建工具模块
整合了原有的build目录中的构建功能
"""
import json
from pathlib import Path
from typing import List, Dict, Any


def build_from_chunks(chunks_file_path: str, extracted_file_path: str = None) -> str:
    """
    从分块文件构建提取结果

    Args:
        chunks_file_path: 分块文件路径
        extracted_file_path: 提取结果文件路径（如果未指定则自动生成）

    Returns:
        构建结果文件路径
    """
    if extracted_file_path is None:
        chunks_path = Path(chunks_file_path)
        extracted_file_path = str(chunks_path.parent / f"{chunks_path.stem.replace('_chunks', '')}_extracted.json")

    # 读取分块文件
    with open(chunks_file_path, 'r', encoding='utf-8-sig') as f:
        chunks = json.load(f)

    # 将每个chunk转换为对应的结构化数据
    # 注意：这里我们模拟数据，实际情况下需要通过LLM进行转换
    extracted_data = []
    for chunk in chunks:
        # 根据chunk内容推测类型
        number = chunk.get('number', '')
        content = chunk.get('content', '')

        # 简单判断是否是context还是question
        if any(keyword in number for keyword in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']):
            # 这是一个context
            extracted_data.append({
                'type': 'context',
                'number': number,
                'content': content,
                'answer': '',
                'analysis': ''
            })
        elif re.match(r'^\d+', number):  # 以数字开头，认为是题目
            # 这是一个question
            extracted_data.append({
                'type': 'question',
                'number': number,
                'content': content,
                'answer': '',
                'analysis': ''
            })
        else:
            # 默认作为context处理
            extracted_data.append({
                'type': 'context',
                'number': number,
                'content': content,
                'answer': '',
                'analysis': ''
            })

    # 保存提取结果
    with open(extracted_file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    print(f"从分块文件构建提取结果完成: {extracted_file_path}")
    return extracted_file_path


def reorder_extracted_data(input_file: str, output_file: str = None) -> str:
    """
    重新排序提取的数据，确保context和question的逻辑顺序

    Args:
        input_file: 输入的提取文件路径
        output_file: 输出文件路径（如果未指定则自动生成）

    Returns:
        重排序后的文件路径
    """
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_reordered{input_path.suffix}")

    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # 简单排序：按编号排序
    def sort_key(item):
        number = item.get('number', '')
        # 处理带括号的编号如 "22(1)", "22(2)"
        if '(' in number and ')' in number:
            main_num, sub_num = number.split('(')
            sub_num = sub_num.rstrip(')')
            try:
                return (float(main_num), float(sub_num))
            except:
                return (number, 0)
        elif '（' in number and '）' in number:
            # 处理中文括号
            main_num, sub_num = number.split('（')
            sub_num = sub_num.rstrip('）')
            try:
                return (float(main_num), float(sub_num))
            except:
                return (number, 0)
        else:
            try:
                # 处理中文数字
                chinese_nums = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
                if number in chinese_nums:
                    return (0, chinese_nums[number])  # 中文数字排在前面
                elif number.isdigit():
                    return (1, int(number))  # 阿拉伯数字排在后面
                else:
                    return (2, ord(number[0]) if number else 0)  # 其他字符最后
            except:
                return (2, 0)

    sorted_data = sorted(data, key=sort_key)

    # 保存重排序后的数据
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    print(f"重排序提取数据完成: {output_file}")
    return output_file


def post_process_validate(input_file: str) -> Dict[str, Any]:
    """
    后处理验证

    Args:
        input_file: 输入文件路径

    Returns:
        验证结果
    """
    from .data_validator import validate_data_integrity, validate_number_sequence, validate_field_completeness

    # 执行多项验证
    integrity_result = validate_data_integrity(input_file)
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    sequence_result = validate_number_sequence(data)
    completeness_result = validate_field_completeness(data)

    result = {
        'integrity': integrity_result,
        'sequence': sequence_result,
        'completeness': completeness_result,
        'overall_valid': (
            integrity_result['structure_valid'] and
            sequence_result['is_continuous'] and
            completeness_result['items_with_all_required_fields'] == completeness_result['total_items']
        )
    }

    print(f"后处理验证完成: {input_file}")
    print(f"完整性验证: {'通过' if integrity_result['structure_valid'] else '失败'}")
    print(f"序列连续性: {'连续' if sequence_result['is_continuous'] else '有缺口'}")
    print(f"字段完整性: {completeness_result['items_with_all_required_fields']}/{completeness_result['total_items']} 项完整")

    return result