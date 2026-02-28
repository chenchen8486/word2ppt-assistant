"""
集成测试模块
整合了原有零散的测试脚本功能
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any


def run_end_to_end_test(docx_path: str = "data/01_input_docs/test.docx"):
    """
    运行端到端测试

    Args:
        docx_path: 输入的docx文件路径
    """
    print("=== 开始端到端测试 ===")

    # 检查输入文件是否存在
    input_path = Path(docx_path)
    if not input_path.exists():
        print(f"错误: 输入文件不存在 {docx_path}")
        return False

    try:
        # 1. 导入必要的模块
        from utils.doc_loader import extract_document_content
        from core.chunk_manager import ChunkManager
        from core.llm_client import LLMClient
        import asyncio

        # 2. 文档解析
        print("步骤 1: 解析文档...")
        extraction_result = extract_document_content(str(input_path))
        markdown_path = extraction_result['markdown_file_path']
        print(f"✓ 文档解析完成: {markdown_path}")

        # 3. 内容分块
        print("步骤 2: 内容分块...")
        chunk_manager = ChunkManager()
        chunk_result = chunk_manager.process_markdown_file(markdown_path)
        chunks_path = chunk_result['output_path']
        print(f"✓ 内容分块完成: {chunks_path}")

        # 4. LLM提取
        print("步骤 3: LLM结构化提取...")
        client = LLMClient()
        extracted_result = asyncio.run(client.process_chunks_file(chunks_path))
        extracted_path = extracted_result['output_path']
        print(f"✓ LLM提取完成: {extracted_path}")

        # 5. 渲染
        print("步骤 4: 渲染为Marp...")
        from core.marp_renderer import MarpRenderer
        renderer = MarpRenderer()
        final_md_path = renderer.render_from_file(extracted_path)
        print(f"✓ Marp渲染完成: {final_md_path}")

        # 6. 转换为PPTX
        print("步骤 5: 转换为PPTX...")
        pptx_path = renderer.convert_to_pptx(final_md_path)
        if pptx_path:
            print(f"✓ PPTX转换完成: {pptx_path}")
        else:
            print("✗ PPTX转换失败")
            return False

        print("=== 端到端测试完成 ===")
        return True

    except Exception as e:
        print(f"端到端测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_test_pptx_generation(extracted_json_path: str = "data/02_temp_build/test_extracted.json"):
    """
    测试PPTX生成

    Args:
        extracted_json_path: 提取结果的JSON文件路径
    """
    print("=== 开始PPTX生成测试 ===")

    json_path = Path(extracted_json_path)
    if not json_path.exists():
        print(f"错误: JSON文件不存在 {extracted_json_path}")
        return False

    try:
        from core.marp_renderer import MarpRenderer

        # 渲染为Markdown
        print("步骤 1: 渲染为Marp Markdown...")
        renderer = MarpRenderer()
        final_md_path = renderer.render_from_file(str(json_path))
        print(f"✓ Marp渲染完成: {final_md_path}")

        # 转换为PPTX
        print("步骤 2: 转换为PPTX...")
        pptx_path = renderer.convert_to_pptx(final_md_path)
        if pptx_path:
            print(f"✓ PPTX生成完成: {pptx_path}")
            print("=== PPTX生成测试完成 ===")
            return True
        else:
            print("✗ PPTX转换失败")
            return False

    except Exception as e:
        print(f"PPTX生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_phase3_validation(json_path: str = "data/02_temp_build/test_extracted.json"):
    """
    运行Phase 3验证（渲染验证）

    Args:
        json_path: JSON文件路径
    """
    print("=== 开始Phase 3验证 ===")

    json_file = Path(json_path)
    if not json_file.exists():
        print(f"错误: JSON文件不存在 {json_path}")
        return False

    try:
        from core.marp_renderer import MarpRenderer

        # 尝试渲染
        print("尝试渲染JSON数据...")
        renderer = MarpRenderer()
        md_path = renderer.render_from_file(str(json_file))
        print(f"✓ 渲染成功: {md_path}")

        print("=== Phase 3验证完成 ===")
        return True

    except Exception as e:
        print(f"Phase 3验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_comprehensive_check(json_path: str = "data/02_temp_build/test_extracted.json"):
    """
    运行综合检查

    Args:
        json_path: JSON文件路径
    """
    print("=== 开始综合检查 ===")

    json_file = Path(json_path)
    if not json_file.exists():
        print(f"错误: JSON文件不存在 {json_path}")
        return False

    try:
        # 读取JSON数据
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        # 统计信息
        total_items = len(data)
        error_count = sum(1 for item in data if 'error' in item)
        context_count = sum(1 for item in data if item.get('type') == 'context')
        question_count = sum(1 for item in data if item.get('type') == 'question')

        print(f"总项目数: {total_items}")
        print(f"错误项目数: {error_count}")
        print(f"context项目数: {context_count}")
        print(f"question项目数: {question_count}")

        # 检查必需字段
        missing_fields = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                if 'type' not in item:
                    missing_fields.append(f"项目{i}: 缺少type字段")
                if 'number' not in item:
                    missing_fields.append(f"项目{i}: 缺少number字段")
                if 'content' not in item:
                    missing_fields.append(f"项目{i}: 缺少content字段")

                if item.get('type') == 'question':
                    if 'answer' not in item:
                        missing_fields.append(f"问题{i}: 缺少answer字段")
                    if 'analysis' not in item:
                        missing_fields.append(f"问题{i}: 缺少analysis字段")

        if missing_fields:
            print(f"发现{len(missing_fields)}个字段缺失问题:")
            for field in missing_fields[:10]:  # 只显示前10个
                print(f"  - {field}")
            if len(missing_fields) > 10:
                print(f"  ... 还有{len(missing_fields)-10}个问题")
        else:
            print("√ 所有项目字段完整")

        # 检查数据类型
        type_errors = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                type_errors.append(f"项目{i}: 不是字典类型")
                continue

            if not isinstance(item.get('type'), str):
                type_errors.append(f"项目{i}: type字段不是字符串")
            if not isinstance(item.get('number'), str):
                type_errors.append(f"项目{i}: number字段不是字符串")
            if not isinstance(item.get('content'), str):
                type_errors.append(f"项目{i}: content字段不是字符串")

            if item.get('type') == 'question':
                if not isinstance(item.get('answer'), str):
                    type_errors.append(f"问题{i}: answer字段不是字符串")
                if not isinstance(item.get('analysis'), str):
                    type_errors.append(f"问题{i}: analysis字段不是字符串")

        if type_errors:
            print(f"发现{len(type_errors)}个类型错误:")
            for error in type_errors[:10]:
                print(f"  - {error}")
            if len(type_errors) > 10:
                print(f"  ... 还有{len(type_errors)-10}个错误")
        else:
            print("√ 所有项目类型正确")

        print("=== 综合检查完成 ===")
        return len(missing_fields) == 0 and len(type_errors) == 0

    except Exception as e:
        print(f"综合检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 根据命令行参数执行不同的测试
    if len(sys.argv) < 2:
        print("用法: python integration_tests.py [e2e|pptx|phase3|comprehensive] [file_path]")
        sys.exit(1)

    test_type = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if test_type == "e2e":
        result = run_end_to_end_test(file_path or "data/01_input_docs/test.docx")
    elif test_type == "pptx":
        result = run_test_pptx_generation(file_path or "data/02_temp_build/test_extracted.json")
    elif test_type == "phase3":
        result = run_phase3_validation(file_path or "data/02_temp_build/test_extracted.json")
    elif test_type == "comprehensive":
        result = run_comprehensive_check(file_path or "data/02_temp_build/test_extracted.json")
    else:
        print(f"未知的测试类型: {test_type}")
        sys.exit(1)

    sys.exit(0 if result else 1)