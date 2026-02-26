import os
from markitdown import MarkItDown

def create_golden_workspace(docx_path, output_dir="golden_samples"):
    """
    读取 Word 文档片段，生成供人工编辑的黄金样本工作区。
    采用 utf-8-sig 编码，确保在不同 IDE（如 VS2019, Cursor）中中文显示无乱码。
    """
    if not os.path.exists(docx_path):
        print(f"❌ 找不到文件: {docx_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"🚀 正在解析 {docx_path} ...")

    # 1. 提取原始 Markdown
    md_client = MarkItDown()
    try:
        result = md_client.convert(docx_path)
        raw_md = result.text_content
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return

    # 保存原始对照文本
    raw_md_path = os.path.join(output_dir, "01_raw_input.md")
    with open(raw_md_path, "w", encoding="utf-8-sig") as f:
        f.write(raw_md)

    # 2. 生成目标 JSON 骨架模板 (供 LLM 结构化抽取参考)
    json_template = """[
  {
    "type": "context",
    "text": "在这里填入提取出的纯净导读或背景材料原文..."
  },
  {
    "type": "question",
    "number": "1",
    "content": "在这里填入题干和选项...",
    "answer": "在这里填入答案...",
    "analysis": "在这里填入详解..."
  }
]"""
    json_path = os.path.join(output_dir, "02_target_output.json")
    with open(json_path, "w", encoding="utf-8-sig") as f:
        f.write(json_template)

    # 3. 生成目标 Marp MD 骨架模板 (供最终渲染对照)
    marp_template = """---
marp: true
theme: custom_theme
paginate: true
---

# 一、大题标题
<div class="context-box">
这里是导语和阅读材料，使用稍小字号...
</div>

---

## 1. 题干内容
A. 选项A
B. 选项B

---

## 1. 题干内容
**【答案】** A
**【解析】** 这里是详细的解析过程...
"""
    marp_path = os.path.join(output_dir, "03_target_output.md")
    with open(marp_path, "w", encoding="utf-8-sig") as f:
        f.write(marp_template)

    print(f"✅ 黄金样本车间已创建完毕！存储于: ./{output_dir}/")
    print(f"👉 第一步: 打开 {raw_md_path} 查看 MarkItDown 提取的原始文本。")
    print(f"👉 第二步: 复制里面的内容，人工精简并填入 {json_path}。")
    print(f"👉 第三步: 这份完美的 JSON 将被固化到代码里，作为未来 LLM 的 Few-Shot 提示词！")

if __name__ == "__main__":
    # 使用示例：将你要测试的一小段 word 放在同级目录下
    create_golden_workspace("template_input.docx")
    pass