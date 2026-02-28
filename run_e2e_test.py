#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端测试脚本 - 验证从Word文档到PPTX的完整流程
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.batch_processor import BatchProcessor


def main():
    print("[TEST] 开始端到端测试...")

    # 创建批处理器实例
    def safe_log(msg):
        # 移除或替换可能引起编码问题的Unicode字符
        safe_msg = msg.replace('✓', '[OK]').replace('✗', '[ERROR]')
        try:
            print(f"[LOG] {safe_msg}")
        except UnicodeEncodeError:
            # 如果仍有编码问题，进一步清理
            safe_msg = safe_msg.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"[LOG] {safe_msg}")

    processor = BatchProcessor(
        log_callback=safe_log,
        model_name="deepseek"  # 使用默认模型
    )

    # 测试单个文件处理
    test_docx_path = "data/01_input_docs/test.docx"

    # 检查测试文档是否存在
    if not Path(test_docx_path).exists():
        print(f"[WARN] 测试文档不存在: {test_docx_path}")

        # 尝试查找任何.docx文件
        input_dir = Path("data/01_input_docs/")
        docx_files = list(input_dir.glob("*.docx"))

        if docx_files:
            test_docx_path = str(docx_files[0])
            print(f"[INFO] 使用找到的文档: {test_docx_path}")
        else:
            print("[ERROR] 没有找到任何.docx文件进行测试")
            return

    print(f"[INFO] 开始处理文档: {test_docx_path}")

    try:
        # 处理单个文件
        processor.process_single_file(test_docx_path)
        print("[SUCCESS] 文件处理完成")
    except Exception as e:
        print(f"[ERROR] 处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()