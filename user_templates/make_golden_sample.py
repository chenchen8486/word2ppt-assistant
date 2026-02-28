import json
import os

def create_golden_samples():
    template_dir = r"D:\project\python\word2ppt-assistant\user_templates"
    os.makedirs(template_dir, exist_ok=True)
    
    # 1. 黄金输入样本 (模拟复杂的 Markdown 试卷片段)
    raw_input_content = """**![](data:image/png;base64...)绝密★启用前**
**注意事项：答题前请仔细阅读**

**一、（9分）**
阅读下面一段文字，完成下面小题。
我一直认为，年是中国人的文化修行，书法化身精神图腾。当稠浓黑亮的墨汁落于红纸上，家乡的年就到了。
纸上乾坤大，笔下日月长。春联承传中华文化，一笔一画蕴藏满满的期冀。

1. 下列对文章的理解和分析，不正确的一项是（3分）
A. 春联担当了季候启蒙。
B. 写春联是父亲雷打不动的年俗。
C. 墨汁没有发生任何变化。
D. 春联蕴藏着满满的期冀。

**二、主观题**
24. 阅读下面的材料，根据要求写作。（60分）
材料略。请结合材料写一篇文章。
【答案】略
【解析】
【详解】本题考查学生写作能力。
审题：这是一道引语类材料作文题。材料意在引导学生思考个人成长。
"""

    # 2. 黄金输出样本 (严格对应上面的输入，教会 LLM 如何结构化)
    target_output_json = [
        {
            "type": "context",
            "number": "一",
            "content": "阅读下面一段文字，完成下面小题。\n我一直认为，年是中国人的文化修行，书法化身精神图腾。当稠浓黑亮的墨汁落于红纸上，家乡的年就到了。\n纸上乾坤大，笔下日月长。春联承传中华文化，一笔一画蕴藏满满的期冀。",
            "answer": "",
            "analysis": ""
        },
        {
            "type": "question",
            "number": "1",
            "content": "下列对文章的理解和分析，不正确的一项是（3分）\nA. 春联担当了季候启蒙。\nB. 写春联是父亲雷打不动的年俗。\nC. 墨汁没有发生任何变化。\nD. 春联蕴藏着满满的期冀。",
            "answer": "",
            "analysis": ""
        },
        {
            "type": "question",
            "number": "24",
            "content": "阅读下面的材料，根据要求写作。（60分）\n材料略。请结合材料写一篇文章。",
            "answer": "略",
            "analysis": "【详解】本题考查学生写作能力。\n审题：这是一道引语类材料作文题。材料意在引导学生思考个人成长。"
        }
    ]

    # 保存为文件，强制使用 utf-8-sig
    input_path = os.path.join(template_dir, "01_raw_input.md")
    with open(input_path, 'w', encoding='utf-8-sig') as f:
        f.write(raw_input_content)

    output_path = os.path.join(template_dir, "02_target_output.json")
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        json.dump(target_output_json, f, ensure_ascii=False, indent=2)

    print(f"✅ 黄金样本已成功生成至: {template_dir}")

if __name__ == "__main__":
    create_golden_samples()