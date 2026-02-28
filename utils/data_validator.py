"""
数据验证工具模块
整合了原有的validation目录中的验证功能
"""
import json
import re
from typing import List, Dict, Any


def validate_json_structure(data: Any) -> bool:
    """
    验证JSON数据结构是否合法

    Args:
        data: 待验证的数据

    Returns:
        验证结果
    """
    if not isinstance(data, list):
        return False

    for item in data:
        if not isinstance(item, dict):
            return False

        # 检查必需字段
        required_fields = ['type', 'number', 'content']
        for field in required_fields:
            if field not in item:
                return False

        # 验证 type 值
        item_type = item.get('type', '').lower()
        if item_type not in ['context', 'question']:
            return False

        # 如果是 question 类型，检查额外字段
        if item_type == 'question':
            if 'answer' not in item or 'analysis' not in item:
                return False

    return True


def validate_data_integrity(file_path: str) -> Dict[str, Any]:
    """
    验证数据完整性

    Args:
        file_path: JSON文件路径

    Returns:
        验证结果统计
    """
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    stats = {
        'total_items': len(data),
        'valid_items': 0,
        'invalid_items': 0,
        'contexts': 0,
        'questions': 0,
        'errors': 0,
        'missing_fields': [],
        'structure_valid': True
    }

    for i, item in enumerate(data):
        if isinstance(item, dict):
            if 'error' in item:
                stats['errors'] += 1
                continue

            # 检查必需字段
            required_fields = ['type', 'number', 'content']
            item_valid = True
            for field in required_fields:
                if field not in item:
                    stats['missing_fields'].append(f"Item {i}: missing '{field}'")
                    item_valid = False

            if item_valid:
                item_type = item.get('type', '').lower()
                if item_type == 'context':
                    stats['contexts'] += 1
                elif item_type == 'question':
                    stats['questions'] += 1
                    # 检查question的必需字段
                    for field in ['answer', 'analysis']:
                        if field not in item:
                            stats['missing_fields'].append(f"Question {item.get('number', i)}: missing '{field}'")
                            item_valid = False
                else:
                    item_valid = False

            if item_valid:
                stats['valid_items'] += 1
            else:
                stats['invalid_items'] += 1
        else:
            stats['invalid_items'] += 1

    stats['structure_valid'] = stats['invalid_items'] == 0 and len(stats['missing_fields']) == 0

    return stats


def validate_number_sequence(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    验证题目编号序列是否连续

    Args:
        data: JSON数据列表

    Returns:
        序列验证结果
    """
    numbers = []
    for item in data:
        if isinstance(item, dict) and 'number' in item and item.get('type') == 'question':
            num = item['number']
            # 处理带括号的编号如 "22（1）"
            if '（' in num:
                parts = re.match(r'(\d+)（(\d+)）', num)
                if parts:
                    main_num, sub_num = parts.groups()
                    numbers.append(float(main_num) + float(sub_num)/10.0)
            elif num.isdigit():
                numbers.append(int(num))

    numbers.sort()

    result = {
        'numbers_found': numbers,
        'min_num': min(numbers) if numbers else 0,
        'max_num': max(numbers) if numbers else 0,
        'gaps': [],
        'is_continuous': True
    }

    if numbers:
        expected = list(range(int(result['min_num']), int(result['max_num']) + 1))
        result['gaps'] = [num for num in expected if num not in numbers]
        result['is_continuous'] = len(result['gaps']) == 0

    return result


def validate_field_completeness(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    验证字段完整性

    Args:
        data: JSON数据列表

    Returns:
        字段完整性验证结果
    """
    completeness_stats = {
        'total_items': len(data),
        'items_with_all_required_fields': 0,
        'field_presence': {},
        'issues': []
    }

    required_fields = ['type', 'number', 'content']
    question_specific_fields = ['answer', 'analysis']

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            completeness_stats['issues'].append(f"Item {i} is not a dictionary")
            continue

        # 检查必需字段
        has_all_required = True
        for field in required_fields:
            if field not in item:
                completeness_stats['issues'].append(f"Item {i} missing required field: {field}")
                has_all_required = False
            else:
                completeness_stats['field_presence'][field] = completeness_stats['field_presence'].get(field, 0) + 1

        # 如果是question类型，检查特定字段
        if item.get('type', '').lower() == 'question':
            for field in question_specific_fields:
                if field not in item:
                    completeness_stats['issues'].append(f"Question {item.get('number', i)} missing field: {field}")
                    has_all_required = False
                else:
                    completeness_stats['field_presence'][field] = completeness_stats['field_presence'].get(field, 0) + 1

        if has_all_required:
            completeness_stats['items_with_all_required_fields'] += 1

    return completeness_stats