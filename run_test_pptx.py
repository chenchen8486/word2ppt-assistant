#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简测试脚本 - 验证PPTX生成器功能
"""

import os
from pathlib import Path
from core.pptx_generator import PPTXGenerator

def main():
    # 定义文件路径
    json_path = "data/02_temp_build/test_extracted.json"
    template_path = "data/template.pptx"
    output_path = "data/03_output_pptx/test_output.pptx"

    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 检查输入文件是否存在
    if not Path(json_path).exists():
        print(f"错误: 找不到输入文件 {json_path}")
        # 尝试其他可能的路径
        alternative_paths = [
            "data/02_temp_build/test_extracted.json",
            "data/test_extracted.json",
            "data/02_temp_build/test_final_uniform.md"  # 如果JSON不存在，尝试MD文件
        ]

        found_path = None
        for alt_path in alternative_paths:
            if Path(alt_path).exists():
                found_path = alt_path
                break

        if found_path:
            print(f"找到了替代文件: {found_path}")
            json_path = found_path
        else:
            print("错误: 找不到任何输入文件")
            return

    if not Path(template_path).exists():
        print(f"错误: 找不到模板文件 {template_path}")
        return

    # 创建生成器实例
    generator = PPTXGenerator()

    print("开始生成PPTX...")
    print(f"输入: {json_path}")
    print(f"模板: {template_path}")
    print(f"输出: {output_path}")

    # 生成PPTX
    success = generator.generate(
        json_path=json_path,
        template_path=template_path,
        output_path=output_path
    )

    if success:
        print(f"[SUCCESS] Successfully generated PPTX file: {output_path}")

        # 验证输出文件
        if Path(output_path).exists():
            size = Path(output_path).stat().st_size
            print(f"[INFO] Output file size: {size} bytes")
        else:
            print("[ERROR] Output file not generated")
    else:
        print("[ERROR] PPTX generation failed")

if __name__ == "__main__":
    main()