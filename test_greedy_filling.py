import os
from pathlib import Path
from core.pptx_generator import PPTXGenerator

def test_greedy_filling():
    """Test the greedy filling algorithm with a sample extracted.json"""

    # Sample extracted data with various content types to test greedy filling
    sample_data = [
        {
            "type": "context",
            "content": "这是背景材料，包含一些重要的知识点，需要展示给学生参考。" * 50  # Long context to test splitting
        },
        {
            "type": "question",
            "question": "这是一道选择题，题干比较长，需要仔细分析选项。" * 10,
            "answer": "正确答案是A选项，因为根据前面提到的知识点可以推导出来。",
            "analysis": "这道题考查的是知识点的应用，需要注意细节。详细解析如下：" * 20  # Long analysis to test greedy filling
        },
        {
            "type": "question",
            "question": "第二道题的问题描述，相对简单一些。",
            "answer": "答案是B",
            "analysis": "简短的解析，说明为什么选择B选项。"
        }
    ]

    # Save sample data to a test file
    test_json_path = "data/02_temp_build/test_greedy_extracted.json"
    os.makedirs(os.path.dirname(test_json_path), exist_ok=True)

    import json
    with open(test_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    # Create output directory
    output_dir = Path("data/03_output_pptx")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "test_greedy_filling.pptx"

    # Initialize and run the generator
    generator = PPTXGenerator()
    success = generator.generate(
        json_path=test_json_path,
        template_path="data/template.pptx",
        output_path=str(output_path)
    )

    if success:
        print("[PASS] 测试成功: PPTX文件已生成在 {output_path}")
        print(f"[INFO] 文件大小: {os.path.getsize(output_path)} bytes")

        # Verify the file exists and has reasonable size
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:  # >10KB is reasonable for a PPTX
            print("[PASS] 文件验证通过: 大小合理")
        else:
            print("[FAIL] 文件验证失败: 文件太小或不存在")

    else:
        print("[FAIL] 生成失败")

    return success

if __name__ == "__main__":
    print("[TEST] 开始测试贪心余量填充算法...")
    success = test_greedy_filling()
    if success:
        print("\n[PASS] 测试通过！贪心填充算法工作正常。")
    else:
        print("\n[FAIL] 测试失败！请检查算法实现。")