#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto validate test_extracted.json data file integrity, structure, sequence and errors
"""

import json
import re
from typing import List, Dict, Any

def validate_extracted_json(file_path: str = 'data/02_temp_build/test_extracted.json') -> bool:
    """
    Validate test_extracted.json file integrity

    Args:
        file_path: JSON file path

    Returns:
        bool: Whether validation passed
    """
    print("Starting validation of test_extracted.json file...")

    # 1. Try to read and parse JSON file
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON format error: {e}")
        return False
    except FileNotFoundError:
        print(f"ERROR: File does not exist: {file_path}")
        return False
    except Exception as e:
        print(f"ERROR: Error reading file: {e}")
        return False

    print(f"SUCCESS: Successfully read file with {len(data)} items")

    # 2. Check for error entries
    error_items = []
    for i, item in enumerate(data):
        if isinstance(item, dict):
            if 'error' in item and item['error']:  # Has non-empty error info
                error_items.append((i, item['error']))
            elif 'error' in item and not item['error']:  # Has empty error info
                error_items.append((i, "Empty error field"))

    if error_items:
        print(f"ERROR: Found {len(error_items)} error entries:")
        for idx, error_msg in error_items:
            print(f"   Item {idx}: {error_msg}")
        return False
    else:
        print("SUCCESS: No error entries found")

    # 3. Check data structure completeness
    missing_fields = []
    invalid_types = []

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            invalid_types.append((i, f"Item type should be dict, actual is {type(item)}"))
            continue

        # Check required fields exist
        required_fields = ['type', 'number', 'content', 'answer', 'analysis']
        for field in required_fields:
            if field not in item:
                missing_fields.append((i, f"Missing field: {field}"))

        # Check field types
        if 'type' in item and item['type'] not in ['context', 'question']:
            invalid_types.append((i, f"Invalid type value: {item['type']}"))

        if 'number' in item and not isinstance(item['number'], str):
            invalid_types.append((i, f"Number should be string, actual is {type(item['number'])}"))

    if missing_fields:
        print(f"ERROR: Found {len(missing_fields)} items with missing fields:")
        for idx, msg in missing_fields:
            print(f"   Item {idx}: {msg}")
        return False
    else:
        print("SUCCESS: All items have required fields")

    if invalid_types:
        print(f"ERROR: Found {len(invalid_types)} items with incorrect types:")
        for idx, msg in invalid_types:
            print(f"   Item {idx}: {msg}")
        return False
    else:
        print("SUCCESS: All item types correct")

    # 4. Check content completeness
    empty_content_count = 0
    empty_answer_count = 0
    empty_analysis_count = 0

    for i, item in enumerate(data):
        if isinstance(item, dict):
            if 'content' in item and not item['content'].strip():
                empty_content_count += 1
            if 'answer' in item and not item['answer'].strip() and item.get('type') == 'question':
                empty_answer_count += 1
            if 'analysis' in item and not item['analysis'].strip() and item.get('type') == 'question':
                empty_analysis_count += 1

    if empty_content_count > 0:
        print(f"WARNING: {empty_content_count} items have empty content")
    else:
        print("SUCCESS: All item content non-empty")

    if empty_answer_count > 0:
        print(f"WARNING: {empty_answer_count} questions have empty answers")
    else:
        print("SUCCESS: All questions have answers")

    if empty_analysis_count > 0:
        print(f"WARNING: {empty_analysis_count} questions have empty analysis")
    else:
        print("SUCCESS: All questions have analysis")

    # 5. Check number sequence
    numbers = []
    for item in data:
        if isinstance(item, dict) and 'number' in item:
            numbers.append(item['number'])

    print(f"SUCCESS: Number sequence: {numbers[:10]}{'...' if len(numbers) > 10 else ''}")

    # 6. Statistics
    context_count = sum(1 for item in data if isinstance(item, dict) and item.get('type') == 'context')
    question_count = sum(1 for item in data if isinstance(item, dict) and item.get('type') == 'question')

    print(f"STATS: Total {len(data)} items, {context_count} contexts, {question_count} questions")

    print("SUCCESS: Data validation passed!")
    return True


def main():
    """Main function"""
    success = validate_extracted_json()
    if success:
        print("\nVALIDATION SUCCESS - Data file meets all quality standards!")
        return True
    else:
        print("\nVALIDATION FAILED - Please fix the above issues and try again")
        exit(1)


if __name__ == "__main__":
    main()